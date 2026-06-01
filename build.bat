@echo off
:: ============================================================
::  VORTEX DOWNLOADER  --  Build Script
::  Run this ONCE on your PC to produce VortexDownloader.exe
:: ============================================================

title VORTEX Build

echo.
echo  ==========================================
echo   VORTEX DOWNLOADER  --  EXE Builder
echo  ==========================================
echo.

:: ── 1. Check Python ──────────────────────────────────────────
python --version >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Python not found. Install from https://python.org
    pause & exit /b 1
)

:: ── 2. Install / upgrade build tools ─────────────────────────
echo  [1/5] Installing dependencies...
pip install --upgrade pyinstaller yt-dlp Pillow --quiet
if errorlevel 1 (
    echo  [ERROR] pip install failed.
    pause & exit /b 1
)
echo        Done.

:: ── 3. Check for ffmpeg in .\bin\ ────────────────────────────
echo.
echo  [2/5] Checking for ffmpeg binaries...
if not exist "bin\ffmpeg.exe" (
    echo.
    echo  [!] bin\ffmpeg.exe NOT found.
    echo.
    echo      Download ffmpeg from:
    echo        https://www.gyan.dev/ffmpeg/builds/
    echo      Get the "release essentials" zip, then copy:
    echo        ffmpeg.exe   -->  bin\ffmpeg.exe
    echo        ffprobe.exe  -->  bin\ffprobe.exe
    echo.
    echo      Re-run this script after placing the files.
    echo.
    pause & exit /b 1
)
echo        Found bin\ffmpeg.exe  OK
if exist "bin\ffprobe.exe" (
    echo        Found bin\ffprobe.exe OK
)

:: ── 4. Run PyInstaller ────────────────────────────────────────
echo.
echo  [3/5] Running PyInstaller (this takes ~1-2 minutes)...
echo.

pyinstaller ^
    --noconfirm ^
    --onedir ^
    --windowed ^
    --name "VortexDownloader" ^
    --add-data "bin\ffmpeg.exe;bin" ^
    --add-data "bin\ffprobe.exe;bin" ^
    --hidden-import "yt_dlp" ^
    --hidden-import "yt_dlp.utils" ^
    --hidden-import "yt_dlp.extractor" ^
    --hidden-import "yt_dlp.postprocessor" ^
    --hidden-import "PIL" ^
    --hidden-import "PIL.Image" ^
    --hidden-import "PIL.ImageTk" ^
    --hidden-import "PIL.ImageDraw" ^
    --collect-all yt_dlp ^
    --collect-all PIL ^
    app.py

if errorlevel 1 (
    echo.
    echo  [ERROR] PyInstaller failed. See output above.
    pause & exit /b 1
)

:: ── 5. Done ───────────────────────────────────────────────────
echo.
echo  [4/5] Build complete!
echo.
echo  ============================================================
echo   Your app is ready at:
echo     dist\VortexDownloader\VortexDownloader.exe
echo.
echo   To share with someone:
echo     Zip the entire  dist\VortexDownloader\  folder
echo     They just unzip and double-click VortexDownloader.exe
echo     No Python, no ffmpeg, no pip needed on their PC!
echo  ============================================================
echo.
pause
