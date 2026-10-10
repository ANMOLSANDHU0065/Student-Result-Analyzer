
import re

from result import SUBJECTS


def validate_student(name, roll_number, marks):
    errors = []

    name = str(name or "").strip()
    roll_number = str(roll_number or "").strip()

    if len(name) < 2:
        errors.append("Student name must contain at least 2 characters.")

    if len(name) > 80:
        errors.append("Student name cannot exceed 80 characters.")

    if not re.fullmatch(r"[A-Za-z0-9/_-]{2,30}", roll_number):
        errors.append(
            "Roll number must be 2–30 characters "
            "using letters, numbers, /, _ or -."
        )

    if not isinstance(marks, dict):
        errors.append("Marks must be provided for every subject.")
        return errors

    for subject in SUBJECTS:
        value = marks.get(subject)

        if value is None or str(value).strip() == "":
            errors.append(f"Enter marks for {subject}.")
            continue

        try:
            mark = float(value)
        except (TypeError, ValueError):
            errors.append(f"{subject} marks must be a number.")
            continue

        if not mark.is_integer() or not 0 <= mark <= 100:
            errors.append(f"{subject} marks must be a whole number from 0 to 100.")

    return errors