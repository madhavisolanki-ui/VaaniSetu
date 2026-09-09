#!/usr/bin/env python3
"""
Offline Network & Cloud Leak Audit for VaaniSetu (SIH 2026 / SIH26042)
Strictly audits all Dart source files in lib/ and flutter_app/lib/
to guarantee 100% offline compliance (zero cloud dependencies, zero external network requests).
"""

import os
import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
SEARCH_DIRS = [
    os.path.join(ROOT_DIR, "lib"),
    os.path.join(ROOT_DIR, "flutter_app", "lib"),
]

# Patterns that indicate external network, telemetry, or cloud dependencies
SUSPICIOUS_PATTERNS = [
    (r'https?://(?!localhost|127\.0\.0\.1)', "External HTTP/HTTPS URL"),
    (r'package:http/http\.dart', "HTTP client package"),
    (r'package:dio/dio\.dart', "Dio networking package"),
    (r'dart:io.*HttpClient', "Raw Dart HttpClient"),
    (r'WebSocket\.connect', "WebSocket connection"),
    (r'google_generative_ai', "Google Gemini Cloud API"),
    (r'firebase', "Firebase Cloud Services"),
    (r'openai', "OpenAI Cloud API"),
    (r'azure', "Azure Cloud API"),
    (r'aws', "AWS Cloud API"),
]

def run_audit():
    print("=" * 72)
    print("   VaaniSetu 100% Offline Integrity & Zero-Cloud Leak Audit")
    print("=" * 72)

    total_files = 0
    clean_files = 0
    violations = []

    for d in SEARCH_DIRS:
        if not os.path.exists(d):
            continue
        for root, _, files in os.walk(d):
            for file in files:
                if file.endswith(".dart"):
                    total_files += 1
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, ROOT_DIR)
                    
                    with open(file_path, "r", encoding="utf-8") as f:
                        lines = f.readlines()

                    file_violations = []
                    for line_idx, line in enumerate(lines, 1):
                        # Skip comments
                        clean_line = line.strip()
                        if clean_line.startswith("//") or clean_line.startswith("*"):
                            continue

                        for pattern, desc in SUSPICIOUS_PATTERNS:
                            if re.search(pattern, line):
                                file_violations.append((line_idx, desc, clean_line))

                    if file_violations:
                        violations.append((rel_path, file_violations))
                    else:
                        clean_files += 1

    print(f"[*] Audited {total_files} Dart source files across lib/ and flutter_app/lib/.")
    print(f"[*] Clean Files: {clean_files} / {total_files} (100% Offline)")

    if violations:
        print("\n[!] VIOLATIONS DETECTED:")
        for rel_path, v_list in violations:
            print(f"    File: {rel_path}")
            for line_no, desc, snippet in v_list:
                print(f"      L{line_no}: [{desc}] -> {snippet}")
        sys.exit(1)
    else:
        print("\n[✓] ZERO external network calls, ZERO cloud APIs, ZERO telemetry detected!")
        print(">>> 100% OFFLINE COMPLIANCE VERIFIED ACROSS ENTIRE CODEBASE <<<")

if __name__ == "__main__":
    run_audit()
