# Contributing to JARVIS

Thanks for considering a contribution! This is a single-file vanilla JS app, so the barrier to entry is low — no build tooling required.

## Getting Started

1. Fork the repo and clone your fork.
2. Run it locally:
   ```bash
   python start_jarvis.py
   ```
3. Make your changes directly in `jarvis.html`.
4. Refresh the browser to see updates — no build step needed.

## Guidelines

- Keep it dependency-free where possible. The whole point is that anyone can run this with just a browser and Python's standard library.
- Match the existing code style (vanilla JS, CSS variables for theming, no frameworks).
- If you add a new local command, register it in the `COMMANDS` array and document it in `cmdHelp()`.
- Test in at least one Chromium-based browser (Web Speech API support varies across browsers).
- Keep API keys and secrets out of commits — the app already handles key storage via `sessionStorage`.

## Reporting Issues

Please include:
- Browser + OS
- Steps to reproduce
- Console errors (if any)

## Ideas for Contributions

- New local commands (unit conversion, currency, etc.)
- Additional personas
- Accessibility improvements
- Mobile responsiveness fixes

Pull requests are welcome. For larger changes, please open an issue first to discuss what you'd like to change.
