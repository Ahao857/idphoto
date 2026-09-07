@echo off
chcp 65001 >nul
cd /d "%~dp0"
title 证件照制作工具

REM ---- 选择可用的 Python（优先 3.12，其次 py 默认版本，最后 python）----
set "PY=python"
where py >nul 2>nul
if not errorlevel 1 (
    py -3.12 -c "import sys" >nul 2>nul
    if not errorlevel 1 (set "PY=py -3.12") else (set "PY=py")
)
%PY% -c "import sys" >nul 2>nul
if errorlevel 1 (
    echo [错误] 未检测到可用的 Python，请先到 https://www.python.org/downloads/ 安装 3.9~3.12
    echo 安装时务必勾选 "Add Python to PATH"
    pause & exit /b
)
echo 使用解释器：%PY%
%PY% -c "import sys;print('Python', sys.version.split()[0])"

if not exist venv (
    echo [1/3] 正在创建虚拟环境...
    %PY% -m venv venv
    if errorlevel 1 ( echo 创建虚拟环境失败 & pause & exit /b )
)
call venv\Scripts\activate.bat

if not exist venv\.installed (
    echo [2/3] 正在安装依赖（首次需几分钟，请耐心等待）...
    python -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -U pip
    python -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
    if errorlevel 1 ( echo 安装失败，请检查网络 & pause & exit /b )
    echo ok > venv\.installed
)

echo [3/3] 启动程序，浏览器将自动打开 http://127.0.0.1:7860 ...
python idphoto.py
pause
