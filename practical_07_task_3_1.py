"""
REST API для роботи зі студентами.
Частина 3.1 практичної роботи.
"""

from flask import Flask, request, jsonify

app = Flask(__name__)

students = [
    {
        "id": 1,
        "name": "Іван Петренко",
        "email": "ivan@example.com",
        "course": 2,
        "speciality": "Комп'ютерні науки"
    },
    {
        "id": 2,
        "name": "Марія Коваленко",
        "email": "maria@example.com",
        "course": 3,
        "speciality": "Інженерія програмного забезпечення"
    },
    {
        "id": 3,
        "name": "Олексій Бондар",
        "email": "oleksii@example.com",
        "course": 1,
        "speciality": "Комп'ютерні науки"
    },
    {
        "id": 4,
        "name": "Анна Мельник",
        "email": "anna@example.com",
        "course": 4,
        "speciality": "Кібербезпека"
    }
]


def find_student(student_id):
    return next(
        (student for student in students if student["id"] == student_id),
        None
    )


# GET /api/students
@app.route("/api/students", methods=["GET"])
def get_students():
    result = students.copy()

    # Фільтрація за курсом
    course = request.args.get("course")
    if course:
        try:
            course = int(course)
            result = [
                student for student in result
                if student["course"] == course
            ]
        except ValueError:
            return jsonify({
                "error": "Параметр course повинен бути числом"
            }), 400

    # Фільтрація за спеціальністю
    speciality = request.args.get("speciality")
    if speciality:
        result = [
            student for student in result
            if student["speciality"].lower() == speciality.lower()
        ]

    # Пагінація
    try:
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))
    except ValueError:
        return jsonify({
            "error": "page та per_page повинні бути числами"
        }), 400

    if page < 1 or per_page < 1:
        return jsonify({
            "error": "page та per_page повинні бути більшими за 0"
        }), 400

    total = len(result)

    start = (page - 1) * per_page
    end = start + per_page

    paginated_students = result[start:end]

    return jsonify({
        "students": paginated_students,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": (total + per_page - 1) // per_page
        }
    }), 200


# GET /api/students/<id>
@app.route("/api/students/<int:student_id>", methods=["GET"])
def get_student(student_id):
    student = find_student(student_id)

    if student is None:
        return jsonify({
            "error": "Студента не знайдено"
        }), 404

    return jsonify(student), 200


# POST /api/students
@app.route("/api/students", methods=["POST"])
def create_student():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "error": "JSON-дані обов'язкові"
        }), 400

    required_fields = ["name", "email", "course", "speciality"]

    for field in required_fields:
        if field not in data or str(data[field]).strip() == "":
            return jsonify({
                "error": f"Поле '{field}' є обов'язковим"
            }), 400

    new_id = max(student["id"] for student in students) + 1

    new_student = {
        "id": new_id,
        "name": data["name"],
        "email": data["email"],
        "course": data["course"],
        "speciality": data["speciality"]
    }

    students.append(new_student)

    return jsonify(new_student), 201


# PUT /api/students/<id>
@app.route("/api/students/<int:student_id>", methods=["PUT"])
def update_student(student_id):
    student = find_student(student_id)

    if student is None:
        return jsonify({
            "error": "Студента не знайдено"
        }), 404

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "error": "JSON-дані обов'язкові"
        }), 400

    required_fields = ["name", "email", "course", "speciality"]

    for field in required_fields:
        if field not in data or str(data[field]).strip() == "":
            return jsonify({
                "error": f"Для PUT поле '{field}' є обов'язковим"
            }), 400

    student["name"] = data["name"]
    student["email"] = data["email"]
    student["course"] = data["course"]
    student["speciality"] = data["speciality"]

    return jsonify(student), 200


# PATCH /api/students/<id>
@app.route("/api/students/<int:student_id>", methods=["PATCH"])
def patch_student(student_id):
    student = find_student(student_id)

    if student is None:
        return jsonify({
            "error": "Студента не знайдено"
        }), 404

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "error": "JSON-дані обов'язкові"
        }), 400

    allowed_fields = ["name", "email", "course", "speciality"]

    for field in data:
        if field not in allowed_fields:
            return jsonify({
                "error": f"Недозволене поле: {field}"
            }), 400

    for field, value in data.items():
        if str(value).strip() == "":
            return jsonify({
                "error": f"Поле '{field}' не може бути порожнім"
            }), 400
        student[field] = value

    return jsonify(student), 200


# DELETE /api/students/<id>
@app.route("/api/students/<int:student_id>", methods=["DELETE"])
def delete_student(student_id):
    student = find_student(student_id)

    if student is None:
        return jsonify({
            "error": "Студента не знайдено"
        }), 404

    students.remove(student)

    return "", 204


# GET /api/students/stats
@app.route("/api/students/stats", methods=["GET"])
def student_stats():
    total = len(students)

    courses = {}
    for student in students:
        course = str(student["course"])
        courses[course] = courses.get(course, 0) + 1

    return jsonify({
        "total_students": total,
        "by_course": courses
    }), 200


if __name__ == "__main__":
    app.run(debug=True, port=5005)