"""
JARVIS Brain - Natural Language Understanding & Command Router
Parses spoken/typed commands and routes to the correct handler.
"""

import re
import datetime
import os
import json
from modules.downloader import Downloader
from modules.searcher import Searcher
from modules.system_control import SystemControl
from modules.utilities import Utilities


class Brain:
    def __init__(self, voice, logger, display):
        self.voice = voice
        self.logger = logger
        self.display = display

        # Initialize all modules
        self.downloader = Downloader(voice=voice, logger=logger, display=display)
        self.searcher = Searcher(voice=voice, logger=logger, display=display)
        self.system = SystemControl(voice=voice, logger=logger, display=display)
        self.utils = Utilities(voice=voice, logger=logger, display=display)

        # Intent patterns — order matters (more specific first)
        self.intent_map = [
            # ── YOUTUBE ──────────────────────────────────────────────────────────
            (r"(download|get|save|fetch|grab).{0,30}(youtube|yt|video|song|music|audio|mp3|mp4).{0,80}",
             self._handle_youtube_download),
            (r"(youtube|yt).{0,20}(download|get|save|fetch).{0,80}",
             self._handle_youtube_download),
            (r"play.{0,10}(youtube|yt|video|song|music).{0,60}",
             self._handle_youtube_download),

            # ── INSTAGRAM ────────────────────────────────────────────────────────
            (r"(download|get|save|fetch|grab).{0,30}(instagram|insta|ig|reel|story).{0,80}",
             self._handle_instagram_download),
            (r"(instagram|insta|ig).{0,20}(download|get|save|video|reel|photo|story).{0,80}",
             self._handle_instagram_download),

            # ── GENERAL URL DOWNLOAD ─────────────────────────────────────────────
            (r"(download|get|save).{0,10}(from|at|url|link|https?://).{0,200}",
             self._handle_url_download),
            (r"https?://\S+",
             self._handle_url_download),

            # ── GOOGLE DRIVE ─────────────────────────────────────────────────────
            (r"(fetch|get|download|open|retrieve).{0,30}(google drive|drive|g ?drive).{0,80}",
             self._handle_drive_download),
            (r"(google drive|g ?drive).{0,20}(file|document|doc|sheet|folder).{0,60}",
             self._handle_drive_download),

            # ── WEB SEARCH ───────────────────────────────────────────────────────
            (r"(search|google|look up|find|tell me about|what is|who is|how to|explain|define).{0,200}",
             self._handle_web_search),

            # ── OPEN WEBSITE ─────────────────────────────────────────────────────
            (r"(open|go to|visit|launch|browse).{0,10}(website|site|page|url|browser|chrome|edge|firefox).{0,60}",
             self._handle_open_website),
            (r"(open|go to|visit).{0,5}(www\.|https?://).{0,100}",
             self._handle_open_website),

            # ── WEATHER ──────────────────────────────────────────────────────────
            (r"(weather|temperature|forecast|rain|sunny|climate).{0,60}",
             self._handle_weather),

            # ── DATE & TIME ──────────────────────────────────────────────────────
            (r"(what.{0,5}(time|date|day)|today.{0,10}(date|day)|current time|tell me the time)",
             self._handle_datetime),

            # ── JOKES ────────────────────────────────────────────────────────────
            (r"(tell me a joke|joke|make me laugh|something funny|funny)",
             self._handle_joke),

            # ── CALCULATIONS ─────────────────────────────────────────────────────
            (r"(calculate|compute|what is \d|math|solve|\d+\s*[\+\-\*/]\s*\d+)",
             self._handle_calculate),

            # ── REMINDERS ────────────────────────────────────────────────────────
            (r"(remind me|set a reminder|reminder|alarm|alert).{0,100}",
             self._handle_reminder),

            # ── NOTES ────────────────────────────────────────────────────────────
            (r"(take a note|write down|note|save this|remember this).{0,100}",
             self._handle_note),

            # ── SYSTEM CONTROLS ──────────────────────────────────────────────────
            (r"(shutdown|shut down|power off|turn off).{0,20}(computer|pc|system|machine|windows)",
             self._handle_pc_shutdown),
            (r"(restart|reboot).{0,20}(computer|pc|system)",
             self._handle_pc_restart),
            (r"(volume|sound).{0,20}(up|down|mute|unmute|louder|quieter|increase|decrease)",
             self._handle_volume),
            (r"(screenshot|capture screen|screen capture|take screenshot)",
             self._handle_screenshot),
            (r"(open|launch|start|run).{0,5}(app|application|program|software).{0,40}",
             self._handle_open_app),
            (r"(open|launch|start).{0,5}(notepad|calculator|paint|chrome|firefox|word|excel|vlc).{0,20}",
             self._handle_open_app),

            # ── FILE OPERATIONS ──────────────────────────────────────────────────
            (r"(list|show|display).{0,10}(files|folder|directory|downloads).{0,60}",
             self._handle_list_files),
            (r"(delete|remove|trash).{0,10}(file|folder).{0,60}",
             self._handle_delete_file),

            # ── WIKIPEDIA ────────────────────────────────────────────────────────
            (r"(wikipedia|wiki).{0,200}",
             self._handle_wikipedia),

            # ── NEWS ─────────────────────────────────────────────────────────────
            (r"(news|headlines|latest news|top stories|current events).{0,60}",
             self._handle_news),

            # ── SHUTDOWN JARVIS ──────────────────────────────────────────────────
            (r"(goodbye|bye|exit|quit|stop|shutdown jarvis|turn off jarvis|see you later)",
             self._handle_goodbye),

            # ── IDENTITY ─────────────────────────────────────────────────────────
            (r"(who are you|what are you|introduce yourself|your name)",
             self._handle_identity),

            # ── HELP ─────────────────────────────────────────────────────────────
            (r"(help|what can you do|commands|capabilities|features|list commands)",
             self._handle_help),
        ]

    def process(self, command: str):
        """Parse and route a command string."""
        if not command:
            return

        cmd_lower = command.lower().strip()
        self.logger.log(f"Processing: {command}")

        matched = False
        for pattern, handler in self.intent_map:
            if re.search(pattern, cmd_lower, re.IGNORECASE):
                try:
                    handler(command, cmd_lower)
                except Exception as e:
                    self.logger.error(f"Handler error: {e}")
                    self.voice.speak(f"I encountered an error: {str(e)}")
                    self.display.print_status(f"Handler error: {e}", "ERROR")
                matched = True
                break

        if not matched:
            self.voice.speak(
                "I'm not sure how to handle that. Try rephrasing or say 'help' for a list of commands."
            )
            self.display.print_status("No intent matched. Try 'help'.", "WARN")

    # ─────────────────────────────────────────────────────────────────────────
    # HANDLERS
    # ─────────────────────────────────────────────────────────────────────────

    def _extract_query(self, command: str, stop_words: list) -> str:
        """Remove trigger words to get the core query."""
        result = command
        for word in stop_words:
            result = re.sub(rf"\b{re.escape(word)}\b", "", result, flags=re.IGNORECASE)
        return result.strip(" ,.-")

    def _handle_youtube_download(self, command, cmd_lower):
        stop_words = ["download", "get", "save", "fetch", "grab", "play",
                      "youtube", "yt", "video", "song", "music", "audio",
                      "mp3", "mp4", "from", "please", "jarvis", "a", "the"]
        query = self._extract_query(command, stop_words)
        if not query:
            self.voice.speak("What would you like me to download from YouTube?")
            query = input("  Enter YouTube search query: ").strip()
        self.voice.speak(f"Searching YouTube for: {query}. Starting download now.")
        self.downloader.youtube(query)

    def _handle_instagram_download(self, command, cmd_lower):
        stop_words = ["download", "get", "save", "fetch", "grab",
                      "instagram", "insta", "ig", "reel", "story",
                      "video", "photo", "from", "please", "jarvis", "the"]
        query = self._extract_query(command, stop_words)

        # Check if it's a direct URL
        url_match = re.search(r"https?://\S+", command)
        if url_match:
            url = url_match.group()
            self.voice.speak("Downloading from Instagram URL.")
            self.downloader.instagram(url=url)
        elif query:
            self.voice.speak(f"Downloading Instagram content: {query}")
            self.downloader.instagram(query=query)
        else:
            self.voice.speak("Please provide the Instagram URL.")
            url = input("  Enter Instagram URL: ").strip()
            self.downloader.instagram(url=url)

    def _handle_url_download(self, command, cmd_lower):
        url_match = re.search(r"https?://\S+", command)
        if url_match:
            url = url_match.group()
            self.voice.speak(f"Downloading from URL.")
            self.downloader.general_url(url)
        else:
            stop_words = ["download", "get", "save", "from", "url", "link",
                          "please", "jarvis", "the", "at"]
            query = self._extract_query(command, stop_words)
            self.voice.speak(f"I need a direct URL to download. Please provide the link.")
            url = input("  Enter URL: ").strip()
            if url:
                self.downloader.general_url(url)

    def _handle_drive_download(self, command, cmd_lower):
        stop_words = ["fetch", "get", "download", "open", "retrieve", "from",
                      "google", "drive", "g", "file", "document", "doc",
                      "sheet", "folder", "please", "jarvis", "my", "the"]
        query = self._extract_query(command, stop_words)
        if not query:
            self.voice.speak("What is the file name or ID from Google Drive?")
            query = input("  Enter file name or ID: ").strip()
        self.voice.speak(f"Accessing Google Drive for: {query}")
        self.downloader.google_drive(query)

    def _handle_web_search(self, command, cmd_lower):
        stop_words = ["search", "google", "look up", "find", "tell me about",
                      "what is", "who is", "how to", "explain", "define",
                      "jarvis", "please", "for", "the", "a", "me"]
        query = self._extract_query(command, stop_words)
        if not query:
            self.voice.speak("What would you like me to search?")
            query = input("  Search query: ").strip()
        self.voice.speak(f"Searching the web for: {query}")
        self.searcher.web_search(query)

    def _handle_open_website(self, command, cmd_lower):
        url_match = re.search(r"(https?://\S+|www\.\S+|\S+\.(com|org|net|io|gov|edu)\S*)", command, re.IGNORECASE)
        if url_match:
            site = url_match.group()
            self.voice.speak(f"Opening {site}")
            self.system.open_website(site)
        else:
            stop_words = ["open", "go to", "visit", "launch", "browse",
                          "website", "site", "page", "url", "browser",
                          "chrome", "edge", "firefox", "please", "jarvis", "the"]
            site = self._extract_query(command, stop_words)
            if site:
                self.voice.speak(f"Opening {site}")
                self.system.open_website(site)

    def _handle_weather(self, command, cmd_lower):
        stop_words = ["weather", "temperature", "forecast", "rain", "sunny",
                      "climate", "in", "at", "for", "jarvis", "please", "the",
                      "what", "is", "tell", "me", "about"]
        city = self._extract_query(command, stop_words)
        if not city:
            self.voice.speak("Which city's weather would you like?")
            city = input("  City: ").strip()
        self.voice.speak(f"Fetching weather for {city}")
        self.searcher.weather(city)

    def _handle_datetime(self, command, cmd_lower):
        now = datetime.datetime.now()
        date_str = now.strftime("%A, %B %d, %Y")
        time_str = now.strftime("%I:%M %p")
        msg = f"Today is {date_str}, and the current time is {time_str}."
        self.voice.speak(msg)
        self.display.print_result(msg)

    def _handle_joke(self, command, cmd_lower):
        self.utils.tell_joke()

    def _handle_calculate(self, command, cmd_lower):
        stop_words = ["calculate", "compute", "what is", "math", "solve",
                      "jarvis", "please", "the", "result", "of"]
        expr = self._extract_query(command, stop_words)
        self.utils.calculate(expr)

    def _handle_reminder(self, command, cmd_lower):
        stop_words = ["remind me", "set a reminder", "reminder", "alarm",
                      "alert", "jarvis", "please", "to", "at", "in"]
        content = self._extract_query(command, stop_words)
        self.utils.set_reminder(content, command)

    def _handle_note(self, command, cmd_lower):
        stop_words = ["take a note", "write down", "note", "save this",
                      "remember this", "jarvis", "please", "that"]
        content = self._extract_query(command, stop_words)
        if not content:
            self.voice.speak("What would you like me to note down?")
            content = input("  Note: ").strip()
        self.utils.save_note(content)

    def _handle_pc_shutdown(self, command, cmd_lower):
        self.voice.speak("Warning! You asked me to shut down the computer. Say 'confirm' to proceed.")
        confirm = input("  Confirm shutdown? (yes/no): ").strip().lower()
        if confirm in ["yes", "y", "confirm"]:
            self.system.shutdown_pc()
        else:
            self.voice.speak("Shutdown cancelled.")

    def _handle_pc_restart(self, command, cmd_lower):
        self.voice.speak("You asked me to restart the computer. Say yes to confirm.")
        confirm = input("  Confirm restart? (yes/no): ").strip().lower()
        if confirm in ["yes", "y", "confirm"]:
            self.system.restart_pc()
        else:
            self.voice.speak("Restart cancelled.")

    def _handle_volume(self, command, cmd_lower):
        if any(w in cmd_lower for w in ["up", "louder", "increase"]):
            self.system.volume_up()
        elif any(w in cmd_lower for w in ["down", "quieter", "decrease"]):
            self.system.volume_down()
        elif "mute" in cmd_lower:
            self.system.volume_mute()
        else:
            self.voice.speak("Should I turn volume up, down, or mute?")

    def _handle_screenshot(self, command, cmd_lower):
        self.voice.speak("Taking a screenshot now.")
        self.system.screenshot()

    def _handle_open_app(self, command, cmd_lower):
        stop_words = ["open", "launch", "start", "run", "app", "application",
                      "program", "software", "please", "jarvis", "the"]
        app_name = self._extract_query(command, stop_words)
        if app_name:
            self.voice.speak(f"Opening {app_name}")
            self.system.open_app(app_name)

    def _handle_list_files(self, command, cmd_lower):
        stop_words = ["list", "show", "display", "files", "folder",
                      "directory", "downloads", "jarvis", "please", "my", "the", "in"]
        folder = self._extract_query(command, stop_words)
        self.utils.list_files(folder)

    def _handle_delete_file(self, command, cmd_lower):
        stop_words = ["delete", "remove", "trash", "file", "folder",
                      "jarvis", "please", "the"]
        name = self._extract_query(command, stop_words)
        if name:
            self.voice.speak(f"Are you sure you want to delete {name}?")
            confirm = input("  Confirm delete? (yes/no): ").strip().lower()
            if confirm in ["yes", "y"]:
                self.utils.delete_file(name)
        else:
            self.voice.speak("Please specify the file to delete.")

    def _handle_wikipedia(self, command, cmd_lower):
        stop_words = ["wikipedia", "wiki", "what is", "who is", "tell me about",
                      "jarvis", "please", "the", "a", "search", "find"]
        query = self._extract_query(command, stop_words)
        if not query:
            query = input("  Wikipedia topic: ").strip()
        self.voice.speak(f"Looking up {query} on Wikipedia.")
        self.searcher.wikipedia_search(query)

    def _handle_news(self, command, cmd_lower):
        self.voice.speak("Fetching the latest news headlines.")
        self.searcher.get_news()

    def _handle_goodbye(self, command, cmd_lower):
        self.voice.speak("Goodbye sir. It was a pleasure assisting you. Jarvis signing off.")
        self.display.print_status("Session ended.", "SUCCESS")
        import sys
        sys.exit(0)

    def _handle_identity(self, command, cmd_lower):
        msg = (
            "I am Jarvis — Just A Rather Very Intelligent System. "
            "I am your personal AI assistant, capable of downloading media, "
            "searching the web, controlling your system, setting reminders, "
            "and much more. How may I assist you today?"
        )
        self.voice.speak(msg)
        self.display.print_result(msg)

    def _handle_help(self, command, cmd_lower):
        self.display.print_help()
        self.voice.speak(
            "I've displayed my full capabilities on screen. "
            "You can ask me to download videos, search the web, open apps, "
            "tell you the time, set reminders, and much more."
        )
