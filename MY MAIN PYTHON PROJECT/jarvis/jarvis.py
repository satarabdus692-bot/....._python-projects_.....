1#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║                    JARVIS AI ASSISTANT                       ║
║              Just A Rather Very Intelligent System           ║
╚══════════════════════════════════════════════════════════════╝
"""

import sys
import os
import time
import threading

# Add project root to path
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
    time.sleep(0.5)

    # Test TTS
    voice.speak("Jarvis online. All systems operational. How can I assist you?")
    display.print_status("Jarvis is ready. Listening for commands...", "SUCCESS")
    display.print_help()

    while True:
        try:
            # Choose input mode
            mode = display.get_input_mode()

            if mode == "1":
                # Voice input
                display.print_status("Listening... Speak now!", "LISTEN")
                command = voice.listen()
                if not command:
                    display.print_status("Didn't catch that. Try again.", "WARN")
                    continue
                display.print_command(command)

            elif mode == "2":
                # Text input
                command = input("\n  💬 You: ").strip()
                if not command:
                    continue

            elif mode == "3":
                display.print_help()
                continue

            elif mode == "q":
                voice.speak("Goodbye sir. Jarvis shutting down.")
                display.print_status("Goodbye!", "SUCCESS")
                break

            else:
                continue

            # Process the command
            brain.process(command)

        except KeyboardInterrupt:
            print("\n")
            voice.speak("Jarvis signing off. Goodbye!")
            display.print_status("Session ended by user.", "INFO")
            break
        except Exception as e:
            logger.error(f"Main loop error: {e}")
            display.print_status(f"Error: {e}", "ERROR")


if __name__ == "__main__":
    main()
