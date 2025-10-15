import csv
from datetime import datetime

FILENAME = "workouts.csv"

def log_workout():
    exercise = input("Exercise: ")
    weight = input("Weight (lbs): ")
    reps = input("Reps: ")

    with open(FILENAME, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M"), exercise, weight, reps])
    print("Workout logged!")

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
