import os
import webbrowser

def run(args):
    if not args:
        print("Usage: xdg <https://example.com>")
        return
    
    url = args[0]

    webbrowser.open(url)
