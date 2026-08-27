"""
process_video.py
------------------
Reads a local video file (standing in for a CCTV feed), detects and
recognizes faces against the trained model, and marks each recognized
student "Present" with a timestamp.

Usage:
    python process_video.py --video classroom_footage.mp4

Optional flags:
    --display           Show a live window with detection boxes while processing
    --skip-frames 5      Only process every 6th frame (faster on long videos)

Output:
    Writes/updates data/attendance_status.json, which the Flask dashboard
    (app.py) reads to show live attendance. Each student is marked Present
    on their FIRST confident recognition in the video; later re-detections
    don't change their timestamp.
"""

import argparse
import json
import time
from pathlib import Path
from datetime import datetime, timedelta

import cv2

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
MODEL_PATH = DATA_DIR / "lbph_model.yml"
LABELS_PATH = DATA_DIR / "labels.txt"
CASCADE_PATH = DATA_DIR / "haarcascade_frontalface_default.xml"
STATUS_PATH = DATA_DIR / "attendance_status.json"

# LBPH confidence is a DISTANCE -- lower means a more confident match.
# Tune this after testing against your own video/photos.
CONFIDENCE_THRESHOLD = 75


def load_recognizer():
    if not MODEL_PATH.exists() or not LABELS_PATH.exists():
        raise RuntimeError("No trained model found. Run train_recognizer.py first.")

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(str(MODEL_PATH))

    label_map = {}
    with open(LABELS_PATH) as f:
        for line in f:
            label_id, name = line.strip().split(",", 1)
            label_map[int(label_id)] = name

    return recognizer, label_map


def load_status():
    """All known students start Absent; preserves already-marked Present entries."""
    _, label_map = load_recognizer()
    if STATUS_PATH.exists():
        with open(STATUS_PATH) as f:
            status = json.load(f)
    else:
        status = {}

    # make sure every currently-known student has an entry (new students -> Absent)
    for name in label_map.values():
        if name not in status:
            status[name] = {"status": "Absent", "timestamp": None}

    return status


def save_status(status):
    with open(STATUS_PATH, "w") as f:
        json.dump(status, f, indent=2)


def process_video(video_path: str, display: bool = False, skip_frames: int = 0):
    face_cascade = cv2.CascadeClassifier(str(CASCADE_PATH))
    recognizer, label_map = load_recognizer()
    status = load_status()

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Could not open video file: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    frame_count = 0
    newly_marked = []

    print(f"Processing '{video_path}' (fps={fps:.1f})...")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        if skip_frames > 0 and (frame_count - 1) % (skip_frames + 1) != 0:
            continue

        video_time_seconds = frame_count / fps
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60))

        for (x, y, w, h) in faces:
            face_crop = cv2.resize(gray[y:y + h, x:x + w], (200, 200))
            label_id, confidence = recognizer.predict(face_crop)

            if confidence <= CONFIDENCE_THRESHOLD and label_id in label_map:
                name = label_map[label_id]
                color = (0, 200, 0)

                if status.get(name, {}).get("status") != "Present":
                    # timestamp reflects the video's own timeline, e.g. "12.4s into footage"
                    ts = str(timedelta(seconds=round(video_time_seconds)))
                    status[name] = {
                        "status": "Present",
                        "timestamp": ts,
                        "marked_at_wallclock": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    }
                    newly_marked.append((name, ts))
                    print(f"  [{ts}] Marked PRESENT: {name} (confidence {confidence:.0f})")
            else:
                name = "Unknown"
                color = (0, 0, 255)

            if display:
                cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                cv2.putText(frame, name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        if display:
            cv2.putText(frame, f"t={video_time_seconds:5.1f}s", (10, 25),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            cv2.imshow("Processing video - press q to stop early", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # save periodically so the dashboard can show progress on long videos
        if frame_count % int(fps * 5) == 0:
            save_status(status)

    cap.release()
    if display:
        cv2.destroyAllWindows()

    save_status(status)

    print(f"\nDone. Processed {frame_count} frames ({frame_count / fps:.1f}s of video).")
    if newly_marked:
        print(f"Newly marked present this run: {len(newly_marked)}")
        for name, ts in newly_marked:
            print(f"  - {name} at {ts}")
    else:
        print("No new students were marked present this run.")

    present = sum(1 for s in status.values() if s["status"] == "Present")
    print(f"\nTotal: {present}/{len(status)} students marked Present.")


def main():
    parser = argparse.ArgumentParser(description="Process a classroom video and mark attendance.")
    parser.add_argument("--video", required=True, help="Path to the video file to process")
    parser.add_argument("--display", action="store_true", help="Show a live detection window")
    parser.add_argument("--skip-frames", type=int, default=0,
                         help="Process every Nth frame only (0 = every frame)")
    args = parser.parse_args()

    process_video(args.video, display=args.display, skip_frames=args.skip_frames)


if __name__ == "__main__":
    main()
