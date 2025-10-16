import csv
from datetime import datetime

FILENAME = "workouts.csv"

# Define compound lifts and rep goals
COMPOUND_LIFTS = [
    "Bench Press", "Bench", "Bp", "Incline Bench", "Incline", "Ibp",
    "Overhead Press", "Shoulder Press", "Ohp", "Push Press", "Pushpress",
    "Dips", "Close Grip Bench", "Cgbp",
    "Barbell Row", "Row", "Bbrow", "Pull Up", "Pullup", "Pu",
    "Chin Up", "Chinup", "Cu", "T-Bar Row", "Tbar", "Trow",
    "Lat Pulldown", "Lat", "Lpd", "Deadlift", "Dead", "Dl",
    "Squat", "Sq", "Front Squat", "Front", "Fsq", "Hack Squat", "Hack",
    "Leg Press", "Press", "Lp", "Romanian Deadlift", "Rdl",
    "Sumo Deadlift", "Sumo", "Lunge", "Lunges",
    "Bulgarian Split Squat", "Bulgarian", "Bss",
    "Power Clean", "Clean", "Pcln", "Snatch", "Pendlay Row", "Pendlay",
    "Hip Thrust", "Thrust", "Ht"
]

def get_target_reps(exercise):
    """Return rep goal depending on the movement type."""
    if exercise.title() in COMPOUND_LIFTS:
        return 8
    return 12

def log_workout():
    exercise = input("Exercise: ").strip().title()
    sets = int(input("How many sets did you do? "))
    target_reps = get_target_reps(exercise)

    hit_target = False

    for s in range(1, sets + 1):
        print(f"\n--- Set {s} ---")
        weight = float(input("Weight (lbs): "))
        reps = int(input("Reps: "))

        # Log each set
        with open(FILENAME, mode="a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M"), exercise, weight, reps])

        # Check progression logic for this set
        if reps >= target_reps:
            hit_target = True

    print("\n✅ Workout logged!")

    if hit_target:
        print(f"🔥 You hit your target reps ({target_reps}) for {exercise}!")
        print("👉 Time to increase weight next session.")
    else:
        print(f"💪 Keep training — aim for {target_reps} reps before increasing weight.")

def view_history():
    try:
        with open(FILENAME, mode="r") as file:
            reader = csv.reader(file)
            print("\n--- Workout History ---")
            for row in reader:
                print(f"{row[0]} | {row[1]}: {row[2]} lbs × {row[3]} reps")
    except FileNotFoundError:
        print("No workouts logged yet!")

def main():
    while True:
        print("\n--- Fitness Tracker ---")
        print("1. Log workout")
        print("2. View history")
        print("3. Quit")

        choice = input("Choose an option: ")

        if choice == "1":
            log_workout()
        elif choice == "2":
            view_history()
        elif choice == "3":
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()
