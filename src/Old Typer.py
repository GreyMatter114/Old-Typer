from tkinter import Tk, Toplevel, Label
from gui import PredictorApp

"""for pkg in ["nltk", "speechrecognition", "pyaudio", "pillow"]:
     ensure_installed(pkg)"""

import nltk
nltk.download("brown")

from trie import build_trie, save_trie, load_trie
from history import init_db, is_stale

import json, subprocess, sys, importlib.util

def load_config(path="./config.json"):
    with open(path) as f:
        return json.load(f)

def show_splash():
    splash = Toplevel()
    splash.overrideredirect(True)
    splash.configure(bg="#222222")
    splash.geometry("400x200+500+300")
    Label(
        splash,
        text="Building or Loading Trie…",
        font=("Helvetica", 16),
        bg="#222222",
        fg="white"
    ).pack(expand=True)
    return splash


if __name__ == "__main__":
    config = load_config()
    root = Tk()
    root.geometry("900x600")
    root.withdraw()  # hide main window during splash

    splash = show_splash()
    root.update()
    conn = init_db(config["history_db_path"])
    if is_stale(conn, config["stale_days"]):
        trie = build_trie()
        save_trie(trie, config["trie_cache_path"])
    else:
        trie = load_trie(config["trie_cache_path"])
        if not trie:
            trie = build_trie()
            save_trie(trie, config["trie_cache_path"])

    splash.destroy()
    root.deiconify()
    app = PredictorApp(root, config, trie, conn)
    root.mainloop()
