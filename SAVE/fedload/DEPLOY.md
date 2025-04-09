# 🚀 Fed Load Deployment

## 🧱 Prerequisites
- Python 3.8+
- Optional: virtualenv or venv

## 📦 Install Dependencies
```bash
pip install -r requirements.txt
```

## ▶️ Run from Local Directory
```bash
python fed_load/main.py --load_url http://localhost:8000/page.html --load_out results.csv
```

## 📂 Run from GitHub
```bash
git clone https://github.com/YOUR_USER/fed_load.git
cd fed_load
python fed_load/main.py
```

## 🔁 Alternate Config Options
- Via file: `load_config.json`
- Via environment:
  - `LOAD_URL`
  - `LOAD_OUT`
  - `LOAD_AGENT`
- Via command-line:
  - `--load_url`, `--load_out`, `--load_agent`
