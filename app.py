import csv
import io
import os
import re
from functools import wraps

from flask import (
    Flask, jsonify, render_template, request,
    session, redirect, url_for, make_response
)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.exceptions import BadRequest

import database as db


app = Flask(__name__)

app.secret_key = os.environ.get(
    "SECRET_KEY",
    "scholardesk-local-development-key-change-before-deployment"
)

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.environ.get("COOKIE_SECURE") == "1",
)

db.initialize_database()

SUBJECTS = db.SUBJECTS


def json_error(message, status=400):
    return jsonify({"success": False, "message": message}), status


def login_required(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            return json_error("Please log in to continue.", 401)
        return function(*args, **kwargs)
    return wrapper


def current_user_id():
    return session.get("user_id")


def get_json_data():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise ValueError("Please submit valid form data.")
    return data


def validate_student(data):
    name = str(data.get("name", "")).strip()
    roll_number = str(data.get("roll_number", "")).strip()

    if not name:
        raise ValueError("Student name is required.")

    if not roll_number:
        raise ValueError("Roll number is required.")

    if len(name) > 100 or len(roll_number) > 40:
        raise ValueError("Name or roll number is too long.")

    email = str(data.get("email", "")).strip()
    phone = str(data.get("phone", "")).strip()
    dob = str(data.get("dob", "")).strip()
    gender = str(data.get("gender", "")).strip()
    address = str(data.get("address", "")).strip()

    if email and not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        raise ValueError("Please enter a valid student email.")

    if phone and not re.fullmatch(r"[0-9+\-\s()]{7,20}", phone):
        raise ValueError("Please enter a valid phone number.")

    if gender not in ("", "Male", "Female", "Other", "Prefer not to say"):
        raise ValueError("Please select a valid gender.")

    if len(address) > 500:
        raise ValueError("Address must be 500 characters or fewer.")

    incoming_marks = data.get("marks", {})
    if not isinstance(incoming_marks, dict):
        raise ValueError("Please enter valid marks.")

    marks = {}

    database_keys = {
        "Python": "python",
        "Java": "java",
        "DBMS": "dbms",
        "Web Development": "web_development",
        "Computer Networks": "computer_networks",
    }

    for subject in SUBJECTS:
        raw_value = incoming_marks.get(subject, 0)

        try:
            mark = float(raw_value)
        except (TypeError, ValueError):
            raise ValueError(f"Marks for {subject} must be a number.")

        if mark < 0 or mark > 100:
            raise ValueError(f"Marks for {subject} must be between 0 and 100.")

        marks[subject] = mark

    return {
        "name": name,
        "roll_number": roll_number,
        "email": email,
        "phone": phone,
        "dob": dob,
        "gender": gender,
        "address": address,
        "marks": marks,
    }


def add_result_fields(student):
    student = dict(student)

    marks = {
        "Python": student["python"],
        "Java": student["java"],
        "DBMS": student["dbms"],
        "Web Development": student["web_development"],
        "Computer Networks": student["computer_networks"],
    }

    total = sum(marks.values())
    percentage = total / len(SUBJECTS)
    passed = all(mark >= 33 for mark in marks.values())

    if not passed:
        grade = "F"
        status = "Fail"
    elif percentage >= 90:
        grade = "A+"
        status = "Pass"
    elif percentage >= 80:
        grade = "A"
        status = "Pass"
    elif percentage >= 70:
        grade = "B"
        status = "Pass"
    elif percentage >= 60:
        grade = "C"
        status = "Pass"
    elif percentage >= 50:
        grade = "D"
        status = "Pass"
    else:
        grade = "E"
        status = "Pass"

    student["marks"] = marks
    student["total"] = round(total, 2)
    student["maximum_marks"] = len(SUBJECTS) * 100
    student["percentage"] = round(percentage, 2)
    student["grade"] = grade
    student["status"] = status

    return student


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/auth/me", methods=["GET"])
def auth_me():
    user_id = current_user_id()

    if not user_id:
        return jsonify({"authenticated": False})

    user = db.get_user_by_id(user_id)

    if not user:
        session.clear()
        return jsonify({"authenticated": False})

    return jsonify({"authenticated": True, "user": user})


@app.route("/api/auth/register", methods=["POST"])
def register():
    try:
        data = get_json_data()
    except ValueError as error:
        return json_error(str(error))

    name = str(data.get("name", "")).strip()
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))

    if len(name) < 2 or len(name) > 100:
        return json_error("Name must contain 2 to 100 characters.")

    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        return json_error("Please enter a valid email address.")

    if len(password) < 8:
        return json_error("Password must contain at least 8 characters.")

    if db.get_user_by_email(email):
        return json_error("An account with this email already exists.", 409)

    try:
        user = db.create_user(
            name,
            email,
            generate_password_hash(password)
        )
    except Exception:
        return json_error("Could not create the account. Please try again.", 500)

    session.clear()
    session["user_id"] = user["id"]

    return jsonify({"success": True, "user": user}), 201


