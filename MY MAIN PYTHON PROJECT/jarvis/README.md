# 🤖 JARVIS AI Assistant
### Just A Rather Very Intelligent System — v2.0

A complete Python voice assistant that understands natural language and performs real actions: downloading media, searching the web, controlling your system, setting reminders, and much more.

---

## ⚡ Quick Start

```bash
# 1. Install dependencies
python install.py

# 2. Launch Jarvis
python jarvis.py
```

---

## 📁 Project Structure

```
jarvis/
├── jarvis.py               ← Main entry point
├── install.py              ← One-click dependency installer
├── requirements.txt        ← All Python packages
└── modules/
    ├── brain.py            ← NLU + command router (the brain)
    ├── voice.py            ← Text-to-speech & speech recognition
    ├── downloader.py       ← YouTube, Instagram, Drive, URL
    ├── searcher.py         ← Web search, weather, Wikipedia, news
    ├── system_control.py   ← Apps, volume, screenshot, power
    ├── utilities.py        ← Jokes, calculator, reminders, notes
    ├── display.py          ← Colored terminal UI
    └── logger.py           ← Session logging
```

All downloads are saved to `~/jarvis_downloads/`:
```
~/jarvis_downloads/
├── youtube/
├── instagram/
├── google_drive/
├── general/
├── screenshots/
├── notes.json
└── logs/
```

---

## 🎙️ Example Commands

### 📥 Downloads
```
"Download Shape of You by Ed Sheeran from YouTube"
"Download the Python tutorial video from YouTube as MP3"
"Download Instagram reel from https://www.instagram.com/reel/..."
"Fetch my project report from Google Drive"
"Download from https://example.com/file.pdf"
```

### 🔍 Search & Info
```
"Search for quantum computing"
"What is machine learning?"
"Wikipedia Elon Musk"
"Weather in Lahore"
"Show me the latest news"
```

### 🖥️ System Control
```
"Open Chrome"
"Open Notepad"
"Open youtube.com"
"Volume up"     /  "Volume down"   /  "Mute"
"Take a screenshot"
"Shutdown computer"    (asks for confirmation)
```

### 🛠️ Utilities
```
"What time is it?"
"Tell me a joke"
"Calculate 25 * 4 + 100 / 2"
"Remind me in 5 minutes to drink water"
"Remind me in 1 hour 30 minutes for meeting"
"Take a note Buy groceries tomorrow"
"List my downloads"
"Delete file report.pdf"
```

---

## 🛠️ Installation Notes

### PyAudio (microphone support)
- **Windows:** `pip install pipwin && pipwin install pyaudio`
- **Linux:** `sudo apt install portaudio19-dev python3-pyaudio`
- **macOS:** `brew install portaudio && pip install pyaudio`

> ⚠️ If PyAudio fails, Jarvis still works — just use **Text Mode (option 2)** when prompted.

### yt-dlp (YouTube & Instagram)
```bash
pip install yt-dlp
# Update regularly:
yt-dlp -U
```

### Windows Volume Control
```bash
pip install pycaw comtypes
```

---

## ⚙️ Configuration

Edit `modules/downloader.py` to change the download folder:
```python
self.base = Path("D:/MyDownloads")   # Change to any path you want
```

---

## 🔑 Optional API Keys

| Feature | Service | Where to get |
|---------|---------|--------------|
| Better news | NewsAPI | [newsapi.org](https://newsapi.org) |
| Voice wake word | Porcupine | [picovoice.io](https://picovoice.ai) |

Add keys to a `.env` file in the project root:
```
NEWS_API_KEY=your_key_here
```

---

## 📦 Key Libraries Used

| Library | Purpose |
|---------|---------|
| `pyttsx3` | Offline text-to-speech |
| `SpeechRecognition` | Voice input via Google API |
| `yt-dlp` | YouTube + 1000+ sites download |
| `instaloader` | Instagram media download |
| `gdown` | Google Drive download |
| `requests` | HTTP / weather API |
| `wikipedia` | Wikipedia summaries |
| `feedparser` | RSS news feeds |
| `pyautogui` | Screenshots |

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| No voice output | Check speakers; pyttsx3 may need `espeak` on Linux |
| Microphone not working | Use Text Mode; install PyAudio |
| YouTube download fails | Run `pip install -U yt-dlp` |
| Instagram download fails | Provide the full post/reel URL |
| Google Drive fails | Install `gdown`; ensure file is publicly shared |

---

*Built with ❤️ — Powered by Python*
