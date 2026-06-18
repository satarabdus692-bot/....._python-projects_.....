"""
JARVIS Display
Colored terminal output, banners, and status messages.
"""

import os
import sys


class Colors:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"

    BLACK   = "\033[30m"
    RED     = "\033[31m"
    GREEN   = "\033[32m"
    YELLOW  = "\033[33m"
    BLUE    = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN    = "\033[36m"
    WHITE   = "\033[37m"

    BG_BLACK  = "\033[40m"
    BG_BLUE   = "\033[44m"
    BG_CYAN   = "\033[46m"

    # Bright variants
    BRIGHT_GREEN  = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE   = "\033[94m"
    BRIGHT_CYAN   = "\033[96m"
    BRIGHT_RED    = "\033[91m"
    BRIGHT_WHITE  = "\033[97m"


C = Colors


class Display:
    def __init__(self):
        # Disable colors on Windows if ANSI not supported
        if sys.platform == "win32":
            try:
                import colorama
                colorama.init()
            except ImportError:
                pass

    def _color(self, text, *codes):
        return "".join(codes) + text + C.RESET

    def startup_banner(self):
        os.system("cls" if os.name == "nt" else "clear")
        banner = f"""
{C.BRIGHT_BLUE}{C.BOLD}
  ╔══════════════════════════════════════════════════════════════════╗
  ║                                                                  ║
  ║    ██╗ █████╗ ██████╗ ██╗   ██╗██╗███████╗                      ║
  ║    ██║██╔══██╗██╔══██╗██║   ██║██║██╔════╝                      ║
  ║    ██║███████║██████╔╝██║   ██║██║███████╗                      ║
  ║ ██ ██║██╔══██║██╔══██╗╚██╗ ██╔╝██║╚════██║                      ║
  ║ ╚████╔╝██║  ██║██║  ██║ ╚████╔╝ ██║███████║                     ║
  ║  ╚═══╝ ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚═╝╚══════╝                     ║
  ║                                                                  ║
  ║      Just A Rather Very Intelligent System  v2.0                 ║
  ║      Your Personal AI Voice Assistant                            ║
  ║                                                                  ║
  ╚══════════════════════════════════════════════════════════════════╝
{C.RESET}"""
        print(banner)

    def print_status(self, message: str, level: str = "INFO"):
        icons = {
            "INFO":     (C.BRIGHT_BLUE,   "ℹ"),
            "SUCCESS":  (C.BRIGHT_GREEN,  "✓"),
            "WARN":     (C.BRIGHT_YELLOW, "⚠"),
            "ERROR":    (C.BRIGHT_RED,    "✗"),
            "DOWNLOAD": (C.BRIGHT_CYAN,   "⬇"),
            "SEARCH":   (C.MAGENTA,       "🔍"),
            "LISTEN":   (C.BRIGHT_CYAN,   "🎙"),
            "NEWS":     (C.BRIGHT_YELLOW, "📰"),
        }
        color, icon = icons.get(level, (C.WHITE, "•"))
        print(f"  {color}{icon}{C.RESET}  {message}")

    def print_command(self, command: str):
        print(f"\n  {C.BRIGHT_GREEN}➤{C.RESET}  {C.BOLD}You said:{C.RESET} {C.BRIGHT_WHITE}{command}{C.RESET}")

    def print_result(self, result: str):
        print(f"\n  {C.BRIGHT_CYAN}▌{C.RESET}  {result}\n")

    def print_help(self):
        help_text = f"""
  {C.BRIGHT_BLUE}{C.BOLD}╔══ JARVIS CAPABILITIES ══════════════════════════════════════╗{C.RESET}
  {C.CYAN}║  📥 DOWNLOADS{C.RESET}
  {C.DIM}║     "Download [song/video] [title] from YouTube"
  ║     "Download [reel/post] from Instagram [URL]"
  ║     "Download from [URL]"
  ║     "Fetch [filename] from Google Drive"{C.RESET}

  {C.CYAN}║  🔍 SEARCH & INFO{C.RESET}
  {C.DIM}║     "Search for [topic]"   |  "What is [topic]?"
  ║     "Wikipedia [topic]"     |  "Latest news"
  ║     "Weather in [city]"{C.RESET}

  {C.CYAN}║  🖥️  SYSTEM{C.RESET}
  {C.DIM}║     "Open [app name]"       |  "Open [website]"
  ║     "Volume up/down/mute"   |  "Take a screenshot"
  ║     "Shutdown computer"     |  "Restart computer"{C.RESET}

  {C.CYAN}║  🛠️  UTILITIES{C.RESET}
  {C.DIM}║     "What time is it?"      |  "Tell me a joke"
  ║     "Calculate [expression]" | "Remind me in X minutes"
  ║     "Take a note [text]"     |  "List files"{C.RESET}

  {C.BRIGHT_BLUE}{C.BOLD}╚═════════════════════════════════════════════════════════════╝{C.RESET}
"""
        print(help_text)

    def get_input_mode(self) -> str:
        print(f"\n  {C.BRIGHT_BLUE}┌── Input Mode ────────────────────────┐{C.RESET}")
        print(f"  {C.BRIGHT_BLUE}│{C.RESET}  [1] 🎙️  Voice   [2] ⌨️  Type   [3] ❓ Help   [Q] Quit  {C.BRIGHT_BLUE}│{C.RESET}")
        print(f"  {C.BRIGHT_BLUE}└──────────────────────────────────────┘{C.RESET}")
        choice = input("  Choice: ").strip().lower()
        return choice
