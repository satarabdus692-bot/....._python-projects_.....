"""
JARVIS Searcher
Web search, weather, Wikipedia, news headlines.
"""

import webbrowser
import urllib.parse
import json
import re


class Searcher:
    def __init__(self, voice, logger, display):
        self.voice = voice
        self.logger = logger
        self.display = display

    # ─────────────────────────────────────────────────────────────────────────
    # WEB SEARCH
    # ─────────────────────────────────────────────────────────────────────────

    def web_search(self, query: str):
        """Open Google search or use googlesearch-python to show results."""
        self.logger.log(f"Web search: {query}")

        # Try to show results in terminal first
        try:
            from googlesearch import search as gsearch
            self.display.print_status(f"Top results for: {query}", "SEARCH")
            results = []
            for i, url in enumerate(gsearch(query, num_results=5), 1):
                results.append(url)
                print(f"  {i}. {url}")

            self.voice.speak(f"I found {len(results)} results. Opening the top result in your browser.")
            if results:
                webbrowser.open(results[0])

        except ImportError:
            # Fallback: open browser
            encoded = urllib.parse.quote_plus(query)
            url = f"https://www.google.com/search?q={encoded}"
            self.voice.speak(f"Opening Google search for: {query}")
            webbrowser.open(url)

        except Exception as e:
            # Silent fallback
            encoded = urllib.parse.quote_plus(query)
            webbrowser.open(f"https://www.google.com/search?q={encoded}")

    # ─────────────────────────────────────────────────────────────────────────
    # WEATHER
    # ─────────────────────────────────────────────────────────────────────────

    def weather(self, city: str):
        """Fetch weather using wttr.in (no API key required)."""
        try:
            import requests
            encoded = urllib.parse.quote_plus(city)
            url = f"https://wttr.in/{encoded}?format=j1"
            r = requests.get(url, timeout=10)
            r.raise_for_status()
            data = r.json()

            current = data["current_condition"][0]
            temp_c   = current["temp_C"]
            temp_f   = current["temp_F"]
            feels_c  = current["FeelsLikeC"]
            humidity = current["humidity"]
            desc     = current["weatherDesc"][0]["value"]
            wind     = current["windspeedKmph"]
            uv       = current.get("uvIndex", "N/A")

            msg = (
                f"Weather in {city}: {desc}. "
                f"Temperature: {temp_c}°C ({temp_f}°F). "
                f"Feels like {feels_c}°C. "
                f"Humidity: {humidity}%. Wind: {wind} km/h. UV index: {uv}."
            )
            self.voice.speak(msg)
            self.display.print_result(msg)

            # 3-day forecast
            print("\n  📅 3-Day Forecast:")
            for day in data["weather"][:3]:
                date      = day["date"]
                max_c     = day["maxtempC"]
                min_c     = day["mintempC"]
                day_desc  = day["hourly"][4]["weatherDesc"][0]["value"]
                print(f"     {date}: {day_desc}, High {max_c}°C / Low {min_c}°C")

        except Exception as e:
            self.voice.speak(f"Could not fetch weather for {city}. Opening browser instead.")
            webbrowser.open(f"https://wttr.in/{urllib.parse.quote_plus(city)}")
            self.logger.error(f"Weather error: {e}")

    # ─────────────────────────────────────────────────────────────────────────
    # WIKIPEDIA
    # ─────────────────────────────────────────────────────────────────────────

    def wikipedia_search(self, query: str):
        """Return a Wikipedia summary."""
        try:
            import wikipedia
            wikipedia.set_lang("en")
            results = wikipedia.search(query, results=3)
            if not results:
                self.voice.speak("No Wikipedia results found.")
                return

            summary = wikipedia.summary(results[0], sentences=3)
            self.voice.speak(summary)
            self.display.print_result(f"📖 Wikipedia — {results[0]}:\n\n{summary}")
            self.logger.log(f"Wikipedia: {query}")

        except ImportError:
            encoded = urllib.parse.quote_plus(query)
            webbrowser.open(f"https://en.wikipedia.org/wiki/Special:Search?search={encoded}")
        except Exception as e:
            encoded = urllib.parse.quote_plus(query)
            webbrowser.open(f"https://en.wikipedia.org/wiki/Special:Search?search={encoded}")
            self.logger.error(f"Wikipedia error: {e}")

    # ─────────────────────────────────────────────────────────────────────────
    # NEWS
    # ─────────────────────────────────────────────────────────────────────────

    def get_news(self, category: str = "general", country: str = "us"):
        """Fetch top news headlines using NewsAPI or RSS fallback."""
        # Try newsapi
        try:
            import requests
            # Free RSS-based approach (no API key needed)
            feeds = {
                "BBC":     "http://feeds.bbci.co.uk/news/rss.xml",
                "Reuters": "https://feeds.reuters.com/reuters/topNews",
                "CNN":     "http://rss.cnn.com/rss/edition.rss",
            }

            try:
                import feedparser
                self.display.print_status("Latest Headlines:", "NEWS")
                count = 0
                for source, feed_url in feeds.items():
                    feed = feedparser.parse(feed_url)
                    for entry in feed.entries[:3]:
                        count += 1
                        title = entry.get("title", "No title")
                        link  = entry.get("link", "")
                        print(f"  {count:2}. [{source}] {title}")
                        if link:
                            print(f"       {link}")

                if count:
                    self.voice.speak(f"I found {count} latest headlines. Check your screen.")
                else:
                    self._news_browser_fallback()

            except ImportError:
                self._news_browser_fallback()

        except Exception as e:
            self._news_browser_fallback()
            self.logger.error(f"News error: {e}")

    def _news_browser_fallback(self):
        self.voice.speak("Opening BBC News in your browser.")
        webbrowser.open("https://www.bbc.com/news")
