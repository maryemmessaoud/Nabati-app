# app/database.py
import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent.parent / "data" / "detections.db"

def init_db():
    """Initialise la base de données."""
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS detections (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            date        TEXT NOT NULL,
            heure       TEXT NOT NULL,
            plante      TEXT NOT NULL,
            maladie     TEXT NOT NULL,
            confiance   REAL NOT NULL,
            saine       INTEGER NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def log_detection(plant: str, disease: str, confidence: float):
    """Enregistre une détection dans la base."""
    init_db()
    now = datetime.now()
    is_healthy = 1 if "healthy" in disease.lower() else 0
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    c.execute("""
        INSERT INTO detections (date, heure, plante, maladie, confiance, saine)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        now.strftime("%Y-%m-%d"),
        now.strftime("%H:%M:%S"),
        plant,
        disease,
        round(confidence, 4),
        is_healthy
    ))
    conn.commit()
    conn.close()

def get_all_detections():
    """Retourne toutes les détections."""
    init_db()
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    c.execute("SELECT * FROM detections ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return rows

def get_stats():
    """Retourne les statistiques globales."""
    init_db()
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()

    stats = {}

    # Total diagnostics
    c.execute("SELECT COUNT(*) FROM detections")
    stats["total"] = c.fetchone()[0]

    # Plantes saines vs malades
    c.execute("SELECT COUNT(*) FROM detections WHERE saine=1")
    stats["saines"] = c.fetchone()[0]
    stats["malades"] = stats["total"] - stats["saines"]

    # Top 5 maladies
    c.execute("""
        SELECT maladie, COUNT(*) as count
        FROM detections WHERE saine=0
        GROUP BY maladie
        ORDER BY count DESC LIMIT 5
    """)
    stats["top_maladies"] = c.fetchall()

    # Top 5 plantes
    c.execute("""
        SELECT plante, COUNT(*) as count
        FROM detections
        GROUP BY plante
        ORDER BY count DESC LIMIT 5
    """)
    stats["top_plantes"] = c.fetchall()

    # Détections par jour (7 derniers jours)
    c.execute("""
        SELECT date, COUNT(*) as count
        FROM detections
        GROUP BY date
        ORDER BY date DESC LIMIT 7
    """)
    stats["par_jour"] = c.fetchall()

    # Confiance moyenne
    c.execute("SELECT AVG(confiance) FROM detections")
    avg = c.fetchone()[0]
    stats["confiance_moyenne"] = round(avg, 3) if avg else 0

    conn.close()
    return stats