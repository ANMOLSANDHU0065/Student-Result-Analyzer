
from result import SUBJECTS, analyze_result


def test_full_marks():
    marks = {subject: 100 for subject in SUBJECTS}
    result = analyze_result(marks)

    assert result["total"] == 500
    assert result["maximum"] == 500
    assert result["percentage"] == 100
    assert result["cgpa"] == 10
    assert result["grade"] == "A+"
    assert result["status"] == "PASS"


def test_existing_sample_result():
    marks = {
        "Python": 75,
        "Java": 50,
        "DBMS": 69,
        "Web Development": 90,
        "Computer Networks": 80,
    }
    result = analyze_result(marks)

    assert result["total"] == 364
    assert result["percentage"] == 72.8
    assert result["grade"] == "B"
    assert result["status"] == "PASS"


def test_one_subject_below_passing_marks():
    marks = {subject: 70 for subject in SUBJECTS}
    marks["Java"] = 20

    result = analyze_result(marks)

    assert result["status"] == "FAIL"


def test_zero_marks():
    marks = {subject: 0 for subject in SUBJECTS}
    result = analyze_result(marks)

    assert result["total"] == 0
    assert result["percentage"] == 0
    assert result["cgpa"] == 0
    assert result["grade"] == "F"
    assert result["status"] == "FAIL"