@app.route("/api/auth/login", methods=["POST"])
def login():
    try:
        data = get_json_data()
    except ValueError as error:
        return json_error(str(error))

    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))

    user = db.get_user_by_email(email)

    if not user or not check_password_hash(user["password_hash"], password):
        return json_error("Incorrect email or password.", 401)

    session.clear()
    session["user_id"] = user["id"]

    return jsonify({
        "success": True,
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
        }
    })


@app.route("/api/auth/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"success": True})


@app.route("/api/students", methods=["GET"])
@login_required
def list_students():
    students = [
        add_result_fields(student)
        for student in db.get_all_students(current_user_id())
    ]

    return jsonify({"students": students})


@app.route("/api/students", methods=["POST"])
@login_required
def create_student():
    try:
        data = validate_student(get_json_data())
        student = db.save_student(current_user_id(), data)
    except ValueError as error:
        return json_error(str(error))
    except Exception as error:
        if "UNIQUE constraint failed" in str(error):
            return json_error("This roll number already exists in your account.", 409)
        return json_error("Could not save this student.", 500)

    return jsonify({
        "success": True,
        "student": add_result_fields(student)
    }), 201


@app.route("/api/students/<int:student_id>", methods=["PUT"])
@login_required
def update_student(student_id):
    try:
        data = validate_student(get_json_data())
        student = db.save_student(
            current_user_id(),
            data,
            student_id=student_id
        )
    except ValueError as error:
        return json_error(str(error))
    except Exception as error:
        if "UNIQUE constraint failed" in str(error):
            return json_error("This roll number already exists in your account.", 409)
        return json_error("Could not update this student.", 500)

    if not student:
        return json_error("Student not found in your account.", 404)

    return jsonify({
        "success": True,
        "student": add_result_fields(student)
    })


@app.route("/api/students/<int:student_id>", methods=["DELETE"])
@login_required
def remove_student(student_id):
    deleted = db.delete_student(student_id, current_user_id())

    if not deleted:
        return json_error("Student not found in your account.", 404)

    return jsonify({"success": True})


@app.route("/api/summary", methods=["GET"])
@login_required
def summary():
    students = [
        add_result_fields(student)
        for student in db.get_all_students(current_user_id())
    ]

    total = len(students)
    passed = sum(student["status"] == "Pass" for student in students)
    failed = total - passed
    average = (
        sum(student["percentage"] for student in students) / total
        if total else 0
    )

    return jsonify({
        "total_students": total,
        "passed": passed,
        "failed": failed,
        "average_percentage": round(average, 2),
        "pass_rate": round((passed / total) * 100, 2) if total else 0,
    })


@app.route("/api/export", methods=["GET"])
@login_required
def export_students():
    students = [
        add_result_fields(student)
        for student in db.get_all_students(current_user_id())
    ]

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "Name", "Roll Number", "Email", "Phone", "Date of Birth",
        "Gender", "Address", *SUBJECTS, "Total", "Percentage",
        "Grade", "Status"
    ])

    for student in students:
        writer.writerow([
            student["name"],
            student["roll_number"],
            student["email"],
            student["phone"],
            student["dob"],
            student["gender"],
            student["address"],
            *[student["marks"][subject] for subject in SUBJECTS],
            student["total"],
            student["percentage"],
            student["grade"],
            student["status"],
        ])

    response = make_response("\ufeff" + output.getvalue())
    response.headers["Content-Type"] = "text/csv; charset=utf-8"
    response.headers["Content-Disposition"] = "attachment; filename=scholardesk_results.csv"
    return response


if __name__ == "__main__":
    app.run(debug=True)