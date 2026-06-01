#!/usr/bin/env python3
"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  VORTEX DOWNLOADER  —  by Claude
  Supports: YouTube, Instagram, TikTok,
            Twitter/X, Facebook & more
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Requirements:
    pip install yt-dlp Pillow requests
    ffmpeg must be installed and in PATH

Run:
    python3 video_downloader.py
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
import sys
import io
import urllib.request
import urllib.parse

# --- Bundled Binary Path Resolution ------------------------------------------
def _get_base_dir():
    if getattr(sys, "frozen", False):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))

def _setup_ffmpeg_path():
    exe_dir = os.path.dirname(sys.executable) if getattr(sys, "frozen", False)               else os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(exe_dir, "bin"),
        os.path.join(_get_base_dir(), "bin"),
        _get_base_dir(),
    ]
    for folder in candidates:
        ffmpeg = os.path.join(folder, "ffmpeg.exe")
        if os.path.isfile(ffmpeg):
            os.environ["PATH"] = folder + os.pathsep + os.environ.get("PATH", "")
            os.environ["FFMPEG_LOCATION"] = folder
            return folder
    return None

FFMPEG_DIR = _setup_ffmpeg_path()


# ─── URL Cleaner ──────────────────────────────────────────────────────────────
# Params to KEEP per platform (everything else is stripped)
_KEEP_PARAMS = {
    "youtube.com": ["v", "clip"],
    "youtu.be":    [],          # video id is in path, no params needed
    "music.youtube.com": ["v"],
}
# Params that are always junk regardless of platform
_JUNK_PARAMS = {
    "list", "index", "start_radio", "pp", "si", "feature", "app",
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "fbclid", "igshid", "ref", "referrer", "tracking", "source",
    "ab_channel", "t",   # keep 't' only if you want timestamps — removed for simplicity
}

def clean_url(raw: str) -> str:
    """Strip playlist/tracking junk and return the cleanest watchable URL."""
    raw = raw.strip()
    try:
        p = urllib.parse.urlparse(raw)
    except Exception:
        return raw

    host = p.netloc.lower().replace("www.", "")
    params = urllib.parse.parse_qs(p.query, keep_blank_values=False)

    # youtu.be short links → convert to full watch URL
    if host == "youtu.be":
        video_id = p.path.lstrip("/").split("/")[0]
        if video_id:
            return f"https://www.youtube.com/watch?v={video_id}"
        return raw

    # YouTube / YouTube Music — keep only 'v' (and 'clip' for clips)
    if host in ("youtube.com", "music.youtube.com"):
        keep = _KEEP_PARAMS.get(host, [])
        clean_params = {k: v for k, v in params.items() if k in keep}
        new_query = urllib.parse.urlencode(clean_params, doseq=True)
        cleaned = urllib.parse.urlunparse((p.scheme, p.netloc, p.path, "", new_query, ""))
        return cleaned

    # All other platforms — just strip known junk params
    clean_params = {k: v for k, v in params.items() if k not in _JUNK_PARAMS}
    new_query = urllib.parse.urlencode(clean_params, doseq=True)
    return urllib.parse.urlunparse((p.scheme, p.netloc, p.path, "", new_query, ""))

try:
    import yt_dlp
except ImportError:
    print("Installing yt-dlp..."); os.system(f"{sys.executable} -m pip install yt-dlp -q")
    import yt_dlp

try:
    from PIL import Image, ImageTk, ImageDraw, ImageFilter
except ImportError:
    print("Installing Pillow..."); os.system(f"{sys.executable} -m pip install Pillow -q")
    from PIL import Image, ImageTk, ImageDraw, ImageFilter

# ─── Color Palette ────────────────────────────────────────────────────────────
BG       = "#0d0d0f"
SURFACE  = "#16161a"
SURFACE2 = "#1e1e24"
BORDER   = "#2a2a35"
ACCENT   = "#7c5cfc"
ACCENT2  = "#a78bfa"
SUCCESS  = "#22d3a5"
ERROR    = "#ff5c7a"
TEXT     = "#f0eeff"
SUBTEXT  = "#8b8aa8"
WHITE    = "#ffffff"


