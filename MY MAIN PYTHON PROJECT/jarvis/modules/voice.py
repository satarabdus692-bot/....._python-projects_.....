"""
JARVIS Voice Engine
Text-to-Speech (TTS) and Speech-to-Text (STT) wrapper.
Falls back gracefully when microphone is unavailable.
"""

import sys
import os


class VoiceEngine:
    def __init__(self):
        self.tts_engine = None
        self.recognizer = None
        self.microphone = None
        self.tts_available = False
        self.stt_available = False

        self._init_tts()
        self._init_stt()

    # ── TTS ──────────────────────────────────────────────────────────────────

    def _init_tts(self):
        """Initialize pyttsx3 for offline TTS."""
        try:
            import pyttsx3
            self.tts_engine = pyttsx3.init()
            self.tts_engine.setProperty("rate", 175)   # Words per minute
            self.tts_engine.setProperty("volume", 0.95)

            # Try to pick a male voice
            voices = self.tts_engine.getProperty("voices")
            for voice in voices:
                if "male" in voice.name.lower() or "david" in voice.name.lower():
                    self.tts_engine.setProperty("voice", voice.id)
                    break

            self.tts_available = True
        except Exception as e:
            print(f"  [WARN] TTS unavailable: {e}. Falling back to print-only mode.")
            self.tts_available = False

    def speak(self, text: str):
        """Say something out loud (or print if TTS unavailable)."""
        print(f"\n  🤖 Jarvis: {text}")
        if self.tts_available:
            try:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            except Exception:
                pass  # Silent fail — text already printed

    # ── STT ──────────────────────────────────────────────────────────────────

    def _init_stt(self):
        """Initialize speech_recognition."""
        try:
            import speech_recognition as sr
            self.recognizer = sr.Recognizer()
            self.recognizer.energy_threshold = 3000
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.pause_threshold = 0.8

            # Quick microphone check (non-blocking)
            with sr.Microphone() as src:
                self.recognizer.adjust_for_ambient_noise(src, duration=0.3)
            self.stt_available = True
        except Exception as e:
            print(f"  [WARN] Microphone/STT unavailable: {e}")
            self.stt_available = False

    def listen(self, timeout: int = 10) -> str:
        """Record and transcribe one spoken utterance."""
        if not self.stt_available:
            print("  [INFO] Voice input unavailable. Please use text mode (option 2).")
            return ""

        import speech_recognition as sr
        try:
            with sr.Microphone() as source:
                print("  🎙️  Recording...")
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=15)

            print("  🔄 Transcribing...")
            text = self.recognizer.recognize_google(audio)
            return text.strip()

        except sr.WaitTimeoutError:
            return ""
        except sr.UnknownValueError:
            return ""
        except sr.RequestError as e:
            print(f"  [ERROR] STT API error: {e}")
            return ""
        except Exception as e:
            print(f"  [ERROR] Listen error: {e}")
            return ""
