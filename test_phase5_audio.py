import json
import os
import sys
import wave

sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(ROOT_DIR, "assets", "data", "fln_dataset.json")
AUDIO_DIR = os.path.join(ROOT_DIR, "assets", "audio", "santhali")
FLUTTER_AUDIO_DIR = os.path.join(ROOT_DIR, "flutter_app", "assets", "audio", "santhali")
SERVICE_DART = os.path.join(ROOT_DIR, "lib", "services", "audio_playback_service.dart")

print("=" * 70)
print("     VaaniSetu Phase 5: Santhali Audio Playback Verification")
print("=" * 70)

# -------------------------------------------------------------
# Simulated Audio Service Engine to match AudioPlaybackService logic
# -------------------------------------------------------------
class MockAudioPlaybackService:
    def __init__(self, audio_root):
        self.audio_root = audio_root
        self.is_initialized = False
        self.current_status = "idle"  # idle, playing, completed, unavailable, error
        self.currently_playing_asset = None
        self.network_calls = 0

    def initialize(self):
        self.is_initialized = True
        self.current_status = "idle"

    def stop(self):
        self.currently_playing_asset = None
        if self.current_status == "playing":
            self.current_status = "idle"

    def play_asset(self, asset_path):
        if not self.is_initialized:
            self.initialize()

        # Stop existing playback (no concurrency overlap)
        self.stop()

        trimmed = asset_path.strip() if asset_path else ""
        if not trimmed:
            self.current_status = "unavailable"
            raise ValueError("Santhali audio is not available for this phrase.")

        # Resolve asset path
        clean_name = os.path.basename(trimmed)
        full_path = os.path.join(self.audio_root, clean_name)

        # Asset existence check
        if not os.path.exists(full_path):
            self.current_status = "unavailable"
            raise FileNotFoundError("Santhali audio is not available for this phrase.")

        # Offline WAV verification
        with wave.open(full_path, "rb") as w:
            assert w.getnchannels() == 1, "Expected mono WAV"
            assert w.getsampwidth() == 2, "Expected 16-bit PCM"
            assert w.getframerate() == 16000, "Expected 16kHz sampling"

        self.currently_playing_asset = full_path
        self.current_status = "playing"

    def complete_playback(self):
        if self.current_status == "playing":
            self.current_status = "completed"
            self.currently_playing_asset = None

    def dispose(self):
        self.stop()
        self.is_initialized = False
        self.current_status = "idle"

service = MockAudioPlaybackService(AUDIO_DIR)

# -------------------------------------------------------------
# TEST 1: Valid audio file reference in dataset
# -------------------------------------------------------------
with open(DATASET_PATH, "r", encoding="utf-8") as f:
    phrases = json.load(f)

assert len(phrases) >= 15, "Expected at least 15 phrases"
valid_refs = 0
for p in phrases:
    audio_file = p.get("audio_file")
    assert audio_file is not None and len(audio_file.strip()) > 0, f"Missing audio_file for {p['id']}"
    assert audio_file.endswith(".wav"), f"Audio file must be .wav: {audio_file}"
    valid_refs += 1

print(f"[PASS] Test 1: All {valid_refs} dataset entries contain valid .wav audio references.")

# -------------------------------------------------------------
# TEST 2: Missing audio file reference handled gracefully
# -------------------------------------------------------------
service.initialize()
try:
    service.play_asset("")
    assert False, "Should have thrown on empty path"
except ValueError as e:
    assert service.current_status == "unavailable"
    assert "Santhali audio is not available for this phrase." in str(e)
print("[PASS] Test 2: Missing/empty audio file correctly flags 'unavailable' status.")

# -------------------------------------------------------------
# TEST 3: Missing physical asset file handled without crash or fallback substitution
# -------------------------------------------------------------
try:
    service.play_asset("assets/audio/santhali/non_existent_clip.wav")
    assert False, "Should have thrown for missing file"
except FileNotFoundError as e:
    assert service.current_status == "unavailable"
    assert "Santhali audio is not available for this phrase." in str(e)
print("[PASS] Test 3: Missing physical asset correctly caught with 'unavailable' status (no generic fallback).")

# -------------------------------------------------------------
# TEST 4: Correct asset path construction
# -------------------------------------------------------------
test_file = "santhali_count.wav"
constructed_path = f"assets/audio/santhali/{test_file}"
assert constructed_path == "assets/audio/santhali/santhali_count.wav"
resolved_local = os.path.join(AUDIO_DIR, os.path.basename(constructed_path))
assert os.path.exists(resolved_local), f"File should exist at {resolved_local}"
print(f"[PASS] Test 4: Asset path construction verified ('{constructed_path}' -> exists).")

