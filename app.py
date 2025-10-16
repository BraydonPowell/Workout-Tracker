from flask import Flask, render_template, request, redirect
import csv
from datetime import datetime

app = Flask(__name__)

FILENAME = "workouts.csv"

COMPOUND_LIFTS = [
    "Bench Press", "Bench", "Bp", "Incline Bench", "Incline", "Ibp",
    "Overhead Press", "Shoulder Press", "Ohp", "Push Press", "Pushpress",
    "Dips", "Close Grip Bench", "Cgbp", "Barbell Row", "Row", "Bbrow",
    "Pull Up", "Pullup", "Pu", "Chin Up", "Chinup", "Cu", "T-Bar Row",
    "Tbar", "Trow", "Lat Pulldown", "Lat", "Lpd", "Deadlift", "Dead", "Dl",
    "Squat", "Sq", "Front Squat", "Front", "Fsq", "Hack Squat", "Hack",
    "Leg Press", "Press", "Lp", "Romanian Deadlift", "Rdl", "Sumo Deadlift",
    "Sumo", "Lunge", "Lunges", "Bulgarian Split Squat", "Bulgarian", "Bss",
    "Power Clean", "Clean", "Pcln", "Snatch", "Pendlay Row", "Pendlay",
    "Hip Thrust", "Thrust", "Ht"
]

def get_target_reps(exercise):
    for lift in COMPOUND_LIFTS:
        if lift.lower() == exercise.lower():
            return 8
    return 12


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/log', methods=['POST'])
def log_workout():
    exercise = request.form['exercise'].strip().title()
    weight = float(request.form['weight'])
    reps = int(request.form['reps'])
    sets = int(request.form['sets'])
    target_reps = get_target_reps(exercise)

    with open(FILENAME, mode="a", newline="") as file:
        writer = csv.writer(file)
        for _ in range(sets):
            writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M"), exercise, weight, reps])

    message = ""
    if reps >= target_reps:
        message = f"🔥 You hit your target reps ({target_reps}) for {exercise}! Time to increase weight next session."
    else:
        message = f"💪 Keep going — aim for {target_reps} reps before increasing weight."

    return render_template('index.html', message=message)


@app.route('/history')
def history():
    try:
        with open(FILENAME, mode="r") as file:
            reader = csv.reader(file)
            data = list(reader)
        return render_template('history.html', data=data)
    except FileNotFoundError:
        return render_template('history.html', data=[])


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)