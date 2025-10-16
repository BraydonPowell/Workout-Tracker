from flask import Flask, render_template, request, redirect, url_for
import csv
from datetime import datetime
import os
from urllib.parse import unquote

app = Flask(__name__)

FILENAME = "workouts.csv"
SESSION_FILE = "current_session.txt"

# Use seconds everywhere so sessions are always unique
DT_TS_FMT = "%Y-%m-%d %H:%M:%S"   # for row timestamps and for the datetime prefix in session names

COMPOUND_LIFTS = [
    # --- Bench Variations ---
    "Bench Press", "Bench", "Bp", "Flat Bench", "Bb Bench", "Bb Press",
    "Barbell Bench", "Barbell Press", "Db Bench", "Db Press", "Dumbbell Bench",
    "Incline Bench", "Incline", "Ibp", "Incline Dumbbell Bench", "Incline Db Bench",
    "Decline Bench", "Decline", "Db Decline", "Cg Bench", "Close Grip Bench",
    "Cgbp", "Close Grip", "Pause Bench", "Paused Bench", "Spoto Press", "Incline Dumbell Press",

    # --- Overhead / Shoulder Press ---
    "Overhead Press", "Shoulder Press", "Ohp", "Ohp Press", "Push Press", "Pushpress",
    "Strict Press", "Military Press", "Seated Press", "Seated OHP", "Arnold Press",

    # --- Dips / Triceps ---
    "Dips", "Weighted Dips", "Ring Dips", "Tricep Dips", "Parallel Bar Dips",
    "Close Grip Press", "Cg Press",

    # --- Rows / Back ---
    "Barbell Row", "Bb Row", "Row", "Bbrow", "Bent Over Row", "Pendlay Row", "Pendlay",
    "Seal Row", "Machine Row", "Cable Row", "T-Bar Row", "Tbar", "Trow", "One Arm Row",
    "Single Arm Row", "Dumbbell Row", "Db Row",

    # --- Pulls / Lats ---
    "Pull Up", "Pullup", "Pu", "Weighted Pull Up", "Wide Grip Pull Up", "Chin Up",
    "Chinup", "Cu", "Weighted Chin Up", "Neutral Grip Pull Up", "Lat Pulldown",
    "Lat", "Lpd", "Cable Pulldown", "Pulldown",

    # --- Deadlift Variations ---
    "Deadlift", "Dead", "Dl", "Conventional Deadlift", "Sumo Deadlift", "Sumo",
    "Romanian Deadlift", "Rdl", "Rack Pull", "Block Pull", "Deficit Deadlift",
    "Trap Bar Deadlift", "Hex Bar Deadlift", "Hex Bar", "Trap Bar", "Snatch Grip Deadlift",
    "Speed Deadlift", "Paused Deadlift",

    # --- Squat Variations ---
    "Squat", "Sq", "High Bar Squat", "Low Bar Squat", "Front Squat", "Front", "Fsq",
    "Pause Squat", "Paused Squat", "Tempo Squat", "Box Squat", "Hack Squat", "Hack",
    "Goblet Squat", "Safety Bar Squat", "Ssb Squat", "Anderson Squat",

    # --- Leg Movements ---
    "Leg Press", "Press", "Lp", "Single Leg Press", "Bulgarian Split Squat",
    "Bulgarian", "Bss", "Lunge", "Lunges", "Walking Lunge", "Reverse Lunge",
    "Front Foot Elevated Lunge", "Split Squat", "Step Up", "Box Step Up",

    # --- Olympic Lifts / Explosive ---
    "Power Clean", "Clean", "Pcln", "Hang Clean", "Clean and Jerk", "Jerk",
    "Snatch", "Power Snatch", "Hang Snatch", "Push Jerk",

    # --- Hip / Posterior Chain ---
    "Hip Thrust", "Thrust", "Ht", "Barbell Hip Thrust", "Glute Bridge", "Single Leg Hip Thrust",
    "Good Morning", "Goodmorning", "Reverse Hyper", "Cable Kickback",

    # --- Misc Compound / Lower Body ---
    "Step Ups", "Walking Lunge", "Deficit Lunge", "Pistol Squat", "Shrug", "Bb Shrug",
    "Db Shrug", "Trap Shrug", "Farmer Carry", "Yoke Carry"
]


# ---------------- Helper Functions ---------------- #

