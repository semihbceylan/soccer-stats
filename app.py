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
    # Create teams table
    cursor.execute('''CREATE TABLE IF NOT EXISTS teams (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL UNIQUE)''')
    # Create players table
    cursor.execute('''CREATE TABLE IF NOT EXISTS players (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        surname TEXT NOT NULL,
                        jersey_number INTEGER NOT NULL,
                        team_id INTEGER NOT NULL,
                        image_path TEXT NOT NULL,
                        FOREIGN KEY (team_id) REFERENCES teams (id))''')
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
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM teams")
    teams = cursor.fetchall()  # Fetch all available teams
    conn.close()

    if request.method == 'POST':
        name = request.form['name']
        surname = request.form['surname']
        jersey_number = request.form['jersey_number']
        team_id = request.form['team_id']
        image = request.files.get('image')

        if image and allowed_file(image.filename):
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
            image.save(image_path)
            image_path = image_path.replace('\\', '/')  # Ensure forward slashes
        else:
            image_path = 'uploads/default_player.jpg'

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO players (name, surname, jersey_number, team_id, image_path) VALUES (?, ?, ?, ?, ?)",
            (name, surname, jersey_number, team_id, image_path))
        conn.commit()
        conn.close()

        return redirect(url_for('team_management'))

    return render_template('team_management/add_player.html', teams=teams)

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
        image = request.files.get('image')

        if image:
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename).replace('\\', '/')
            image.save(image_path)
            cursor.execute("UPDATE players SET name = ?, surname = ?, jersey_number = ?, image_path = ? WHERE id = ?",
                           (name, surname, jersey_number, image_path, player_id))
        else:
            cursor.execute("UPDATE players SET name = ?, surname = ?, jersey_number = ? WHERE id = ?",
                           (name, surname, jersey_number, player_id))

        conn.commit()
        conn.close()
        return redirect(url_for('team_management'))

    cursor.execute("SELECT * FROM players WHERE id = ?", (player_id,))
    player = cursor.fetchone()
    conn.close()
    return render_template('team_management/update_player.html', player=player)

@app.route('/add-team', methods=['GET', 'POST'])
def add_team():
    if request.method == 'POST':
        team_name = request.form['team_name']
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO teams (name) VALUES (?)", (team_name,))
            conn.commit()
        except sqlite3.IntegrityError:
            return "Team already exists!"
        finally:
            conn.close()
        return redirect(url_for('team_management'))
    return render_template('team_management/add_team.html')

@app.route('/homepage')
def homepage():
    return render_template('homepage.html')

@app.route('/team-management')
def team_management():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Fetch teams and their players
    cursor.execute("""
        SELECT teams.name AS team_name, players.id, players.name, players.surname, players.jersey_number, players.image_path
        FROM players
        INNER JOIN teams ON players.team_id = teams.id
        ORDER BY teams.name, players.jersey_number
    """)
    data = cursor.fetchall()

    # Group players by team
    teams = {}
    for row in data:
        team_name = row[0]
        player = {
            'id': row[1],
            'name': row[2],
            'surname': row[3],
            'jersey_number': row[4],
            'image_path': row[5]
        }
        if team_name not in teams:
            teams[team_name] = []
        teams[team_name].append(player)

    conn.close()
    return render_template('team_management/index.html', teams=teams)

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
