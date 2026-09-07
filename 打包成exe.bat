@echo off
chcp 65001 >nul
cd /d "%~dp0"
call venv\Scripts\activate.bat
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple pyinstaller
pyinstaller --noconfirm --onedir --name 证件照工具 ^
  --collect-all gradio --collect-all gradio_client --collect-all safehttpx ^
  --collect-all groovy --collect-all rembg --collect-all onnxruntime ^
  --collect-all pymatting --collect-all pooch ^
  --add-data "models;models" ^
  --hidden-import=PIL._tkinter_finder ^
  idphoto.py
echo.
echo 打包完成：dist\证件照工具\证件照工具.exe
echo 把 dist\证件照工具 整个文件夹压缩即可发给他人，对方无需安装 Python
pause
