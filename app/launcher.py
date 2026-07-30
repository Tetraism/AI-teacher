import http.server
import os
import queue
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time
import tkinter as tk
from tkinter import ttk
import urllib.request
import webbrowser
from pathlib import Path

OLLAMA_HOST = "http://127.0.0.1:11434"
WEB_PORT = 8765
OLLAMA_INSTALLER_URL = "https://ollama.com/download/OllamaSetup.exe"
LOG_FILE = Path(tempfile.gettempdir()) / "moreai_error.log"
CREATE_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)


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
    installer = Path(tempfile.gettempdir()) / "OllamaSetup.exe"
    urllib.request.urlretrieve(OLLAMA_INSTALLER_URL, installer)
    subprocess.run(
        [str(installer), "/VERYSILENT", "/SUPPRESSMSGBOXES", "/NORESTART"],
        check=False,
        creationflags=CREATE_NO_WINDOW,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(3)
    exe = find_ollama_exe()
    if not exe:
        raise RuntimeError("ההתקנה הסתיימה אך לא נמצא ollama.exe.")
    return exe


def is_server_up():
    try:
        urllib.request.urlopen(f"{OLLAMA_HOST}/api/version", timeout=1)
        return True
    except Exception:
        return False


def start_server(ollama_exe):
    if is_server_up():
        return None
    env = os.environ.copy()
    env["OLLAMA_ORIGINS"] = "*"
    proc = subprocess.Popen(
        [ollama_exe, "serve"],
        env=env,
        creationflags=CREATE_NO_WINDOW,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    for _ in range(30):
        if is_server_up():
            return proc
        time.sleep(1)
    raise RuntimeError("שרת ה-AI לא עלה בזמן.")


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


class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("המורה שלי")
        w, h = 360, 200
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() - w) // 2
        y = (self.root.winfo_screenheight() - h) // 2
        self.root.geometry(f"{w}x{h}+{x}+{y}")
        self.root.resizable(False, False)

        tk.Label(self.root, text="המורה שלי", font=("Segoe UI", 16, "bold")).pack(pady=(22, 6))

        self.status_var = tk.StringVar(value="מתחיל...")
        self.status_label = tk.Label(self.root, textvariable=self.status_var, font=("Segoe UI", 10))
        self.status_label.pack(pady=4)

        self.progress = ttk.Progressbar(self.root, mode="indeterminate", length=260)
        self.progress.pack(pady=10)
        self.progress.start(12)

        self.close_btn = tk.Button(self.root, text="סגור", width=12, command=self.on_close)
        self.close_btn.pack(pady=6)

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.event_queue = queue.Queue()
        self.ollama_proc = None
        self.root.after(150, self.poll_queue)
        threading.Thread(target=self.worker, daemon=True).start()

    def report(self, text):
        self.event_queue.put(("status", text))

    def worker(self):
        try:
            ollama_exe = find_ollama_exe()
            if not ollama_exe:
                self.report("מתקין את Ollama...")
                ollama_exe = install_ollama()
            self.report("מפעיל את מנוע ה-AI...")
            self.ollama_proc = start_server(ollama_exe)
            self.report("מכין את הממשק...")
            port = start_web_server()
            webbrowser.open(f"http://127.0.0.1:{port}/index.html")
            self.event_queue.put(("ready", None))
        except Exception as e:
            LOG_FILE.write_text(str(e), encoding="utf-8")
            self.event_queue.put(("error", str(e)))

    def poll_queue(self):
        try:
            while True:
                kind, payload = self.event_queue.get_nowait()
                if kind == "status":
                    self.status_var.set(payload)
                elif kind == "ready":
                    self.progress.stop()
                    self.progress.pack_forget()
                    self.status_var.set("המורה פועל ✓ — אפשר לדבר איתו בדפדפן שנפתח")
                elif kind == "error":
                    self.progress.stop()
                    self.status_label.config(fg="red")
                    self.status_var.set(f"שגיאה: {payload}")
        except queue.Empty:
            pass
        self.root.after(150, self.poll_queue)

    def on_close(self):
        if self.ollama_proc is not None:
            self.ollama_proc.terminate()
        self.root.destroy()

    def run(self):
        self.root.mainloop()


def main():
    App().run()


if __name__ == "__main__":
    main()
