"""
CRUD: Update та Delete для блогу.
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

app = Flask(__name__)
app.secret_key = "blog-secret-key"


# Форма редагування
EDIT_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Редагування</title>
</head>
<body>

    <h1>Редагування публікації</h1>

    {% with messages = get_flashed_messages() %}
        {% if messages %}
            <div style="color: green;">
                {{ messages[0] }}
            </div>
        {% endif %}
    {% endwith %}

    <form method="POST">

        <label>Заголовок:</label><br>
        <input
            type="text"
            name="title"
            value="{{ post.title }}"
            required
            style="width:400px;"
        >
        <br><br>

        <label>Автор:</label><br>
        <input
            type="text"
            name="author"
            value="{{ post.author }}"
            required
        >
        <br><br>

        <label>Зміст:</label><br>
        <textarea
            name="content"
            rows="10"
            cols="50"
            required
        >{{ post.content }}</textarea>
        <br><br>

        <button type="submit">Зберегти зміни</button>

        <a href="{{ url_for('post_detail', post_id=post.id) }}">
            Скасувати
        </a>

    </form>

</body>
</html>
"""


# Сторінка підтвердження видалення
DELETE_CONFIRM_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Видалення</title>
</head>
<body>

    <h1>Підтвердження видалення</h1>

    <p>
        Ви дійсно бажаєте видалити публікацію
        "<strong>{{ post.title }}</strong>"?
    </p>

    <form method="POST">
        <button type="submit" style="color: red;">
            Так, видалити
        </button>

        <a href="{{ url_for('post_detail', post_id=post.id) }}">
            Скасувати
        </a>
    </form>

</body>
</html>
"""


# Список публікацій
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

</body>
</html>
"""


# Деталі публікації
DETAIL_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>{{ post.title }}</title>
</head>
<body>

    {% with messages = get_flashed_messages() %}
        {% if messages %}
            <div style="color: green;">
                {{ messages[0] }}
            </div>
        {% endif %}
    {% endwith %}

    <h1>{{ post.title }}</h1>

    <p>
        <strong>Автор:</strong> {{ post.author }}
    </p>

    <p>
        <strong>Дата:</strong> {{ post.created_at }}
    </p>

    <hr>

    <p>{{ post.content }}</p>

    <hr>

    <a href="{{ url_for('post_edit', post_id=post.id) }}">
        Редагувати
    </a>

    |

    <a href="{{ url_for('post_delete', post_id=post.id) }}">
        Видалити
    </a>

    |

    <a href="{{ url_for('post_list') }}">
        До списку
    </a>

</body>
</html>
"""


# GET /posts — список
@app.route("/posts")
def post_list():
    posts = posts_db

    return render_template_string(
        LIST_TEMPLATE,
        posts=posts
    )


# GET /posts/<id> — деталі
@app.route("/posts/<int:post_id>")
def post_detail(post_id):
    post = next(
        (post for post in posts_db if post["id"] == post_id),
        None
    )

    if post is None:
        abort(404)

    return render_template_string(
        DETAIL_TEMPLATE,
        post=post
    )


# GET + POST /posts/<id>/edit
@app.route("/posts/<int:post_id>/edit", methods=["GET", "POST"])
def post_edit(post_id):
    """UPDATE: редагування публікації."""

    post = next(
        (post for post in posts_db if post["id"] == post_id),
        None
    )

    if post is None:
        abort(404)

    if request.method == "POST":

        title = request.form.get("title", "").strip()
        author = request.form.get("author", "").strip()
        content = request.form.get("content", "").strip()

        # Валідація
        if not title or not author or not content:
            flash("Усі поля повинні бути заповнені.")

            return render_template_string(
                EDIT_TEMPLATE,
                post={
                    "id": post_id,
                    "title": title,
                    "author": author,
                    "content": content
                }
            ), 400

        # Оновлення даних
        post["title"] = title
        post["author"] = author
        post["content"] = content

        flash("Публікацію успішно оновлено.")

        return redirect(
            url_for(
                "post_detail",
                post_id=post_id
            )
        )

    # GET — форма з поточними даними
    return render_template_string(
        EDIT_TEMPLATE,
        post=post
    )


# GET + POST /posts/<id>/delete
@app.route("/posts/<int:post_id>/delete", methods=["GET", "POST"])
def post_delete(post_id):
    """DELETE: видалення публікації з підтвердженням."""

    post = next(
        (post for post in posts_db if post["id"] == post_id),
        None
    )

    if post is None:
        abort(404)

    # POST — підтверджене видалення
    if request.method == "POST":

        posts_db.remove(post)

        flash("Публікацію успішно видалено.")

        return redirect(
            url_for("post_list")
        )

    # GET — сторінка підтвердження
    return render_template_string(
        DELETE_CONFIRM_TEMPLATE,
        post=post
    )


# Тимчасове сховище
posts_db = [
    {
        "id": 1,
        "title": "Перша публікація",
        "content": "Зміст першої...",
        "author": "Іван",
        "created_at": "2025-01-15"
    },
    {
        "id": 2,
        "title": "Друга публікація",
        "content": "Зміст другої...",
        "author": "Марія",
        "created_at": "2025-01-20"
    }
]


if __name__ == "__main__":
    app.run(debug=True, port=5004)