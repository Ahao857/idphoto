# 证件照制作工具 · ID Photo Studio

> 上传照片 → AI 自动抠图 → 一键换红 / 白 / 蓝底 → 一寸 / 二寸等尺寸 → 相纸排版 → 300 DPI 高清无损导出

[English](#english) | [中文](#中文)

---

## 中文

### ✨ 功能

- 🤖 **AI 自动抠图**：基于 `rembg`（u2net_human_seg 模型），发丝/边缘细节干净
- 🎨 **红 / 白 / 蓝底一键切换**
- 📐 **标准证件尺寸**：一寸、小一寸、大一寸、二寸、小二寸（300 DPI，像素与公安标准一致）
- 🖼️ **相纸排版**：5 寸 / 6 寸 / A4，支持自动排满、1×1～4×4 多种版式，可显示裁切线
- 🔍 **实时预览**：拖动滑块微调人像缩放与位置
- 💾 **高清无损导出**：PNG 无损 + JPG 100% 质量，全部 300 DPI，打印店可直接用

### 🚀 快速开始

**Windows**

```bat
双击 一键安装并运行.bat
```

**Mac / Linux**

```bash
chmod +x run.sh
./run.sh
```

首次运行会自动创建虚拟环境、安装依赖，并打开浏览器 `http://127.0.0.1:7860`。

### 🧩 离线模型（可选）

抠图模型 `u2net_human_seg.onnx`（约 170MB）首次运行会自动下载。需要离线/分发时，手动放到：

```
models/u2net_human_seg.onnx
```

下载地址：<https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2net_human_seg.onnx>

### 📦 打包成免安装 exe（Windows）

```bat
双击 打包成exe.bat
```

产物在 `dist\证件照工具\`，整个文件夹压缩即可发给他人，对方无需安装 Python。

### 🖼️ 效果预览

| 抠图结果 | 一寸三底色 | 相纸排版（6 寸 2×4） |
| --- | --- | --- |
| ![cut](samples/out_cut.png) | ![colors](samples/compare_sizes_colors.jpg) | ![sheet](samples/sheet_6in_2x4.jpg) |

> 样张见 `samples/` 目录（本地运行生成，仓库已包含）。

### 📄 许可

[MIT](LICENSE)

---

## English

### ✨ Features

- 🤖 **AI auto cutout** powered by `rembg` (u2net_human_seg), clean hair/edge detail
- 🎨 One-click **red / white / blue background** swap
- 📐 **Standard ID sizes**: 1-inch, small/large 1-inch, 2-inch, small 2-inch (300 DPI)
- 🖼️ **Sheet layout**: 5″/6″/A4 paper, auto-fill or 1×1–4×4 grids, optional cut lines
- 🔍 **Live preview** with sliders for scale and position
- 💾 **Lossless export**: PNG (no compression) + JPG (quality 100), all at 300 DPI

### 🚀 Quick Start

**Windows**: double-click `一键安装并运行.bat`
**Mac / Linux**: `./run.sh`

Opens `http://127.0.0.1:7860` in your browser.

### 🧩 Offline model (optional)

The `u2net_human_seg.onnx` (~170MB) model downloads automatically on first run.
For offline / distribution use, place it at `models/u2net_human_seg.onnx`
(download: <https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2net_human_seg.onnx>).

### 📦 Build standalone exe (Windows)

Double-click `打包成exe.bat` → output in `dist\证件照工具\`.

### 📄 License

[MIT](LICENSE)
