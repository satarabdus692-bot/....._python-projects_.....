#!/usr/bin/env python3
"""
JARVIS Local Server Launcher
Run this instead of opening jarvis.html directly.
Serves over http://localhost:8080 so mic + APIs work correctly.

Usage:
    python start_jarvis.py
"""

import http.server
import socketserver
import webbrowser
import threading
import os
import sys

PORT = 8080
DIR  = os.path.dirname(os.path.abspath(__file__))

class CORSHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIR, **kwargs)

    def end_headers(self):
        # Allow all origins so fetch() calls work from localhost
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        # Permissions policy: allow mic
        self.send_header("Permissions-Policy", "microphone=*")
        super().end_headers()

    def log_message(self, fmt, *args):
        # Suppress noisy request logs
        pass


def open_browser():
    url = f"http://localhost:{PORT}/jarvis.html"
    print(f"  Opening → {url}")
    webbrowser.open(url)


def main():
    os.chdir(DIR)
    print("\n" + "═" * 52)
    print("  JARVIS — Local Web Server")
    print("═" * 52)
    print(f"  Serving:  {DIR}")
    print(f"  URL:      http://localhost:{PORT}/jarvis.html")
    print(f"  Stop:     Ctrl+C")
    print("═" * 52 + "\n")

    # Open browser after short delay
    threading.Timer(0.8, open_browser).start()

    with socketserver.TCPServer(("", PORT), CORSHandler) as httpd:
        httpd.allow_reuse_address = True
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n  Server stopped. Goodbye!\n")
            sys.exit(0)


if __name__ == "__main__":
    main()
