import webbrowser
import urllib.parse


# Helper: safely encode query
def _encode_query(query):
    return urllib.parse.quote(query)


# 1️⃣ Open Any Website
def open_website(url):
    try:
        if not url.startswith("http"):
            url = "https://" + url

        webbrowser.open(url)
        return f"Opening {url}"
    except Exception as e:
        return f"Error opening website: {e}"


# 2️⃣ Search Google
def search_google(query):
    try:
        encoded = _encode_query(query)
        url = f"https://www.google.com/search?q={encoded}"
        webbrowser.open(url)
        return f"Searching Google for '{query}'."
    except Exception as e:
        return f"Error searching Google: {e}"


# 3️⃣ Search YouTube
def search_youtube(query):
    try:
        encoded = _encode_query(query)
        url = f"https://www.youtube.com/results?search_query={encoded}"
        webbrowser.open(url)
        return f"Searching YouTube for '{query}'."
    except Exception as e:
        return f"Error searching YouTube: {e}"


# 4️⃣ Open GitHub
def open_github():
    try:
        webbrowser.open("https://github.com")
        return "Opening GitHub."
    except Exception as e:
        return f"Error opening GitHub: {e}"


# 5️⃣ Open Gmail
def open_gmail():
    try:
        webbrowser.open("https://mail.google.com")
        return "Opening Gmail."
    except Exception as e:
        return f"Error opening Gmail: {e}"
