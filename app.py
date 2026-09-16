from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import sqlite3
import re

app = Flask(__name__)
CORS(app)

DB_NAME = "students.db"

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            age INTEGER NOT NULL,
            course TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def valid_email(email):
    return re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email) is not None

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/students/", methods=["GET"])
def get_students():
    search = request.args.get("search", "").strip()
    conn = get_db()

    if search:
        rows = conn.execute("""
            SELECT * FROM students
            WHERE name LIKE ? OR email LIKE ? OR course LIKE ?
            ORDER BY id DESC
        """, (f"%{search}%", f"%{search}%", f"%{search}%")).fetchall()
    else:
        rows = conn.execute("SELECT * FROM students ORDER BY id DESC").fetchall()

    conn.close()
    return jsonify([dict(row) for row in rows])

@app.route("/api/students/<int:student_id>/", methods=["GET"])
def get_student(student_id):
    conn = get_db()
    row = conn.execute("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()
    conn.close()

    if row is None:
        return jsonify({"error": "Student not found"}), 404

    return jsonify(dict(row))

@app.route("/api/students/", methods=["POST"])
def create_student():
    data = request.get_json(silent=True) or {}

    name = str(data.get("name", "")).strip()
    email = str(data.get("email", "")).strip()
    course = str(data.get("course", "")).strip()
    age = data.get("age")

    if not name or not email or not course or age in (None, ""):
        return jsonify({"error": "All fields are required"}), 400

    if not valid_email(email):
        return jsonify({"error": "Enter a valid email address"}), 400

    try:
        age = int(age)
    except (ValueError, TypeError):
        return jsonify({"error": "Age must be a number"}), 400

    if age < 15 or age > 100:
        return jsonify({"error": "Age must be between 15 and 100"}), 400

    conn = get_db()
    try:
        cursor = conn.execute(
            "INSERT INTO students (name, email, age, course) VALUES (?, ?, ?, ?)",
            (name, email, age, course)
        )
        conn.commit()
        student_id = cursor.lastrowid
        row = conn.execute("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()
        return jsonify(dict(row)), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "Email already exists"}), 409
    finally:
        conn.close()

@app.route("/api/students/<int:student_id>/", methods=["PUT", "PATCH"])
def update_student(student_id):
    data = request.get_json(silent=True) or {}

    name = str(data.get("name", "")).strip()
    email = str(data.get("email", "")).strip()
    course = str(data.get("course", "")).strip()
    age = data.get("age")

    if not name or not email or not course or age in (None, ""):
        return jsonify({"error": "All fields are required"}), 400

    if not valid_email(email):
        return jsonify({"error": "Enter a valid email address"}), 400

    try:
        age = int(age)
    except (ValueError, TypeError):
        return jsonify({"error": "Age must be a number"}), 400

    if age < 15 or age > 100:
        return jsonify({"error": "Age must be between 15 and 100"}), 400

    conn = get_db()
    try:
        existing = conn.execute(
            "SELECT id FROM students WHERE id = ?", (student_id,)
        ).fetchone()

        if existing is None:
            return jsonify({"error": "Student not found"}), 404

        conn.execute("""
            UPDATE students
            SET name = ?, email = ?, age = ?, course = ?
            WHERE id = ?
        """, (name, email, age, course, student_id))
        conn.commit()

        row = conn.execute(
            "SELECT * FROM students WHERE id = ?", (student_id,)
        ).fetchone()

        return jsonify(dict(row))
    except sqlite3.IntegrityError:
        return jsonify({"error": "Email already exists"}), 409
    finally:
        conn.close()

@app.route("/api/students/<int:student_id>/", methods=["DELETE"])
def delete_student(student_id):
    conn = get_db()
    cursor = conn.execute("DELETE FROM students WHERE id = ?", (student_id,))
    conn.commit()
    deleted = cursor.rowcount
    conn.close()

    if deleted == 0:
        return jsonify({"error": "Student not found"}), 404

    return jsonify({"message": "Student deleted successfully"})

@app.errorhandler(404)
def not_found(error):
    if request.path.startswith("/api/"):
        return jsonify({"error": "API endpoint not found"}), 404
    return error

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