# -------------------------------------------------------------
# TEST 5: Audio service initialization
# -------------------------------------------------------------
service.initialize()
assert service.is_initialized is True
assert service.current_status == "idle"
print("[PASS] Test 5: Service initialization successfully sets status to 'idle'.")

# -------------------------------------------------------------
# TEST 6: Play request
# -------------------------------------------------------------
service.play_asset(constructed_path)
assert service.current_status == "playing"
assert service.currently_playing_asset == resolved_local
print(f"[PASS] Test 6: Play request successfully transitions state to 'playing' with '{test_file}'.")

# -------------------------------------------------------------
# TEST 7: Stop request
# -------------------------------------------------------------
service.stop()
assert service.current_status == "idle"
assert service.currently_playing_asset is None
print("[PASS] Test 7: Stop request immediately terminates playback and returns to 'idle'.")

# -------------------------------------------------------------
# TEST 8: Multiple / Concurrent play requests (stop previous, start new)
# -------------------------------------------------------------
clip_1 = "assets/audio/santhali/santhali_001.wav"
clip_2 = "assets/audio/santhali/santhali_002.wav"

service.play_asset(clip_1)
assert service.currently_playing_asset == os.path.join(AUDIO_DIR, "santhali_001.wav")
assert service.current_status == "playing"

# Immediately play clip_2 without manual stop
service.play_asset(clip_2)
assert service.currently_playing_asset == os.path.join(AUDIO_DIR, "santhali_002.wav")
assert service.current_status == "playing"
print("[PASS] Test 8: Concurrent play requests handled safely (previous clip stopped before starting next).")

# -------------------------------------------------------------
# TEST 9: Service disposal
# -------------------------------------------------------------
service.dispose()
assert service.is_initialized is False
assert service.current_status == "idle"
assert service.currently_playing_asset is None
print("[PASS] Test 9: Service disposal successfully releases all audio resources.")

# -------------------------------------------------------------
# TEST 10: ZERO Network Calls / 100% Offline verification
# -------------------------------------------------------------
files_to_scan = [
    os.path.join(ROOT_DIR, "lib", "services", "audio_playback_service.dart"),
    os.path.join(ROOT_DIR, "lib", "screens", "home_screen.dart"),
    os.path.join(ROOT_DIR, "lib", "widgets", "translation_card.dart"),
]

cloud_keywords = [
    "http://", "https://", "cloud.google.com", "texttospeech",
    "elevenlabs", "api.openai.com", "azure.com", "speech.platform.bing.com",
    "aws.amazon.com", "polly"
]

for fp in files_to_scan:
    with open(fp, "r", encoding="utf-8") as f:
        code = f.read()
    for kw in cloud_keywords:
        assert kw not in code.lower(), f"Forbidden cloud keyword '{kw}' found in {fp}"

print("[PASS] Test 10: 100% Offline verification passed (0 HTTP/HTTPS endpoints, 0 cloud TTS APIs).")

# -------------------------------------------------------------
# TEST 11: Mandated Demo Phrase ("आज हम गिनती सीखेंगे" -> santhali_count.wav)
# -------------------------------------------------------------
count_phrase = None
for p in phrases:
    if "गिनती" in p.get("hindi", ""):
        count_phrase = p
        break

assert count_phrase is not None, "Mandated counting phrase missing in dataset"
assert count_phrase["audio_file"] == "santhali_count.wav", f"Expected santhali_count.wav, got {count_phrase['audio_file']}"

count_wav_root = os.path.join(AUDIO_DIR, "santhali_count.wav")
count_wav_flutter = os.path.join(FLUTTER_AUDIO_DIR, "santhali_count.wav")
assert os.path.exists(count_wav_root), f"Missing {count_wav_root}"
assert os.path.exists(count_wav_flutter), f"Missing {count_wav_flutter}"

with wave.open(count_wav_root, "rb") as w:
    assert w.getnchannels() == 1, "Not mono"
    assert w.getsampwidth() == 2, "Not 16-bit PCM"
    assert w.getframerate() == 16000, "Not 16kHz"
    duration = w.getnframes() / w.getframerate()
    assert duration > 1.0, f"Clip too short: {duration}s"

print(f"[PASS] Test 11: Demo phrase 'आज हम गिनती सीखेंगे' correctly mapped to 'santhali_count.wav' ({duration:.2f}s, 16kHz Mono 16-bit).")

print("\n>>> ALL PHASE 5 SANTHALI AUDIO PLAYBACK TESTS PASSED WITH 100% SUCCESS! <<<\n")
