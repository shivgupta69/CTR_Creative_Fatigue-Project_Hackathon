import cv2
import pytesseract
from PIL import Image
import os
import numpy as np
from moviepy.editor import VideoFileClip
import speech_recognition as sr
import json
from fatigue_evaluator import evaluate_fatigue

# --- CONFIG ---
VIDEO_PATH = "input_video.mp4"
OUTPUT_DIR = "output"
FRAME_INTERVAL = 3

os.makedirs(OUTPUT_DIR, exist_ok=True)

cap = cv2.VideoCapture(VIDEO_PATH)

if not cap.isOpened():
    print(f"Error: Could not open video file '{VIDEO_PATH}'. Check the name or path.")
    exit()

fps = cap.get(cv2.CAP_PROP_FPS)
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

if fps == 0:
    print(" Error: FPS is 0. Video metadata could not be read. Try using a different video.")
    cap.release()
    exit()

duration_sec = int(total_frames / fps)
print(f"Video loaded: {VIDEO_PATH}")
print(f" Duration: {duration_sec}s, FPS: {fps}, Total Frames: {total_frames}")

# --- Frame Sampling & OCR ---
text_outputs = []

for t in range(0, duration_sec, FRAME_INTERVAL):
    cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
    success, frame = cap.read()
    if not success:
        print(f" Could not read frame at {t}s.")
        continue

    frame_path = os.path.join(OUTPUT_DIR, f"frame_{t}.jpg")
    cv2.imwrite(frame_path, frame)

    pil_img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    extracted_text = pytesseract.image_to_string(pil_img)

    text_outputs.append({
        "timestamp_sec": t,
        "image": frame_path,
        "text": extracted_text.strip()
    })

cap.release()

# Save text output
with open(os.path.join(OUTPUT_DIR, "extracted_text.txt"), "w", encoding="utf-8") as f:
    for item in text_outputs:
        f.write(f"[Time: {item['timestamp_sec']}s]
")
        f.write(f"Frame: {item['image']}
")
        f.write("Detected Text:
")
        f.write(item['text'] or "(No text found)")
        f.write("
" + "-"*40 + "
")

# --- Audio to Text ---
print("
     Extracting Audio...")
video = VideoFileClip(VIDEO_PATH)
audio_path = os.path.join(OUTPUT_DIR, "audio.wav")
video.audio.write_audiofile(audio_path, verbose=False, logger=None)

recognizer = sr.Recognizer()
with sr.AudioFile(audio_path) as source:
    audio_data = recognizer.record(source)

try:
    audio_text = recognizer.recognize_google(audio_data)
except sr.UnknownValueError:
    audio_text = "(Could not recognize speech)"
except sr.RequestError as e:
    audio_text = f"(Speech recognition failed: {e})"

with open(os.path.join(OUTPUT_DIR, "transcribed_audio.txt"), "w", encoding="utf-8") as f:
    f.write("Transcribed Audio Text:

")
    f.write(audio_text)

# --- Fatigue Signal Estimation ---
total_words = sum(len(item['text'].split()) for item in text_outputs)
frame_count = len(text_outputs)
avg_words_per_frame = total_words / frame_count if frame_count else 0

if avg_words_per_frame > 20:
    text_density = "high"
elif avg_words_per_frame > 10:
    text_density = "medium"
else:
    text_density = "low"

scene_change_time = None
last_frame_gray = None
threshold = 30_000_000

for item in text_outputs:
    frame_img = cv2.imread(item["image"])
    gray = cv2.cvtColor(frame_img, cv2.COLOR_BGR2GRAY)

    if last_frame_gray is not None:
        diff = cv2.absdiff(gray, last_frame_gray)
        diff_score = np.sum(diff)
        if diff_score > threshold and scene_change_time is None:
            scene_change_time = item["timestamp_sec"]

    last_frame_gray = gray

hook_time_sec = scene_change_time if scene_change_time else 5.0

# --- Simulated Campaign Data + Model Call ---
creative_meta = {
    "creative_id": "input_video",
    "peak_ctr": 1.5,
    "current_ctr": 0.7,
    "days_running": 12,
    "avg_frequency": 3.4,
    "hook_time_sec": hook_time_sec,
    "text_density": text_density,
    "visual_variation": "low"
}

fatigue_result = evaluate_fatigue(creative_meta)

# Save JSON
with open(os.path.join(OUTPUT_DIR, "fatigue_report.json"), "w", encoding="utf-8") as f:
    json.dump(fatigue_result, f, indent=4)

# Save Human Dashboard
with open(os.path.join(OUTPUT_DIR, "fatigue_dashboard.txt"), "w", encoding="utf-8") as f:
    f.write(" CREATIVE FATIGUE DASHBOARD
")
    f.write("=" * 40 + "
")
    f.write(f"Creative ID     : {fatigue_result['creative_id']}
")
    f.write(f"Fatigue Risk    : {fatigue_result['fatigue_risk']}

")
    f.write(" Reasons for Fatigue:
")
    for r in fatigue_result['reasons']:
        f.write(f" - {r}
")
    f.write("
     Recommended Actions:
")
    for r in fatigue_result['recommendations']:
        f.write(f" - {r}
")

print("
     All processing complete. See output folder.")
