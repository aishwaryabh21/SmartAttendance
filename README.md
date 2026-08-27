<<<<<<< HEAD
# VisiClass Phase 1 — Face Recognition Attendance from a Recorded Video Feed

Phase 1 of 4: reads a local video file (standing in for a CCTV feed), detects
and recognizes faces against a folder of known student photos, and marks
attendance with a timestamp on a live web dashboard.

This has been tested end-to-end (training, video processing, and the web
dashboard) using real face photos in this environment — it works. You just
need to swap in your own student photos and video before tomorrow.

---

## Project structure

```
smart_attendance_phase1/
  requirements.txt
  train_recognizer.py       # Step 1: learn faces from known_students/
  process_video.py          # Step 2: process a video file, mark attendance
  app.py                    # Step 3: Flask web dashboard
  known_students/           # PUT STUDENT PHOTOS HERE
  templates/index.html      # dashboard page
  static/style.css          # dashboard styling (CCTV monitor theme)
  static/app.js             # dashboard live-polling logic
  data/
    haarcascade_frontalface_default.xml   # bundled face detector
    lbph_model.yml                         # trained model (generated)
    labels.txt                             # label map (generated)
    attendance_status.json                 # live attendance data (generated)
```

---

## Setup (do this tonight)

```bash
pip install -r requirements.txt
```

### 1. Add student photos
Put 1–3 clear, front-facing photos per student in `known_students/`. Either:
```
known_students/Aishwarya.jpg
```
or (better accuracy with multiple photos):
```
known_students/Aishwarya/photo1.jpg
known_students/Aishwarya/photo2.jpg
```

### 2. Train the recognizer
```bash
python train_recognizer.py
```
This prints which students were successfully trained and warns you about
any photo it couldn't find a face in — check this output before moving on.

### 3. Get your video file
Record or export a short classroom video (a phone video works fine —
see the notes on filming below). Save it somewhere accessible, e.g.
`classroom_video.mp4`.

### 4. Process the video
```bash
python process_video.py --video classroom_video.mp4 --skip-frames 4
```
This reads through the whole file, recognizes faces, and writes results to
`data/attendance_status.json`. Add `--display` if you want to watch it
detect faces live while processing (press `q` to stop early).

### 5. Run the dashboard
```bash
python app.py
```
Open **http://localhost:5000** in your browser. It shows enrolled students,
who's Present/Absent, and the timestamp they were recognized — auto-refreshing
every 2 seconds.

---

## Demo flow for tomorrow

1. Have the dashboard open in a browser tab **before** your professor arrives,
   showing everyone as "Absent" (or already processed, your choice).
2. If you want the live effect: run `process_video.py` again in a terminal
   while the dashboard is visible — students will visibly flip to "Present"
   with a timestamp as processing finds them, since the dashboard polls
   automatically.
3. Point out the timestamp column — this is the exact video-time each
   student was first recognized, not wall-clock time, which is the more
   meaningful number for an attendance record.

---

## Filming tips (if using your phone for the video)

- Landscape orientation (portrait video can appear sideways in OpenCV).
- Convert `.mov` to `.mp4` first if your phone saves in that format:
  ```bash
  ffmpeg -i video.mov -c:v libx264 -crf 20 -preset veryfast -c:a aac video.mp4
  ```
- Reasonably close, well-lit, front-facing shots work far better than a wide
  classroom shot — see the "Known limitations" note below.

---

## Tuning

- `process_video.py` → `CONFIDENCE_THRESHOLD` (currently 75): LBPH confidence
  is a *distance* — lower is a better match. Lower this number if you're
  getting false-positive matches; raise it if real students aren't being
  recognized.
- `--skip-frames N`: processes every (N+1)th frame. Use a higher number for
  long videos to finish faster; use 0 to process every frame for max accuracy
  on a short clip.

## Known limitations (worth mentioning if asked)

- Best with reasonably close, front-facing, well-lit faces — a wide/angled
  CCTV-style shot of a full classroom will reduce accuracy, since each face
  becomes very small in pixel terms. This is expected and a natural
  "Phase 2/3" improvement to mention (e.g. a higher-resolution camera, or a
  deep-learning-based recognizer instead of LBPH).
- Each student is marked Present on their FIRST confident recognition in the
  video and stays Present for the rest of that run — this models "attendance
  taken once," not continuous monitoring (that's the scope of the later
  Engagement phase of the overall project).
=======
# SmartAttendance
Classroom attendance system using OpenCV YuNet face detection + SFace recognition
>>>>>>> e16b4b394b7eecf057ca65b0469d6be72315b621