class RoundedButton(tk.Canvas):
    def __init__(self, parent, text, command=None, width=160, height=42,
                 bg=ACCENT, fg=WHITE, hover_bg=ACCENT2, radius=10, font_size=11, **kw):
        super().__init__(parent, width=width, height=height,
                         bg=parent["bg"] if hasattr(parent, "__getitem__") else BG,
                         highlightthickness=0, cursor="hand2", **kw)
        self.command = command
        self.bg_color = bg
        self.hover_color = hover_bg
        self.fg = fg
        self.r = radius
        self.w = width
        self.h = height
        self.text = text
        self.font_size = font_size
        self._draw(bg)
        self.bind("<Enter>", lambda e: self._draw(hover_bg))
        self.bind("<Leave>", lambda e: self._draw(bg))
        self.bind("<Button-1>", lambda e: command() if command else None)

    def _draw(self, color):
        self.delete("all")
        r = self.r
        w, h = self.w, self.h
        self.create_arc(0, 0, 2*r, 2*r, start=90, extent=90, fill=color, outline="")
        self.create_arc(w-2*r, 0, w, 2*r, start=0, extent=90, fill=color, outline="")
        self.create_arc(0, h-2*r, 2*r, h, start=180, extent=90, fill=color, outline="")
        self.create_arc(w-2*r, h-2*r, w, h, start=270, extent=90, fill=color, outline="")
        self.create_rectangle(r, 0, w-r, h, fill=color, outline="")
        self.create_rectangle(0, r, w, h-r, fill=color, outline="")
        self.create_text(w//2, h//2, text=self.text, fill=self.fg,
                         font=("Segoe UI", self.font_size, "bold"))


