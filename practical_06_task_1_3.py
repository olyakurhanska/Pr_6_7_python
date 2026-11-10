"""
Cookies та sessions у Flask.
"""

from flask import Flask, request, make_response, session, redirect, url_for, jsonify

app = Flask(__name__)

app.secret_key = "super-secret-key-for-session"


# --- Робота з Cookies ---

@app.route("/set-theme/<theme>")
def set_theme(theme):
    """Встановити тему через cookie."""

    response = make_response(
        jsonify({
            "message": "Тему встановлено",
            "theme": theme
        })
    )

    response.set_cookie(
        "theme",
        theme,
        max_age=30 * 24 * 60 * 60,
        httponly=True,
        samesite="Lax"
    )

    return response


@app.route("/get-theme")
def get_theme():
    """Прочитати тему з cookie."""

    theme = request.cookies.get("theme", "light")

    return jsonify({
        "theme": theme
    })


@app.route("/set-language/<lang>")
def set_language(lang):
    """Встановити мову через cookie."""

    response = make_response(
        jsonify({
            "message": "Мову встановлено",
            "language": lang
        })
    )

    response.set_cookie(
        "language",
        lang,
        max_age=30 * 24 * 60 * 60,
        httponly=True,
        samesite="Lax"
    )

    return response


@app.route("/preferences")
def preferences():
    """Показати всі збережені уподобання з cookies."""

    return jsonify({
        "cookies": request.cookies.to_dict()
    })


# --- Робота з Sessions ---

@app.route("/cart/add/<int:product_id>")
def add_to_cart(product_id):
    """Додати товар до кошика (session)."""

    if product_id not in products_db:
        return jsonify({
            "error": "Товар не знайдено"
        }), 404

    cart = session.get("cart", [])

    cart.append(product_id)

    session["cart"] = cart

    return jsonify({
        "message": "Товар додано до кошика",
        "cart": cart
    })


@app.route("/cart")
def view_cart():
    """Переглянути кошик."""

    cart = session.get("cart", [])

    products = []

    for product_id in cart:
        if product_id in products_db:
            product = products_db[product_id].copy()
            product["id"] = product_id
            products.append(product)

    return jsonify({
        "cart": cart,
        "products": products
    })


@app.route("/cart/clear")
def clear_cart():
    """Очистити кошик."""

    session.pop("cart", None)

    return jsonify({
        "message": "Кошик очищено",
        "cart": []
    })


@app.route("/login", methods=["POST"])
def login():
    """Імітація входу — зберегти ім'я у session."""

    username = request.form.get("username")

    if not username:
        return jsonify({
            "error": "Необхідно вказати username"
        }), 400

    session["username"] = username

    return jsonify({
        "message": "Вхід виконано",
        "username": username
    })


@app.route("/logout")
def logout():
    """Вихід — очистити session."""

    session.pop("username", None)

    return jsonify({
        "message": "Вихід виконано"
    })


@app.route("/profile")
def profile():
    """Профіль користувача — залежить від session."""

    username = session.get("username")

    if not username:
        return redirect(url_for("login_page"))

    return jsonify({
        "username": username,
        "message": "Це профіль користувача"
    })


@app.route("/login-page")
def login_page():
    """Сторінка для імітації входу."""

    return """
    <h1>Вхід</h1>

    <form method="POST" action="/login">
        <label>Ім'я користувача:</label>
        <input type="text" name="username" required>
        <button type="submit">Увійти</button>
    </form>
    """


# Тимчасова "база" товарів
products_db = {
    1: {"name": "Ноутбук", "price": 25000},
    2: {"name": "Смартфон", "price": 12000},
    3: {"name": "Навушники", "price": 2000},
}


if __name__ == "__main__":
    app.run(debug=True, port=5002)