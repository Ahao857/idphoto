# -*- coding: utf-8 -*-
"""
证件照制作工具
功能：自动抠图 + 红白蓝换底 + 一寸/二寸等尺寸 + 相纸排版 + 300DPI 高清无损导出
运行：python idphoto.py
"""
import os, time, tempfile

# 让 AI 模型优先从项目下 models/ 目录读取（便于离线使用和打包分发）
_MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
if os.path.isdir(_MODEL_DIR):
    os.environ["U2NET_HOME"] = _MODEL_DIR

import numpy as np
from PIL import Image, ImageOps, ImageDraw
import gradio as gr
from rembg import remove, new_session

# =============== 基础参数 ===============
DPI = 300
def mm2px(mm):
    return round(mm / 25.4 * DPI)

# 证件照尺寸（300 DPI 标准像素）
SIZES = {
    "一寸 25×35mm":    (mm2px(25), mm2px(35)),   # 295×413
    "小一寸 22×32mm":  (mm2px(22), mm2px(32)),
    "大一寸 33×48mm":  (mm2px(33), mm2px(48)),
    "二寸 35×49mm":    (mm2px(35), mm2px(49)),   # 413×579
    "小二寸 35×45mm":  (mm2px(35), mm2px(45)),
}

# 证件照标准底色
COLORS = {
    "红底": (255, 0, 0),
    "白底": (255, 255, 255),
    "蓝底": (67, 142, 219),
}

# 相纸规格
PAPERS = {
    "5寸相纸 3.5×5in":  (mm2px(89), mm2px(127)),
    "6寸相纸 4×6in":    (mm2px(102), mm2px(152)),
    "A4 210×297mm":     (mm2px(210), mm2px(297)),
}

# 排版方式（列, 行）
LAYOUTS = {
    "自动排满": None,
    "1×1（单张）": (1, 1),
    "2×2（4张）": (2, 2),
    "2×4（8张）": (2, 4),
    "3×3（9张）": (3, 3),
    "3×4（12张）": (3, 4),
    "4×4（16张）": (4, 4),
}

# =============== AI 模型会话（懒加载） ===============
_SESSION = None
def get_session():
    global _SESSION
    if _SESSION is None:
        # 人像专用模型；想更精细可换 "isnet-general-use" 或 "birefnet-portrait"
        _SESSION = new_session("u2net_human_seg")
    return _SESSION

# =============== 第 1 步：抠图 ===============
def do_cutout(img, matting):
    if img is None:
        raise gr.Error("请先上传照片")
    img = ImageOps.exif_transpose(img).convert("RGBA")
    kw = dict(session=get_session())
    if matting:
        kw.update(
            alpha_matting=True,
            alpha_matting_foreground_threshold=240,
            alpha_matting_background_threshold=10,
            alpha_matting_erode_size=10,
        )
    try:
        out = remove(img, **kw)
    except Exception:
        # 发丝优化失败时退回普通模式
        out = remove(img, session=get_session())
    return out, out

# =============== 第 2 步：裁剪 + 换底 ===============
def make_photo(cut, size_name, color_name, zoom, dx, dy):
    if cut is None:
        return None
    tw, th = SIZES[size_name]
    color = COLORS[color_name]
    W, H = cut.size

    # 根据透明通道找到人像范围
    alpha = np.array(cut.split()[-1])
    ys, xs = np.where(alpha > 20)
    if len(xs) == 0:
        bx0, by0, bx1, by1 = 0, 0, W, H
    else:
        bx0, by0, bx1, by1 = xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
    bw = bx1 - bx0
    ratio = tw / th

    # 裁剪框：宽度为人像宽度的 1.5 倍（可由 zoom 调整），头顶留 12% 空白
    crop_w = bw * 1.5 / zoom
    crop_h = crop_w / ratio
    top = by0 - 0.12 * crop_h
    # 若裁剪框超出照片底部则贴底；若贴底会切到头顶则放大裁剪框
    if top + crop_h > H:
        top = H - crop_h
        if top > by0 - 0.03 * crop_h:
            crop_h = (H - by0) / 0.92
            crop_w = crop_h * ratio
            top = H - crop_h
    cx = (bx0 + bx1) / 2
    left = cx - crop_w / 2
    left += dx * crop_w
    top += dy * crop_h

    canvas = Image.new("RGBA", (int(crop_w), int(crop_h)), color + (255,))
    canvas.alpha_composite(cut, (int(-left), int(-top)))
    photo = canvas.convert("RGB").resize((tw, th), Image.LANCZOS)
    return photo

