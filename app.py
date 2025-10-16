from flask import Flask, render_template, request, redirect, url_for
import csv
from datetime import datetime, timedelta
import os

app = Flask(__name__)

FILENAME = "workouts.csv"

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


DT_FMT = "%Y-%m-%d %H:%M"


# ---------------- Helper Functions ---------------- #

def get_target_reps(exercise: str) -> int:
    """Return target reps based on whether it's a compound or isolation lift."""
    for lift in COMPOUND_LIFTS:
        if lift.lower() == exercise.lower():
            return 8
    return 12


def read_rows():
    """Read CSV -> list of dict rows with parsed datetime."""
    rows = []
    try:
        with open(FILENAME, "r", newline="") as f:
            reader = csv.reader(f)
            for r in reader:
                if len(r) != 4:
                    continue
                ts, ex, w, reps = r
                try:
                    rows.append({
                        "ts": datetime.strptime(ts, DT_FMT),
                        "exercise": ex.strip(),
                        "weight": float(w),
                        "reps": int(reps),
                        "ts_str": ts
                    })
                except Exception:
                    continue
    except FileNotFoundError:
        pass
    return rows


def find_previous_session_ts(rows, exercise: str, current_session_ts: datetime):
    """Find the most recent session timestamp for exercise before this one."""
    ts_candidates = sorted(
        {r["ts"] for r in rows if r["exercise"].lower() == exercise.lower() and r["ts"] < current_session_ts}
    )
    return ts_candidates[-1] if ts_candidates else None


def group_session_top_weight(rows, exercise: str, session_ts: datetime):
    """Return top weight for the given exercise at a specific session time."""
    same_session = [r for r in rows if r["exercise"].lower() == exercise.lower() and r["ts"] == session_ts]
    return max((r["weight"] for r in same_session), default=None)


def find_last_weight(rows, exercise: str):
    """Return last logged weight for an exercise."""
    for r in sorted(rows, key=lambda x: x["ts"], reverse=True):
        if r["exercise"].lower() == exercise.lower():
            return r["weight"]
    return None


def round_to_step(x: float, step: float = 0.5) -> float:
    """Round to nearest step (default 0.5kg)."""
    return round(x / step) * step


# ---------------- Routes ---------------- #

@app.route("/", methods=["GET", "POST"])
def index():
    rows = read_rows()
    last_weights = {r["exercise"]: r["weight"] for r in rows}

    if request.method == "POST":
        exercise = request.form["exercise"].strip().title()
        weights = request.form.getlist("weight[]")
        reps_list = request.form.getlist("reps[]")

        # Clean input
        sets = []
        for w, r in zip(weights, reps_list):
            if w.strip() and r.strip():
                try:
                    sets.append((float(w), int(r)))
                except ValueError:
                    continue

        if not sets:
            return render_template("index.html", message="Please enter at least one valid set.", last_weights=last_weights)

        # Log timestamp for session
        now = datetime.now()
        session_ts_str = now.strftime(DT_FMT)

        # Write all sets
        with open(FILENAME, "a", newline="") as f:
            writer = csv.writer(f)
            for w, r in sets:
                writer.writerow([session_ts_str, exercise, w, r])

        # Re-read after writing
        all_rows = read_rows()
        current_session_ts = datetime.strptime(session_ts_str, DT_FMT)
        target_reps = get_target_reps(exercise)

        # --- Progressive Overload Logic ---
        avg_reps = sum(r for _, r in sets) / len(sets)
        curr_top = max(w for w, _ in sets)
        prev_ts = find_previous_session_ts(all_rows, exercise, current_session_ts)
        prev_top = group_session_top_weight(all_rows, exercise, prev_ts) if prev_ts else None

        if avg_reps >= target_reps:
            suggested = round_to_step(curr_top * 1.025, 0.5)
            message = (
                f"🔥 Solid work! Your average reps were {avg_reps:.1f}. "
                f"Consider moving from {curr_top:g} kg → {suggested:g} kg next session."
            )
        elif avg_reps >= target_reps * 0.8:
            message = (
                f"💪 Almost there! Average reps: {avg_reps:.1f} (target {target_reps}). "
                f"Stay at {curr_top:g} kg until you consistently hit {target_reps}."
            )
        else:
            lighter = round_to_step(curr_top * 0.95, 0.5)
            message = (
                f"⚠️ Average reps were {avg_reps:.1f}, well below target {target_reps}. "
                f"Consider lowering to {lighter:g} kg next session to refine form."
            )

        return render_template("index.html", message=message, last_weights=last_weights)

    return render_template("index.html", last_weights=last_weights)


@app.route("/history")
def history():
    data = []
    hours = request.args.get("hours", None)

    if not os.path.exists(FILENAME):
        return render_template("history.html", grouped_data=[], hours=hours)

    try:
        with open(FILENAME, "r", newline="") as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) < 4:
                    continue
                date_str, exercise, weight, reps = row[:4]
                try:
                    date_obj = datetime.strptime(date_str.strip(), DT_FMT)
                    weight = float(weight)
                    reps = int(reps)

                    if hours:
                        cutoff = datetime.now() - timedelta(hours=float(hours))
                        if date_obj < cutoff:
                            continue

                    data.append({
                        "date": date_obj.strftime("%Y-%m-%d"),
                        "datetime": date_obj,
                        "exercise": exercise.strip(),
                        "weight": weight,
                        "reps": reps,
                    })
                except Exception:
                    continue

        # Sort by actual datetime (most recent first)
        data.sort(key=lambda x: x["datetime"], reverse=True)

        # Group by exercise and date
        grouped = {}
        for entry in data:
            key = (entry["exercise"], entry["date"])
            grouped.setdefault(key, []).append((entry["weight"], entry["reps"]))

        grouped_data = [
            {"exercise": ex, "date": dt, "sets": sets}
            for (ex, dt), sets in grouped.items()
        ]

        # Sort groups by actual date (descending)
        grouped_data.sort(key=lambda x: datetime.strptime(x["date"], "%Y-%m-%d"), reverse=True)

    except FileNotFoundError:
        grouped_data = []

    return render_template("history.html", grouped_data=grouped_data, hours=hours)


# ---------------- Main ---------------- #

if __name__ == "__main__":
    app.run(debug=True)
