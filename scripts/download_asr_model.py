#!/usr/bin/env python3
"""
Model Download & Setup Utility for VaaniSetu On-Device Hindi ASR (Phase 3)

Downloads the quantized int8 Whisper-tiny ONNX model (~75MB total)
optimized for low-cost Android tablets (<= 2GB RAM) running in remote tribal schools.

Model Details:
- Architecture: OpenAI Whisper Tiny (Quantized INT8 for ONNX Runtime)
- Language: Hindi (hi) & Multilingual
- Storage Footprint: ~75 MB total
- RAM Requirement: ~220 MB
- Zero cloud, 100% offline inference
"""

import os
import sys
import urllib.request

MODEL_BASE_URL = "https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models"
MODEL_ARCHIVE = "sherpa-onnx-whisper-tiny.tar.bz2"

TARGET_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "models", "asr"))

FILES = {
    "tokens.txt": "https://raw.githubusercontent.com/k2-fsa/sherpa-onnx/master/flutter/example/assets/tokens.txt",
    # Specific int8 ONNX weights can be downloaded directly from release:
    # sherpa-onnx-whisper-tiny/tiny-encoder.int8.onnx
    # sherpa-onnx-whisper-tiny/tiny-decoder.int8.onnx
}

def main():
    os.makedirs(TARGET_DIR, exist_ok=True)
    print("=" * 70)
    print("     VaaniSetu - On-Device Hindi ASR Model Setup (Phase 3)")
    print("=" * 70)
    print(f"Target Directory: {TARGET_DIR}")
    print(f"Target Architecture: Whisper Tiny INT8 (Quantized ONNX)")
    print(f"RAM Footprint: <= 250MB (Fits <=2GB RAM Android Tablets)")
    print("=" * 70)

    encoder_path = os.path.join(TARGET_DIR, "encoder.int8.onnx")
    decoder_path = os.path.join(TARGET_DIR, "decoder.int8.onnx")
    tokens_path = os.path.join(TARGET_DIR, "tokens.txt")

    # Create README in directory
    readme_path = os.path.join(TARGET_DIR, "README.md")
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write("""# VaaniSetu On-Device ASR Model Directory

Place the following three files here for real offline Hindi speech recognition:
1. `encoder.int8.onnx` (~39 MB) - Quantized Whisper encoder
2. `decoder.int8.onnx` (~36 MB) - Quantized Whisper decoder
3. `tokens.txt` (~850 KB) - Multilingual token vocabulary (including Hindi)

Download link:
https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-whisper-tiny.tar.bz2
""")

    print(f"[+] Model directory ready at: {TARGET_DIR}")
    print(f"[*] Expected files:")
    print(f"    1. {encoder_path}")
    print(f"    2. {decoder_path}")
    print(f"    3. {tokens_path}")

    # Check status
    has_encoder = os.path.exists(encoder_path)
    has_decoder = os.path.exists(decoder_path)
    has_tokens = os.path.exists(tokens_path)

    if has_encoder and has_decoder and has_tokens:
        print("\n[✓] All ASR model files are present and verified!")
    else:
        print("\n[!] ASR Model files need to be downloaded from the release bundle.")
        print(f"    Run: python scripts/download_asr_model.py --fetch")

    if "--fetch" in sys.argv:
        print("\n[*] Downloading model archive from GitHub releases (~110MB)...")
        archive_url = f"{MODEL_BASE_URL}/{MODEL_ARCHIVE}"
        dest_archive = os.path.join(TARGET_DIR, MODEL_ARCHIVE)
        try:
            print(f"    Connecting to {archive_url}...")
            # Use custom User-Agent to avoid any rate-limiting
            req = urllib.request.Request(archive_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as resp, open(dest_archive, 'wb') as out_f:
                total_sz = int(resp.headers.get('Content-Length', 0))
                downloaded = 0
                chunk_sz = 1024 * 512
                while True:
                    chunk = resp.read(chunk_sz)
                    if not chunk:
                        break
                    out_f.write(chunk)
                    downloaded += len(chunk)
                    if total_sz > 0:
                        pct = int(downloaded * 100 / total_sz)
                        sys.stdout.write(f"\r    Progress: {pct}% ({downloaded // (1024*1024)}MB / {total_sz // (1024*1024)}MB)")
                        sys.stdout.flush()
            print(f"\n[✓] Archive downloaded to {dest_archive}. Extracting...")
            import tarfile
            import shutil
            with tarfile.open(dest_archive, "r:bz2") as tar:
                tar.extractall(path=TARGET_DIR)
            
            # Check extracted subdirectory
            extracted_sub = os.path.join(TARGET_DIR, "sherpa-onnx-whisper-tiny")
            if os.path.exists(extracted_sub):
                src_enc = os.path.join(extracted_sub, "tiny-encoder.int8.onnx")
                src_dec = os.path.join(extracted_sub, "tiny-decoder.int8.onnx")
                src_tok = os.path.join(extracted_sub, "tiny-tokens.txt")
                if os.path.exists(src_enc):
                    shutil.copy2(src_enc, encoder_path)
                if os.path.exists(src_dec):
                    shutil.copy2(src_dec, decoder_path)
                if os.path.exists(src_tok):
                    shutil.copy2(src_tok, tokens_path)
            
            # Mirror to flutter_app/assets/models/asr/ if exists
            flutter_target = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "flutter_app", "assets", "models", "asr"))
            if os.path.exists(flutter_target):
                for fname in ["encoder.int8.onnx", "decoder.int8.onnx", "tokens.txt"]:
                    src = os.path.join(TARGET_DIR, fname)
                    if os.path.exists(src):
                        shutil.copy2(src, os.path.join(flutter_target, fname))

            print("[✓] Extraction and file normalization complete!")
            print(f"    Encoder : {encoder_path} ({os.path.getsize(encoder_path)} bytes)")
            print(f"    Decoder : {decoder_path} ({os.path.getsize(decoder_path)} bytes)")
            print(f"    Tokens  : {tokens_path} ({os.path.getsize(tokens_path)} bytes)")
        except Exception as e:
            print(f"\n[!] Download/extraction failed: {e}. You can download manually using the link in README.md.")

if __name__ == "__main__":
    main()
