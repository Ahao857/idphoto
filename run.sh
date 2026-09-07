#!/bin/bash
cd "$(dirname "$0")"
[ -d venv ] || python3 -m venv venv
source venv/bin/activate
if [ ! -f venv/.installed ]; then
  pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -U pip
  pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt && touch venv/.installed
fi
python idphoto.py
