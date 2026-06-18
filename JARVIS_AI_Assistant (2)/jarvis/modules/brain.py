"""
JARVIS Brain - Natural Language Understanding & Command Router
"""

import re
import datetime
import os
import sys
from modules.downloader import Downloader
from modules.searcher import Searcher
from modules.system_control import SystemControl
from modules.utilities import Utilities

# ── Known websites (name → URL) ──────────────────────────────────────────────
KNOWN_SITES = {
    "youtube":    "https://www.youtube.com",
    "yt":         "https://www.youtube.com",
    "google":     "https://www.google.com",
    "facebook":   "https://www.facebook.com",
    "instagram":  "https://www.instagram.com",
    "twitter":    "https://www.twitter.com",
    "x":          "https://www.x.com",
    "reddit":     "https://www.reddit.com",
    "github":     "https://www.github.com",
    "netflix":    "https://www.netflix.com",
    "amazon":     "https://www.amazon.com",
    "wikipedia":  "https://www.wikipedia.org",
    "gmail":      "https://mail.google.com",
    "whatsapp":   "https://web.whatsapp.com",
    "linkedin":   "https://www.linkedin.com",
    "tiktok":     "https://www.tiktok.com",
    "spotify":    "https://open.spotify.com",
    "chatgpt":    "https://chat.openai.com",
    "claude":     "https://claude.ai",
    "stackoverflow": "https://stackoverflow.com",
    "twitch":     "https://www.twitch.tv",
}

# ── Known apps (name → executable per OS) ────────────────────────────────────
KNOWN_APPS = [
    "notepad", "calculator", "paint", "chrome", "firefox", "edge",
    "word", "excel", "powerpoint", "vlc", "explorer", "task manager",
    "terminal", "vscode", "spotify", "discord", "cmd", "settings",
]


