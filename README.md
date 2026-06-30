<div align="center">

# 🤖 JARVIS — Local Web Edition

**A Tony Stark-style AI assistant that runs entirely in your browser.**
Voice control · Wake word · Live weather & news · Translation · Free key-less AI fallback

[![License](https://img.shields.io/badge/license-Unlicense-blue.svg)](#-license)
[![Platform](https://img.shields.io/badge/platform-Web-success.svg)]()
[![Python](https://img.shields.io/badge/python-3.x-yellow.svg)]()
[![No Build Step](https://img.shields.io/badge/build-none%20required-brightgreen.svg)]()

<img src="screenshots/banner.svg" alt="JARVIS interface preview" width="100%">

</div>

---

## ✨ Features

| Capability | Description |
|---|---|
| 🗣️ **Voice I/O** | Press `Ctrl+M` or click the mic to talk to JARVIS; replies are spoken back |
| 👂 **Wake word** | Say *"Hey Jarvis"* to activate hands-free |
| 🧠 **AI conversation** | Bring your own Anthropic/OpenAI key, **or** run with zero keys using the built-in free web-lookup fallback |
| 🔍 **Smart fallback search** | No API key? JARVIS queries Wikipedia's free public API for a real answer instead of a canned reply, and falls back to a Google search link if nothing's found |
| 🌍 **Translation** | 40+ languages via a free public translation API |
| ☁️ **Live weather** | Optional OpenWeatherMap key for real forecasts |
| 📰 **News headlines** | Pulls live BBC News RSS, no key required |
| ⏰ **Reminders, calculator, jokes & facts** | Handy local utility commands |
| 🎨 **Iron Man-inspired HUD** | Animated scanlines, waveform visualizer, holographic styling |

---

## 🚀 Quick Start

### Option 1 — One-click launch (Windows)
1. Download or clone this repo.
2. Double-click **`START_JARVIS.bat`**.
3. Your browser opens automatically at `http://localhost:8080/jarvis.html`.

### Option 2 — Any OS (Python)
```bash
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>
python start_jarvis.py
```
This spins up a tiny local server (required so the microphone and `fetch()` calls work correctly — opening `jarvis.html` directly via `file://` will not work for those features).

### Option 3 — No Python at all
Just open `jarvis.html` directly in your browser. Voice input and some network calls may be restricted by the browser without a local server, but core chat and the local knowledge fallback still work.

---

## ⚙️ Configuration

Click the **⚙ Config** gear icon in the app to:
- Choose a persona: `JARVIS`, `Friendly`, or `Sarcastic`
- Add an **Anthropic** or **OpenAI** API key for full conversational AI *(optional — stored only in `sessionStorage`, never sent anywhere except that provider)*
- Add an optional **OpenWeatherMap** key for live weather

No keys? No problem — JARVIS automatically falls back to a free, key-less Wikipedia lookup for factual questions, and offers a one-click Google search when it can't find an answer locally.

---

## 🗂️ Project Structure

```
.
├── jarvis.html         # The entire app — UI, styles, and logic in one file
├── start_jarvis.py      # Local HTTP server launcher (enables mic + fetch)
├── START_JARVIS.bat     # Windows one-click launcher
└── README.md
```

---

## 🛡️ Privacy

- Everything runs **client-side** in your browser.
- API keys are stored in `sessionStorage` only — cleared when you close the tab — and are never sent anywhere except directly to the provider you configured.
- The free fallback lookup only contacts Wikipedia's public API and (when you choose to open it) Google search.

---

## 🧩 Tech Stack

Vanilla HTML / CSS / JavaScript — no frameworks, no build step, no `node_modules`. The Web Speech API powers voice recognition and synthesis.

---

## 🗺️ Roadmap

- [ ] Local conversation memory/history persistence
- [ ] Plugin system for custom commands
- [ ] Dark/light theme toggle
- [ ] PWA / offline support

Contributions welcome — see [CONTRIBUTING.md](CONTRIBUTING.md).

---

## 📄 License

Released into the public domain — see [LICENSE](LICENSE).

---

<div align="center">
<sub>Built with ⚡ for tinkerers who want their own desk AI.</sub>
</div>
