"""Batch-generate Adhiraj's fixed office lines in his cloned voice (fal.ai MiniMax voice clone via Emergent Universal Key)."""
import os, sys, time, json, subprocess, concurrent.futures as cf
from urllib.parse import urlparse
import requests
from dotenv import load_dotenv

load_dotenv("/app/backend/.env")
load_dotenv("/app/frontend/.env")
KEY = os.environ["EMERGENT_LLM_KEY"]
# Fal Universal Key supports queue inference through Emergent proxy, not Platform APIs.
BASE = os.environ.get("INTEGRATION_PROXY_URL", "https://integrations.emergentagent.com").rstrip("/") + "/api/v1/fal"
ENDPOINT = "fal-ai/minimax/speech-2.8-hd"
CLONE = "fal-ai/minimax/voice-clone"
VOICE_FILE = "/app/scripts/.adhiraj_voice_id"
REF = os.environ["REACT_APP_BACKEND_URL"].rstrip("/") + "/tmpref/ref.mp3"
OUT = "/app/frontend/public/game/assets/adhiraj"
FF = __import__("imageio_ffmpeg").get_ffmpeg_exe()

LINES = {
    "open-1": "Sit. Security says there was “an incident”. They used the air quotes, so I am assuming it is a small one.",
    "open-2": "Sit. Security says there was “an incident”. They did not use the air quotes this time.",
    "open-3": "Sit. Security has called me three times. I did not know they had my number. I would like that to stop being true.",
    "open-4": "Sit. Four guards are outside my door. One of them is taking notes. I did not know they took notes.",
    "open-5": "Sit. There is a guard outside my window describing you to another guard. He is using his hands. It is not flattering.",
    "mid-1": "I have run eleven hackathons. In ten of them, nobody needed me to get up from this chair.",
    "mid-2": "The rules are on page two of the welcome email. Page one is the Wi-Fi password. I understand why nobody reaches page two.",
    "mid-3": "I am not angry. Anger requires surprise.",
    "mid-4": "Your team’s noon update said “vibes”. One word. Lowercase.",
    "mid-5": "When I was a student I also made bad decisions. I made them quietly, and indoors.",
    "mid-6": "Security wants a written apology. I told them I would read it to you instead. That is worse.",
    "mid-7": "There is a form for this. I am going to fill it in slowly, while you watch.",
    "mid-8": "Do you know what a programme director does all day? Neither did I, until about forty minutes ago.",
    "mid-9": "Someone from the sponsor’s team saw it. They asked if it was part of the demo. I said “not yet”.",
    "apo-1": "Noted.",
    "apo-2": "That was nearly sincere. I will write down “nearly”.",
    "apo-3": "Thank you. Please do not make me remember it.",
    "apo-4": "Apology received. Not accepted. Received.",
    "again-2": "Back already. I kept the chair warm. Not on purpose.",
    "again-3": "Third time. I have started a spreadsheet. It has a chart now.",
    "close-long": "That took longer than it needed to. So did this whole day.",
    "close-quiet": "…Fine. Most people talk. You didn’t. I will tell a judge your team is “one to watch”. Do not make me a liar. Go.",
    "close-apo": "Apology logged. Security will stand down. Go and build something. Ideally a reputation.",
    "close-default": "That is enough. Security has been told you are my problem now. I would prefer you were nobody’s problem. Go.",
    "brushoff": "Do you need something?",
}


def H(extra=None):
    h = {"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}
    if extra:
        h.update(extra)
    return h


def trusted(u):
    c, q = urlparse(u), urlparse(BASE + "/queue")
    if c.scheme != q.scheme or c.netloc != q.netloc or not c.path.startswith(q.path + "/"):
        raise RuntimeError("untrusted queue url")
    return u


def get(u, deadline):
    for a in range(5):
        try:
            return requests.get(u, headers=H(), timeout=60)
        except (requests.ConnectTimeout, requests.ReadTimeout, requests.ConnectionError):
            if a == 4 or time.monotonic() > deadline:
                raise
            time.sleep(2 ** a)


def run(endpoint, payload, lid):
    r = requests.post(BASE + "/proxy", headers=H({"X-Fal-Target-Url": "https://queue.fal.run/" + endpoint}), json=payload, timeout=60)
    if r.status_code == 402:
        raise RuntimeError("Insufficient Universal Key credits")
    r.raise_for_status()
    sub = r.json(); su, ru = trusted(sub["status_url"]), trusted(sub["response_url"])
    deadline = time.monotonic() + 600
    while time.monotonic() < deadline:
        s = get(su, deadline); s.raise_for_status(); st = (s.json().get("status") or "").upper()
        if st in ("COMPLETED", "OK"):
            res = get(ru, deadline); res.raise_for_status(); body = res.json(); break
        if st in ("FAILED", "CANCELLED", "CANCELED", "ERROR"):
            raise RuntimeError(f"{lid} failed: {st}")
        time.sleep(2)
    else:
        raise RuntimeError(f"{lid} timed out")
    return body


def clean(text):
    return text.replace("“", '"').replace("”", '"').replace("’", "'").replace("…", "... ")


def clone_voice():
    body = run(CLONE, {"audio_url": REF, "text": clean(LINES["mid-1"]), "model": "speech-02-hd", "need_volume_normalization": True}, "clone")
    open(VOICE_FILE, "w").write(body["custom_voice_id"])
    return body["custom_voice_id"]


def gen(lid):
    vid = open(VOICE_FILE).read().strip()
    body = run(ENDPOINT, {"prompt": clean(LINES[lid]), "voice_setting": {"voice_id": vid}, "output_format": "url", "language_boost": "English"}, lid)
    url = (body.get("audio") or {}).get("url")
    if not url:
        raise RuntimeError(f"{lid} no audio in result: {json.dumps(body)[:300]}")
    raw = f"/tmp/adh_raw_{lid}"
    with open(raw, "wb") as f:
        f.write(requests.get(url, timeout=120).content)
    # mono 64 kbps, trimmed, loudness-matched like the other voice files
    subprocess.run([FF, "-y", "-loglevel", "error", "-i", raw, "-af",
                    "silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,loudnorm=I=-16:TP=-1.5",
                    "-ac", "1", "-ar", "44100", "-b:a", "64k", f"{OUT}/{lid}.mp3"], check=True)
    return lid


if __name__ == "__main__":
    if sys.argv[1:2] == ["clone"]:
        print("voice", clone_voice()); sys.exit()
    ids = sys.argv[1:] or list(LINES)
    os.makedirs(OUT, exist_ok=True)
    with cf.ThreadPoolExecutor(6) as ex:
        futs = {ex.submit(gen, i): i for i in ids}
        for f in cf.as_completed(futs):
            try:
                print("OK", f.result(), flush=True)
            except Exception as e:
                print("FAIL", futs[f], e, flush=True)
