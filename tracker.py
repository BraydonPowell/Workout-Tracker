import csv
from datetime import datetime
from collections import defaultdict

FILENAME = "workouts.csv"

# ------------------------------
# Compound lift list (with nicknames)
# ------------------------------
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

# ------------------------------
# Helper functions
# ------------------------------

def get_target_reps(exercise):
    """Return the rep goal depending on the exercise type."""
    for lift in COMPOUND_LIFTS:
        if lift.lower() == exercise.lower():
            return 8
    return 12


def get_last_weight(exercise):
    """Get the last weight used for a specific exercise."""
    try:
        with open(FILENAME, mode="r") as file:
            reader = csv.reader(file)
            rows = [row for row in reader if row[1].lower() == exercise.lower()]
            if rows:
                return float(rows[-1][2])
    except FileNotFoundError:
        pass
    return None


# ------------------------------
# Core workout functions
# ------------------------------

def log_workout():
    exercise = input("Exercise: ").strip().title()
    sets = int(input("How many sets did you do? "))
    target_reps = get_target_reps(exercise)

    last_weight = get_last_weight(exercise)
    if last_weight:
        print(f"Last used weight for {exercise}: {last_weight} lbs")

    hit_target = False

    for s in range(1, sets + 1):
        print(f"\n--- Set {s} ---")
        if last_weight:
            weight_input = input(f"Weight (lbs) [press Enter to keep {last_weight}]: ").strip()
        else:
            weight_input = input("Weight (lbs): ").strip()

        # Use last weight if user presses Enter
        if weight_input == "" and last_weight:
            weight = last_weight
        else:
            weight = float(weight_input)

        reps = int(input("Reps: "))

        # Log each set
        with open(FILENAME, mode="a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M"), exercise, weight, reps])

        if reps >= target_reps:
            hit_target = True

    print("\n✅ Workout logged!")

    if hit_target:
        print(f"🔥 You hit your target reps ({target_reps}) for {exercise}!")
        print("👉 Time to increase weight next session.")
    else:
        print(f"💪 Keep going — aim for {target_reps} reps before increasing weight.")


def view_history():
    """View full workout history."""
    try:
        with open(FILENAME, mode="r") as file:
            reader = csv.reader(file)
            print("\n--- Workout History ---")
            for row in reader:
                print(f"{row[0]} | {row[1]}: {row[2]} lbs × {row[3]} reps")
    except FileNotFoundError:
        print("No workouts logged yet!")


def view_last_workout():
    """Display the most recent workout grouped by date and exercise."""
    try:
        with open(FILENAME, mode="r") as file:
            reader = csv.reader(file)
            data = list(reader)

        if not data:
            print("No workouts logged yet!")
            return

        # Get the most recent workout date
        last_date = data[-1][0].split(" ")[0]

        # Group sets by exercise
        workout_summary = defaultdict(list)
        for row in data:
            date = row[0].split(" ")[0]
            if date == last_date:
                exercise = row[1]
                weight = row[2]
                reps = row[3]
                workout_summary[exercise].append(f"{weight}x{reps}")

        print(f"\n--- Last Workout ({last_date}) ---")
        for exercise, sets in workout_summary.items():
            print(f"{exercise}: {', '.join(sets)}")

    except FileNotFoundError:
        print("No workouts logged yet!")


# ------------------------------
# Main menu
# ------------------------------

def main():
    while True:
        print("\n--- Fitness Tracker ---")
        print("1. Log workout")
        print("2. View history")
        print("3. View last workout")
        print("4. Quit")

        choice = input("Choose an option: ")

        if choice == "1":
            log_workout()
        elif choice == "2":
            view_history()
        elif choice == "3":
            view_last_workout()
        elif choice == "4":
            break
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()
    