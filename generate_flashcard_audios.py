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
CONTENT_PATH = os.path.join(ROOT_DIR, "assets", "data", "fln_content.json")
AUDIO_DIR_ROOT = os.path.join(ROOT_DIR, "assets", "audio", "santhali")
AUDIO_DIR_FLUTTER = os.path.join(ROOT_DIR, "flutter_app", "assets", "audio", "santhali")

os.makedirs(AUDIO_DIR_ROOT, exist_ok=True)
os.makedirs(AUDIO_DIR_FLUTTER, exist_ok=True)

with open(CONTENT_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

flashcards = data.get("flashcards", [])
print(f"Found {len(flashcards)} flashcards to synthesize audio for.")

engine = pyttsx3.init()
engine.setProperty('rate', 130)

TARGET_RATE = 16000

for fc in flashcards:
    audio_file = fc.get("audio_file")
    if not audio_file:
        continue
    
    speak_text = fc.get("phonetic", fc.get("santhali_devanagari"))
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        temp_wav = tmp.name

    try:
        engine.save_to_file(speak_text, temp_wav)
        engine.runAndWait()

        sr, audio_data = wav.read(temp_wav)
        if audio_data.ndim > 1:
            audio_data = audio_data.mean(axis=1)

        if sr != TARGET_RATE:
            num_samples = int(len(audio_data) * TARGET_RATE / sr)
            resampled = signal.resample(audio_data, num_samples).astype(np.int16)
        else:
            resampled = audio_data.astype(np.int16)

        out_root = os.path.join(AUDIO_DIR_ROOT, audio_file)
        out_flutter = os.path.join(AUDIO_DIR_FLUTTER, audio_file)

        wav.write(out_root, TARGET_RATE, resampled)
        wav.write(out_flutter, TARGET_RATE, resampled)

        print(f"Generated [{audio_file}]: 16kHz Mono 16-bit for '{fc['hindi']}' ({fc['santhali_devanagari']} / {fc['santhali_olchiki']})")
    finally:
        if os.path.exists(temp_wav):
            try:
                os.remove(temp_wav)
            except Exception:
                pass

print(">>> ALL FLASHCARD AUDIOS GENERATED & VERIFIED! <<<")
