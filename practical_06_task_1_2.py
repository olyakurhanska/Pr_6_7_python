"""
Views/контролери для обробки запитів у Flask.
"""

from flask import Flask, request, jsonify
from functools import wraps

app = Flask(__name__)


# Декоратор для валідації JSON-запитів
def validate_json(required_fields):
    """Декоратор для валідації JSON-запитів."""

    def decorator(f):

        @wraps(f)
        def wrapper(*args, **kwargs):
            data = request.get_json(silent=True)

            if data is None:
                return jsonify({"error": "Очікується JSON"}), 400

            missing = [
                field for field in required_fields
                if field not in data
            ]

            if missing:
                return jsonify({
                    "error": f"Відсутні поля: {', '.join(missing)}"
                }), 400

            return f(*args, **kwargs)

        return wrapper

    return decorator


# --- View-функції ---

@app.route("/api/items", methods=["GET"])
def get_items():
    """GET /api/items — список елементів з фільтрацією."""

    # Отримання параметрів фільтрації з request.args
    category = request.args.get("category")
    min_price = request.args.get("min_price", type=float)
    max_price = request.args.get("max_price", type=float)
    sort = request.args.get("sort", "name")
    order = request.args.get("order", "asc")

    items = list(items_db.values())

    # Фільтрація за категорією
    if category:
        items = [
            item for item in items
            if item["category"].lower() == category.lower()
        ]

    # Фільтрація за мінімальною ціною
    if min_price is not None:
        items = [
            item for item in items
            if item["price"] >= min_price
        ]

    # Фільтрація за максимальною ціною
    if max_price is not None:
        items = [
            item for item in items
            if item["price"] <= max_price
        ]

    # Сортування
    if sort not in ["name", "price", "category"]:
        sort = "name"

    items.sort(
        key=lambda item: item[sort],
        reverse=(order == "desc")
    )

    return jsonify({
        "count": len(items),
        "items": items
    }), 200


@app.route("/api/items", methods=["POST"])
@validate_json(["name", "price", "category"])
def create_item():
    """POST /api/items — створити елемент з валідацією."""

    global next_id

    data = request.get_json()

    # Валідація name
    name = str(data["name"]).strip()

    if not name:
        return jsonify({
            "error": "Поле name не може бути порожнім"
        }), 400

    # Валідація price
    try:
        price = float(data["price"])
    except (TypeError, ValueError):
        return jsonify({
            "error": "Поле price повинно бути числом"
        }), 400

    if price <= 0:
        return jsonify({
            "error": "Ціна повинна бути більшою за 0"
        }), 400

    category = str(data["category"]).strip()

    if not category:
        return jsonify({
            "error": "Поле category не може бути порожнім"
        }), 400

    new_item = {
        "id": next_id,
        "name": name,
        "price": price,
        "category": category
    }

    items_db[next_id] = new_item
    next_id += 1

    return jsonify(new_item), 201


@app.route("/api/items/<int:item_id>", methods=["GET"])
def get_item(item_id):
    """GET /api/items/:id — отримати деталі елемента."""

    item = items_db.get(item_id)

    if item is None:
        return jsonify({
            "error": "Елемент не знайдено"
        }), 404

    return jsonify(item), 200


@app.route("/api/items/<int:item_id>", methods=["PUT"])
@validate_json(["name", "price", "category"])
def update_item(item_id):
    """PUT /api/items/:id — оновити елемент повністю."""

    item = items_db.get(item_id)

    if item is None:
        return jsonify({
            "error": "Елемент не знайдено"
        }), 404

    data = request.get_json()

    name = str(data["name"]).strip()

    if not name:
        return jsonify({
            "error": "Поле name не може бути порожнім"
        }), 400

    try:
        price = float(data["price"])
    except (TypeError, ValueError):
        return jsonify({
            "error": "Поле price повинно бути числом"
        }), 400

    if price <= 0:
        return jsonify({
            "error": "Ціна повинна бути більшою за 0"
        }), 400

    category = str(data["category"]).strip()

    if not category:
        return jsonify({
            "error": "Поле category не може бути порожнім"
        }), 400

    item["name"] = name
    item["price"] = price
    item["category"] = category

    return jsonify(item), 200


@app.route("/api/items/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    """DELETE /api/items/:id — видалити елемент."""

    if item_id not in items_db:
        return jsonify({
            "error": "Елемент не знайдено"
        }), 404

    del items_db[item_id]

    return "", 204


# --- Обробка помилок ---

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Ресурс не знайдено"
    }), 404


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "error": "Некоректний запит"
    }), 400


# Тимчасова "база даних"
items_db = {
    1: {
        "id": 1,
        "name": "Ноутбук",
        "price": 25000,
        "category": "електроніка"
    },
    2: {
        "id": 2,
        "name": "Книга Python",
        "price": 500,
        "category": "книги"
    },
    3: {
        "id": 3,
        "name": "Навушники",
        "price": 2000,
        "category": "електроніка"
    }
}

next_id = 4


if __name__ == "__main__":
    app.run(debug=True, port=5001)