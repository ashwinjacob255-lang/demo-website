from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime

app = Flask(__name__)

# ---------- Database setup ----------
def init_db():
    conn = sqlite3.connect('database.db')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS moods (
            id   INTEGER PRIMARY KEY AUTOINCREMENT,
            mood TEXT,
            note TEXT,
            date TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# ---------- Routes ----------

# GET / → show the page with all saved moods
@app.route('/')
def index():
    conn = sqlite3.connect('database.db')
    moods = conn.execute(
        'SELECT mood, note, date FROM moods ORDER BY id DESC'
    ).fetchall()
    conn.close()
    total_entries = len(moods)
    latest_mood = moods[0][0] if moods else 'No moods logged yet'
    return render_template(
        'index.html',
        moods=moods,
        total_entries=total_entries,
        latest_mood=latest_mood
    )

# POST /save → save mood and note, then redirect back
@app.route('/save', methods=['POST'])
def save():
    mood = request.form['mood']
    note = request.form['note']
    date = datetime.now().strftime('%Y-%m-%d %H:%M')

    conn = sqlite3.connect('database.db')
    conn.execute(
        'INSERT INTO moods (mood, note, date) VALUES (?, ?, ?)',
        (mood, note, date)
    )
    conn.commit()
    conn.close()

    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
