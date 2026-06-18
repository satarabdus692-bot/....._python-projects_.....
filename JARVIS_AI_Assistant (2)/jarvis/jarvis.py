#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║                    JARVIS AI ASSISTANT                       ║
║              Just A Rather Very Intelligent System           ║
╚══════════════════════════════════════════════════════════════╝
"""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.brain import Brain
from modules.voice import VoiceEngine
from modules.display import Display
from modules.logger import JarvisLogger


def main():
    display = Display()
    display.startup_banner()

    logger = JarvisLogger()
    voice = VoiceEngine()
    brain = Brain(voice=voice, logger=logger, display=display)

    display.print_status("Initializing systems...", "INFO")
    time.sleep(0.3)

    voice.speak("Jarvis online. All systems operational. How can I assist you?")
    display.print_status("Jarvis is ready.", "SUCCESS")
    display.print_help()

    # Auto-detect best input mode
    if not voice.stt_available:
        display.print_status(
            "Microphone unavailable — defaulting to TEXT mode. Just type your commands!",
            "WARN"
        )
        default_mode = "2"
    else:
        default_mode = None   # ask every loop

    while True:
        try:
            if default_mode == "2":
                # Skip the mode menu entirely — go straight to text input
                try:
                    raw = input("\n  💬 You: ").strip()
                except EOFError:
                    break
                if not raw:
                    continue
                if raw.lower() in ("q", "quit", "exit", "bye", "goodbye"):
                    voice.speak("Goodbye sir. Jarvis shutting down.")
                    display.print_status("Goodbye!", "SUCCESS")
                    break
                if raw == "?":
                    display.print_help()
                    continue
                brain.process(raw)

            else:
                # Full mode menu (voice available)
                mode = display.get_input_mode()

                if mode == "1":
                    display.print_status("Listening... Speak now!", "LISTEN")
                    command = voice.listen()
                    if not command:
                        display.print_status("Didn't catch that. Please try again.", "WARN")
                        continue
                    display.print_command(command)
                    brain.process(command)

                elif mode == "2":
                    try:
                        command = input("\n  💬 You: ").strip()
                    except EOFError:
                        break
                    if not command:
                        continue
                    brain.process(command)

                elif mode == "3":
                    display.print_help()

                elif mode in ("q", "quit", "exit"):
                    voice.speak("Goodbye sir. Jarvis shutting down.")
                    display.print_status("Goodbye!", "SUCCESS")
                    break

        except KeyboardInterrupt:
            print("\n")
            voice.speak("Jarvis signing off. Goodbye!")
            display.print_status("Session ended by user.", "INFO")
            break
        except Exception as e:
            logger.error(f"Main loop error: {e}")
            display.print_status(f"Unexpected error: {e}", "ERROR")


if __name__ == "__main__":
    main()
