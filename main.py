# ============================================================
# 🚀 DJ_NAIMO - DETA SPACE WATCHER
# ============================================================

from fastapi import FastAPI
import requests
from bs4 import BeautifulSoup
from deta import Deta

DETA_PROJECT_KEY = "ISI_KEY_PROJECT_DETA_KAMU"
COLAB_WEBHOOK = "https://palmier-nondescriptive-stacee.ngrok-free.dev/render"
NCS_RELEASES = "https://ncs.io/releases"

app = FastAPI()
deta = Deta(DETA_PROJECT_KEY)
db = deta.Base("ncs_releases")

@app.get("/")
def home():
    return {"status": "ok", "msg": "DJ Naimo watcher aktif"}

def check_new_ncs():
    html = requests.get(NCS_RELEASES).text
    soup = BeautifulSoup(html, "html.parser")
    links = [a["href"] for a in soup.find_all("a", href=True) if a["href"].startswith("https://ncs.io/")]
    new_links = []
    for link in links:
        key = link.split("/")[-1]
        if not db.get(key):
            db.put({"key": key, "url": link})
            new_links.append(link)
    return new_links

def trigger_colab_render(ncs_url):
    try:
        payload = {"ncs_url": ncs_url}
        r = requests.post(COLAB_WEBHOOK, json=payload)
        print("🚀 Trigger dikirim ke Colab:", ncs_url, "→", r.status_code)
    except Exception as e:
        print("⚠️ Gagal kirim trigger:", e)

@app.get("/check")
def manual_check():
    new_links = check_new_ncs()
    for link in new_links:
        trigger_colab_render(link)
    return {"found": len(new_links), "links": new_links}
