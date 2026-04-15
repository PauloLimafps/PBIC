"""
keep_alive.py — Script de backup para manter o Streamlit ativo.

Como usar:
    pip install requests
    python keep_alive.py

O script pinga o app a cada 20 minutos indefinidamente.
Pressione Ctrl+C para parar.

Alternativa: use o GitHub Actions em .github/workflows/cron_keep_alive.yml
(que é a solução principal e não requer esta máquina ligada).
"""

import time
import requests
from datetime import datetime

APP_URL = "https://pbic-avaliacao.streamlit.app/"
INTERVAL_MINUTES = 20


def ping():
    try:
        resp = requests.get(APP_URL, timeout=30)
        status = resp.status_code
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if 200 <= status < 400:
            print(f"[{now}] OK — HTTP {status} — App ativo.")
        else:
            print(f"[{now}] AVISO — HTTP {status} — App pode estar hibernando.")
    except requests.exceptions.Timeout:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{now}] TIMEOUT — O app demorou mais de 30s para responder.")
    except requests.exceptions.ConnectionError as e:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{now}] ERRO DE CONEXÃO — {e}")


if __name__ == "__main__":
    print(f"Keep-alive iniciado. Pingando '{APP_URL}' a cada {INTERVAL_MINUTES} minutos.")
    print("Pressione Ctrl+C para parar.\n")

    while True:
        ping()
        time.sleep(INTERVAL_MINUTES * 60)
