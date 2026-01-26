# 🎥 Creative Fatigue Detection Prototype

This project contains two Python-based prototypes for analyzing video ads and detecting creative fatigue:

---

## 🔹 Version 1: `basic_video_analysis.py`

- Extracts key frames from a video
- Uses OCR to detect on-screen text
- Extracts audio and transcribes it to text using speech recognition

---

## 🔹 Version 2: `extract_fatigue_from_video.py`

Builds on the basic version and adds:

- Estimates hook timing and text density
- Simulates campaign metrics like CTR and frequency
- Evaluates creative fatigue risk
- Outputs human-readable fatigue dashboard
- Generates fatigue_report.json and fatigue_dashboard.txt

---

## 🧪 How to Run

```bash
pip install -r requirements.txt
python extract_fatigue_from_video.py
```

Put your video file in the same folder as `input_video.mp4`.

Outputs will be saved in the `/output/` folder.

---

## 📦 Requirements

- OpenCV
- pytesseract
- moviepy
- numpy
- speechrecognition
