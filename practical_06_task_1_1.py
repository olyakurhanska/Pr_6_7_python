"""
Маршрутизація Flask: GET, POST, динамічні параметри.
"""

from flask import Flask, request, render_template_string, redirect, url_for

app = Flask(__name__)


# Шаблон HTML для демонстрації
BASE_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>{{ title }}</title>
</head>
<body>
    <h1>{{ title }}</h1>

    <nav>
        <a href="{{ url_for('index') }}">Головна</a> |
        <a href="{{ url_for('post_list') }}">Публікації</a> |
        <a href="{{ url_for('search') }}">Пошук</a>
    </nav>

    <hr>

    {{ content | safe }}
</body>
</html>
"""


# Головна сторінка (GET /)
@app.route("/")
def index():
    content = """
    <p>Ласкаво просимо до демонстраційного Flask-застосунку!</p>
    <p>Доступні маршрути:</p>
    <ul>
        <li>/</li>
        <li>/posts</li>
        <li>/posts/&lt;id&gt;</li>
        <li>/posts/create</li>
        <li>/search?q=...</li>
        <li>/archive/&lt;year&gt;/&lt;month&gt;</li>
        <li>/user/&lt;username&gt;</li>
    </ul>
    """

    return render_template_string(
        BASE_TEMPLATE,
        title="Головна сторінка",
        content=content
    )


# Список публікацій (GET /posts)
@app.route("/posts")
def post_list():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    start = (page - 1) * per_page
    end = start + per_page

    posts = posts_db[start:end]

    content = f"<p>Сторінка: {page}, кількість на сторінці: {per_page}</p>"

    if posts:
        content += "<ul>"
        for post in posts:
            content += (
                f'<li>'
                f'<a href="{url_for("post_detail", post_id=post["id"])}">'
                f'{post["title"]}'
                f'</a> — {post["author"]}'
                f'</li>'
            )
        content += "</ul>"
    else:
        content += "<p>Публікацій не знайдено.</p>"

    return render_template_string(
        BASE_TEMPLATE,
        title="Список публікацій",
        content=content
    )


# Деталі публікації (GET /posts/<int:post_id>)
@app.route("/posts/<int:post_id>")
def post_detail(post_id):
    post = next(
        (post for post in posts_db if post["id"] == post_id),
        None
    )

    if post is None:
        return "Публікацію не знайдено", 404

    content = f"""
    <h2>{post["title"]}</h2>
    <p><strong>Автор:</strong> {post["author"]}</p>
    <p>{post["content"]}</p>
    """

    return render_template_string(
        BASE_TEMPLATE,
        title="Деталі публікації",
        content=content
    )


# Створення публікації (GET + POST /posts/create)
@app.route("/posts/create", methods=["GET", "POST"])
def post_create():
    global next_id

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()
        author = request.form.get("author", "").strip()

        if not title or not content or not author:
            return """
            <h1>Помилка</h1>
            <p>Усі поля є обов'язковими.</p>
            <a href="/posts/create">Повернутися до форми</a>
            """, 400

        new_post = {
            "id": next_id,
            "title": title,
            "content": content,
            "author": author
        }

        posts_db.append(new_post)
        next_id += 1

        # Перенаправлення після успішного створення
        return redirect(url_for("post_detail", post_id=new_post["id"]))

    content = """
    <form method="POST">
        <p>
            <label>Заголовок:</label><br>
            <input type="text" name="title" required>
        </p>

        <p>
            <label>Автор:</label><br>
            <input type="text" name="author" required>
        </p>

        <p>
            <label>Зміст:</label><br>
            <textarea name="content" rows="8" cols="50" required></textarea>
        </p>

        <button type="submit">Створити</button>
    </form>
    """

    return render_template_string(
        BASE_TEMPLATE,
        title="Створення публікації",
        content=content
    )


# Пошук (GET /search?q=query)
@app.route("/search")
def search():
    query = request.args.get("q", "").strip()

    if not query:
        content = """
        <form method="GET">
            <label>Пошук:</label>
            <input type="text" name="q">
            <button type="submit">Знайти</button>
        </form>
        """
    else:
        results = [
            post for post in posts_db
            if query.lower() in post["title"].lower()
            or query.lower() in post["content"].lower()
        ]

        content = f"<p>Результати пошуку для: <strong>{query}</strong></p>"

        if results:
            content += "<ul>"
            for post in results:
                content += (
                    f'<li>'
                    f'<a href="{url_for("post_detail", post_id=post["id"])}">'
                    f'{post["title"]}'
                    f'</a>'
                    f'</li>'
                )
            content += "</ul>"
        else:
            content += "<p>Нічого не знайдено.</p>"

    return render_template_string(
        BASE_TEMPLATE,
        title="Пошук",
        content=content
    )


# Архів за датою (GET /archive/<int:year>/<int:month>)
@app.route("/archive/<int:year>/<int:month>")
def archive(year, month):
    content = f"""
    <p>Архів публікацій за:</p>
    <p><strong>Рік:</strong> {year}</p>
    <p><strong>Місяць:</strong> {month}</p>
    """

    return render_template_string(
        BASE_TEMPLATE,
        title="Архів",
        content=content
    )


# Профіль користувача (GET /user/<username>)
@app.route("/user/<username>")
def user_profile(username):
    content = f"""
    <h2>Профіль користувача</h2>
    <p><strong>Ім'я користувача:</strong> {username}</p>
    """

    return render_template_string(
        BASE_TEMPLATE,
        title="Профіль",
        content=content
    )


# Тимчасове сховище даних
posts_db = [
    {
        "id": 1,
        "title": "Вступ до Python",
        "content": "Python — потужна мова програмування.",
        "author": "Іван"
    },
    {
        "id": 2,
        "title": "Flask для початківців",
        "content": "Flask — мікрофреймворк для Python.",
        "author": "Марія"
    },
    {
        "id": 3,
        "title": "REST API",
        "content": "REST — архітектурний стиль веб-сервісів.",
        "author": "Петро"
    }
]

next_id = 4


if __name__ == "__main__":
    app.run(debug=True, port=5000)