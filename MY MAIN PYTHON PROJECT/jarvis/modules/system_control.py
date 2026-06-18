"""
JARVIS System Control
Open apps, control volume, take screenshots, shutdown/restart PC.
"""

import os
import sys
import platform
import subprocess
import webbrowser
import re


SYSTEM = platform.system()  # "Windows" | "Linux" | "Darwin"


class SystemControl:
    def __init__(self, voice, logger, display):
        self.voice = voice
        self.logger = logger
        self.display = display

        # Map common app names to executables
        self.app_map = {
            "notepad":      {"Windows": "notepad.exe",  "Linux": "gedit",       "Darwin": "TextEdit"},
            "calculator":   {"Windows": "calc.exe",     "Linux": "gnome-calculator", "Darwin": "Calculator"},
            "paint":        {"Windows": "mspaint.exe",  "Linux": "gimp",        "Darwin": ""},
            "chrome":       {"Windows": "chrome",       "Linux": "google-chrome","Darwin": "Google Chrome"},
            "firefox":      {"Windows": "firefox",      "Linux": "firefox",     "Darwin": "Firefox"},
            "edge":         {"Windows": "msedge",       "Linux": "microsoft-edge","Darwin": ""},
            "word":         {"Windows": "winword.exe",  "Linux": "libreoffice --writer","Darwin": "Microsoft Word"},
            "excel":        {"Windows": "excel.exe",    "Linux": "libreoffice --calc","Darwin": "Microsoft Excel"},
            "powerpoint":   {"Windows": "powerpnt.exe", "Linux": "libreoffice --impress","Darwin": ""},
            "vlc":          {"Windows": "vlc",          "Linux": "vlc",         "Darwin": "VLC"},
            "explorer":     {"Windows": "explorer.exe", "Linux": "nautilus",    "Darwin": "Finder"},
            "task manager": {"Windows": "taskmgr.exe",  "Linux": "gnome-system-monitor","Darwin": "Activity Monitor"},
            "terminal":     {"Windows": "cmd.exe",      "Linux": "gnome-terminal","Darwin": "Terminal"},
            "vscode":       {"Windows": "code",         "Linux": "code",        "Darwin": "Visual Studio Code"},
            "spotify":      {"Windows": "spotify",      "Linux": "spotify",     "Darwin": "Spotify"},
            "discord":      {"Windows": "discord",      "Linux": "discord",     "Darwin": "Discord"},
        }

    # ─────────────────────────────────────────────────────────────────────────
    # OPEN APP
    # ─────────────────────────────────────────────────────────────────────────

    def open_app(self, app_name: str):
        app_lower = app_name.lower().strip()
        executable = None

        for key, platforms in self.app_map.items():
            if key in app_lower:
                executable = platforms.get(SYSTEM, "")
                break

        if not executable:
            executable = app_name  # try as-is

        try:
            if SYSTEM == "Windows":
                os.startfile(executable)
            elif SYSTEM == "Darwin":
                subprocess.Popen(["open", "-a", executable])
            else:
                subprocess.Popen([executable], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            self.display.print_status(f"Opened: {app_name}", "SUCCESS")
            self.logger.log(f"Opened app: {app_name}")
        except Exception as e:
            self.voice.speak(f"Could not open {app_name}. It may not be installed.")
            self.display.print_status(f"App open error: {e}", "ERROR")

    # ─────────────────────────────────────────────────────────────────────────
    # OPEN WEBSITE
    # ─────────────────────────────────────────────────────────────────────────

    def open_website(self, url: str):
        if not re.match(r"https?://", url, re.IGNORECASE):
            if re.match(r"www\.", url, re.IGNORECASE):
                url = "https://" + url
            else:
                url = "https://www." + url

        try:
            webbrowser.open(url)
            self.display.print_status(f"Opened: {url}", "SUCCESS")
        except Exception as e:
            self.display.print_status(f"Browser error: {e}", "ERROR")

    # ─────────────────────────────────────────────────────────────────────────
    # VOLUME CONTROL
    # ─────────────────────────────────────────────────────────────────────────

    def volume_up(self):
        self._volume_change("up")

    def volume_down(self):
        self._volume_change("down")

    def volume_mute(self):
        self._volume_change("mute")

    def _volume_change(self, action: str):
        try:
            if SYSTEM == "Windows":
                from ctypes import cast, POINTER
                from comtypes import CLSCTX_ALL
                from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
                import math

                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                volume = cast(interface, POINTER(IAudioEndpointVolume))

                current = volume.GetMasterVolumeLevelScalar()

                if action == "up":
                    new_vol = min(1.0, current + 0.1)
                    volume.SetMasterVolumeLevelScalar(new_vol, None)
                    self.voice.speak(f"Volume increased to {int(new_vol * 100)}%")
                elif action == "down":
                    new_vol = max(0.0, current - 0.1)
                    volume.SetMasterVolumeLevelScalar(new_vol, None)
                    self.voice.speak(f"Volume decreased to {int(new_vol * 100)}%")
                elif action == "mute":
                    muted = volume.GetMute()
                    volume.SetMute(not muted, None)
                    self.voice.speak("Muted" if not muted else "Unmuted")

            elif SYSTEM == "Linux":
                if action == "up":
                    subprocess.run(["amixer", "-D", "pulse", "sset", "Master", "10%+"], capture_output=True)
                    self.voice.speak("Volume increased.")
                elif action == "down":
                    subprocess.run(["amixer", "-D", "pulse", "sset", "Master", "10%-"], capture_output=True)
                    self.voice.speak("Volume decreased.")
                elif action == "mute":
                    subprocess.run(["amixer", "-D", "pulse", "sset", "Master", "toggle"], capture_output=True)
                    self.voice.speak("Volume toggled.")

            elif SYSTEM == "Darwin":
                if action == "up":
                    subprocess.run(["osascript", "-e", "set volume output volume (output volume of (get volume settings) + 10)"])
                elif action == "down":
                    subprocess.run(["osascript", "-e", "set volume output volume (output volume of (get volume settings) - 10)"])
                elif action == "mute":
                    subprocess.run(["osascript", "-e", "set volume with output muted"])

            self.logger.log(f"Volume {action}")

        except Exception as e:
            self.voice.speak("Could not adjust volume.")
            self.display.print_status(f"Volume error: {e}", "ERROR")

    # ─────────────────────────────────────────────────────────────────────────
    # SCREENSHOT
    # ─────────────────────────────────────────────────────────────────────────

    def screenshot(self):
        from pathlib import Path
        from datetime import datetime
        out_dir = Path.home() / "jarvis_downloads" / "screenshots"
        out_dir.mkdir(parents=True, exist_ok=True)
        filename = out_dir / f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"

        try:
            import pyautogui
            img = pyautogui.screenshot()
            img.save(str(filename))
            self.voice.speak(f"Screenshot saved.")
            self.display.print_status(f"Screenshot: {filename}", "SUCCESS")

        except ImportError:
            try:
                from PIL import ImageGrab
                img = ImageGrab.grab()
                img.save(str(filename))
                self.voice.speak("Screenshot saved.")
                self.display.print_status(f"Screenshot: {filename}", "SUCCESS")
            except Exception:
                try:
                    if SYSTEM == "Linux":
                        subprocess.run(["scrot", str(filename)])
                        self.voice.speak("Screenshot saved.")
                    elif SYSTEM == "Darwin":
                        subprocess.run(["screencapture", str(filename)])
                        self.voice.speak("Screenshot saved.")
                    elif SYSTEM == "Windows":
                        subprocess.run(["snippingtool"], capture_output=True)
                except Exception as e:
                    self.display.print_status(f"Screenshot failed: {e}", "ERROR")

        except Exception as e:
            self.display.print_status(f"Screenshot error: {e}", "ERROR")

    # ─────────────────────────────────────────────────────────────────────────
    # POWER
    # ─────────────────────────────────────────────────────────────────────────

    def shutdown_pc(self):
        self.display.print_status("Shutting down...", "WARN")
        self.logger.log("System shutdown initiated")
        try:
            if SYSTEM == "Windows":
                os.system("shutdown /s /t 1")
            elif SYSTEM in ("Linux", "Darwin"):
                os.system("sudo shutdown -h now")
        except Exception as e:
            self.display.print_status(f"Shutdown error: {e}", "ERROR")

    def restart_pc(self):
        self.display.print_status("Restarting...", "WARN")
        self.logger.log("System restart initiated")
        try:
            if SYSTEM == "Windows":
                os.system("shutdown /r /t 1")
            elif SYSTEM in ("Linux", "Darwin"):
                os.system("sudo shutdown -r now")
        except Exception as e:
            self.display.print_status(f"Restart error: {e}", "ERROR")
