"""
app.py

Flask web application for EduMentor - an adaptive study planning assistant.
Students enter their subjects with current performance details, and the
assistant returns a prioritized, time-allocated study plan for the day.
"""

from flask import Flask, render_template, request, jsonify
from planner import Subject, generate_study_plan

app = Flask(__name__)

MAX_SUBJECTS = 12          # basic safeguard against oversized/abusive payloads
MAX_TOTAL_MINUTES = 900    # 15 hours, a generous real-world ceiling


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/plan", methods=["POST"])
def api_plan():
    """
    Accepts JSON like:
    {
        "total_minutes": 180,
        "subjects": [
            {"name": "Maths", "marks_percent": 45, "difficulty": 4,
             "days_to_exam": 3, "is_weak_topic": true},
            ...
        ]
    }
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid or missing JSON body"}), 400

    total_minutes = data.get("total_minutes")
    raw_subjects = data.get("subjects")

    if not isinstance(total_minutes, (int, float)) or total_minutes <= 0:
        return jsonify({"error": "total_minutes must be a positive number"}), 400
    if total_minutes > MAX_TOTAL_MINUTES:
        return jsonify({"error": f"total_minutes must be at most {MAX_TOTAL_MINUTES}"}), 400
    if not isinstance(raw_subjects, list) or not raw_subjects:
        return jsonify({"error": "subjects must be a non-empty list"}), 400
    if len(raw_subjects) > MAX_SUBJECTS:
        return jsonify({"error": f"Maximum {MAX_SUBJECTS} subjects allowed"}), 400

    subjects = []
    for entry in raw_subjects:
        try:
            name = str(entry.get("name", "")).strip()
            if not name:
                raise ValueError("Each subject needs a non-empty name")
            subjects.append(Subject(
                name=name[:50],  # cap length to keep things sane
                marks_percent=float(entry.get("marks_percent", 0)),
                difficulty=int(entry.get("difficulty", 1)),
                days_to_exam=int(entry.get("days_to_exam", 30)),
                is_weak_topic=bool(entry.get("is_weak_topic", False)),
            ))
        except (ValueError, TypeError) as exc:
            return jsonify({"error": f"Invalid subject data: {exc}"}), 400

    try:
        plan = generate_study_plan(subjects, int(total_minutes))
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify({
        "plan": [
            {
                "subject": block.subject,
                "minutes": block.minutes,
                "priority_score": block.priority_score,
                "reason": block.reason,
            }
            for block in plan
        ]
    })


if __name__ == "__main__":
    # debug=False by default for safety; set FLASK_DEBUG=1 env var for local dev if needed
    app.run(host="0.0.0.0", port=5000)
