import os
import shutil
import subprocess
import sys
import tempfile
import tkinter as tk
from pathlib import Path

APP_NAME = "המורה שלי"
SHORTCUT_NAME = "AI Teacher"  # ASCII on purpose: WScript.Shell's CreateShortcut silently fails to write a .lnk whose filename contains Hebrew characters
APP_EXE_NAME = "MoreAI.exe"
INSTALL_DIR = Path(os.environ["LOCALAPPDATA"]) / "MoreAI"
CREATE_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)
LOG_FILE = Path(tempfile.gettempdir()) / "moreai_setup_error.log"


def resource_path(*parts):
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))
    return base.joinpath(*parts)


def create_shortcut(target, shortcut_path, working_dir):
    ps_script = (
        '$WshShell = New-Object -ComObject WScript.Shell\n'
        f'$Shortcut = $WshShell.CreateShortcut("{shortcut_path}")\n'
        f'$Shortcut.TargetPath = "{target}"\n'
        f'$Shortcut.WorkingDirectory = "{working_dir}"\n'
        f'$Shortcut.IconLocation = "{target}"\n'
        '$Shortcut.Save()\n'
    )
    script_file = Path(tempfile.gettempdir()) / f"moreai_shortcut_{os.getpid()}.ps1"
    script_file.write_text(ps_script, encoding="utf-8-sig")
    try:
        subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-File", str(script_file)],
            check=True,
            creationflags=CREATE_NO_WINDOW,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
        )
    finally:
        script_file.unlink(missing_ok=True)


def install():
    INSTALL_DIR.mkdir(parents=True, exist_ok=True)
    dst = INSTALL_DIR / APP_EXE_NAME
    shutil.copy2(resource_path(APP_EXE_NAME), dst)

    start_menu = Path(os.environ["APPDATA"]) / "Microsoft" / "Windows" / "Start Menu" / "Programs"
    create_shortcut(dst, start_menu / f"{SHORTCUT_NAME}.lnk", INSTALL_DIR)

    desktop = Path(os.environ["USERPROFILE"]) / "Desktop"
    if desktop.exists():
        create_shortcut(dst, desktop / f"{SHORTCUT_NAME}.lnk", INSTALL_DIR)


def main():
    root = tk.Tk()
    root.title(f"התקנת {APP_NAME}")
    w, h = 380, 170
    root.update_idletasks()
    x = (root.winfo_screenwidth() - w) // 2
    y = (root.winfo_screenheight() - h) // 2
    root.geometry(f"{w}x{h}+{x}+{y}")
    root.resizable(False, False)

    tk.Label(root, text=f"מתקין את {APP_NAME}", font=("Segoe UI", 14, "bold")).pack(pady=(20, 8))
    status_var = tk.StringVar(value="מעתיק קבצים ויוצר קיצורי דרך...")
    status_label = tk.Label(root, textvariable=status_var, font=("Segoe UI", 10), wraplength=340, justify="center")
    status_label.pack(pady=6)
    close_btn = tk.Button(root, text="סגור", width=12, state="disabled", command=root.destroy)
    close_btn.pack(pady=10)

    def run_install():
        try:
            install()
            status_var.set(f'ההתקנה הושלמה בהצלחה!\nאפשר לפתוח את "{APP_NAME}" מתפריט התחל או משולחן העבודה.')
        except Exception as e:
            import traceback
            LOG_FILE.write_text(traceback.format_exc(), encoding="utf-8")
            status_label.config(fg="red")
            status_var.set(f"שגיאה בהתקנה: {e}")
        close_btn.config(state="normal")

    root.after(200, run_install)
    root.mainloop()


if __name__ == "__main__":
    main()
