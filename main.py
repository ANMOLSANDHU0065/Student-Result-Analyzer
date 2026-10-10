
from student import SUBJECTS, create_student
from validation import (
    validate_name,
    validate_roll_number,
    validate_marks
)
from result import analyze_result
from storage import load_students, save_student, initialize_storage


def get_valid_input(prompt, validator):
    """Keep asking until the input is valid."""

    while True:
        try:
            return validator(input(prompt))
        except ValueError as error:
            print(f"Error: {error}")


def display_student(student):
    """Display one student's marks and result."""

    result = analyze_result(student)

    print("\n" + "=" * 45)
    print("             STUDENT RESULT")
    print("=" * 45)
    print(f"Name       : {student['name']}")
    print(f"Roll Number: {student['roll_number']}")
    print("-" * 45)

    for subject, marks in student["marks"].items():
        print(f"{subject:<25} {marks:>3}/100")

    print("-" * 45)
    print(f"Total      : {result['total']}/{result['maximum']}")
    print(f"Percentage : {result['percentage']}%")
    print(f"Grade      : {result['grade']}")
    print(f"Status     : {result['status']}")
    print("=" * 45)


def add_student():
    """Collect and save a new student's details."""

    students = load_students()

    name = get_valid_input("Enter student name: ", validate_name)

    roll_number = get_valid_input(
        "Enter roll number: ",
        validate_roll_number
    )

    if any(
        s["roll_number"].casefold() == roll_number.casefold()
        for s in students
    ):
        print("Error: This roll number already exists.")
        return

    marks = {}

    for subject in SUBJECTS:
        marks[subject] = get_valid_input(
            f"Enter marks for {subject} (0-100): ",
            validate_marks
        )

    student = create_student(name, roll_number, marks)

    try:
        save_student(student)
        print("\nStudent record saved successfully!")
        display_student(student)
    except (OSError, ValueError, csv.Error) as error:
        print(f"Could not save the student record: {error}")


def view_all_students():
    """Display all saved student records."""

    try:
        students = load_students()

        if not students:
            print("\nNo student records found.")
            return

        for student in students:
            display_student(student)

    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"Could not read student records: {error}")


def search_student():
    """Search for a student using their roll number."""

    roll_number = input("Enter roll number to search: ").strip()

    if not roll_number:
        print("Roll number cannot be empty.")
        return

    try:
        students = load_students()

        for student in students:
            if student["roll_number"].casefold() == roll_number.casefold():
                display_student(student)
                return

        print("Student not found.")

    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"Could not search student records: {error}")


def class_summary():
    """Show class average and topper."""

    try:
        students = load_students()

        if not students:
            print("\nNo student records available for analysis.")
            return

        results = [
            (student, analyze_result(student))
            for student in students
        ]

        average = round(
            sum(result["percentage"] for _, result in results)
            / len(results),
            2
        )

        topper, topper_result = max(
            results,
            key=lambda item: item[1]["percentage"]
        )

        passed = sum(
            result["status"] == "PASS"
            for _, result in results
        )

        failed = len(students) - passed

        print("\n" + "=" * 40)
        print("             CLASS SUMMARY")
        print("=" * 40)
        print(f"Total Students : {len(students)}")
        print(f"Class Average  : {average}%")
        print(f"Passed         : {passed}")
        print(f"Failed         : {failed}")
        print(f"Class Topper   : {topper['name']}")
        print(f"Topper Roll No.: {topper['roll_number']}")
        print(f"Topper Score   : {topper_result['percentage']}%")
        print("=" * 40)

    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"Could not analyze class results: {error}")


def main():
    """Run the Student Result Analyzer application."""

    try:
        initialize_storage()
    except OSError as error:
        print(f"Could not initialize CSV storage: {error}")
        return

    while True:
        print("\n========== STUDENT RESULT ANALYZER ==========")
        print("1. Add Student")
        print("2. View All Students")
        print("3. Search Student")
        print("4. Class Summary")
        print("5. Exit")

        choice = input("Choose an option (1-5): ").strip()

        if choice == "1":
            add_student()
        elif choice == "2":
            view_all_students()
        elif choice == "3":
            search_student()
        elif choice == "4":
            class_summary()
        elif choice == "5":
            print("Thank you for using Student Result Analyzer!")
            break
        else:
            print("Invalid choice. Please enter a number from 1 to 5.")


if __name__ == "__main__":
    import csv
    main()



    