#!/bin/bash
# 🛠 Setup Python environment for Fed Load

python3 -m venv venv
source venv/bin/activate
pip install -r fed_load/requirements.txt
echo "Environment ready. To activate later, run: source venv/bin/activate"
