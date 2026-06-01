# ⬡ VORTEX — Universal Video Downloader

> A sleek, dark-themed desktop app for downloading videos and audio from YouTube, Instagram, TikTok, Twitter/X, Facebook, and hundreds of other platforms.

![Python](https://img.shields.io/badge/Python-3.8%2B-7c5cfc?style=flat-square&logo=python&logoColor=white)
![yt-dlp](https://img.shields.io/badge/powered%20by-yt--dlp-a78bfa?style=flat-square)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-22d3a5?style=flat-square)
![License](https://img.shields.io/badge/license-MIT-ff5c7a?style=flat-square)

---

## ✨ Features

- **Multi-platform support** — YouTube, Instagram, TikTok, Twitter/X, Facebook, and [1000+ more sites](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md) via yt-dlp
- **MP4 or MP3** — Download full video or extract audio-only with one click
- **Quality selector** — Choose from all available resolutions (144p → 4K) or bitrates (128–320 kbps)
- **Live thumbnail preview** — Loads the video thumbnail with title, uploader, duration, and view count before downloading
- **Smart URL cleaner** — Automatically strips tracking params, playlist IDs, and junk from pasted URLs
- **Real-time progress** — Progress bar with download speed and ETA
- **Custom save location** — Browse to any folder on your system
- **Scrollable activity log** — Color-coded status messages for every step

---

## 📸 Screenshots

> _Add screenshots of your app here by dragging images into this section on GitHub._

---

## 🔧 Requirements

| Dependency | Version | Purpose |
|---|---|---|
| Python | 3.8+ | Runtime |
| [yt-dlp](https://github.com/yt-dlp/yt-dlp) | latest | Video extraction & downloading |
| [Pillow](https://python-pillow.org/) | 9.0+ | Thumbnail rendering |
| [ffmpeg](https://ffmpeg.org/) | any recent | Audio/video merging & conversion |

> **Note:** `yt-dlp` and `Pillow` are installed automatically on first run if missing. `ffmpeg` must be installed separately.

---

## 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/vortex-downloader.git
cd vortex-downloader
```

### 2. Install Python dependencies

```bash
pip install yt-dlp Pillow
```

### 3. Install ffmpeg

<details>
<summary><strong>Windows</strong></summary>

Download from [ffmpeg.org](https://ffmpeg.org/download.html) and either:
- Add the `bin/` folder to your system PATH, **or**
- Drop `ffmpeg.exe` into a `bin/` folder next to `video_downloader.py` — Vortex will find it automatically.

</details>

<details>
<summary><strong>macOS</strong></summary>

```bash
brew install ffmpeg
```

</details>

<details>
<summary><strong>Linux</strong></summary>

```bash
sudo apt install ffmpeg        # Debian/Ubuntu
sudo dnf install ffmpeg        # Fedora
sudo pacman -S ffmpeg          # Arch
```

</details>

### 4. Run the app

```bash
python video_downloader.py
```

---

## 🖥️ Usage

1. **Paste a URL** into the input field and press **Enter** or click **FETCH**
2. The app loads the thumbnail, title, uploader, and available quality options
3. Choose **MP4** (video) or **MP3** (audio) and pick a quality from the dropdown
4. Select a save folder with **BROWSE** (defaults to `~/Downloads`)
5. Click **↓ DOWNLOAD** and watch the progress bar

### URL Cleaning

Vortex automatically sanitizes URLs before fetching. For example:

```
# Input (messy share link)
https://www.youtube.com/watch?v=dQw4w9WgXcQ&list=PL...&si=abc&utm_source=share

# Cleaned automatically
https://www.youtube.com/watch?v=dQw4w9WgXcQ
```

Stripped parameters include: `list`, `si`, `utm_*`, `fbclid`, `igshid`, `ref`, `ab_channel`, and more. `youtu.be` short links are also converted to full watch URLs.

---

## 📂 Project Structure

```
vortex-downloader/
├── video_downloader.py   # Main application
├── bin/                  # Optional: place ffmpeg.exe here (Windows)
│   └── ffmpeg.exe
└── README.md
```

---

## ⚙️ Building a Standalone Executable (Optional)

You can bundle the app into a single `.exe` with [PyInstaller](https://pyinstaller.org/):

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name Vortex video_downloader.py
```

To bundle ffmpeg alongside it, place `ffmpeg.exe` in a `bin/` folder and add `--add-binary "bin/ffmpeg.exe;bin"` to the command.

---

## 🐛 Troubleshooting

| Issue | Fix |
|---|---|
| `ffmpeg not found` error | Ensure ffmpeg is in PATH or in a `bin/` folder next to the script |
| Download fails on Instagram/TikTok | Log in via browser cookies: add `"cookiesfrombrowser": "chrome"` to `ydl_opts` |
| No audio in downloaded MP4 | ffmpeg is required for merging — make sure it's installed |
| Thumbnail not loading | Likely a network timeout; the download will still work fine |
| `yt-dlp` site not supported | Check the [supported sites list](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md) |

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature/my-feature`
5. Open a Pull Request

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

## ⚠️ Disclaimer

Vortex is intended for downloading content you have the right to download (e.g. your own uploads, public domain content, or content explicitly permitted by the platform). Always respect copyright law and the terms of service of the platforms you use.

---

<div align="center">
  Built with Python, yt-dlp, and <code>⬡ VORTEX</code> vibes.
</div>
