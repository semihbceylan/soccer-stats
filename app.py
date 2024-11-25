from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

# Initialize the Flask app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

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

# Routes
@app.route('/')
def index():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM players")
    players = cursor.fetchall()
    conn.close()
    return render_template('index.html', players=players)

@app.route('/add', methods=['GET', 'POST'])
def add_player():
    if request.method == 'POST':
        name = request.form['name']
        surname = request.form['surname']
        jersey_number = request.form['jersey_number']
        image = request.files['image']

        # Save the image
        if image:
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
            image.save(image_path)
        else:
            image_path = ""

        # Add to the database
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

        # Update image only if a new one is uploaded
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

if __name__ == '__main__':
    app.run(debug=True)
