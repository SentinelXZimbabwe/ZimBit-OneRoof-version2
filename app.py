import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename
import functions  # Super-user + RBAC engine

app = Flask(__name__)
app.secret_key = "supersecretkey"

# =========================
# CONFIGURATION
# =========================
UPLOAD_FOLDER = "static/uploads"
CONTENT_DB = "databases/content.db"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# CMS (Content Admin)
USERNAME = "12344978"
PASSWORD = "13@274"

# Super User (System Admin)
SUPER_USER = "admin"
SUPER_PASS = "admin123"


# =========================
# DATABASE INITIALISATION
# =========================
def init_db():
    conn = sqlite3.connect(CONTENT_DB)
    c = conn.cursor()

    # NEWS TABLE
    c.execute("""
    CREATE TABLE IF NOT EXISTS news (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        content TEXT,
        category TEXT
    )
    """)

    # ADS TABLE
    c.execute("""
    CREATE TABLE IF NOT EXISTS ads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        content TEXT,
        image TEXT
    )
    """)

    conn.commit()
    conn.close()


init_db()
functions.init_users_db()  # Super-user DB


# =========================
# LANDING PAGE
# =========================
@app.route("/")
def landing():
    conn = sqlite3.connect(CONTENT_DB)
    c = conn.cursor()

    ads = c.execute(
        "SELECT title, content, image FROM ads"
    ).fetchall()

    conn.close()

    return render_template("landing.html", ads=ads)


# =========================
# NEWS PAGE
# =========================
@app.route("/news")
def news():
    conn = sqlite3.connect(CONTENT_DB)
    c = conn.cursor()

    news = c.execute(
        "SELECT title, content, category FROM news"
    ).fetchall()

    conn.close()

    return render_template("news-update.html", news=news)


# =========================
# CMS LOGIN (CONTENT ADMIN)
# =========================
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        if (request.form.get("username") == USERNAME and
            request.form.get("password") == PASSWORD):

            session["cms_user"] = True
            return redirect(url_for("upload"))

    return render_template("login.html")


# =========================
# CMS UPLOAD SYSTEM
# =========================
@app.route("/upload", methods=["GET", "POST"])
def upload():

    if not session.get("cms_user"):
        return redirect(url_for("login"))

    if request.method == "POST":

        content_type = request.form.get("type")
        title = request.form.get("title")
        content = request.form.get("content")

        conn = sqlite3.connect(CONTENT_DB)
        c = conn.cursor()

        # -------------------------
        # NEWS INSERT
        # -------------------------
        if content_type == "news":
            category = request.form.get("category")

            c.execute("""
                INSERT INTO news (title, content, category)
                VALUES (?, ?, ?)
            """, (title, content, category))

        # -------------------------
        # ADS INSERT
        # -------------------------
        elif content_type == "ad":

            file = request.files.get("image")
            filename = None

            if file and file.filename != "":
                filename = secure_filename(file.filename)
                file.save(os.path.join(UPLOAD_FOLDER, filename))

            c.execute("""
                INSERT INTO ads (title, content, image)
                VALUES (?, ?, ?)
            """, (title, content, filename))

        conn.commit()
        conn.close()

        return redirect(url_for("landing"))

    return render_template("upload.html")


# =========================
# CMS LOGOUT
# =========================
@app.route("/logout")
def logout():
    session.pop("cms_user", None)
    return redirect(url_for("landing"))


# =========================
# SUPER USER LOGIN PAGE
# =========================
@app.route("/super-user", methods=["GET", "POST"])
def super_user_login():

    if request.method == "POST":
        u = request.form.get("username")
        p = request.form.get("password")

        if u == SUPER_USER and p == SUPER_PASS:
            session["super"] = True
            return redirect(url_for("super_dashboard"))

    return render_template("super-user-login.html")


# =========================
# SUPER USER DASHBOARD (FULL CONTROL + KPI + CRUD)
# =========================
@app.route("/super-dashboard", methods=["GET", "POST"])
def super_dashboard():

    if not session.get("super"):
        return redirect(url_for("super_user_login"))

    # -------------------------
    # CREATE USER
    # -------------------------
    if request.method == "POST" and "create" in request.form:
        functions.create_user(
            request.form.get("username"),
            request.form.get("password"),
            request.form.get("role")
        )

    # -------------------------
    # UPDATE USER
    # -------------------------
    if request.method == "POST" and "update" in request.form:
        functions.update_user(
            request.form.get("id"),
            request.form.get("username"),
            request.form.get("password"),
            request.form.get("role")
        )

    # -------------------------
    # DELETE USER
    # -------------------------
    if request.method == "POST" and "delete" in request.form:
        functions.delete_user(request.form.get("id"))

    users = functions.get_users()
    kpis = functions.get_kpis()

    return render_template(
        "super-user-dashboard.html",
        users=users,
        kpis=kpis
    )


# =========================
# SUPER USER LOGOUT
# =========================
@app.route("/super-logout")
def super_logout():
    session.pop("super", None)
    return redirect(url_for("super_user_login"))


# =========================
# RUN APPLICATION
# =========================
if __name__ == "__main__":
    app.run(debug=True)
