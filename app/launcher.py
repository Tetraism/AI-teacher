import http.server
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time
import urllib.request
import webbrowser
from pathlib import Path

OLLAMA_HOST = "http://127.0.0.1:11434"
WEB_PORT = 8765
OLLAMA_INSTALLER_URL = "https://ollama.com/download/OllamaSetup.exe"


def log(msg):
    print(f"[המורה שלי] {msg}", flush=True)


def resource_path(*parts):
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))
    return base.joinpath(*parts)


def find_ollama_exe():
    exe = shutil.which("ollama")
    if exe:
        return exe
    candidate = Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Ollama" / "ollama.exe"
    if candidate.exists():
        return str(candidate)
    return None


def install_ollama():
    log("Ollama לא נמצא במערכת - מוריד ומתקין...")
    installer = Path(tempfile.gettempdir()) / "OllamaSetup.exe"
    urllib.request.urlretrieve(OLLAMA_INSTALLER_URL, installer)
    log("מריץ את תוכנת ההתקנה (ייתכן שיוצג חלון התקנה קצר)...")
    subprocess.run([str(installer), "/VERYSILENT", "/SUPPRESSMSGBOXES", "/NORESTART"], check=False)
    time.sleep(3)
    exe = find_ollama_exe()
    if not exe:
        raise RuntimeError("ההתקנה הסתיימה אך לא נמצא ollama.exe. נסה/י להריץ את התוכנה מחדש.")
    log("Ollama הותקן בהצלחה.")
    return exe


def is_server_up():
    try:
        urllib.request.urlopen(f"{OLLAMA_HOST}/api/version", timeout=1)
        return True
    except Exception:
        return False


def start_server(ollama_exe):
    if is_server_up():
        log("שרת Ollama כבר פועל.")
        return
    log("מפעיל את שרת Ollama...")
    env = os.environ.copy()
    env["OLLAMA_ORIGINS"] = "*"
    creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    subprocess.Popen(
        [ollama_exe, "serve"],
        env=env,
        creationflags=creationflags,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    for _ in range(30):
        if is_server_up():
            log("שרת Ollama פעיל.")
            return
        time.sleep(1)
    raise RuntimeError("שרת Ollama לא עלה בזמן.")


def free_port(preferred):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("127.0.0.1", preferred))
            return preferred
        except OSError:
            s.bind(("127.0.0.1", 0))
            return s.getsockname()[1]


def start_web_server():
    port = free_port(WEB_PORT)
    web_dir = str(resource_path("web"))

    def handler(*args, **kwargs):
        return http.server.SimpleHTTPRequestHandler(*args, directory=web_dir, **kwargs)

    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", port), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return port


def main():
    log("מפעיל את המורה שלי...")
    ollama_exe = find_ollama_exe() or install_ollama()

    start_server(ollama_exe)

    port = start_web_server()
    url = f"http://127.0.0.1:{port}/index.html"
    log(f"פותח דפדפן בכתובת {url}")
    webbrowser.open(url)

    log("האפליקציה פועלת. אפשר לסגור את החלון הזה (Ctrl+C) כדי לצאת.")
    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        log("להתראות!")


if __name__ == "__main__":
    main()
