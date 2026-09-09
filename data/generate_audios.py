import json
import os
import pyttsx3

DATA_PATH = os.path.join(os.path.dirname(__file__), "fln_dataset.json")
AUDIOS_DIR = os.path.join(os.path.dirname(__file__), "audios")

os.makedirs(AUDIOS_DIR, exist_ok=True)

with open(DATA_PATH, "r", encoding="utf-8") as f:
    dataset = json.load(f)

print(f"Loaded {len(dataset)} items from {DATA_PATH}")

engine = pyttsx3.init()
engine.setProperty('rate', 145)  # clear, pedagogically suitable classroom pace

for item in dataset:
    item_id = item["id"]
    # We use phonetic Santhali with Devanagari hints for the TTS voice engine
    speak_text = item.get("santhali_phonetic", item["santhali_devanagari"])
    
    wav_filename = f"santhali_{item_id}.wav"
    mp3_filename = f"santhali_{item_id}.mp3"
    
    wav_path = os.path.join(AUDIOS_DIR, wav_filename)
    mp3_path = os.path.join(AUDIOS_DIR, mp3_filename)
    
    engine.save_to_file(speak_text, wav_path)
    engine.runAndWait()
    
    # Also create mp3 copy/alias if needed
    if os.path.exists(wav_path) and not os.path.exists(mp3_path):
        with open(wav_path, "rb") as src, open(mp3_path, "wb") as dst:
            dst.write(src.read())

print(f"Successfully generated all {len(dataset)} Santhali classroom audio clips in {AUDIOS_DIR}!")