# =============== 第 3 步：排版 ===============
def make_sheet(photo, paper_name, layout_name, gap_mm, cut_lines):
    if photo is None:
        return None
    pw, ph = PAPERS[paper_name]
    w, h = photo.size
    gap = mm2px(gap_mm)

    def capacity(PW, PH):
        return max(0, (PW - gap) // (w + gap)), max(0, (PH - gap) // (h + gap))

    if LAYOUTS[layout_name] is None:
        # 自动排满：比较纵向/横向纸张哪种放得多
        c1, r1 = capacity(pw, ph)
        c2, r2 = capacity(ph, pw)
        if c2 * r2 > c1 * r1:
            pw, ph, cols, rows = ph, pw, c2, r2
        else:
            cols, rows = c1, r1
    else:
        cols, rows = LAYOUTS[layout_name]
        if cols * w + (cols + 1) * gap > pw or rows * h + (rows + 1) * gap > ph:
            pw, ph = ph, pw  # 尝试横向纸张
            if cols * w + (cols + 1) * gap > pw or rows * h + (rows + 1) * gap > ph:
                raise gr.Error(f"{paper_name} 放不下 {layout_name}，请换更大的纸或减少数量")
    if cols == 0 or rows == 0:
        raise gr.Error("纸张太小，放不下一张照片")

    sheet = Image.new("RGB", (pw, ph), (255, 255, 255))
    draw = ImageDraw.Draw(sheet)
    total_w = cols * w + (cols - 1) * gap
    total_h = rows * h + (rows - 1) * gap
    ox, oy = (pw - total_w) // 2, (ph - total_h) // 2
    for r in range(rows):
        for c in range(cols):
            x, y = ox + c * (w + gap), oy + r * (h + gap)
            sheet.paste(photo, (x, y))
            if cut_lines:
                draw.rectangle([x - 1, y - 1, x + w, y + h], outline=(180, 180, 180), width=1)
    return sheet

# =============== 导出（无损 / 不压缩） ===============
def export(cut, size_name, color_name, zoom, dx, dy,
           paper_name, layout_name, gap_mm, cut_lines):
    if cut is None:
        raise gr.Error("请先点击「一键抠图」")
    photo = make_photo(cut, size_name, color_name, zoom, dx, dy)
    sheet = make_sheet(photo, paper_name, layout_name, gap_mm, cut_lines)

    out_dir = os.path.join(tempfile.gettempdir(), "idphoto_out")
    os.makedirs(out_dir, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    tag = f"{size_name.split()[0]}_{color_name}"
    paper_tag = paper_name.split()[0]
    files = []

    p = os.path.join(out_dir, f"证件照_{tag}_{ts}.png")
    photo.save(p, "PNG", dpi=(DPI, DPI), compress_level=0); files.append(p)

    p = os.path.join(out_dir, f"证件照_{tag}_{ts}.jpg")
    photo.save(p, "JPEG", quality=100, subsampling=0, dpi=(DPI, DPI)); files.append(p)

    p = os.path.join(out_dir, f"排版_{tag}_{paper_tag}_{ts}.png")
    sheet.save(p, "PNG", dpi=(DPI, DPI), compress_level=0); files.append(p)

    p = os.path.join(out_dir, f"排版_{tag}_{paper_tag}_{ts}.jpg")
    sheet.save(p, "JPEG", quality=100, subsampling=0, dpi=(DPI, DPI)); files.append(p)

    return files, photo, sheet

# =============== 界面 ===============
with gr.Blocks(title="证件照制作工具") as demo:
    gr.Markdown("## 📷 证件照制作工具：自动抠图 · 红白蓝换底 · 一寸/二寸 · 排版 · 高清导出")
    cut_state = gr.State(None)

    # ① 上传 + 抠图
    with gr.Row():
        with gr.Column():
            inp = gr.Image(type="pil", label="① 上传照片（正面、光线均匀效果最佳）")
            matting = gr.Checkbox(True, label="发丝边缘优化（更精细，稍慢）")
            btn_cut = gr.Button("✂️ 一键抠图", variant="primary")
        with gr.Column():
            cut_view = gr.Image(type="pil", label="抠图结果（透明底）", format="png")

    # ② 尺寸 / 底色 / 微调
    gr.Markdown("### ② 尺寸 / 底色 / 构图微调（实时预览）")
    with gr.Row():
        with gr.Column():
            size = gr.Radio(list(SIZES), value="一寸 25×35mm", label="照片尺寸")
            color = gr.Radio(list(COLORS), value="蓝底", label="背景颜色")
            zoom = gr.Slider(0.5, 2.0, 1.0, step=0.02, label="缩放（大=人像更大）")
            dx = gr.Slider(-0.3, 0.3, 0.0, step=0.01, label="左右平移")
            dy = gr.Slider(-0.3, 0.3, 0.0, step=0.01, label="上下平移")
        with gr.Column():
            photo_view = gr.Image(type="pil", label="单张预览", format="png")

    # ③ 排版
    gr.Markdown("### ③ 排版")
    with gr.Row():
        with gr.Column():
            paper = gr.Radio(list(PAPERS), value="6寸相纸 4×6in", label="相纸")
            layout = gr.Dropdown(list(LAYOUTS), value="自动排满", label="排版方式")
            gap = gr.Slider(0, 10, 2, step=0.5, label="照片间距 (mm)")
            lines = gr.Checkbox(True, label="显示裁切线")
        with gr.Column():
            sheet_view = gr.Image(type="pil", label="排版预览", format="png")

    # ④ 导出
    btn_export = gr.Button(
        "⬇️ 生成并导出高清文件（PNG无损 + JPG 100%质量，300DPI）",
        variant="primary", size="lg")
    files_out = gr.Files(label="下载文件")

    # 事件绑定
    btn_cut.click(do_cutout, [inp, matting], [cut_state, cut_view]) \
           .then(make_photo, [cut_state, size, color, zoom, dx, dy], photo_view) \
           .then(make_sheet, [photo_view, paper, layout, gap, lines], sheet_view)

    for comp in (size, color, zoom, dx, dy):
        comp.change(make_photo, [cut_state, size, color, zoom, dx, dy], photo_view) \
            .then(make_sheet, [photo_view, paper, layout, gap, lines], sheet_view)

    for comp in (paper, layout, gap, lines):
        comp.change(make_sheet, [photo_view, paper, layout, gap, lines], sheet_view)

    btn_export.click(
        export,
        [cut_state, size, color, zoom, dx, dy, paper, layout, gap, lines],
        [files_out, photo_view, sheet_view])

if __name__ == "__main__":
    demo.launch(inbrowser=True)
