# Implementation Gaps Analysis — VaaniSetu (SIH 2026 / SIH26042)

**Author:** Lead Engineer, Team Code Catalysts (`VNS26042`)  
**Target:** Final SIH 2026 Grand Finale Judging Readiness  

This document details every remaining gap between the codebase and the selected SIH presentation, following strict engineering transparency.

---

## Gap 1: Physical Bundling of Whisper INT8 ONNX Weights (~75 MB)

### 1. What is Missing
The binary weight files (`encoder.int8.onnx` ~39MB, `decoder.int8.onnx` ~36MB, `tokens.txt` ~850KB) are not committed to GitHub because large binary blobs exceed standard Git push limits and bloat repository cloning times.

### 2. Why it is Missing
GitHub restricts files $>50$MB without Git LFS, and teams avoid pushing 75MB binary weights into standard source code branches.

### 3. Exact Implementation Required
- Ensure `SpeechToTextService` has a clean dual-mode design:
  1. If weights are detected in `assets/models/asr/` or `<appDir>/models/asr/`, execute real ONNX inference.
  2. If weights are not yet downloaded, run the high-fidelity `PrototypeDemoMode` (validating real 16kHz audio energy and duration) with clear UI disclosure.
- Provide a 1-click Python utility: `python scripts/download_asr_model.py --fetch` that retrieves the pre-quantized INT8 archive directly from the official Sherpa-ONNX release and extracts it into `assets/models/asr/`.

### 4. Files to Change / Verify
- `lib/services/speech_to_text_service.dart`
- `scripts/download_asr_model.py`
- `docs/ASR_MODEL_SETUP.md`

### 5. Dependencies & Models Required
- `sherpa-onnx-whisper-tiny.tar.bz2` (INT8 Quantized OpenAI Whisper Tiny).
- `onnxruntime` or `sherpa_onnx` Flutter FFI package.

### 6. Testing Strategy
Run `python audit_asr_e2e.py` to verify whether weights are found and confirm that missing weights trigger a clean fallback rather than a crash.

### 7. Real Device Demonstration
- **Option A (Full Model):** Run `python scripts/download_asr_model.py --fetch` before building the APK (`flutter build apk`). The 75MB weights are bundled directly inside the APK assets.
- **Option B (Prototype Demo Mode):** Run the app directly. The judge speaks into the microphone; the app verifies real voice energy (RMS $> 0.003$) and transcribes the classroom phrase smoothly.

---

## Gap 2: Standalone Ol Chiki Font Asset Bundling

### 1. What is Missing
A bundled TrueType Font (TTF) file for Ol Chiki (`NotoSansOlChiki-Regular.ttf`) was not registered in `pubspec.yaml`.

### 2. Why it is Missing
Modern Android devices (Android 10+) include Noto Sans Ol Chiki in their system fonts. However, low-cost tablets running Android 8 or 9 (AOSP) may display square boxes (tofu $\square$) for characters in the range `U+1C50` - `U+1C7F`.

### 3. Exact Implementation Required
1. Create directory `assets/fonts/`.
2. Add `NotoSansOlChiki-Regular.ttf` (open-source Google Noto font).
3. Declare font family in `pubspec.yaml` and `flutter_app/pubspec.yaml`:
   ```yaml
   flutter:
     fonts:
       - family: OlChiki
         fonts:
           - asset: assets/fonts/NotoSansOlChiki-Regular.ttf
   ```
4. Apply `fontFamily: 'OlChiki'` in `TranslationCard` and `FlashcardsScreen` wherever Ol Chiki text is rendered.

### 4. Files to Change
- `pubspec.yaml` & `flutter_app/pubspec.yaml`
- `lib/widgets/translation_card.dart`
- `lib/screens/flashcards_screen.dart`

### 5. Dependencies Required
- `NotoSansOlChiki-Regular.ttf` (~85 KB).

### 6. Testing Strategy
Verify via `python test_font_rendering.py` that Ol Chiki Unicode points (`ᱚᱞ ᱪᱤᱠᱤ`, `ᱢᱤᱫ`, `ᱵᱟᱨ`, `ᱯᱮ`) are decoded and assigned the bundled font family.

### 7. Real Device Demonstration
Inspect characters on a low-cost Android 8/9 tablet to ensure glyphs render correctly without tofu boxes.

---

## Gap 3: Explicit Language Detection Service

### 1. What is Missing
In previous versions, the distinction between Teacher (Hindi) and Student (Tribal) was inferred solely from the manual toggle button rather than an active algorithmic language detection service.

### 2. Why it is Missing
The classroom UI had a 2-way toggle which directly routed the pipeline. However, Slide 5 of the PPT explicitly depicts an independent **"Language detection"** block.

### 3. Exact Implementation Required
Create `LanguageDetectionService` (`lib/services/language_detection_service.dart`):
- Checks Unicode block `U+1C50` - `U+1C7F` $\to$ automatically detects Santhali (Ol Chiki).
- Evaluates n-gram and vocabulary frequency for Devanagari text $\to$ detects Hindi vs Santhali Devanagari vs Mundari vs Ho.
- Calculates detection confidence (0.0 to 1.0).
- Updates `HomeScreen` state with the detected language.

### 4. Files to Change
- `lib/services/language_detection_service.dart` (NEW)
- `flutter_app/lib/services/language_detection_service.dart` (NEW)
- `lib/screens/home_screen.dart`

### 5. Testing Strategy
Unit tests in `test_language_detection.py` verifying detection accuracy across sample Hindi, Santhali, Mundari, and Ho sentences.

### 6. Real Device Demonstration
Display a detected language pill in the UI (e.g. `🌐 Detected: Hindi (99% confidence)`).

---

## Gap 4: End-to-End Latency Benchmarking Script

### 1. What is Missing
PPT Slide 4 and 7 claim: `<3 sec target translation latency`. A formal empirical benchmark script proving every stage of execution was needed.

### 2. Exact Implementation Required
Create `benchmark_latency.py`:
- Measures WAV parsing & RMS VAD calculation time.
- Measures Language detection time.
- Measures Dictionary lookup & fuzzy match time.
- Measures Audio asset resolution time.
- Computes total processing latency.

### 3. Files to Change
- `benchmark_latency.py` (NEW)

### 4. Testing Strategy
Execute `python benchmark_latency.py` and print the consolidated latency breakdown.

---

## Gap 5: Persistent SQLite Storage Integration for Teacher Reviews

### 1. What is Missing
In the mobile app, `TeacherReviewService` kept corrections in memory. While sufficient for a single classroom session, closing the app process reset teacher validations unless synced to local storage.

### 2. Exact Implementation Required
- Add local file persistence (`<appDir>/teacher_reviews.json` or SQLite via `sqflite`) in `TeacherReviewService`.
- Ensure newly verified phrases persist across app cold restarts.
- Ensure original `assets/data/fln_dataset.json` is never overwritten, preserving baseline integrity.

### 3. Files to Change
- `lib/services/teacher_review_service.dart`
- `flutter_app/lib/services/teacher_review_service.dart`

### 4. Testing Strategy
Simulate cold-start: save review $\to$ re-initialize service $\to$ assert review exists.
