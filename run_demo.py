import os
import socket
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

import uvicorn  # type: ignore[import-not-found]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

def find_available_port(start_port):
    """Return the first available localhost port starting at start_port."""
    for port in range(start_port, start_port + 20):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            if sock.connect_ex(("127.0.0.1", port)) != 0:
                return port
    raise RuntimeError(f"No available localhost port found near {start_port}")

def main():
    requested_port = int(os.environ.get("VAANISETU_PORT", "8000"))
    port = find_available_port(requested_port)
    server_url = f"http://127.0.0.1:{port}"

    print("=" * 70)
    print("      VaaniSetu (VaaniSetu) - Smart India Hackathon 2026")
    print("         Problem Statement ID: SIH26042 | Team Code Catalysts")
    print("=" * 70)
    print(f"[*] Starting VaaniSetu Offline Edge AI Server on {server_url} ...")
    print("[*] Edge Mode: <= 2GB RAM Offline Mode Active")
    print("=" * 70)

    # Open browser automatically after brief delay
    def open_browser():
        time.sleep(1.2)
        print(f"[*] Launching browser to {server_url} ...")
        webbrowser.open(server_url)

    import threading
    threading.Thread(target=open_browser, daemon=True).start()

    from backend.app.main import app
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="info")

if __name__ == "__main__":
    main()
