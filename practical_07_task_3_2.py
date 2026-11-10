"""
REST API: serializer, API key, APIError та logging.
Частина 3.2 практичної роботи.
"""

from functools import wraps

from flask import Flask, request, jsonify

app = Flask(__name__)

API_KEY = "my-secret-key"

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


# -------------------------
# Serializer
# -------------------------

def serialize_student(student, fields=None):
    if not fields:
        return student.copy()

    return {
        field: student[field]
        for field in fields
        if field in student
    }


# -------------------------
# APIError
# -------------------------

class APIError(Exception):
    def __init__(self, message, status_code=400):
        self.message = message
        self.status_code = status_code


@app.errorhandler(APIError)
def handle_api_error(error):
    return jsonify({
        "error": error.message
    }), error.status_code


# -------------------------
# API key decorator
# -------------------------

def require_api_key(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        api_key = request.headers.get("X-API-Key")

        if api_key != API_KEY:
            raise APIError(
                "Невірний або відсутній API ключ",
                401
            )

        return function(*args, **kwargs)

    return wrapper


# -------------------------
# Logging
# -------------------------

@app.before_request
def before_request():
    print(
        f"[BEFORE] {request.method} "
        f"{request.path}"
    )


@app.after_request
def after_request(response):
    print(
        f"[AFTER] {request.method} "
        f"{request.path} "
        f"-> {response.status_code}"
    )
    return response


# -------------------------
# GET students
# -------------------------

@app.route("/api/students", methods=["GET"])
def get_students():
    result = students.copy()

    # Текстовий пошук
    search = request.args.get("search", "").strip().lower()

    if search:
        result = [
            student for student in result
            if search in student["name"].lower()
            or search in student["email"].lower()
            or search in student["speciality"].lower()
        ]

    # Вибір полів
    fields_param = request.args.get("fields")

    if fields_param:
        fields = [
            field.strip()
            for field in fields_param.split(",")
            if field.strip()
        ]
    else:
        fields = None

    serialized = [
        serialize_student(student, fields)
        for student in result
    ]

    return jsonify({
        "students": serialized,
        "count": len(serialized)
    }), 200


# -------------------------
# Protected endpoint
# -------------------------

@app.route("/api/protected", methods=["GET"])
@require_api_key
def protected():
    return jsonify({
        "message": "Доступ дозволено",
        "data": "Захищені дані API"
    }), 200


# -------------------------
# API error test
# -------------------------

@app.route("/api/error", methods=["GET"])
def api_error():
    raise APIError(
        "Демонстраційна помилка API",
        400
    )


if __name__ == "__main__":
    app.run(debug=True, port=5006)