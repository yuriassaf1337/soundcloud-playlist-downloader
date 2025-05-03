import os
import shutil
import tempfile
import zipfile
import threading
import tkinter as tk
import subprocess
import sys
from tkinter import messagebox, filedialog, scrolledtext

def get_icon_temp_path():
    if getattr(sys, 'frozen', False):  # .exe
        return os.path.join(sys._MEIPASS, 'helper', 'sc.ico')
    else:
        return os.path.abspath("helper/sc.ico")  # dev

def check_ffmpeg():
    try:
        subprocess.run(['ffmpeg', '-version'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except FileNotFoundError:
        return False

def ensure_yt_dlp_installed():
    try:
        import yt_dlp
        return True
    except ImportError:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "yt-dlp"])
            return True
        except subprocess.CalledProcessError:
            messagebox.showerror("error", "failed to install yt-dlp.\nplease install it manually with cmdline:\n>> pip install yt-dlp")
            return False


def insert_log(log_output, message, tag=None):
    log_output.configure(state=tk.NORMAL)
    log_output.insert(tk.END, message + "\n", tag)
    log_output.see(tk.END)
    log_output.configure(state=tk.DISABLED)

def setup_log_tags(log_output):
    log_output.tag_config("info", foreground="orange")
    log_output.tag_config("success", foreground="lightgreen")
    log_output.tag_config("error", foreground="red")
    log_output.tag_config("title", foreground="gray")
    log_output.tag_config("done", foreground="green")

def download_playlist(playlist_url, zip_name, output_dir, log_output):
    insert_log(log_output, "🔍 checking dependencies...", "info")
    if not check_ffmpeg():
        messagebox.showerror(
            "ffmpeg not found",
            "install it from https://www.gyan.dev/ffmpeg/builds/ and add to system path\n"
        )
        return

    if not ensure_yt_dlp_installed():
        return

    import yt_dlp
    from yt_dlp.utils import DownloadError

    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(output_dir, f"{zip_name}.zip")
    seen_files = set()

    def hook(d):
        if d['status'] == 'downloading':
            filename = d.get('filename', '')
            if filename and filename not in seen_files:
                seen_files.add(filename)
                clean_name = os.path.splitext(filename)[0]
                insert_log(log_output, f"🎵 downloading: {os.path.basename(clean_name)}", "info")
        elif d['status'] == 'finished':
            raw_name = os.path.basename(d.get('filename', ''))
            clean_name = os.path.splitext(raw_name)[0]
            insert_log(log_output, f"✔ finished: {clean_name}", "success")

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(temp_dir, '%(title)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320',
        }],
        'quiet': True,
        'noplaylist': False,
        'progress_hooks': [hook]
    }

    try:
        insert_log(log_output, "📥 downloading playlist...\n", "title")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([playlist_url])

        insert_log(log_output, "\n📦 zipping files...", "info")
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, temp_dir)
                    zipf.write(file_path, arcname)

        shutil.rmtree(temp_dir)
        insert_log(log_output, f"\n✔ done! zipped playlist saved as: {zip_path}", "done")
    except DownloadError as e:
        error_msg = str(e)
        if "HTTP Error 404" in error_msg or "Unable to download JSON metadata" in error_msg:
            user_msg = "❌ couldn't find the playlist. it either doesn't exist or is private."
        else:
            user_msg = f"❌ download error: {error_msg}"
        insert_log(log_output, user_msg, "error")
        messagebox.showerror("error", user_msg)
    except Exception as e:
        insert_log(log_output, f"❌ unexpected error: {str(e)}", "error")
        messagebox.showerror("error", str(e))

def start_download(entry_url, log_output):
    url = entry_url.get().strip()

    if not url:
        messagebox.showwarning("missing URL", "please paste a soundcloud playlist URL.")
        return

    zip_path = filedialog.asksaveasfilename(
        title="save zip as",
        defaultextension=".zip",
        filetypes=[("ZIP files", "*.zip")],
        initialfile="playlist.zip"
    )
    if not zip_path:
        return

    zipname = os.path.splitext(os.path.basename(zip_path))[0]
    output_dir = os.path.dirname(zip_path)

    log_output.delete(1.0, tk.END)
    thread = threading.Thread(target=download_playlist, args=(url, zipname, output_dir, log_output))
    thread.start()

def create_gui():
    root = tk.Tk()
    root.title("soundcloud playlist downloader")
    root.geometry("500x340")
    icon_path = get_icon_temp_path()
    root.iconbitmap(icon_path)
    root.configure(bg="#1e1e1e")

    label_style = {"fg": "white", "bg": "#1e1e1e", "font": ("Segoe UI", 10)}
    entry_style = {"bg": "#2d2d2d", "fg": "white", "insertbackground": "white", "width": 80, "relief": "flat"}

    tk.Label(root, text="soundcloud playlist URL:", **label_style).pack(pady=(10, 2))
    entry_url = tk.Entry(root, **entry_style)
    entry_url.pack(pady=5)

    tk.Button(
        root,
        text="save to zip file",
        command=lambda: start_download(entry_url, log_output),
        bg="#3a3a3a",
        fg="white",
        relief="flat",
        padx=10,
        pady=5
    ).pack(pady=15)

    log_output = scrolledtext.ScrolledText(
        root,
        height=15,
        bg="#121212",
        fg="white",
        insertbackground="white",
        font=("Consolas", 10),
        state=tk.DISABLED
    )
    log_output.pack(padx=10, pady=10, fill="both", expand=True)

    scrollbar = log_output.vbar
    scrollbar.pack_forget()
    log_output.bind("<MouseWheel>", lambda e: log_output.yview_scroll(-1 * (e.delta // 120), "units"))

    setup_log_tags(log_output)
    root.mainloop()

if __name__ == "__main__":
    create_gui()
