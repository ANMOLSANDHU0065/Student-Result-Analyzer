
SUBJECTS = [
    "Python",
    "Java",
    "DBMS",
    "Web Development",
    "Computer Networks"
]


def create_student(name, roll_number, marks):
    """Create and return a student record."""

    student = {
        "name": name,
        "roll_number": roll_number,
        "marks": marks
    }

    return student