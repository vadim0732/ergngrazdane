import os
import re
import sqlite3
from datetime import datetime
from functools import wraps

from flask import (
    Flask, g, render_template, request, redirect,
    url_for, session, flash, abort, send_from_directory
)
from werkzeug.security import generate_password_hash, check_password_hash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "app.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "db", "schema.sql")

app = Flask(__name__)
app.secret_key = "change-me-on-exam"

# ---------- БД ----------
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db

@app.teardown_appcontext
def close_db(exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()

def init_db():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    with app.app_context():
        db = get_db()
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            db.executescript(f.read())
        db.execute(
            "INSERT INTO users (login, password_hash, full_name, phone, email, role) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            ("Admin", generate_password_hash("EgrnNET"),
             "Администратор", "8(900)000-00-00", "admin@egrn.local", "admin")
        )
        db.commit()
        print("БД инициализирована:", DB_PATH)

# ---------- helpers ----------
def login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapper

def admin_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        if session.get("role") != "admin":
            abort(403)
        return view(*args, **kwargs)
    return wrapper

@app.context_processor
def inject_user():
    return {
        "current_user": {
            "id": session.get("user_id"),
            "login": session.get("login"),
            "role": session.get("role"),
        } if "user_id" in session else None
    }

# ---------- публичные ----------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        login = request.form.get("login", "").strip()
        password = request.form.get("password", "")
        full_name = request.form.get("full_name", "").strip()
        phone = request.form.get("phone", "").strip()
        email = request.form.get("email", "").strip()

        errors = []
        if not re.fullmatch(r"[A-Za-z0-9]{6,}", login):
            errors.append("Логин: латиница и цифры, не менее 6 символов")
        if len(password) < 8:
            errors.append("Пароль — минимум 8 символов")
        if not re.fullmatch(r"[А-Яа-яЁё\s]+", full_name):
            errors.append("ФИО: только кириллица и пробелы")
        if not re.fullmatch(r"8\(\d{3}\)\d{3}-\d{2}-\d{2}", phone):
            errors.append("Телефон в формате 8(XXX)XXX-XX-XX")
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
            errors.append("Некорректный e-mail")

        db = get_db()
        if not errors and db.execute(
            "SELECT 1 FROM users WHERE login = ?", (login,)
        ).fetchone():
            errors.append("Такой логин уже занят")

        if errors:
            for e in errors:
                flash(e, "error")
            return render_template("register.html", form=request.form)

        db.execute(
            "INSERT INTO users (login, password_hash, full_name, phone, email) "
            "VALUES (?, ?, ?, ?, ?)",
            (login, generate_password_hash(password), full_name, phone, email)
        )
        db.commit()
        flash("Пользователь создан. Войдите.", "success")
        return redirect(url_for("login"))

    return render_template("register.html", form={})

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        login_ = request.form.get("login", "").strip()
        password = request.form.get("password", "")
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE login = ?", (login_,)).fetchone()
        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session["user_id"] = user["id"]
            session["login"] = user["login"]
            session["role"] = user["role"]
            return redirect(url_for("admin" if user["role"] == "admin" else "applications"))
        flash("Неверный логин или пароль", "error")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

# ---------- кабинет ----------
@app.route("/applications")
@login_required
def applications():
    db = get_db()
    rows = db.execute(
        """SELECT a.*, s.name AS service_name
           FROM applications a
           JOIN services s ON s.id = a.service_id
           WHERE a.user_id = ?
           ORDER BY a.created_at DESC""",
        (session["user_id"],)
    ).fetchall()
    return render_template("applications.html", applications=rows)

@app.route("/applications/new", methods=["GET", "POST"])
@login_required
def new_application():
    db = get_db()
    services = db.execute("SELECT * FROM services ORDER BY id").fetchall()

    if request.method == "POST":
        service_id = request.form.get("service_id")
        receive_date = request.form.get("receive_date", "").strip()
        payment = request.form.get("payment")

        errors = []
        try:
            datetime.strptime(receive_date, "%d.%m.%Y")
        except ValueError:
            errors.append("Дата в формате ДД.ММ.ГГГГ")
        if not service_id:
            errors.append("Выберите услугу")
        if payment not in ("Наличные", "Перевод"):
            errors.append("Выберите способ оплаты")

        if errors:
            for e in errors:
                flash(e, "error")
            return render_template("new_application.html",
                                   services=services, form=request.form)

        db.execute(
            "INSERT INTO applications (user_id, service_id, receive_date, payment) "
            "VALUES (?, ?, ?, ?)",
            (session["user_id"], service_id, receive_date, payment)
        )
        db.commit()
        flash("Заявка отправлена", "success")
        return redirect(url_for("applications"))

    return render_template("new_application.html", services=services, form={})

@app.route("/applications/<int:app_id>/review", methods=["POST"])
@login_required
def add_review(app_id):
    db = get_db()
    row = db.execute(
        "SELECT * FROM applications WHERE id = ? AND user_id = ?",
        (app_id, session["user_id"])
    ).fetchone()
    if not row:
        abort(404)
    if row["status"] != "Услуга оказана":
        flash("Отзыв доступен только после оказания услуги", "error")
    else:
        text = request.form.get("review", "").strip()
        if text:
            db.execute("UPDATE applications SET review = ? WHERE id = ?", (text, app_id))
            db.commit()
            flash("Спасибо за отзыв", "success")
    return redirect(url_for("applications"))

# ---------- админ ----------
@app.route("/admin")
@admin_required
def admin():
    db = get_db()
    status = request.args.get("status", "")
    try:
        page = max(int(request.args.get("page", 1)), 1)
    except ValueError:
        page = 1
    per_page = 5
    offset = (page - 1) * per_page

    where, params = "", []
    if status in ("Новая", "В обработке", "Услуга оказана"):
        where = "WHERE a.status = ?"
        params.append(status)

    total = db.execute(
        f"SELECT COUNT(*) FROM applications a {where}", params
    ).fetchone()[0]

    rows = db.execute(
        f"""SELECT a.*, s.name AS service_name,
                   u.login AS user_login, u.full_name
            FROM applications a
            JOIN services s ON s.id = a.service_id
            JOIN users u ON u.id = a.user_id
            {where}
            ORDER BY a.created_at DESC
            LIMIT ? OFFSET ?""",
        (*params, per_page, offset)
    ).fetchall()

    pages = (total + per_page - 1) // per_page
    return render_template("admin.html", applications=rows,
                           status=status, page=page, pages=pages)

@app.route("/admin/<int:app_id>/status", methods=["POST"])
@admin_required
def change_status(app_id):
    new_status = request.form.get("status")
    if new_status not in ("Новая", "В обработке", "Услуга оказана"):
        abort(400)
    db = get_db()
    db.execute("UPDATE applications SET status = ? WHERE id = ?", (new_status, app_id))
    db.commit()
    flash("Статус обновлён", "success")
    return redirect(url_for(
        "admin",
        status=request.args.get("status", ""),
        page=request.args.get("page", 1)
    ))

# ---------- мобильные страницы ----------
@app.route("/mobile/<path:filename>")
def mobile_files(filename):
    mobile_dir = os.path.join(BASE_DIR, "mobile")
    return send_from_directory(mobile_dir, filename)

# ---------- CLI ----------
@app.cli.command("init-db")
def cli_init_db():
    init_db()

if __name__ == "__main__":
    if not os.path.exists(DB_PATH):
        init_db()
    app.run(host="127.0.0.1", port=5001, debug=True)