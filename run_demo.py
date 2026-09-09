import os
import sys
import time
import webbrowser

# Ensure UTF-8 output in Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import uvicorn

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, "backend"))

def main():
    print("=" * 70)
    print("      VaaniSetu (VaaniSetu) - Smart India Hackathon 2026")
    print("         Problem Statement ID: SIH26042 | Team Code Catalysts")
    print("=" * 70)
    print("[*] Starting VaaniSetu Offline Edge AI Server on http://127.0.0.1:8000 ...")
    print("[*] Bhoomi (Member 1) Dataset: 30 FLN Sentences & Audios Loaded")
    print("[*] Bhavya (Member 6) UI: Single-Screen Layout & Multi-Module Hub Active")
    print("[*] Edge Mode: <= 2GB RAM Offline Mode Active")
    print("=" * 70)

    # Open browser automatically after brief delay
    def open_browser():
        time.sleep(1.2)
        print("[*] Launching browser to http://127.0.0.1:8000 ...")
        webbrowser.open("http://127.0.0.1:8000")

    import threading
    threading.Thread(target=open_browser, daemon=True).start()

    from app.main import app
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")

if __name__ == "__main__":
    main()