class VortexDownloader(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("VORTEX  ·  Video Downloader")
        self.geometry("720x820")
        self.minsize(680, 740)
        self.configure(bg=BG)
        self.resizable(True, True)

        # State
        self.video_info = None
        self.thumbnail_image = None
        self.download_path = tk.StringVar(value=os.path.expanduser("~/Downloads"))
        self.format_var = tk.StringVar(value="mp4")
        self.quality_var = tk.StringVar(value="best")
        self.formats_list = []

        self._build_ui()
        self._center_window()

    def _center_window(self):
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 720) // 2
        y = (self.winfo_screenheight() - 820) // 2
        self.geometry(f"720x820+{x}+{y}")

    # ─── UI Construction ──────────────────────────────────────────────────────
    def _build_ui(self):
        # Header
        hdr = tk.Frame(self, bg=SURFACE, height=64)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text="⬡  VORTEX", font=("Courier New", 17, "bold"),
                 fg=ACCENT2, bg=SURFACE).pack(side="left", padx=24, pady=16)
        tk.Label(hdr, text="Universal Video Downloader",
                 font=("Segoe UI", 9), fg=SUBTEXT, bg=SURFACE).pack(side="left", pady=20)

        # Separator
        tk.Frame(self, bg=ACCENT, height=2).pack(fill="x")

        # Scroll canvas for main content
        outer = tk.Frame(self, bg=BG)
        outer.pack(fill="both", expand=True)

        self.canvas_scroll = tk.Canvas(outer, bg=BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(outer, orient="vertical", command=self.canvas_scroll.yview)
        self.canvas_scroll.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.canvas_scroll.pack(side="left", fill="both", expand=True)

        self.main = tk.Frame(self.canvas_scroll, bg=BG)
        self.canvas_win = self.canvas_scroll.create_window((0, 0), window=self.main, anchor="nw")
        self.main.bind("<Configure>", lambda e: self.canvas_scroll.configure(
            scrollregion=self.canvas_scroll.bbox("all")))
        self.canvas_scroll.bind("<Configure>", lambda e: self.canvas_scroll.itemconfig(
            self.canvas_win, width=e.width))
        self.canvas_scroll.bind_all("<MouseWheel>", lambda e: self.canvas_scroll.yview_scroll(
            -1 * (e.delta // 120), "units"))

        self._build_url_section()
        self._build_thumbnail_section()
        self._build_options_section()
        self._build_path_section()
        self._build_download_section()
        self._build_log_section()

    def _section(self, label):
        f = tk.Frame(self.main, bg=BG)
        f.pack(fill="x", padx=24, pady=(18, 0))
        tk.Label(f, text=label, font=("Courier New", 9, "bold"),
                 fg=SUBTEXT, bg=BG).pack(anchor="w")
        tk.Frame(self.main, bg=BORDER, height=1).pack(fill="x", padx=24, pady=(4, 0))
        return f

    def _card(self, parent=None):
        p = parent or self.main
        c = tk.Frame(p, bg=SURFACE2, padx=16, pady=14)
        c.pack(fill="x", padx=24, pady=(8, 0))
        return c

    def _build_url_section(self):
        self._section("01  /  VIDEO URL")
        card = self._card()
        row = tk.Frame(card, bg=SURFACE2)
        row.pack(fill="x")

        self.url_entry = tk.Entry(row, font=("Consolas", 11), bg=SURFACE,
                                  fg=TEXT, insertbackground=ACCENT2,
                                  relief="flat", bd=0)
        self.url_entry.pack(side="left", fill="x", expand=True, ipady=10, padx=(0, 10))
        self.url_entry.insert(0, "Paste video URL here…")
        self.url_entry.config(fg=SUBTEXT)
        self.url_entry.bind("<FocusIn>", self._clear_placeholder)
        self.url_entry.bind("<FocusOut>", self._restore_placeholder)
        self.url_entry.bind("<Return>", lambda e: self._fetch_info())
        tk.Frame(row, bg=BORDER, width=1).pack(side="left", fill="y", padx=(0, 10))

        fetch_btn = RoundedButton(row, "  FETCH  ", command=self._fetch_info,
                                  width=100, height=38, bg=ACCENT, font_size=10)
        fetch_btn.pack(side="left")

    def _build_thumbnail_section(self):
        self._section("02  /  PREVIEW")
        self.thumb_card = self._card()
        self.thumb_label = tk.Label(self.thumb_card, text="─  No video loaded  ─",
                                    font=("Segoe UI", 10), fg=SUBTEXT, bg=SURFACE2,
                                    height=10)
        self.thumb_label.pack(fill="x")
        self.title_label = tk.Label(self.thumb_card, text="",
                                    font=("Segoe UI", 11, "bold"), fg=TEXT,
                                    bg=SURFACE2, wraplength=620, justify="left")
        self.title_label.pack(anchor="w", pady=(8, 0))
        self.meta_label = tk.Label(self.thumb_card, text="",
                                   font=("Segoe UI", 9), fg=SUBTEXT,
                                   bg=SURFACE2, justify="left")
        self.meta_label.pack(anchor="w", pady=(2, 0))

    def _build_options_section(self):
        self._section("03  /  FORMAT & QUALITY")
        card = self._card()
        row = tk.Frame(card, bg=SURFACE2)
        row.pack(fill="x")

        # Format toggle
        fmt_lbl = tk.Label(row, text="Format:", font=("Segoe UI", 10),
                           fg=SUBTEXT, bg=SURFACE2)
        fmt_lbl.pack(side="left", padx=(0, 10))

        self.mp4_btn = self._toggle_btn(row, "MP4 (Video)", "mp4")
        self.mp3_btn = self._toggle_btn(row, "MP3 (Audio)", "mp3")
        self._update_format_btns()

        # Quality row
        row2 = tk.Frame(card, bg=SURFACE2)
        row2.pack(fill="x", pady=(12, 0))
        tk.Label(row2, text="Quality:", font=("Segoe UI", 10),
                 fg=SUBTEXT, bg=SURFACE2).pack(side="left", padx=(0, 10))

        self.quality_combo = ttk.Combobox(row2, textvariable=self.quality_var,
                                          state="readonly", width=40,
                                          font=("Consolas", 10))
        self.quality_combo["values"] = ["── Fetch a video first ──"]
        self.quality_combo.current(0)
        self.quality_combo.pack(side="left")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TCombobox", fieldbackground=SURFACE,
                        background=SURFACE, foreground=TEXT,
                        selectbackground=ACCENT, selectforeground=WHITE,
                        arrowcolor=ACCENT2)

    def _toggle_btn(self, parent, label, value):
        btn = tk.Label(parent, text=label, font=("Segoe UI", 10, "bold"),
                       cursor="hand2", padx=16, pady=6)
        btn.bind("<Button-1>", lambda e: self._set_format(value))
        btn.pack(side="left", padx=(0, 8))
        return btn

    def _set_format(self, val):
        self.format_var.set(val)
        self._update_format_btns()
        if self.video_info:
            self._populate_qualities()

    def _update_format_btns(self):
        v = self.format_var.get()
        for btn, bval in [(self.mp4_btn, "mp4"), (self.mp3_btn, "mp3")]:
            if bval == v:
                btn.config(bg=ACCENT, fg=WHITE)
            else:
                btn.config(bg=SURFACE, fg=SUBTEXT)

    def _build_path_section(self):
        self._section("04  /  SAVE LOCATION")
        card = self._card()
        row = tk.Frame(card, bg=SURFACE2)
        row.pack(fill="x")

        path_entry = tk.Entry(row, textvariable=self.download_path,
                              font=("Consolas", 10), bg=SURFACE, fg=TEXT,
                              insertbackground=ACCENT2, relief="flat", bd=0)
        path_entry.pack(side="left", fill="x", expand=True, ipady=8, padx=(0, 10))

        browse_btn = RoundedButton(row, "  BROWSE  ", command=self._browse_path,
                                   width=110, height=36, bg=SURFACE, hover_bg=BORDER,
                                   fg=ACCENT2, font_size=10)
        browse_btn.pack(side="left")

    def _build_download_section(self):
        tk.Frame(self.main, bg=BG, height=12).pack()
        btn_frame = tk.Frame(self.main, bg=BG)
        btn_frame.pack(pady=4)
        self.dl_btn = RoundedButton(btn_frame, "  ↓  DOWNLOAD  ", command=self._start_download,
                                    width=220, height=50, bg=ACCENT, hover_bg=ACCENT2,
                                    font_size=13)
        self.dl_btn.pack()

        self.progress_var = tk.DoubleVar()
        style = ttk.Style()
        style.configure("Vortex.Horizontal.TProgressbar",
                        troughcolor=SURFACE2, background=ACCENT,
                        bordercolor=SURFACE2, lightcolor=ACCENT, darkcolor=ACCENT)
        self.progress_bar = ttk.Progressbar(self.main, variable=self.progress_var,
                                            maximum=100,
                                            style="Vortex.Horizontal.TProgressbar",
                                            length=400)
        self.progress_bar.pack(pady=(12, 0))
        self.progress_label = tk.Label(self.main, text="", font=("Consolas", 9),
                                       fg=SUBTEXT, bg=BG)
        self.progress_label.pack(pady=(4, 0))

    def _build_log_section(self):
        self._section("05  /  LOG")
        log_card = self._card()
        self.log_text = tk.Text(log_card, height=7, bg=SURFACE, fg=SUCCESS,
                                font=("Consolas", 9), relief="flat", bd=0,
                                state="disabled", wrap="word",
                                insertbackground=ACCENT)
        self.log_text.pack(fill="x")

    # ─── Placeholder ──────────────────────────────────────────────────────────
    def _clear_placeholder(self, e):
        if self.url_entry.get() == "Paste video URL here…":
            self.url_entry.delete(0, "end")
            self.url_entry.config(fg=TEXT)

    def _restore_placeholder(self, e):
        if not self.url_entry.get():
            self.url_entry.insert(0, "Paste video URL here…")
            self.url_entry.config(fg=SUBTEXT)

    # ─── Logging ──────────────────────────────────────────────────────────────
    def _log(self, msg, color=None):
        self.log_text.config(state="normal")
        tag = f"c{len(self.log_text.get('1.0','end'))}"
        self.log_text.insert("end", msg + "\n", tag)
        if color:
            self.log_text.tag_config(tag, foreground=color)
        self.log_text.see("end")
        self.log_text.config(state="disabled")

    # ─── Browse Path ──────────────────────────────────────────────────────────
    def _browse_path(self):
        path = filedialog.askdirectory(initialdir=self.download_path.get())
        if path:
            self.download_path.set(path)

    # ─── Fetch Info ───────────────────────────────────────────────────────────
    def _fetch_info(self):
        raw = self.url_entry.get().strip()
        if not raw or raw == "Paste video URL here…":
            messagebox.showwarning("No URL", "Please paste a video URL first.")
            return

        url = clean_url(raw)
        if url != raw:
            # Update the entry box to show the cleaned URL
            self.url_entry.config(fg=TEXT)
            self.url_entry.delete(0, "end")
            self.url_entry.insert(0, url)
            self._log(f"✂  Cleaned URL → {url}", ACCENT2)

        self._log(f"⟳ Fetching info: {url}", SUBTEXT)
        self.title_label.config(text="Loading…")
        threading.Thread(target=self._fetch_thread, args=(url,), daemon=True).start()

    def _fetch_thread(self, url):
        try:
            ydl_opts = {"quiet": True, "no_warnings": True, "skip_download": True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
            self.video_info = info
            self.after(0, self._on_info_loaded, info)
        except Exception as ex:
            self.after(0, self._log, f"✗ Error: {ex}", ERROR)
            self.after(0, self.title_label.config, {"text": ""})

    def _on_info_loaded(self, info):
        title = info.get("title", "Unknown Title")
        duration = info.get("duration", 0)
        uploader = info.get("uploader", info.get("channel", "Unknown"))
        mins, secs = divmod(int(duration or 0), 60)
        views = info.get("view_count")
        views_str = f"{views:,}" if views else "N/A"

        self.title_label.config(text=title)
        self.meta_label.config(
            text=f"  👤 {uploader}   ⏱ {mins}:{secs:02d}   👁 {views_str} views")
        self._log(f"✓ Loaded: {title}", SUCCESS)
        self._load_thumbnail(info.get("thumbnail"))
        self._populate_qualities()

    def _load_thumbnail(self, url):
        if not url:
            return
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            data = urllib.request.urlopen(req, timeout=10).read()
            img = Image.open(io.BytesIO(data))

            # Crop to 16:9
            w, h = img.size
            target_h = int(w * 9 / 16)
            if target_h < h:
                top = (h - target_h) // 2
                img = img.crop((0, top, w, top + target_h))

            img = img.resize((620, 349), Image.LANCZOS)

            # Vignette overlay
            vignette = Image.new("RGBA", img.size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(vignette)
            for i in range(40):
                alpha = int(180 * (i / 40) ** 2)
                draw.rectangle([i, i, img.width - i, img.height - i],
                                outline=(0, 0, 0, alpha))
            img = img.convert("RGBA")
            img = Image.alpha_composite(img, vignette).convert("RGB")

            self.thumbnail_image = ImageTk.PhotoImage(img)
            self.thumb_label.config(image=self.thumbnail_image, text="", height=0,
                                    bg=SURFACE2)
        except Exception as ex:
            self._log(f"⚠ Thumbnail failed: {ex}", SUBTEXT)

    def _populate_qualities(self):
        if not self.video_info:
            return
        fmt = self.format_var.get()
        formats = self.video_info.get("formats", [])

        if fmt == "mp3":
            self.quality_combo["values"] = [
                "128 kbps  (small)",
                "192 kbps  (good)",
                "256 kbps  (great)",
                "320 kbps  (best)",
            ]
            self.quality_var.set("192 kbps  (good)")
        else:
            seen = set()
            opts = []
            for f in reversed(formats):
                h = f.get("height")
                vcodec = f.get("vcodec", "none")
                if h and vcodec and vcodec != "none" and h not in seen:
                    seen.add(h)
                    note = f.get("format_note", "")
                    size = f.get("filesize") or f.get("filesize_approx")
                    sz = f"  ~{size//1024//1024} MB" if size else ""
                    opts.append(f"{h}p  {note}{sz}")
            if not opts:
                opts = ["Best available"]
            opts.insert(0, "Best available  (recommended)")
            self.quality_combo["values"] = opts
            self.quality_var.set(opts[0])

        self._log(f"✓ {len(self.quality_combo['values'])} quality options loaded", SUCCESS)

    # ─── Download ─────────────────────────────────────────────────────────────
    def _start_download(self):
        if not self.video_info:
            messagebox.showwarning("No Video", "Fetch a video first.")
            return
        save_path = self.download_path.get()
        if not os.path.isdir(save_path):
            messagebox.showerror("Bad Path", "Download folder does not exist.")
            return

        self.progress_var.set(0)
        self.progress_label.config(text="Starting…", fg=SUBTEXT)
        threading.Thread(target=self._download_thread, daemon=True).start()

    def _download_thread(self):
        url = self.video_info.get("webpage_url") or self.url_entry.get().strip()
        fmt = self.format_var.get()
        quality = self.quality_var.get()
        out_path = self.download_path.get()

        outtmpl = os.path.join(out_path, "%(title)s.%(ext)s")

        if fmt == "mp3":
            # Parse bitrate
            bitrate = "192"
            if "128" in quality: bitrate = "128"
            elif "256" in quality: bitrate = "256"
            elif "320" in quality: bitrate = "320"

            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": outtmpl,
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": bitrate,
                }],
                "progress_hooks": [self._progress_hook],
                "quiet": True,
                **(({"ffmpeg_location": FFMPEG_DIR}) if FFMPEG_DIR else {}),
            }
        else:
            # MP4 with video + audio merged
            if "Best" in quality:
                fmt_selector = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best"
            else:
                # Extract height from quality string like "1080p  HD  ~45 MB"
                h = quality.split("p")[0].strip()
                try:
                    h = int(h)
                    fmt_selector = (
                        f"bestvideo[height<={h}][ext=mp4]+bestaudio[ext=m4a]/"
                        f"bestvideo[height<={h}]+bestaudio/best[height<={h}]"
                    )
                except ValueError:
                    fmt_selector = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best"

            ydl_opts = {
                "format": fmt_selector,
                "outtmpl": outtmpl,
                "merge_output_format": "mp4",
                "postprocessors": [{
                    "key": "FFmpegVideoConvertor",
                    "preferedformat": "mp4",
                }],
                "progress_hooks": [self._progress_hook],
                "quiet": True,
                **(({"ffmpeg_location": FFMPEG_DIR}) if FFMPEG_DIR else {}),
            }

        try:
            self._log(f"⬇  Downloading [{fmt.upper()}] — {quality}", ACCENT2)
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            self.after(0, self._on_done)
        except Exception as ex:
            self.after(0, self._log, f"✗ Download failed: {ex}", ERROR)
            self.after(0, self.progress_label.config,
                       {"text": "Download failed.", "fg": ERROR})

    def _progress_hook(self, d):
        if d["status"] == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate", 0)
            downloaded = d.get("downloaded_bytes", 0)
            speed = d.get("speed", 0) or 0
            eta = d.get("eta", 0) or 0
            pct = (downloaded / total * 100) if total else 0

            speed_str = f"{speed/1024/1024:.1f} MB/s" if speed > 0 else "…"
            eta_str = f"{eta}s" if eta else "…"
            label = f"{pct:.1f}%  ·  {speed_str}  ·  ETA {eta_str}"

            self.after(0, self.progress_var.set, pct)
            self.after(0, self.progress_label.config, {"text": label, "fg": SUBTEXT})

        elif d["status"] == "finished":
            self.after(0, self.progress_var.set, 99)
            self.after(0, self.progress_label.config,
                       {"text": "Merging / Converting…", "fg": ACCENT2})

    def _on_done(self):
        self.progress_var.set(100)
        self.progress_label.config(text="✓  Download complete!", fg=SUCCESS)
        self._log(f"✓  Saved to: {self.download_path.get()}", SUCCESS)
        messagebox.showinfo("Done!", f"File saved to:\n{self.download_path.get()}")


if __name__ == "__main__":
    app = VortexDownloader()
    app.mainloop()