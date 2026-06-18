"""
JARVIS Downloader
Handles YouTube, Instagram, general URL, and Google Drive downloads.
"""

import os
import re
import sys
import subprocess
import requests
from pathlib import Path
from datetime import datetime


class Downloader:
    def __init__(self, voice, logger, display):
        self.voice = voice
        self.logger = logger
        self.display = display

        # Base download folder
        self.base = Path(os.path.expanduser("~/jarvis_downloads"))
        self.dirs = {
            "youtube":      self.base / "youtube",
            "instagram":    self.base / "instagram",
            "google_drive": self.base / "google_drive",
            "general":      self.base / "general",
        }
        for d in self.dirs.values():
            d.mkdir(parents=True, exist_ok=True)

    # ─────────────────────────────────────────────────────────────────────────
    # YOUTUBE
    # ─────────────────────────────────────────────────────────────────────────

    def youtube(self, query: str, audio_only: bool = False):
        """
        Download a YouTube video or audio-only file.
        Uses yt-dlp (preferred) or pytube as fallback.
        """
        out_dir = self.dirs["youtube"]

        # Ask format preference
        print("\n  📺 Download format:")
        print("     [1] Best video + audio (MP4)")
        print("     [2] Audio only (MP3)")
        print("     [3] Best quality (any format)")
        choice = input("  Choose [1/2/3, default 1]: ").strip() or "1"

        if choice == "2":
            fmt = "bestaudio/best"
            ext = "mp3"
            pp = [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}]
            audio_only = True
        elif choice == "3":
            fmt = "best"
            ext = "%(ext)s"
            pp = []
        else:
            fmt = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"
            ext = "mp4"
            pp = []

        self.display.print_status(f"Downloading: {query}", "DOWNLOAD")

        # Build search query (prepend ytsearch: if not a URL)
        if not re.match(r"https?://", query):
            search_target = f"ytsearch:{query}"
        else:
            search_target = query

        # ── Try yt-dlp ────────────────────────────────────────────────────────
        try:
            import yt_dlp

            ydl_opts = {
                "format": fmt,
                "outtmpl": str(out_dir / "%(title)s.%(ext)s"),
                "quiet": False,
                "no_warnings": False,
                "progress_hooks": [self._yt_hook],
                "noplaylist": True,
            }
            if audio_only:
                ydl_opts["postprocessors"] = pp

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([search_target])

            self.voice.speak(f"Download complete. Saved to {out_dir}")
            self.display.print_status(f"Saved to: {out_dir}", "SUCCESS")
            self.logger.log(f"YouTube downloaded: {query} -> {out_dir}")
            return

        except ImportError:
            self.display.print_status("yt-dlp not installed. Trying pytube...", "WARN")

        # ── Fallback: pytube ──────────────────────────────────────────────────
        try:
            from pytube import YouTube, Search

            if re.match(r"https?://", query):
                url = query
            else:
                results = Search(query).results
                if not results:
                    self.voice.speak("No results found on YouTube.")
                    return
                url = results[0].watch_url
                self.display.print_status(f"Found: {results[0].title}", "INFO")

            yt = YouTube(url)
            self.display.print_status(f"Title: {yt.title}", "INFO")

            if audio_only:
                stream = yt.streams.filter(only_audio=True).first()
            else:
                stream = (yt.streams.filter(progressive=True, file_extension="mp4")
                    .order_by("resolution").desc().first())

            if not stream:
                stream = yt.streams.first()

            path = stream.download(output_path=str(out_dir))
            self.voice.speak(f"Download complete. Saved to downloads folder.")
            self.display.print_status(f"Saved: {path}", "SUCCESS")
            self.logger.log(f"YouTube (pytube) downloaded: {query}")

        except Exception as e:
            self.voice.speak(f"Download failed: {str(e)}")
            self.display.print_status(f"YouTube error: {e}", "ERROR")
            self.logger.error(f"YouTube download error: {e}")
            print("\n  💡 Tip: Install yt-dlp for best results: pip install yt-dlp")

    def _yt_hook(self, d):
        if d["status"] == "downloading":
            percent = d.get("_percent_str", "?").strip()
            speed   = d.get("_speed_str", "?").strip()
            eta     = d.get("_eta_str", "?").strip()
            print(f"\r  ⬇️  {percent}  Speed: {speed}  ETA: {eta}    ", end="", flush=True)
        elif d["status"] == "finished":
            print()
            self.display.print_status("Processing file...", "INFO")

    # ─────────────────────────────────────────────────────────────────────────
    # INSTAGRAM
    # ─────────────────────────────────────────────────────────────────────────

    def instagram(self, url: str = None, query: str = None):
        """Download Instagram content using yt-dlp (handles reels, posts, stories)."""
        out_dir = self.dirs["instagram"]

        if not url and query:
            # yt-dlp can also search instagram via URL; ask user
            self.voice.speak("Please provide the direct Instagram URL for the reel or post.")
            url = input("  Instagram URL: ").strip()
            if not url:
                return

        if not url:
            self.voice.speak("No URL provided.")
            return

        self.display.print_status(f"Downloading from Instagram: {url}", "DOWNLOAD")

        try:
            import yt_dlp

            ydl_opts = {
                "outtmpl": str(out_dir / "%(uploader)s_%(id)s.%(ext)s"),
                "quiet": False,
                "progress_hooks": [self._yt_hook],
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            self.voice.speak("Instagram download complete.")
            self.display.print_status(f"Saved to: {out_dir}", "SUCCESS")
            self.logger.log(f"Instagram downloaded: {url}")

        except ImportError:
            # Fallback: instaloader
            self._instagram_instaloader(url, out_dir)
        except Exception as e:
            self.voice.speak(f"Instagram download failed: {str(e)}")
            self.display.print_status(f"Error: {e}", "ERROR")
            self.logger.error(f"Instagram download error: {e}")

    def _instagram_instaloader(self, url: str, out_dir: Path):
        try:
            import instaloader
            L = instaloader.Instaloader(
                dirname_pattern=str(out_dir / "{target}"),
                download_video_thumbnails=False,
                save_metadata=False,
            )
            shortcode = re.search(r"/p/([^/]+)|/reel/([^/]+)", url)
            if shortcode:
                code = shortcode.group(1) or shortcode.group(2)
                post = instaloader.Post.from_shortcode(L.context, code)
                L.download_post(post, target=str(out_dir))
                self.voice.speak("Instagram download complete via instaloader.")
                self.display.print_status(f"Saved to: {out_dir}", "SUCCESS")
            else:
                self.voice.speak("Could not extract post ID from URL.")
        except ImportError:
            self.voice.speak("Please install yt-dlp: pip install yt-dlp")
        except Exception as e:
            self.voice.speak(f"Download failed: {str(e)}")
            self.display.print_status(f"Error: {e}", "ERROR")

    # ─────────────────────────────────────────────────────────────────────────
    # GENERAL URL
    # ─────────────────────────────────────────────────────────────────────────

    def general_url(self, url: str):
        """Download any file from a direct URL with progress bar."""
        out_dir = self.dirs["general"]

        try:
            import yt_dlp
            # First try yt-dlp (handles most video/audio sites)
            ydl_opts = {
                "outtmpl": str(out_dir / "%(title)s.%(ext)s"),
                "quiet": False,
                "progress_hooks": [self._yt_hook],
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if info:
                    ydl.download([url])
                    self.voice.speak("Download complete.")
                    self.display.print_status(f"Saved to: {out_dir}", "SUCCESS")
                    return
        except Exception:
            pass

        # Fallback: requests stream download
        try:
            self.display.print_status(f"Downloading: {url}", "DOWNLOAD")
            r = requests.get(url, stream=True, timeout=30)
            r.raise_for_status()

            # Determine filename
            filename = url.split("/")[-1].split("?")[0] or f"download_{datetime.now().strftime('%H%M%S')}"
            if not Path(filename).suffix:
                ct = r.headers.get("content-type", "")
                ext_map = {"image/jpeg": ".jpg", "image/png": ".png",
                            "video/mp4": ".mp4", "application/pdf": ".pdf"}
                filename += ext_map.get(ct.split(";")[0].strip(), ".bin")

            out_path = out_dir / filename
            total = int(r.headers.get("content-length", 0))
            downloaded = 0

            with open(out_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total:
                            pct = downloaded / total * 100
                            print(f"\r  ⬇️  {pct:.1f}%  ({downloaded:,} / {total:,} bytes)  ", end="", flush=True)
            print()

            self.voice.speak(f"Download complete. Saved as {filename}")
            self.display.print_status(f"Saved: {out_path}", "SUCCESS")
            self.logger.log(f"General URL downloaded: {url}")

        except Exception as e:
            self.voice.speak(f"Download failed: {str(e)}")
            self.display.print_status(f"Error: {e}", "ERROR")
            self.logger.error(f"General URL download error: {e}")

    # ─────────────────────────────────────────────────────────────────────────
    # GOOGLE DRIVE
    # ─────────────────────────────────────────────────────────────────────────

    def google_drive(self, file_id_or_name: str):
        """
        Download a file from Google Drive.
        Supports: direct file ID, shareable link, or file name (with gdown).
        """
        out_dir = self.dirs["google_drive"]
        self.display.print_status(f"Accessing Google Drive: {file_id_or_name}", "DOWNLOAD")

        # Extract file ID from a shareable URL if needed
        url_match = re.search(r"/d/([a-zA-Z0-9_-]{25,})", file_id_or_name)
        if url_match:
            file_id = url_match.group(1)
        elif re.match(r"^[a-zA-Z0-9_-]{25,}$", file_id_or_name):
            file_id = file_id_or_name
        else:
            # Treat as a search name — user must provide ID
            self.voice.speak(
                "Google Drive requires a file ID or shareable link. "
                "Please provide the file ID or the share link."
            )
            file_id = input("  File ID or share link: ").strip()
            url_match = re.search(r"/d/([a-zA-Z0-9_-]{25,})", file_id)
            if url_match:
                file_id = url_match.group(1)

        if not file_id:
            self.voice.speak("No valid file ID provided.")
            return

        # ── Try gdown ────────────────────────────────────────────────────────
        try:
            import gdown
            out_path = str(out_dir) + "/"
            url = f"https://drive.google.com/uc?id={file_id}"
            result = gdown.download(url, out_path, quiet=False, fuzzy=True)

            if result:
                self.voice.speak(f"Google Drive file downloaded successfully.")
                self.display.print_status(f"Saved to: {out_dir}", "SUCCESS")
                self.logger.log(f"Google Drive downloaded: {file_id}")
            else:
                self.voice.speak("Download failed. The file may be private or the ID may be incorrect.")

        except ImportError:
            # Fallback: direct requests (public files only)
            self._gdrive_requests(file_id, out_dir)
        except Exception as e:
            self.voice.speak(f"Google Drive error: {str(e)}")
            self.display.print_status(f"Error: {e}", "ERROR")
            self.logger.error(f"Google Drive error: {e}")

    def _gdrive_requests(self, file_id: str, out_dir: Path):
        try:
            self.display.print_status("Using direct download (public files only)...", "INFO")
            session = requests.Session()
            url = f"https://docs.google.com/uc?export=download&id={file_id}"
            r = session.get(url, stream=True)

            # Handle Google's download warning token
            token = None
            for key, value in r.cookies.items():
                if key.startswith("download_warning"):
                    token = value
                    break

            if token:
                r = session.get(url, params={"confirm": token}, stream=True)

            r.raise_for_status()
            filename = f"gdrive_{file_id[:8]}.bin"
            out_path = out_dir / filename

            with open(out_path, "wb") as f:
                for chunk in r.iter_content(32768):
                    if chunk:
                        f.write(chunk)

            self.voice.speak("Google Drive file downloaded.")
            self.display.print_status(f"Saved: {out_path}", "SUCCESS")

        except Exception as e:
            self.voice.speak(f"Google Drive download failed: {str(e)}")
            self.display.print_status(f"Error: {e}", "ERROR")
            print("\n  💡 Tip: Install gdown for better Google Drive support: pip install gdown")
