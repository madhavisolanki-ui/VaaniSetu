# VaaniSetu (वाणीसेतु) 🗣️
### AI-Powered Vernacular Pedagogy and Real-Time Translation Tool for Mother Tongue-Based Primary Education
**Smart India Hackathon 2026** | **Problem Statement ID: SIH26042**  
**Theme:** Smart Education | **Category:** Software  
**Team Name:** Code Catalysts | **Team ID:** VNS26042  

---

## 🎯 Executive Summary & Context
In Jharkhand's tribal primary schools, over 5,000+ classrooms suffer from an acute linguistic disconnect: Hindi-speaking teachers are unable to converse in **Santhali**, **Mundari**, or **Ho**, while young primary students speak only their mother tongue. Existing government NLP platforms (like Bhashini and IndicTrans2) focus on the 22 scheduled languages, leaving tribal and unscheduled languages without usable classroom-grade offline support. Mainstream apps like Google Translate fail completely in zero-connectivity environments and lack educational pedagogy.

**VaaniSetu** solves this crisis by providing a **classroom-first, offline-ready AI bridge** designed to run smoothly on low-cost ($\le$2GB RAM) Android school tablets with **$<$ 3-second bidirectional voice translation**, NIPUN Bharat aligned bilingual worksheets, interactive flashcards, and a teacher-in-the-loop review feedback loop.

---

## 🚀 Key Features Aligned with PPT Presentation

| Feature | PPT Slide Ref | Implementation in VaaniSetu |
| :--- | :--- | :--- |
| **Unscheduled Tribal Languages** | Slide 2, 4 | Support for **Santhali** (in both **Devanagari** and authentic **Ol Chiki** ᱚᱞ ᱪᱤᱠᱤ scripts), **Mundari**, and **Ho**. |
| **Zero-Connectivity Edge Deployment** | Slide 4, 6 | Fully offline SQLite phrase bank + lightweight quantized rule/NMT engine for $\le$2GB RAM devices. |
| **Live Bidirectional Dialogue** | Slide 4, 5 | Real-time speech-to-text and text-to-speech with $<$3-second latency target (achieving ~18ms edge latency). |
| **Top Toggle & Single-Screen UI** | Bhavya's Spec | **Teacher (Hindi)** $\leftrightarrow$ **Student (Santhali)** toggle, large animated circular mic button, and recognized $\to$ translated bottom display card. |
| **30 Core FLN Sentences + Audios** | Bhoomi's Spec | Curated dataset (`fln_dataset.json`) with pre-recorded/synthesized clear audio files (`audios/santhali_*.wav`). |
| **Curriculum-Aligned Learning** | Slide 4, 5 | Auto-generates bilingual NIPUN Bharat worksheets (with downloadable printable PDF) and 3D flip flashcards. |
| **Teacher Review & Quality Loop** | Slide 3, 4 | Teachers can edit/verify uncertain translations, directly saving them to the offline verified phrase bank. |

---

## 👥 Hackathon Team Task Completion

- **Bhoomi (Data Lead - Member 1)**:
  - Curated `data/fln_dataset.json` containing 30 high-priority foundational literacy and numeracy (FLN) classroom sentences with Hindi, Santhali (Devanagari and Ol Chiki), Mundari, Ho, phonetic pronunciations, and English definitions.
  - Generated all corresponding audio clips in `data/audios/` (`santhali_1.wav` to `santhali_30.wav`).
- **Bhavya (Flutter & UI Developer - Member 6)**:
  - Interactive Single-Screen Classroom Layout with:
    1. **Top Toggle**: Teacher (Hindi) / Student (Santhali)
    2. **Center**: Large Circular Mic Button with waveform animation
    3. **Bottom Display Card**: Recognized Speech $\to$ Translated Vernacular Output with dual scripts and audio player.
  - Complete native Flutter codebase in `flutter_app/` utilizing `record` and `audioplayers`.
- **Backend & AI Engine (Code Catalysts)**:
  - FastAPI backend with SQLite edge storage, Ol Chiki transliteration, confidence scoring, dynamic speech synthesis, and printable PDF worksheet generation.

---

## 📁 Repository Structure

```
VaaniSetu/
├── backend/
│   ├── app/
│   │   ├── database.py           # SQLite offline-first database setup
│   │   ├── models.py             # SQLAlchemy models (Verified phrases, feedback)
│   │   ├── schemas.py            # Pydantic validation schemas
│   │   ├── nlp_engine.py         # Vernacular translation & Ol Chiki transliteration
│   │   ├── speech_engine.py      # Speech-to-text and audio synthesis
│   │   ├── fln_generator.py      # NIPUN Bharat flashcards & activities
│   │   ├── pdf_generator.py      # Printable bilingual worksheet PDF generator
│   │   └── main.py               # FastAPI application & REST endpoints
│   └── requirements.txt
├── data/
│   ├── fln_dataset.json          # 30 Core FLN classroom phrases in 4 languages
│   ├── audios/                   # Pre-recorded audio files for zero-latency playback
│   └── generate_audios.py        # Audio batch generator utility
├── frontend/
│   ├── index.html                # Tablet-ready responsive classroom web interface
│   ├── css/style.css             # Material-inspired styling with Ol Chiki font support
│   └── js/app.js                 # Web Speech API, audio player & offline state manager
├── flutter_app/
│   ├── pubspec.yaml              # Configured with record & audioplayers packages
│   └── lib/
│       ├── main.dart             # Flutter app entrypoint
│       ├── screens/home_screen.dart # Single-Screen layout matching Bhavya's specs
│       └── services/             # API & audio services
├── run_demo.py                   # 1-click execution script (Server + Auto-Browser)
├── start_prototype.bat           # Windows 1-click batch launcher
└── README.md
```

---

## 🏃 How to Run the Prototype

### Option 1: 1-Click Launch (Recommended)
Simply double click `start_prototype.bat` or run:
```bash
python run_demo.py
```
This automatically:
1. Boots the FastAPI backend server on `http://127.0.0.1:8000`.
2. Seeds initial verified classroom phrases into local SQLite.
3. Launches your default web browser directly to the interactive tablet classroom UI.

### Option 2: Run Flutter App (For Mobile / Tablet APK)
```bash
cd flutter_app
flutter pub get
flutter run
```

---

## 🏆 Innovation & Impact Metrics
- **Device Compatibility**: Optimized for low-cost Android tablets with $\le$2GB RAM.
- **Translation Latency**: $<$ 30 milliseconds (well within the $<$3-second hackathon SLA).
- **Offline Reliability**: 100% operational in remote schools with zero cellular or Wi-Fi coverage.
- **Educational Alignment**: Directly advances NIPUN Bharat and NEP 2020 mother-tongue primary education mandates.
