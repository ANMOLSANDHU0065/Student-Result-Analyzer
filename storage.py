
import csv
from pathlib import Path

from student import SUBJECTS


DATA_FILE = Path(__file__).resolve().parent / "students.csv"

FIELDNAMES = ["name", "roll_number"] + SUBJECTS


def initialize_storage():
    """Create the CSV file with headers if it does not exist."""

    if not DATA_FILE.exists() or DATA_FILE.stat().st_size == 0:
        with DATA_FILE.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
            writer.writeheader()


def load_students():
    """Load student records from CSV safely."""

    initialize_storage()
    students = []

    with DATA_FILE.open("r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        for line_number, row in enumerate(reader, start=2):
            if not row or not row.get("name") or not row.get("roll_number"):
                continue

            try:
                marks = {}

                for subject in SUBJECTS:
                    value = row.get(subject)

                    if value is None or not value.strip():
                        raise ValueError(
                            f"Missing marks for {subject}."
                        )

                    marks[subject] = int(value)

                    if not 0 <= marks[subject] <= 100:
                        raise ValueError(
                            f"Marks for {subject} must be between 0 and 100."
                        )

                students.append({
                    "name": row["name"].strip(),
                    "roll_number": row["roll_number"].strip(),
                    "marks": marks
                })

            except (ValueError, AttributeError) as error:
                raise ValueError(
                    f"Invalid student data on CSV line {line_number}: {error}"
                ) from error

    return students

def save_student(student):
    """Save a new student record to the CSV file."""

    students = load_students()
    new_roll = student["roll_number"].casefold()

    if any(
        existing["roll_number"].casefold() == new_roll
        for existing in students
    ):
        raise ValueError("This roll number already exists.")

    row = {
        "name": student["name"],
        "roll_number": student["roll_number"]
    }

    for subject in SUBJECTS:
        row[subject] = student["marks"][subject]

    with DATA_FILE.open("a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        writer.writerow(row)