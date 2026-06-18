"""
JARVIS Utilities
Jokes, calculator, reminders, notes, file listing & deletion.
"""

import os
import re
import json
import math
import random
import threading
import datetime
from pathlib import Path


class Utilities:
    def __init__(self, voice, logger, display):
        self.voice = voice
        self.logger = logger
        self.display = display
        self.notes_file = Path.home() / "jarvis_downloads" / "notes.json"
        self.notes_file.parent.mkdir(parents=True, exist_ok=True)

        self.jokes = [
            ("Why do programmers prefer dark mode?", "Because light attracts bugs!"),
            ("Why did the computer catch a cold?", "It left its Windows open!"),
            ("How do you comfort a JavaScript bug?", "You console it!"),
            ("Why did the AI go to therapy?", "It had too many deep issues!"),
            ("What's a computer's favorite snack?", "Microchips!"),
            ("Why was the math book sad?", "Because it had too many problems!"),
            ("What did Siri say to Jarvis?", "Don't worry, I am not your replacement!"),
            ("Why do Java developers wear glasses?", "Because they don't C sharp!"),
            ("How does a computer get drunk?", "It takes screenshots!"),
            ("What's a robot's favorite music?", "Heavy metal!"),
            ("Why did the programmer quit?", "Because they didn't get arrays!"),
            ("What do you call 8 hobbits?", "A hobbyte!"),
        ]

    # ─────────────────────────────────────────────────────────────────────────
    # JOKES
    # ─────────────────────────────────────────────────────────────────────────

    def tell_joke(self):
        setup, punchline = random.choice(self.jokes)
        self.voice.speak(setup)
        self.display.print_result(f"  😂 {setup}")
        import time; time.sleep(2)
        self.voice.speak(punchline)
        self.display.print_result(f"     👉 {punchline}")
        self.logger.log("Joke told")

    # ─────────────────────────────────────────────────────────────────────────
    # CALCULATOR
    # ─────────────────────────────────────────────────────────────────────────

    def calculate(self, expression: str):
        """Safely evaluate a mathematical expression."""
        if not expression:
            self.voice.speak("What would you like me to calculate?")
            expression = input("  Expression: ").strip()

        try:
            # Clean up natural language
            expression = expression.replace("x", "*").replace("×", "*")
            expression = expression.replace("÷", "/").replace("^", "**")
            expression = re.sub(r"[^0-9\+\-\*\/\.\(\)\%\*\s]", "", expression)
            expression = expression.strip()

            if not expression:
                self.voice.speak("I couldn't parse that expression.")
                return

            # Safe eval with math functions available
            safe_globals = {k: getattr(math, k) for k in dir(math) if not k.startswith("_")}
            safe_globals["__builtins__"] = {}
            result = eval(expression, safe_globals)

            # Format result
            if isinstance(result, float) and result.is_integer():
                result = int(result)

            msg = f"The answer is {result}"
            self.voice.speak(msg)
            self.display.print_result(f"  🧮 {expression} = {result}")
            self.logger.log(f"Calculated: {expression} = {result}")

        except ZeroDivisionError:
            self.voice.speak("You cannot divide by zero, sir.")
        except Exception as e:
            self.voice.speak(f"Could not calculate that expression.")
            self.display.print_status(f"Calc error: {e}", "ERROR")

    # ─────────────────────────────────────────────────────────────────────────
    # REMINDERS
    # ─────────────────────────────────────────────────────────────────────────

    def set_reminder(self, content: str, original_command: str):
        """Parse time from command and set a threading timer."""
        # Try to extract minutes / seconds / hours
        minutes = 0
        seconds = 0
        hours   = 0

        hour_match   = re.search(r"(\d+)\s*(hour|hr)s?", original_command, re.IGNORECASE)
        min_match    = re.search(r"(\d+)\s*(minute|min)s?", original_command, re.IGNORECASE)
        sec_match    = re.search(r"(\d+)\s*(second|sec)s?", original_command, re.IGNORECASE)

        if hour_match:   hours   = int(hour_match.group(1))
        if min_match:    minutes = int(min_match.group(1))
        if sec_match:    seconds = int(sec_match.group(1))

        total_seconds = hours * 3600 + minutes * 60 + seconds

        if total_seconds == 0:
            self.voice.speak("How long should the reminder be? Tell me in minutes.")
            try:
                mins = int(input("  Minutes: ").strip())
                total_seconds = mins * 60
            except ValueError:
                self.voice.speak("Invalid time. Reminder not set.")
                return

        # Clean up the reminder message
        stop_words = ["remind me", "set a reminder", "reminder", "alarm",
                      "alert", "to", "after", "in", "for", "please", "jarvis",
                      str(hours), str(minutes), str(seconds),
                      "hour", "hours", "hr", "minute", "minutes", "min", "second", "seconds", "sec"]
        message = content
        for w in stop_words:
            message = re.sub(rf"\b{re.escape(w)}\b", "", message, flags=re.IGNORECASE)
        message = message.strip(" ,.-") or "Time's up!"

        human_time = ""
        if hours:    human_time += f"{hours} hour{'s' if hours > 1 else ''} "
        if minutes:  human_time += f"{minutes} minute{'s' if minutes > 1 else ''} "
        if seconds:  human_time += f"{seconds} second{'s' if seconds > 1 else ''}"
        human_time = human_time.strip()

        self.voice.speak(f"Reminder set for {human_time}: {message}")
        self.display.print_status(f"⏰ Reminder in {human_time}: {message}", "INFO")

        def _fire():
            self.voice.speak(f"Reminder: {message}")
            self.display.print_status(f"⏰ REMINDER: {message}", "SUCCESS")
            print(f"\n  🔔 REMINDER: {message}\n")

        timer = threading.Timer(total_seconds, _fire)
        timer.daemon = True
        timer.start()
        self.logger.log(f"Reminder set: {message} in {total_seconds}s")

    # ─────────────────────────────────────────────────────────────────────────
    # NOTES
    # ─────────────────────────────────────────────────────────────────────────

    def save_note(self, content: str):
        notes = self._load_notes()
        entry = {
            "id":        len(notes) + 1,
            "timestamp": datetime.datetime.now().isoformat(),
            "content":   content,
        }
        notes.append(entry)
        with open(self.notes_file, "w") as f:
            json.dump(notes, f, indent=2)

        self.voice.speak(f"Note saved: {content}")
        self.display.print_status(f"📝 Note #{entry['id']} saved.", "SUCCESS")
        self.logger.log(f"Note saved: {content}")

    def list_notes(self):
        notes = self._load_notes()
        if not notes:
            self.voice.speak("You have no saved notes.")
            return
        print("\n  📝 Your Notes:")
        for n in notes:
            print(f"     [{n['id']}] {n['timestamp'][:16]}  —  {n['content']}")
        self.voice.speak(f"You have {len(notes)} saved notes.")

    def _load_notes(self):
        if self.notes_file.exists():
            try:
                with open(self.notes_file) as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    # ─────────────────────────────────────────────────────────────────────────
    # FILE OPERATIONS
    # ─────────────────────────────────────────────────────────────────────────

    def list_files(self, folder: str = ""):
        if not folder:
            target = Path.home() / "jarvis_downloads"
        else:
            # Allow relative or absolute paths
            target = Path(folder).expanduser()
            if not target.is_absolute():
                target = Path.home() / "jarvis_downloads" / folder

        if not target.exists():
            self.voice.speak(f"Folder not found: {target}")
            return

        items = list(target.iterdir())
        if not items:
            self.voice.speak("The folder is empty.")
            return

        print(f"\n  📁 Contents of {target}:")
        dirs  = [i for i in items if i.is_dir()]
        files = [i for i in items if i.is_file()]

        for d in sorted(dirs):
            print(f"     📂 {d.name}/")
        for f in sorted(files):
            size = f.stat().st_size
            size_str = self._human_size(size)
            print(f"     📄 {f.name}  ({size_str})")

        self.voice.speak(f"Found {len(dirs)} folders and {len(files)} files in {target.name}.")

    def delete_file(self, name: str):
        from pathlib import Path
        import glob

        # Search in common locations
        search_dirs = [
            Path.home() / "jarvis_downloads",
            Path.home() / "Downloads",
            Path.home() / "Desktop",
        ]

        found = []
        for d in search_dirs:
            matches = list(d.rglob(f"*{name}*"))
            found.extend(matches)

        if not found:
            self.voice.speak(f"No files matching {name} were found.")
            return

        print(f"\n  🗂️  Matches ({len(found)}):")
        for i, p in enumerate(found, 1):
            print(f"     {i}. {p}")

        try:
            choice = int(input("  Delete which number? (0 = cancel): "))
            if choice == 0:
                self.voice.speak("Deletion cancelled.")
                return
            target = found[choice - 1]
            if target.is_dir():
                import shutil
                shutil.rmtree(target)
            else:
                target.unlink()
            self.voice.speak(f"Deleted {target.name}")
            self.display.print_status(f"Deleted: {target}", "SUCCESS")
        except (ValueError, IndexError):
            self.voice.speak("Invalid selection.")

    def _human_size(self, size_bytes: int) -> str:
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} PB"
