# wget.py
import sys
import urllib.request
import os

def run(args):
    if not args:
        print("Usage: wget <url>")
        return
    
    url = args[0]
    filename = args[1] if len(args) > 1 else os.path.basename(url.split("?")[0])
    
    try:
        urllib.request.urlretrieve(url, filename)
        print(f"[wget] Downloaded to '{filename}'")
    except Exception as e:
        print(f"[wget] Error: {e}")