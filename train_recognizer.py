"""
train_recognizer.py
---------------------
Trains the face recognizer from a folder of known student photos.

FOLDER STRUCTURE (either style works):

  known_students/
    Aishwarya/
      photo1.jpg
      photo2.jpg
    Apoorva/
      photo1.jpg

  -- OR, simpler, one photo per student --

  known_students/
    Aishwarya.jpg
    Apoorva.jpg

Run this once (and again any time you add/change photos):

    python train_recognizer.py

It detects the face in each photo, crops it, and trains an OpenCV LBPH
face recognizer. The trained model is saved to data/lbph_model.yml.
"""

from pathlib import Path
import cv2
import numpy as np

BASE_DIR = Path(__file__).parent
KNOWN_DIR = BASE_DIR / "known_students"
DATA_DIR = BASE_DIR / "data"
MODEL_PATH = DATA_DIR / "lbph_model.yml"
LABELS_PATH = DATA_DIR / "labels.txt"
CASCADE_PATH = DATA_DIR / "haarcascade_frontalface_default.xml"

FACE_SIZE = (200, 200)
IMAGE_EXTS = {".jpg", ".jpeg", ".png"}

face_cascade = cv2.CascadeClassifier(str(CASCADE_PATH))
if face_cascade.empty():
    raise RuntimeError(f"Could not load cascade file at {CASCADE_PATH}")


def extract_face(image_path: Path):
    """Detect the largest face in an image and return it cropped+resized, or None."""
    img = cv2.imread(str(image_path))
    if img is None:
        print(f"  [skip] could not read {image_path.name}")
        return None

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(60, 60))

    if len(faces) == 0:
        print(f"  [skip] no face found in {image_path.name}")
        return None

    # if multiple faces are in the photo, use the largest one (most likely the subject)
    x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
    face_crop = cv2.resize(gray[y:y + h, x:x + w], FACE_SIZE)
    return face_crop


def collect_training_data():
    """
    Returns (images, labels, label_map) by scanning known_students/,
    supporting both the per-student-folder and flat-file layouts.
    """
    images, labels = [], []
    label_map = {}  # int label -> student name
    next_label = 0

    if not KNOWN_DIR.exists() or not any(KNOWN_DIR.iterdir()):
        raise RuntimeError(
            f"No student photos found in {KNOWN_DIR}. "
            "Add photos as known_students/<Name>.jpg or known_students/<Name>/photo1.jpg"
        )

    for entry in sorted(KNOWN_DIR.iterdir()):
        if entry.is_dir():
            student_name = entry.name
            photo_paths = [p for p in entry.iterdir() if p.suffix.lower() in IMAGE_EXTS]
        elif entry.is_file() and entry.suffix.lower() in IMAGE_EXTS:
            student_name = entry.stem
            photo_paths = [entry]
        else:
            continue

        if not photo_paths:
            continue

        print(f"Processing {student_name} ({len(photo_paths)} photo(s))...")
        label_map[next_label] = student_name
        found_any = False

        for photo_path in photo_paths:
            face = extract_face(photo_path)
            if face is not None:
                images.append(face)
                labels.append(next_label)
                found_any = True

        if found_any:
            next_label += 1
        else:
            del label_map[next_label]
            print(f"  [warning] no usable face photos for {student_name}, skipping them entirely")

    return images, labels, label_map


def main():
    DATA_DIR.mkdir(exist_ok=True)
    images, labels, label_map = collect_training_data()

    if not images:
        raise RuntimeError("No usable face images found across all students. Check your photos.")

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.train(images, np.array(labels))
    recognizer.save(str(MODEL_PATH))

    with open(LABELS_PATH, "w") as f:
        for label_id, name in label_map.items():
            f.write(f"{label_id},{name}\n")

    print(f"\nTrained on {len(images)} face images across {len(label_map)} student(s):")
    for name in label_map.values():
        print(f"  - {name}")
    print(f"\nModel saved to {MODEL_PATH}")


if __name__ == "__main__":
    main()
