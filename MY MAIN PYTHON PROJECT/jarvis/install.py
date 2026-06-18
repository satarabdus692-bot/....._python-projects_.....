#!/usr/bin/env python3
"""
JARVIS Auto-Installer
Run this once before launching Jarvis for the first time.
"""

import sys
import subprocess
import platform

SYSTEM = platform.system()

PACKAGES = [
    "requests",
    "pyttsx3",
    "SpeechRecognition",
    "yt-dlp",
    "pytube",
    "instaloader",
    "gdown",
    "googlesearch-python",
    "wikipedia",
    "feedparser",
    "pyautogui",
    "Pillow",
    "colorama",
]

WINDOWS_EXTRA = ["pycaw", "comtypes"]
OPTIONAL = ["pyaudio"]  # handled separately due to platform quirks


def install(package):
    print(f"  Installing {package}...", end=" ", flush=True)
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", package, "--quiet"],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        print("✓")
    else:
        print(f"✗  ({result.stderr.strip()[:80]})")


def install_pyaudio():
    print("\n  Installing PyAudio (microphone support)...")
    if SYSTEM == "Windows":
        # Try pipwin first
        result = subprocess.run([sys.executable, "-m", "pip", "install", "pipwin", "--quiet"],
                                capture_output=True)
        if result.returncode == 0:
            subprocess.run([sys.executable, "-m", "pipwin", "install", "pyaudio"])
        else:
            subprocess.run([sys.executable, "-m", "pip", "install", "pyaudio"])
    else:
        subprocess.run([sys.executable, "-m", "pip", "install", "pyaudio"])


def main():
    print("\n" + "═" * 60)
    print("  JARVIS — Dependency Installer")
    print("═" * 60)
    print(f"  Python: {sys.version.split()[0]}  |  OS: {SYSTEM}\n")

    print("  Upgrading pip...")
    subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip", "--quiet"])

    print("\n  Installing core packages:")
    for pkg in PACKAGES:
        install(pkg)

    if SYSTEM == "Windows":
        print("\n  Installing Windows extras:")
        for pkg in WINDOWS_EXTRA:
            install(pkg)

    install_pyaudio()

    print("\n" + "═" * 60)
    print("  Installation complete!")
    print("  Run Jarvis with:  python jarvis.py")
    print("═" * 60 + "\n")


if __name__ == "__main__":
    main()
