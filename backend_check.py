#!/usr/bin/env python3
"""
Backend health check script
Run: python3 backend_check.py
"""

import urllib.request
import json
import sys

def check_endpoint(url, name):
    try:
        req = urllib.request.Request(url, timeout=10)
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            print(f"  [OK] {name}: {url}")
            print(f"       Response: {json.dumps(data, ensure_ascii=False, indent=2)[:200]}")
            return True
    except Exception as e:
        print(f"  [FAIL] {name}: {url}")
        print(f"         Error: {e}")
        return False

def main():
    base = "http://localhost:5000"
    endpoints = [
        (f"{base}/api/health", "Health Check"),
        (f"{base}/api/version", "Version Info"),
        (f"{base}/api/user/profile", "User Profile"),
        (f"{base}/api/favorites", "Favorites"),
        (f"{base}/api/help/register", "Help Center"),
        (f"{base}/api/about", "About Us"),
    ]

    print("=" * 50)
    print("Backend Service Check")
    print("=" * 50)

    ok = 0
    for url, name in endpoints:
        if check_endpoint(url, name):
            ok += 1
        print()

    print("=" * 50)
    print(f"Result: {ok}/{len(endpoints)} passed")
    if ok == len(endpoints):
        print("All services are running normally!")
        return 0
    else:
        print("Some services failed. Check logs/gunicorn.log for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