class Brain:
    def __init__(self, voice, logger, display):
        self.voice   = voice
        self.logger  = logger
        self.display = display

        self.downloader = Downloader(voice=voice, logger=logger, display=display)
        self.searcher   = Searcher(voice=voice, logger=logger, display=display)
        self.system     = SystemControl(voice=voice, logger=logger, display=display)
        self.utils      = Utilities(voice=voice, logger=logger, display=display)

        # ── Intent patterns (most-specific first) ────────────────────────────
        # Each tuple: (compiled_regex, handler_method)
        self._intents = [

            # ── GOODBYE / SHUTDOWN JARVIS ─────────────────────────────────
            (r"\b(goodbye|bye|exit|quit|stop jarvis|shutdown jarvis|turn off jarvis|"
             r"see you|see you later|that('s| is) all|signing off)\b",
             self._do_goodbye),

            # ── IDENTITY ──────────────────────────────────────────────────
            (r"\b(who are you|what are you|your name|introduce yourself|"
             r"are you (an ai|a bot|jarvis))\b",
             self._do_identity),

            # ── HELP ──────────────────────────────────────────────────────
            (r"\b(help|what can you do|commands|capabilities|features|"
             r"list commands|show commands)\b",
             self._do_help),

            # ── YOUTUBE DOWNLOAD ──────────────────────────────────────────
            (r"(download|get|save|grab|fetch).{0,40}"
             r"(youtube|yt|video|song|music|audio|mp3|mp4)",
             self._do_yt_download),
            (r"(youtube|yt).{0,20}(download|save|get|fetch)",
             self._do_yt_download),

            # ── INSTAGRAM DOWNLOAD ────────────────────────────────────────
            (r"(download|get|save|grab|fetch).{0,40}"
             r"(instagram|insta|ig|reel|story)",
             self._do_insta_download),
            (r"(instagram|insta|ig).{0,20}(download|save|reel|video|photo)",
             self._do_insta_download),

            # ── GENERAL URL DOWNLOAD (direct link) ────────────────────────
            (r"(download|save|get|fetch).{0,20}(https?://\S+)",
             self._do_url_download),
            (r"https?://\S+",
             self._do_url_download),

            # ── GOOGLE DRIVE ──────────────────────────────────────────────
            (r"(fetch|get|download|open|retrieve).{0,30}"
             r"(google drive|drive|gdrive|g drive)",
             self._do_drive_download),

            # ── OPEN WEBSITE — named sites ────────────────────────────────
            # "go to youtube", "open youtube", "open youtube.com", etc.
            (r"(open|go to|visit|launch|browse|navigate to|take me to|show me).{0,10}"
             r"(" + "|".join(KNOWN_SITES.keys()) + r")\b",
             self._do_open_known_site),

            # bare site names without an action verb
            (r"^(" + "|".join(KNOWN_SITES.keys()) + r")(\.com|\.org|\.net|\.io)?\s*$",
             self._do_open_known_site),

            # ── OPEN WEBSITE — explicit URL or domain ─────────────────────
            (r"(open|go to|visit|launch|browse|navigate to|take me to).{0,10}"
             r"(www\.|https?://)",
             self._do_open_url),
            (r"(open|go to|visit)\s+([\w\-]+\.(com|org|net|io|gov|edu|co)[\S]*)",
             self._do_open_url),

            # ── OPEN APPLICATION ──────────────────────────────────────────
            (r"(open|launch|start|run|execute).{0,5}"
             r"(" + "|".join(KNOWN_APPS) + r")\b",
             self._do_open_app),
            (r"(open|launch|start|run).{0,10}(app|application|program|software)\s+\S+",
             self._do_open_app),

            # ── WEATHER ───────────────────────────────────────────────────
            (r"\b(weather|temperature|forecast|rain|sunny|climate|humidity)\b",
             self._do_weather),

            # ── DATE / TIME ───────────────────────────────────────────────
            (r"(what.{0,5}(time|date|day)|today.{0,10}(date|day)"
             r"|current time|what day|tell me the time|what is the time)",
             self._do_datetime),

            # ── JOKE ──────────────────────────────────────────────────────
            (r"\b(joke|tell me a joke|make me laugh|funny|humor|laugh)\b",
             self._do_joke),

            # ── CALCULATOR ────────────────────────────────────────────────
            (r"(calculate|compute|solve|math|what is \d|\d+\s*[\+\-\*\/\^]\s*\d+)",
             self._do_calculate),

            # ── REMINDER ──────────────────────────────────────────────────
            (r"\b(remind me|set (a |an )?reminder|set (an )?alarm|reminder|alarm|alert)\b",
             self._do_reminder),

            # ── NOTES ─────────────────────────────────────────────────────
            (r"\b(take a note|write (this |it )?down|note( down)?|save this|"
             r"remember this|make a note)\b",
             self._do_note),

            # ── LIST NOTES ────────────────────────────────────────────────
            (r"\b(show( my)? notes|list( my)? notes|read( my)? notes|my notes)\b",
             self._do_list_notes),

            # ── SCREENSHOT ────────────────────────────────────────────────
            (r"\b(screenshot|screen(shot| capture)|capture( the)? screen|"
             r"take a (screenshot|snap|picture of (the )?screen))\b",
             self._do_screenshot),

            # ── VOLUME ────────────────────────────────────────────────────
            (r"\b(volume|sound).{0,20}(up|increase|louder|higher|raise|boost)\b",
             self._do_vol_up),
            (r"\b(volume|sound).{0,20}(down|decrease|quieter|lower|reduce)\b",
             self._do_vol_down),
            (r"\b(mute|unmute|silence|quiet)\b",
             self._do_vol_mute),
            (r"\b(turn (up|down|off) (the )?(volume|sound))\b",
             self._do_volume_smart),

            # ── PC SHUTDOWN / RESTART ─────────────────────────────────────
            (r"\b(shutdown|shut down|power off|turn off).{0,20}"
             r"(computer|pc|system|machine|laptop|windows|this)\b",
             self._do_pc_shutdown),
            (r"\b(restart|reboot).{0,20}(computer|pc|system|machine|laptop)\b",
             self._do_pc_restart),

            # ── LIST FILES ────────────────────────────────────────────────
            (r"\b(list|show|display).{0,10}(files|folder|directory|downloads|my files)\b",
             self._do_list_files),

            # ── WIKIPEDIA ─────────────────────────────────────────────────
            (r"\b(wikipedia|wiki)\b",
             self._do_wikipedia),

            # ── NEWS ──────────────────────────────────────────────────────
            (r"\b(news|headlines|latest news|top stories|current events|"
             r"what('s| is) happening)\b",
             self._do_news),

            # ── WEB SEARCH — catch-all (must be near-last) ────────────────
            (r"\b(search( for)?|google|look up|find|what is|who is|"
             r"how (to|do|does|did|can)|tell me about|explain|define|"
             r"when (is|was|did)|where (is|was)|why (is|was|did))\b",
             self._do_web_search),
        ]

        # Pre-compile all patterns
        self._compiled = [
            (re.compile(pat, re.IGNORECASE), fn)
            for pat, fn in self._intents
        ]

    # ─────────────────────────────────────────────────────────────────────────
    # PUBLIC: process a command string
    # ─────────────────────────────────────────────────────────────────────────

    def process(self, command: str):
        if not command:
            return
        cmd = command.strip()
        self.logger.log(f"Command: {cmd}")

        for regex, handler in self._compiled:
            if regex.search(cmd):
                try:
                    handler(cmd)
                except Exception as e:
                    self.logger.error(f"Handler error: {e}")
                    self.voice.speak(f"Sorry, I ran into an error: {e}")
                    self.display.print_status(f"Error: {e}", "ERROR")
                return

        # Nothing matched — try a smart fallback before giving up
        self._smart_fallback(cmd)

    # ─────────────────────────────────────────────────────────────────────────
    # HELPERS
    # ─────────────────────────────────────────────────────────────────────────

    def _strip(self, command: str, *words) -> str:
        """Remove specific words/phrases from command."""
        result = command
        for w in words:
            result = re.sub(rf"\b{re.escape(w)}\b", " ", result, flags=re.IGNORECASE)
        return re.sub(r"\s{2,}", " ", result).strip(" ,.-")

    def _after(self, command: str, *trigger_words) -> str:
        """Return text after the first matched trigger word."""
        for w in trigger_words:
            m = re.search(rf"\b{re.escape(w)}\b(.+)", command, re.IGNORECASE)
            if m:
                return m.group(1).strip(" ,.-")
        return command

    # ─────────────────────────────────────────────────────────────────────────
    # SMART FALLBACK
    # ─────────────────────────────────────────────────────────────────────────

    def _smart_fallback(self, cmd: str):
        """Last resort: check for bare site names or do a web search."""
        cmd_lower = cmd.lower().strip()

        # Single word that is a known site?
        for name, url in KNOWN_SITES.items():
            if re.fullmatch(rf"{re.escape(name)}(\.com|\.org|\.net|\.io)?", cmd_lower):
                self.voice.speak(f"Opening {name}.")
                self.system.open_website(url)
                return

        # Looks like a domain name?
        if re.search(r"\b\w+\.(com|org|net|io|gov|edu)\b", cmd_lower):
            self._do_open_url(cmd)
            return

        # Default: google it
        self.voice.speak(f"Let me search that for you.")
        self.searcher.web_search(cmd)

    # ─────────────────────────────────────────────────────────────────────────
    # HANDLERS
    # ─────────────────────────────────────────────────────────────────────────

    def _do_goodbye(self, cmd):
        self.voice.speak("Goodbye sir. It was a pleasure. Jarvis signing off.")
        self.display.print_status("Session ended.", "SUCCESS")
        sys.exit(0)

    def _do_identity(self, cmd):
        msg = ("I am Jarvis — Just A Rather Very Intelligent System. "
               "Your personal AI assistant. I can download videos, search the web, "
               "control your system, set reminders, and much more. How may I help?")
        self.voice.speak(msg)
        self.display.print_result(msg)

    def _do_help(self, cmd):
        self.display.print_help()
        self.voice.speak("Full command list is on screen.")

    # ── Downloads ─────────────────────────────────────────────────────────────

    def _do_yt_download(self, cmd):
        noise = ["download", "get", "save", "grab", "fetch", "please",
                 "jarvis", "youtube", "yt", "video", "song", "music",
                 "audio", "mp3", "mp4", "from", "the", "a", "an"]
        query = self._strip(cmd, *noise)
        if not query:
            self.voice.speak("What would you like me to download from YouTube?")
            query = input("  YouTube search: ").strip()
        if query:
            self.voice.speak(f"Downloading from YouTube: {query}")
            self.downloader.youtube(query)

    def _do_insta_download(self, cmd):
        url_m = re.search(r"https?://\S+", cmd)
        if url_m:
            self.voice.speak("Downloading from Instagram.")
            self.downloader.instagram(url=url_m.group())
        else:
            self.voice.speak("Please paste the Instagram post or reel URL.")
            url = input("  Instagram URL: ").strip()
            if url:
                self.downloader.instagram(url=url)

    def _do_url_download(self, cmd):
        url_m = re.search(r"https?://\S+", cmd)
        if url_m:
            self.voice.speak("Starting download.")
            self.downloader.general_url(url_m.group())
        else:
            self.voice.speak("Please provide the direct download URL.")
            url = input("  URL: ").strip()
            if url:
                self.downloader.general_url(url)

    def _do_drive_download(self, cmd):
        noise = ["fetch", "get", "download", "open", "retrieve", "from",
                 "google", "drive", "gdrive", "g", "file", "document",
                 "doc", "sheet", "folder", "please", "jarvis", "my", "the"]
        query = self._strip(cmd, *noise)
        if not query:
            self.voice.speak("What is the Google Drive file ID or share link?")
            query = input("  File ID / link: ").strip()
        if query:
            self.voice.speak(f"Accessing Google Drive.")
            self.downloader.google_drive(query)

    # ── Open website ──────────────────────────────────────────────────────────

    def _do_open_known_site(self, cmd):
        cmd_lower = cmd.lower()
        for name, url in KNOWN_SITES.items():
            if re.search(rf"\b{re.escape(name)}\b", cmd_lower):
                self.voice.speak(f"Opening {name}.")
                self.system.open_website(url)
                return
        # Fallback
        self._do_open_url(cmd)

    def _do_open_url(self, cmd):
        # Extract explicit URL
        url_m = re.search(r"(https?://\S+|www\.\S+|\w[\w\-]+\.(com|org|net|io|gov|edu|co)\S*)", cmd, re.IGNORECASE)
        if url_m:
            url = url_m.group()
            self.voice.speak(f"Opening {url}")
            self.system.open_website(url)
        else:
            noise = ["open", "go to", "visit", "launch", "browse",
                     "navigate to", "take me to", "show me",
                     "website", "site", "page", "please", "jarvis"]
            site = self._strip(cmd, *noise)
            if site:
                self.voice.speak(f"Opening {site}")
                self.system.open_website(site)

    # ── Open app ──────────────────────────────────────────────────────────────

    def _do_open_app(self, cmd):
        noise = ["open", "launch", "start", "run", "execute", "please",
                 "jarvis", "app", "application", "program", "software", "the"]
        app = self._strip(cmd, *noise)
        if app:
            self.voice.speak(f"Opening {app}.")
            self.system.open_app(app)

    # ── Info ──────────────────────────────────────────────────────────────────

    def _do_weather(self, cmd):
        noise = ["weather", "temperature", "forecast", "rain", "sunny",
                 "climate", "humidity", "in", "at", "for", "jarvis",
                 "please", "what", "is", "tell", "me", "the", "about",
                 "today", "tomorrow"]
        city = self._strip(cmd, *noise)
        if not city:
            self.voice.speak("Which city?")
            city = input("  City: ").strip()
        if city:
            self.voice.speak(f"Fetching weather for {city}.")
            self.searcher.weather(city)

    def _do_datetime(self, cmd):
        now      = datetime.datetime.now()
        date_str = now.strftime("%A, %B %d, %Y")
        time_str = now.strftime("%I:%M %p")
        msg = f"Today is {date_str}. The current time is {time_str}."
        self.voice.speak(msg)
        self.display.print_result(msg)

    def _do_joke(self, cmd):
        self.utils.tell_joke()

    def _do_calculate(self, cmd):
        noise = ["calculate", "compute", "solve", "what is", "math",
                 "jarvis", "please", "the", "result", "of"]
        expr = self._strip(cmd, *noise)
        self.utils.calculate(expr)

    def _do_reminder(self, cmd):
        noise = ["remind me", "set a reminder", "set an alarm", "reminder",
                 "alarm", "alert", "jarvis", "please"]
        content = self._strip(cmd, *noise)
        self.utils.set_reminder(content, cmd)

    def _do_note(self, cmd):
        noise = ["take a note", "write down", "note down", "note", "save this",
                 "remember this", "make a note", "jarvis", "please", "that"]
        content = self._strip(cmd, *noise)
        if not content:
            self.voice.speak("What should I note down?")
            content = input("  Note: ").strip()
        if content:
            self.utils.save_note(content)

    def _do_list_notes(self, cmd):
        self.utils.list_notes()

    def _do_screenshot(self, cmd):
        self.voice.speak("Taking a screenshot now.")
        self.system.screenshot()

    def _do_vol_up(self, cmd):
        self.system.volume_up()

    def _do_vol_down(self, cmd):
        self.system.volume_down()

    def _do_vol_mute(self, cmd):
        self.system.volume_mute()

    def _do_volume_smart(self, cmd):
        if "up" in cmd.lower() or "raise" in cmd.lower():
            self.system.volume_up()
        elif "down" in cmd.lower() or "lower" in cmd.lower():
            self.system.volume_down()
        else:
            self.system.volume_mute()

    def _do_pc_shutdown(self, cmd):
        self.voice.speak("Shutdown requested. Type 'yes' to confirm.")
        c = input("  Confirm shutdown? (yes/no): ").strip().lower()
        if c in ("yes", "y"):
            self.system.shutdown_pc()
        else:
            self.voice.speak("Shutdown cancelled.")

    def _do_pc_restart(self, cmd):
        self.voice.speak("Restart requested. Type 'yes' to confirm.")
        c = input("  Confirm restart? (yes/no): ").strip().lower()
        if c in ("yes", "y"):
            self.system.restart_pc()
        else:
            self.voice.speak("Restart cancelled.")

    def _do_list_files(self, cmd):
        noise = ["list", "show", "display", "files", "folder", "directory",
                 "downloads", "jarvis", "please", "my", "the", "in"]
        folder = self._strip(cmd, *noise)
        self.utils.list_files(folder)

    def _do_wikipedia(self, cmd):
        noise = ["wikipedia", "wiki", "jarvis", "please", "search",
                 "look up", "tell me about", "find", "the", "a"]
        query = self._strip(cmd, *noise)
        if not query:
            query = input("  Wikipedia topic: ").strip()
        if query:
            self.voice.speak(f"Looking up {query} on Wikipedia.")
            self.searcher.wikipedia_search(query)

    def _do_news(self, cmd):
        self.voice.speak("Fetching the latest headlines.")
        self.searcher.get_news()

    def _do_web_search(self, cmd):
        noise = ["search for", "search", "google", "look up", "find",
                 "what is", "who is", "how to", "how do", "how does",
                 "how did", "tell me about", "explain", "define",
                 "when is", "when was", "where is", "why is",
                 "jarvis", "please", "the", "a", "an", "me"]
        query = self._strip(cmd, *noise)
        if not query:
            query = cmd   # just use the raw command
        self.voice.speak(f"Searching: {query}")
        self.searcher.web_search(query)
