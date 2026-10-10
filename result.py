
SUBJECTS = [
    "Python",
    "Java",
    "DBMS",
    "Web Development",
    "Computer Networks",
]

MAX_MARKS_PER_SUBJECT = 100
PASS_MARKS = 33


def analyze_result(marks):
    """Calculate a student's academic result."""

    normalized_marks = {
        subject: int(marks.get(subject, 0))
        for subject in SUBJECTS
    }

    total = sum(normalized_marks.values())
    maximum = len(SUBJECTS) * MAX_MARKS_PER_SUBJECT
    percentage = round((total / maximum) * 100, 2)

    # Common illustrative conversion, not an official
    # university-specific CGPA conversion formula.
    cgpa = round(min(percentage / 9.5, 10.0), 2)

    if percentage >= 90:
        grade = "A+"
    elif percentage >= 80:
        grade = "A"
    elif percentage >= 70:
        grade = "B"
    elif percentage >= 60:
        grade = "C"
    elif percentage >= 50:
        grade = "D"
    else:
        grade = "F"

    passed = all(
        mark >= PASS_MARKS
        for mark in normalized_marks.values()
    )

    return {
        "marks": normalized_marks,
        "total": total,
        "maximum": maximum,
        "percentage": percentage,
        "cgpa": cgpa,
        "grade": grade,
        "status": "PASS" if passed else "FAIL",
    }