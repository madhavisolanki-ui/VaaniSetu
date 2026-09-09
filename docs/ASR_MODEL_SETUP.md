# VaaniSetu Phase 3: Real On-Device Hindi ASR Model Specification

## 1. Executive Model Profile

| Parameter | Specification |
| :--- | :--- |
| **Model Name** | `sherpa-onnx-whisper-tiny` (Quantized INT8) |
| **Architecture** | OpenAI Whisper Tiny (Quantized for ONNX Runtime) |
| **Runtime** | ONNX Runtime via Sherpa-ONNX C++ / Dart FFI Engine |
| **Supported Languages** | Hindi (`hi`), English (`en`), Multilingual |
| **Offline Operation** | **100% Offline** (Zero cloud, zero network requests, zero telemetry) |
| **Model Disk Footprint** | **~75 MB total** (`encoder.int8.onnx`: ~39MB, `decoder.int8.onnx`: ~36MB, `tokens.txt`: ~850KB) |
| **Peak RAM Footprint** | **~180 MB – 250 MB** (Optimized specifically for $\le$2GB RAM Android tablets) |
| **Audio Input Format** | **16 kHz, 16-bit Mono Linear PCM WAV** (`recording_<timestamp>.wav`) |
| **Model Storage Location** | `assets/models/asr/` or `<appDocumentsDirectory>/models/asr/` |

---

## 2. End-to-End Audio & Inference Pipeline

```
Teacher speaks in Hindi ("आज हम गिनती सीखेंगे")
                     ↓
Phase 2 AudioRecordingService captures microphone
   [Config: AudioEncoder.wav, 16000 Hz, 1 Channel Mono, 16-bit PCM]
                     ↓
Saved to local device storage: recordedAudioPath = ".../recording_1725902145000.wav"
                     ↓
SpeechToTextService validates WAV header & samples (Sample rate = 16000, Channels = 1)
                     ↓
VAD (Voice Activity Detector) checks minimum acoustic energy
                     ↓
On-Device ONNX Runtime loads quantized weights:
   - assets/models/asr/encoder.int8.onnx
   - assets/models/asr/decoder.int8.onnx
   - assets/models/asr/tokens.txt
                     ↓
Decoder tokens mapped with language code <|hi|> and task <|transcribe|>
                     ↓
Actual recognized Hindi text decoded: "आज हम गिनती सीखेंगे"
                     ↓
HomeScreen state updates -> Displayed in TranslationCard
```

---

## 3. How to Install the Model Weights

Run the automated download utility from the project root:
```bash
python scripts/download_asr_model.py --fetch
```
Or download manually:
1. Download `sherpa-onnx-whisper-tiny.tar.bz2` from:
   `https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-whisper-tiny.tar.bz2`
2. Extract the files into `assets/models/asr/`:
   - `encoder.int8.onnx`
   - `decoder.int8.onnx`
   - `tokens.txt`

---

## 4. Error Handling & Fallbacks
If model weights are not present on the device:
- The app displays: `● ASR model missing` in the Status Indicator.
- A floating SnackBar guides the teacher/developer: *"ASR model files not found. Please place Whisper ONNX weights in assets/models/asr."*
- The app remains completely stable and never crashes.
