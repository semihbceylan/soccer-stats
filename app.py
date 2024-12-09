from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import sqlite3
import os

# Initialize the Flask app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Ensure the uploads directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Database setup
DATABASE = 'team.db'

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS players (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        surname TEXT NOT NULL,
                        jersey_number INTEGER NOT NULL,
                        image_path TEXT NOT NULL)''')
    conn.commit()
    conn.close()

init_db()

# Helper function to validate file type
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Routes
@app.route('/')
def index():
    return redirect(url_for('homepage'))

@app.route('/add', methods=['GET', 'POST'])
def add_player():
    if request.method == 'POST':
        name = request.form['name']
        surname = request.form['surname']
        jersey_number = request.form['jersey_number']
        image = request.files['image']

        if image and allowed_file(image.filename):
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
            image.save(image_path)
        else:
            return "Invalid file type", 400

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO players (name, surname, jersey_number, image_path) VALUES (?, ?, ?, ?)",
                       (name, surname, jersey_number, image_path))
        conn.commit()
        conn.close()

        return redirect(url_for('index'))
    return render_template('add_player.html')

@app.route('/delete/<int:player_id>')
def delete_player(player_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM players WHERE id = ?", (player_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/update/<int:player_id>', methods=['GET', 'POST'])
def update_player(player_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        surname = request.form['surname']
        jersey_number = request.form['jersey_number']
        image = request.files['image']

        if image:
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
            image.save(image_path)
            cursor.execute("UPDATE players SET name = ?, surname = ?, jersey_number = ?, image_path = ? WHERE id = ?",
                           (name, surname, jersey_number, image_path, player_id))
        else:
            cursor.execute("UPDATE players SET name = ?, surname = ?, jersey_number = ? WHERE id = ?",
                           (name, surname, jersey_number, player_id))

        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    cursor.execute("SELECT * FROM players WHERE id = ?", (player_id,))
    player = cursor.fetchone()
    conn.close()
    return render_template('update_player.html', player=player)

@app.route('/homepage')
def homepage():
    return render_template('homepage.html')

@app.route('/team-management')
def team_management():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM players")
    players = cursor.fetchall()
    conn.close()
    return render_template('team_management/index.html', players=players)

@app.route('/track-match')
def track_match():
    return render_template('match_tracking/track_match.html')

@app.route('/match-statistics')
def match_statistics():
    return render_template('match_statistics/statistics.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
