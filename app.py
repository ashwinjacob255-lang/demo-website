import os
from datetime import datetime

from flask import Flask, jsonify, redirect, render_template, request
import psycopg2

app = Flask(__name__)


def get_database_url():
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL environment variable is not set.")

    # Some providers still expose postgres:// URLs, which psycopg2 accepts
    # more reliably after normalizing to postgresql://.
    if database_url.startswith("postgres://"):
        return database_url.replace("postgres://", "postgresql://", 1)
    return database_url


def get_connection():
    return psycopg2.connect(get_database_url())


def init_db():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS moods (
                    id SERIAL PRIMARY KEY,
                    mood TEXT NOT NULL,
                    note TEXT,
                    date TEXT NOT NULL
                )
                """
            )


init_db()


@app.route("/")
def index():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT mood, note, date FROM moods ORDER BY id DESC"
            )
            moods = cursor.fetchall()

    total_entries = len(moods)
    latest_mood = moods[0][0] if moods else "No moods logged yet"
    return render_template(
        "index.html",
        moods=moods,
        total_entries=total_entries,
        latest_mood=latest_mood,
    )


@app.route("/save", methods=["POST"])
def save():
    mood = request.form["mood"]
    note = request.form["note"]
    date = datetime.now().strftime("%Y-%m-%d %H:%M")

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO moods (mood, note, date) VALUES (%s, %s, %s)",
                (mood, note, date),
            )

    return redirect("/")


@app.route("/health")
def health():
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
        return jsonify({"status": "ok", "database": "connected"}), 200
    except Exception as exc:
        return jsonify({"status": "error", "database": "unavailable", "detail": str(exc)}), 503


if __name__ == "__main__":
    app.run(debug=True)
