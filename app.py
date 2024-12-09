from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
from models import init_db, create_player, get_all_players, get_player_by_id, update_player, delete_player

# Initialize the Flask app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['DATABASE'] = 'team.db'

# Ensure the uploads directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize the database
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
            create_player(name, surname, jersey_number, image_path)
        else:
            return "Invalid file type", 400

        return redirect(url_for('index'))
    return render_template('add_player.html')

@app.route('/delete/<int:player_id>')
def delete_player_route(player_id):
    delete_player(player_id)
    return redirect(url_for('index'))

@app.route('/update/<int:player_id>', methods=['GET', 'POST'])
def update_player_route(player_id):
    if request.method == 'POST':
        name = request.form['name']
        surname = request.form['surname']
        jersey_number = request.form['jersey_number']
        image = request.files['image']

        if image:
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
            image.save(image_path)
            update_player(player_id, name, surname, jersey_number, image_path)
        else:
            update_player(player_id, name, surname, jersey_number)

        return redirect(url_for('index'))

    player = get_player_by_id(player_id)
    return render_template('update_player.html', player=player)

@app.route('/homepage')
def homepage():
    return render_template('homepage.html')

@app.route('/team-management')
def team_management():
    players = get_all_players()
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
