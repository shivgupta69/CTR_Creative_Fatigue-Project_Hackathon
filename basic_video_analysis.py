import cv2
import pytesseract
from PIL import Image
import os

# --- CONFIG ---
VIDEO_PATH = "input_video.mp4"
OUTPUT_DIR = "output"
FRAME_INTERVAL = 3

os.makedirs(OUTPUT_DIR, exist_ok=True)

cap = cv2.VideoCapture(VIDEO_PATH)

if not cap.isOpened():
    print(f" Error: Could not open video file '{VIDEO_PATH}'.")
    exit()

fps = cap.get(cv2.CAP_PROP_FPS)
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

if fps == 0:
    print(" Error: FPS is 0.")
    cap.release()
    exit()

duration_sec = int(total_frames / fps)
print(f" Video loaded: {VIDEO_PATH}")
print(f" Duration: {duration_sec}s, FPS: {fps}, Total Frames: {total_frames}")

# --- Frame Sampling & OCR ---
text_outputs = []

for t in range(0, duration_sec, FRAME_INTERVAL):
    cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
    success, frame = cap.read()
    if not success:
        print(f"Could not read frame at {t}s.")
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

print("
Extracted Text from Video Frames:
")
for item in text_outputs:
    print(f"[Time: {item['timestamp_sec']}s]")
    print(" Frame:", item["image"])
    print("Text:
", item["text"] or "(No text found)")
    print("-" * 40)

output_text_path = os.path.join(OUTPUT_DIR, "extracted_text.txt")
with open(output_text_path, "w", encoding="utf-8") as f:
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

from moviepy.editor import VideoFileClip
import speech_recognition as sr

print("
 Extracting Audio for Speech-to-Text...")

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

print("Audio transcription complete!")
