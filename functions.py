import sqlite3

DB_PATH = "databases/users.db"
CONTENT_DB = "databases/content.db"


# =========================
# INIT USERS DB
# =========================
def init_users_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT
    )
    """)

    conn.commit()
    conn.close()


# =========================
# CREATE USER
# =========================
def create_user(username, password, role):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    try:
        c.execute("""
        INSERT INTO users (username, password, role)
        VALUES (?, ?, ?)
        """, (username, password, role))
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()


# =========================
# READ USERS
# =========================
def get_users():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("SELECT id, username, role FROM users")
    data = c.fetchall()

    conn.close()
    return data


# =========================
# UPDATE USER
# =========================
def update_user(user_id, username, password, role):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
    UPDATE users
    SET username=?, password=?, role=?
    WHERE id=?
    """, (username, password, role, user_id))

    conn.commit()
    conn.close()


# =========================
# DELETE USER
# =========================
def delete_user(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.commit()
    conn.close()


# =========================
# KPI SYSTEM (FULL MINISTRY VIEW)
# =========================
def get_kpis():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # USERS
    c.execute("SELECT COUNT(*) FROM users")
    total_users = c.fetchone()[0]

    c.execute("SELECT role, COUNT(*) FROM users GROUP BY role")
    role_breakdown = c.fetchall()

    conn.close()

    # CONTENT DB
    conn2 = sqlite3.connect(CONTENT_DB)
    c2 = conn2.cursor()

    c2.execute("SELECT COUNT(*) FROM news")
    news_count = c2.fetchone()[0]

    c2.execute("SELECT COUNT(*) FROM ads")
    ads_count = c2.fetchone()[0]

    conn2.close()

    return {
        "total_users": total_users,
        "role_breakdown": role_breakdown,
        "news_count": news_count,
        "ads_count": ads_count
    }
