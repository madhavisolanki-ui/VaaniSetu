import json
import os
import sys
import tempfile
import wave
import numpy as np
import pyttsx3
import scipy.io.wavfile as wav
import scipy.signal as signal

sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(ROOT_DIR, "assets", "data", "fln_dataset.json")
FLUTTER_DATASET_PATH = os.path.join(ROOT_DIR, "flutter_app", "assets", "data", "fln_dataset.json")

AUDIO_DIR_ROOT = os.path.join(ROOT_DIR, "assets", "audio", "santhali")
AUDIO_DIR_FLUTTER = os.path.join(ROOT_DIR, "flutter_app", "assets", "audio", "santhali")

os.makedirs(AUDIO_DIR_ROOT, exist_ok=True)
os.makedirs(AUDIO_DIR_FLUTTER, exist_ok=True)

# 1. Update fln_dataset.json so phrase 3 has "santhali_count.wav"
with open(DATASET_PATH, "r", encoding="utf-8") as f:
    items = json.load(f)

for item in items:
    if item.get("id") == "fln_003" or "गिनती" in item.get("hindi", ""):
        item["audio_file"] = "santhali_count.wav"

with open(DATASET_PATH, "w", encoding="utf-8") as f:
    json.dump(items, f, ensure_ascii=False, indent=2)

with open(FLUTTER_DATASET_PATH, "w", encoding="utf-8") as f:
    json.dump(items, f, ensure_ascii=False, indent=2)

print(f"Updated fln_dataset.json with 'santhali_count.wav' for fln_003.")

# 2. Setup pyttsx3 TTS engine to synthesize clear classroom phonetic audio
engine = pyttsx3.init()
engine.setProperty('rate', 135) # Clear, pedagogically deliberate classroom pace

# 3. Generate 16kHz 16-bit Mono WAV for each dataset entry
TARGET_RATE = 16000

for item in items:
    item_id = item["id"]
    audio_file = item.get("audio_file", f"santhali_{item_id}.wav")
    phonetic_text = item.get("phonetic", item.get("santhali_devanagari"))

    # Render TTS to temp file
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        temp_wav = tmp.name

    try:
        engine.save_to_file(phonetic_text, temp_wav)
        engine.runAndWait()

        # Read generated wav
        sr, audio_data = wav.read(temp_wav)

        # Convert to mono if stereo
        if audio_data.ndim > 1:
            audio_data = audio_data.mean(axis=1)

        # Resample to 16kHz
        if sr != TARGET_RATE:
            num_samples = int(len(audio_data) * TARGET_RATE / sr)
            resampled = signal.resample(audio_data, num_samples).astype(np.int16)
        else:
            resampled = audio_data.astype(np.int16)

        # Save to assets/audio/santhali/
        out_root = os.path.join(AUDIO_DIR_ROOT, audio_file)
        out_flutter = os.path.join(AUDIO_DIR_FLUTTER, audio_file)

        wav.write(out_root, TARGET_RATE, resampled)
        wav.write(out_flutter, TARGET_RATE, resampled)

        # Also create santhali_003.wav alias if santhali_count.wav
        if audio_file == "santhali_count.wav":
            wav.write(os.path.join(AUDIO_DIR_ROOT, "santhali_003.wav"), TARGET_RATE, resampled)
            wav.write(os.path.join(AUDIO_DIR_FLUTTER, "santhali_003.wav"), TARGET_RATE, resampled)

        print(f"Generated [{audio_file}]: 16kHz Mono 16-bit ({len(resampled)/TARGET_RATE:.2f}s) for '{item['hindi']}'")
    finally:
        if os.path.exists(temp_wav):
            try:
                os.remove(temp_wav)
            except Exception:
                pass

print("\n--- Audio Verification Check ---")
for f in os.listdir(AUDIO_DIR_ROOT):
    if f.endswith(".wav"):
        fp = os.path.join(AUDIO_DIR_ROOT, f)
        with wave.open(fp, "rb") as w:
            assert w.getnchannels() == 1, f"Not mono: {f}"
            assert w.getsampwidth() == 2, f"Not 16-bit: {f}"
            assert w.getframerate() == 16000, f"Not 16kHz: {f}"
            assert w.getnframes() > 0, f"Empty: {f}"
        print(f"Verified: {f} (16kHz, 1-ch, 16-bit, {os.path.getsize(fp)} bytes)")

print("\n>>> ALL PHASE 5 AUDIO ASSETS GENERATED & VERIFIED SUCCESSFULLY! <<<")
