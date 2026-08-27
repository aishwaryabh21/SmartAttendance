"""
app.py
-------
Simple Flask web dashboard for the attendance system. Reads
data/attendance_status.json (written by process_video.py) and displays
it as a live-updating dashboard: each student's name, Present/Absent
status, and the timestamp they were recognized.

Run:
    python app.py

Then open http://localhost:5000 in a browser. The page polls
/api/status every 2 seconds, so if you re-run process_video.py while
the dashboard is open, it updates without a manual refresh.
"""

import json
from pathlib import Path

from flask import Flask, jsonify, render_template

BASE_DIR = Path(__file__).parent
STATUS_PATH = BASE_DIR / "data" / "attendance_status.json"

app = Flask(__name__)


def load_status():
    if not STATUS_PATH.exists():
        return {}
    with open(STATUS_PATH) as f:
        return json.load(f)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/status")
def api_status():
    status = load_status()

    students = [
        {"name": name, "status": info["status"], "timestamp": info.get("timestamp")}
        for name, info in sorted(status.items())
    ]
    present_count = sum(1 for s in students if s["status"] == "Present")

    return jsonify({
        "students": students,
        "total": len(students),
        "present": present_count,
        "absent": len(students) - present_count,
    })


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