def get_target_reps(exercise: str) -> int:
    for lift in COMPOUND_LIFTS:
        if lift.lower() == exercise.lower():
            return 8
    return 12


def read_rows():
    """
    Read CSV -> list of dict rows.
    Expected schema: timestamp, session_name, exercise, weight, reps
    """
    rows = []
    if not os.path.exists(FILENAME):
        return rows
    with open(FILENAME, newline="") as f:
        reader = csv.reader(f)
        for r in reader:
            if len(r) < 5:
                # skip malformed/old rows
                continue
            ts, session_name, ex, w, reps = r[:5]
            try:
                rows.append({
                    "ts": datetime.strptime(ts, DT_TS_FMT),
                    "session": session_name.strip(),
                    "exercise": ex.strip(),
                    "weight": float(w),
                    "reps": int(reps)
                })
            except Exception:
                # skip any bad row
                continue
    return rows


def get_current_session():
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, "r", encoding="utf-8") as f:
            return f.read().strip() or None
    return None


def set_current_session(workout_title: str):
    """
    Create a unique session name with full timestamp prefix, e.g.:
    '2025-10-16 18:42:05 | Push Day'
    """
    started = datetime.now().strftime(DT_TS_FMT)
    session_name = f"{started} | {workout_title}"
    with open(SESSION_FILE, "w", encoding="utf-8") as f:
        f.write(session_name)
    return session_name


def clear_current_session():
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)


def parse_session_datetime(session_name: str):
    """Extract datetime from 'YYYY-mm-dd HH:MM:SS | Title'. Fallback to datetime.min."""
    try:
        prefix = session_name.split(" | ")[0].strip()
        return datetime.strptime(prefix, DT_TS_FMT)
    except Exception:
        return datetime.min


# ---------------- Routes ---------------- #

@app.route("/")
def index():
    current_session = get_current_session()
    return render_template("index.html", current_session=current_session)


@app.route("/start_workout", methods=["POST"])
def start_workout():
    name = (request.form.get("session_name") or "").strip()
    if not name:
        return redirect(url_for("index"))
    set_current_session(name)
    return redirect(url_for("index"))


@app.route("/end_workout")
def end_workout():
    clear_current_session()
    return redirect(url_for("index"))


@app.route("/log", methods=["POST"])
def log_workout():
    # MUST have an active session
    current_session = get_current_session()
    if not current_session:
        return render_template("index.html", message="⚠️ Start a workout first!")

    exercise = request.form["exercise"].strip().title()
    weights = request.form.getlist("weight[]")
    reps_list = request.form.getlist("reps[]")

    # Clean/validate the sets
    sets = []
    for w, r in zip(weights, reps_list):
        if str(w).strip() and str(r).strip():
            try:
                sets.append((float(w), int(r)))
            except ValueError:
                continue

    if not sets:
        return render_template("index.html", message="Please enter at least one valid set.", current_session=current_session)

    # Write rows with a proper timestamp per set (same minute/second is fine)
    now_str = datetime.now().strftime(DT_TS_FMT)
    with open(FILENAME, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for w, r in sets:
            writer.writerow([now_str, current_session, exercise, w, r])

    return render_template("index.html", message=f"✅ Logged {exercise}!", current_session=current_session)


@app.route("/history")
def history():
    rows = read_rows()
    if not rows:
        return render_template("history.html", sessions=[])

    # Group rows by session -> exercise -> sets
    sessions = {}
    for r in rows:
        sname = r["session"]
        sessions.setdefault(sname, {})
        sessions[sname].setdefault(r["exercise"], []).append((r["weight"], r["reps"]))

    # Sort sessions by their datetime prefix (newest first)
    sorted_sessions = sorted(
        sessions.items(),
        key=lambda x: parse_session_datetime(x[0]),
        reverse=True
    )

    return render_template("history.html", sessions=sorted_sessions)


# Allow spaces and symbols in the session name part of the URL
@app.route("/session/<path:session_name>")
def view_session(session_name):
    session_name = unquote(session_name)
    rows = read_rows()
    data = [r for r in rows if r["session"] == session_name]
    exercises = {}
    for r in data:
        exercises.setdefault(r["exercise"], []).append((r["weight"], r["reps"]))
    return render_template("session.html", session_name=session_name, exercises=exercises)


if __name__ == "__main__":
    app.run(debug=True)
