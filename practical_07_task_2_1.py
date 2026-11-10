"""
CRUD: Create та Read для блогу.
"""

from flask import (
    Flask,
    request,
    render_template_string,
    redirect,
    url_for,
    flash,
    abort
)
from datetime import datetime


app = Flask(__name__)
app.secret_key = "blog-secret-key"


# HTML-шаблон списку публікацій
LIST_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Блог</title>
</head>
<body>

    <h1>Публікації</h1>

    {% with messages = get_flashed_messages() %}
        {% if messages %}
            <div style="color: green;">
                {{ messages[0] }}
            </div>
        {% endif %}
    {% endwith %}

    <a href="{{ url_for('post_create') }}">+ Нова публікація</a>

    <hr>

    {% for post in posts %}
        <article>
            <h2>
                <a href="{{ url_for('post_detail', post_id=post.id) }}">
                    {{ post.title }}
                </a>
            </h2>

            <p>{{ post.content[:100] }}...</p>

            <small>
                {{ post.author }} | {{ post.created_at }}
            </small>
        </article>

        <hr>
    {% endfor %}

    <div>
        {% if page > 1 %}
            <a href="{{ url_for('post_list', page=page - 1) }}">
                ← Попередня
            </a>
        {% endif %}

        <span> Сторінка {{ page }} </span>

        {% if has_next %}
            <a href="{{ url_for('post_list', page=page + 1) }}">
                Наступна →
            </a>
        {% endif %}
    </div>

</body>
</html>
"""


# HTML-шаблон форми
FORM_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>{{ form_title }}</title>
</head>
<body>

    <h1>{{ form_title }}</h1>

    <form method="POST">

        <label>Заголовок:</label><br>
        <input
            type="text"
            name="title"
            value="{{ post.title if post else '' }}"
            required
            style="width:400px;"
        >
        <br><br>

        <label>Автор:</label><br>
        <input
            type="text"
            name="author"
            value="{{ post.author if post else '' }}"
            required
        >
        <br><br>

        <label>Зміст:</label><br>
        <textarea
            name="content"
            rows="10"
            cols="50"
            required
        >{{ post.content if post else '' }}</textarea>
        <br><br>

        <button type="submit">{{ button_text }}</button>

        <a href="{{ url_for('post_list') }}">
            Скасувати
        </a>

    </form>

</body>
</html>
"""


# GET /posts — список публікацій з пагінацією
@app.route("/posts")
def post_list():
    """READ: список усіх публікацій."""

    page = request.args.get("page", 1, type=int)

    if page < 1:
        page = 1

    per_page = 2

    start = (page - 1) * per_page
    end = start + per_page

    posts = posts_db[start:end]

    has_next = end < len(posts_db)

    return render_template_string(
        LIST_TEMPLATE,
        posts=posts,
        page=page,
        has_next=has_next
    )


# GET /posts/<id> — деталі публікації
@app.route("/posts/<int:post_id>")
def post_detail(post_id):
    """READ: деталі однієї публікації."""

    post = next(
        (post for post in posts_db if post["id"] == post_id),
        None
    )

    if post is None:
        abort(404)

    return render_template_string(
        """
        <!DOCTYPE html>
        <html>
        <head>
            <title>{{ post.title }}</title>
        </head>
        <body>

            <h1>{{ post.title }}</h1>

            <p>
                <strong>Автор:</strong>
                {{ post.author }}
            </p>

            <p>
                <strong>Дата:</strong>
                {{ post.created_at }}
            </p>

            <hr>

            <p>{{ post.content }}</p>

            <hr>

            <a href="{{ url_for('post_list') }}">
                ← До списку
            </a>

        </body>
        </html>
        """,
        post=post
    )


# GET + POST /posts/create — створення публікації
@app.route("/posts/create", methods=["GET", "POST"])
def post_create():
    """CREATE: створення нової публікації."""

    global next_id

    if request.method == "POST":

        title = request.form.get("title", "").strip()
        author = request.form.get("author", "").strip()
        content = request.form.get("content", "").strip()

        # Валідація непорожніх полів
        if not title or not author or not content:
            flash("Усі поля повинні бути заповнені.")

            return render_template_string(
                FORM_TEMPLATE,
                form_title="Нова публікація",
                button_text="Створити",
                post={
                    "title": title,
                    "author": author,
                    "content": content
                }
            ), 400

        new_post = {
            "id": next_id,
            "title": title,
            "content": content,
            "author": author,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
        }

        posts_db.append(new_post)
        next_id += 1

        flash("Публікацію успішно створено.")

        return redirect(
            url_for(
                "post_detail",
                post_id=new_post["id"]
            )
        )

    return render_template_string(
        FORM_TEMPLATE,
        form_title="Нова публікація",
        button_text="Створити",
        post=None
    )


# Тимчасове сховище
posts_db = [
    {
        "id": 1,
        "title": "Перша публікація",
        "content": "Це зміст першої публікації.",
        "author": "Іван",
        "created_at": "2025-01-15"
    },
    {
        "id": 2,
        "title": "Друга публікація",
        "content": "Це зміст другої публікації.",
        "author": "Марія",
        "created_at": "2025-01-20"
    },
    {
        "id": 3,
        "title": "Третя публікація",
        "content": "Це зміст третьої публікації.",
        "author": "Петро",
        "created_at": "2025-02-01"
    }
]

next_id = 4


@app.errorhandler(404)
def not_found(error):
    return """
    <h1>404</h1>
    <p>Публікацію не знайдено.</p>
    <a href="/posts">До списку публікацій</a>
    """, 404


if __name__ == "__main__":
    app.run(debug=True, port=5003)