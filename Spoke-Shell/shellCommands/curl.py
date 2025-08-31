# curl.py
import sys
import urllib.request

def run(args):
    if not args:
        print("Usage: curl <url>")
        return
    url = args[0]
    try:
        with urllib.request.urlopen(url) as response:
            charset = response.headers.get_content_charset() or 'utf-8'
            content = response.read().decode(charset, errors='replace')
            print(content)
    except Exception as e:
        print(f"[curl] Error: {e}")