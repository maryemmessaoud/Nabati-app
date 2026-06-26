# app/database.py
import sqlite3
import hashlib
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent.parent / "data" / "nabati.db"

def init_db():
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()

    # Table utilisateurs
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            nom        TEXT NOT NULL,
            prenom     TEXT NOT NULL,
            email      TEXT UNIQUE NOT NULL,
            password   TEXT NOT NULL,
            region     TEXT,
            created_at TEXT NOT NULL
        )
    """)

    # Table plantes
    c.execute("""
        CREATE TABLE IF NOT EXISTS plantes (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER NOT NULL,
            nom_plante TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # Table détections
    c.execute("""
    CREATE TABLE IF NOT EXISTS detections (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id    INTEGER NOT NULL,
        date       TEXT NOT NULL,
        heure      TEXT NOT NULL,
        plante     TEXT NOT NULL,
        maladie    TEXT NOT NULL,
        confiance  REAL NOT NULL,
        saine      INTEGER NOT NULL,
        image_data BLOB,
        conseils   TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
""")

    conn.commit()
    conn.close()

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(nom, prenom, email, password, region="") -> dict:
    init_db()
    try:
        conn = sqlite3.connect(str(DB_PATH))
        c = conn.cursor()
        c.execute("""
            INSERT INTO users (nom, prenom, email, password, region, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (nom, prenom, email, hash_password(password), region,
              datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        user_id = c.lastrowid
        conn.close()
        return {"success": True, "user_id": user_id}
    except sqlite3.IntegrityError:
        return {"success": False, "error": "Email déjà utilisé"}

def login_user(email, password) -> dict:
    init_db()
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    c.execute("""
        SELECT id, nom, prenom, region FROM users
        WHERE email=? AND password=?
    """, (email, hash_password(password)))
    row = c.fetchone()
    conn.close()
    if row:
        return {"success": True, "user_id": row[0], "nom": row[1],
                "prenom": row[2], "region": row[3]}
    return {"success": False, "error": "Email ou mot de passe incorrect"}

def log_detection(user_id, plant, disease, confidence, image_bytes=None, conseils=""):
    init_db()
    now = datetime.now()
    is_healthy = 1 if "healthy" in disease.lower() else 0
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    c.execute("""
        INSERT INTO detections
        (user_id, date, heure, plante, maladie, confiance, saine, image_data, conseils)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (user_id, now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S"),
          plant, disease, round(confidence, 4), is_healthy, image_bytes, conseils))
    conn.commit()
    conn.close()

def get_user_detections(user_id):
    init_db()
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    c.execute("""
        SELECT id, date, heure, plante, maladie, confiance, saine, image_data, conseils
        FROM detections WHERE user_id=?
        ORDER BY id DESC
    """, (user_id,))
    rows = c.fetchall()
    conn.close()
    return rows



def get_user_stats(user_id):
    init_db()
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    stats = {}

    c.execute("SELECT COUNT(*) FROM detections WHERE user_id=?", (user_id,))
    stats["total"] = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM detections WHERE user_id=? AND saine=1", (user_id,))
    stats["saines"] = c.fetchone()[0]
    stats["malades"] = stats["total"] - stats["saines"]

    c.execute("""
        SELECT maladie, COUNT(*) FROM detections
        WHERE user_id=? AND saine=0
        GROUP BY maladie ORDER BY COUNT(*) DESC LIMIT 5
    """, (user_id,))
    stats["top_maladies"] = c.fetchall()

    c.execute("""
        SELECT date, COUNT(*) FROM detections
        WHERE user_id=? GROUP BY date
        ORDER BY date DESC LIMIT 7
    """, (user_id,))
    stats["par_jour"] = c.fetchall()

    c.execute("SELECT AVG(confiance) FROM detections WHERE user_id=?", (user_id,))
    avg = c.fetchone()[0]
    stats["confiance_moyenne"] = round(avg, 3) if avg else 0

    conn.close()
    return stats

def get_global_stats():
    init_db()
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    stats = {}

    c.execute("SELECT COUNT(*) FROM detections")
    stats["total"] = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM detections WHERE saine=1")
    stats["saines"] = c.fetchone()[0]
    stats["malades"] = stats["total"] - stats["saines"]
    c.execute("""
        SELECT maladie, COUNT(*) FROM detections WHERE saine=0
        GROUP BY maladie ORDER BY COUNT(*) DESC LIMIT 5
    """)
    stats["top_maladies"] = c.fetchall()
    c.execute("""
        SELECT date, COUNT(*) FROM detections
        GROUP BY date ORDER BY date DESC LIMIT 7
    """)
    stats["par_jour"] = c.fetchall()
    c.execute("SELECT AVG(confiance) FROM detections")
    avg = c.fetchone()[0]
    stats["confiance_moyenne"] = round(avg, 3) if avg else 0
    c.execute("SELECT COUNT(*) FROM users")
    stats["total_users"] = c.fetchone()[0]

    conn.close()
    return stats