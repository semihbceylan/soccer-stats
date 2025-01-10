from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)

# Where uploaded images go
app.config['UPLOAD_FOLDER'] = 'static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

DATABASE = 'team.db'

def init_db():
    """Initialize the DB (create tables if they don't exist)."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Teams table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS teams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_name TEXT NOT NULL
        )
    ''')

    # Players table (team_id must NOT be NULL if you never want a player without a team)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            surname TEXT NOT NULL,
            jersey_number INTEGER NOT NULL,
            image_path TEXT NOT NULL,
            team_id INTEGER NOT NULL,
            FOREIGN KEY(team_id) REFERENCES teams(id)
        )
    ''')

    conn.commit()
    conn.close()

# Call init_db() at start
init_db()

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    """Check if 'filename' has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


###############################################################################
#                           HELPER: DB Connection
###############################################################################
def get_db():
    """Return a SQLite connection (and you can then create a cursor)."""
    conn = sqlite3.connect(DATABASE)
    # Optional: row_factory for easier dict-like access
    conn.row_factory = sqlite3.Row
    return conn


###############################################################################
#                               HOMEPAGE
###############################################################################
@app.route('/')
def index():
    """Redirect the root URL to the homepage."""
    return redirect(url_for('homepage'))

@app.route('/homepage')
def homepage():
    return render_template('homepage.html')


###############################################################################
#                               TEAM ROUTES
###############################################################################
@app.route('/teams')
def list_teams():
    """Show all teams."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM teams ORDER BY id DESC")
    teams = cursor.fetchall()
    conn.close()

    return render_template('teams/list_teams.html', teams=teams)

@app.route('/teams/add', methods=['GET', 'POST'])
def add_team():
    """Create a new team."""
    if request.method == 'POST':
        team_name = request.form['team_name']

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO teams (team_name) VALUES (?)", (team_name,))
        conn.commit()
        conn.close()

        return redirect(url_for('list_teams'))

    return render_template('teams/add_team.html')

@app.route('/teams/<int:team_id>')
def team_detail(team_id):
    """Show one team's detail page (including all its players)."""
    conn = get_db()
    cursor = conn.cursor()

    # Fetch the team
    cursor.execute("SELECT * FROM teams WHERE id = ?", (team_id,))
    team = cursor.fetchone()
    if not team:
        conn.close()
        return "Team not found", 404

    # Fetch all players for this team
    cursor.execute("SELECT * FROM players WHERE team_id = ?", (team_id,))
    players = cursor.fetchall()

    conn.close()
    return render_template('teams/team_detail.html', team=team, players=players)

@app.route('/teams/<int:team_id>/update', methods=['GET', 'POST'])
def update_team(team_id):
    """Update a team's name."""
    conn = get_db()
    cursor = conn.cursor()

    # Ensure the team exists
    cursor.execute("SELECT * FROM teams WHERE id = ?", (team_id,))
    team = cursor.fetchone()
    if not team:
        conn.close()
        return "Team not found", 404

    if request.method == 'POST':
        new_name = request.form['team_name']
        cursor.execute("UPDATE teams SET team_name = ? WHERE id = ?", (new_name, team_id))
        conn.commit()
        conn.close()
        return redirect(url_for('list_teams'))

    conn.close()
    return render_template('teams/update_team.html', team=team)

@app.route('/teams/<int:team_id>/delete')
def delete_team(team_id):
    """Delete a team (and optionally its players)."""
    conn = get_db()
    cursor = conn.cursor()

    # If you want to also delete the players from this team:
    # cursor.execute("DELETE FROM players WHERE team_id = ?", (team_id,))
    # But be careful if you want to preserve them somewhere else.

    cursor.execute("DELETE FROM teams WHERE id = ?", (team_id,))
    conn.commit()
    conn.close()

    return redirect(url_for('list_teams'))


###############################################################################
#                               PLAYER ROUTES
###############################################################################
@app.route('/players/add', methods=['GET', 'POST'])
def add_player():
    conn = get_db()
    cursor = conn.cursor()

    # Capture team_id from the query string
    team_id = request.args.get('team_id')

    if request.method == 'POST':
        name = request.form['name']
        surname = request.form['surname']
        jersey_number = request.form['jersey_number']
        team_id = request.form.get('team_id')  # team_id from the form

        # Ensure team_id exists
        if not team_id:
            conn.close()
            return "Error: You must select a team.", 400

        image = request.files.get('image')
        if image and allowed_file(image.filename):
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
            image.save(image_path)
            image_path = image_path.replace('\\', '/')
        else:
            image_path = 'uploads/default_player.jpg'

        # Insert the player
        cursor.execute("""
            INSERT INTO players (name, surname, jersey_number, image_path, team_id)
            VALUES (?, ?, ?, ?, ?)
        """, (name, surname, jersey_number, image_path, team_id))
        conn.commit()
        conn.close()

        return redirect(url_for('team_detail', team_id=team_id))

    # GET request: fetch teams for the dropdown
    cursor.execute("SELECT * FROM teams")
    teams = cursor.fetchall()
    conn.close()

    return render_template('players/add_player.html', teams=teams)


@app.route('/players/<int:player_id>/update', methods=['GET', 'POST'])
def update_player(player_id):
    """
    Update a player's data. Possibly change the team or image.
    """
    conn = get_db()
    cursor = conn.cursor()

    # Fetch existing player
    cursor.execute("SELECT * FROM players WHERE id = ?", (player_id,))
    player = cursor.fetchone()
    if not player:
        conn.close()
        return "Player not found", 404

    if request.method == 'POST':
        name = request.form['name']
        surname = request.form['surname']
        jersey_number = request.form['jersey_number']
        new_team_id = request.form.get('team_id')
        if not new_team_id:
            conn.close()
            return "Error: Must select a team.", 400

        image = request.files.get('image')
        if image and allowed_file(image.filename):
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename).replace('\\', '/')
            image.save(image_path)
            cursor.execute("""
                UPDATE players
                SET name = ?, surname = ?, jersey_number = ?, image_path = ?, team_id = ?
                WHERE id = ?
            """, (name, surname, jersey_number, image_path, new_team_id, player_id))
        else:
            # keep old image
            cursor.execute("""
                UPDATE players
                SET name = ?, surname = ?, jersey_number = ?, team_id = ?
                WHERE id = ?
            """, (name, surname, jersey_number, new_team_id, player_id))

        conn.commit()
        conn.close()
        return redirect(url_for('team_detail', team_id=new_team_id))

    # GET: show form
    # Also fetch all teams for dropdown
    cursor.execute("SELECT * FROM teams")
    all_teams = cursor.fetchall()

    conn.close()
    return render_template('players/update_player.html', player=player, all_teams=all_teams)


@app.route('/players/<int:player_id>/delete')
def delete_player(player_id):
    """Delete a player, then redirect to that player's old team page."""
    conn = get_db()
    cursor = conn.cursor()

    # Need the team_id to redirect back
    cursor.execute("SELECT team_id FROM players WHERE id = ?", (player_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return "Player not found", 404
    team_id = row['team_id']

    cursor.execute("DELETE FROM players WHERE id = ?", (player_id,))
    conn.commit()
    conn.close()

    return redirect(url_for('team_detail', team_id=team_id))


###############################################################################
#                          MATCH / STATISTICS ROUTES (Optional)
###############################################################################


###############################################################################
#                       MATCH CREATION AND TRACKING
###############################################################################

@app.route('/start-match', methods=['GET', 'POST'])
def start_match():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Retrieve teams for dropdown
    cursor.execute("SELECT id, team_name FROM teams")
    all_teams = cursor.fetchall()
    conn.close()

    if request.method == 'POST':
        team_1_id = request.form['team_1_id']
        team_2_id = request.form['team_2_id']
        duration = request.form['duration']

        # Save the match info
        start_time = datetime.now().isoformat(timespec='seconds')

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO matches (team_1_id, team_2_id, start_time, duration)
            VALUES (?, ?, ?, ?)
        """, (team_1_id, team_2_id, start_time, duration))
        match_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return redirect(url_for('track_match', match_id=match_id))

    return render_template('match_tracking/start_match.html', teams=all_teams)

@app.route('/track-match/<int:match_id>', methods=['GET', 'POST'])
def track_match(match_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Get match details
    cursor.execute("""
        SELECT m.id, t1.team_name, t2.team_name, m.start_time, m.duration
        FROM matches m
        JOIN teams t1 ON m.team_1_id = t1.id
        JOIN teams t2 ON m.team_2_id = t2.id
        WHERE m.id = ?
    """, (match_id,))
    match = cursor.fetchone()

    if not match:
        conn.close()
        return "Match not found", 404

    match_id, team_1_name, team_2_name, start_time, duration = match

    # Get players for the two teams
    # For demonstration, we’ll assume the user can select any player from the entire list 
    # or you could store relationships between players and teams for a real scenario.
    cursor.execute("SELECT * FROM players")
    players = cursor.fetchall()

    # If an event is submitted
    if request.method == 'POST':
        event_type = request.form['event_type']
        team_id = request.form['team_id']
        player_id = request.form['player_id']  # Might be empty if the event doesn't involve a particular player
        event_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        if not player_id:
            player_id = None

        # Insert event into database
        cursor.execute("""
            INSERT INTO match_events (match_id, team_id, player_id, event_type, event_time)
            VALUES (?, ?, ?, ?, ?)
        """, (match_id, team_id, player_id, event_type, event_time))
        conn.commit()

        return redirect(url_for('track_match', match_id=match_id))

    # Retrieve all teams for event logging
    cursor.execute("SELECT id, team_name FROM teams")
    all_teams = cursor.fetchall()

    # Retrieve events for this match
    cursor.execute("""
        SELECT me.event_type, me.event_time, 
               (SELECT team_name FROM teams WHERE id = me.team_id),
               (SELECT name || ' ' || surname FROM players WHERE id = me.player_id)
        FROM match_events me
        WHERE me.match_id = ?
        ORDER BY me.event_time ASC
    """, (match_id,))
    events = cursor.fetchall()

    conn.close()
    return render_template('match_tracking/track_match.html',
                           match_id=match_id,
                           team_1_name=team_1_name,
                           team_2_name=team_2_name,
                           start_time=start_time,
                           duration=duration,
                           players=players,
                           all_teams=all_teams,
                           events=events)

###############################################################################
#                       MATCH STATISTICS
###############################################################################

@app.route('/match-statistics')
def match_statistics():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Get the list of all matches with team names
    cursor.execute("""
        SELECT m.id, t1.team_name, t2.team_name, m.start_time, m.duration
        FROM matches m
        JOIN teams t1 ON m.team_1_id = t1.id
        JOIN teams t2 ON m.team_2_id = t2.id
        ORDER BY m.id DESC
    """)
    matches = cursor.fetchall()
    conn.close()
    return render_template('match_statistics/statistics.html', matches=matches)

@app.route('/view-match/<int:match_id>')
def view_match(match_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Get basic match info
    cursor.execute("""
        SELECT m.id, t1.team_name, t2.team_name, m.start_time, m.duration
        FROM matches m
        JOIN teams t1 ON m.team_1_id = t1.id
        JOIN teams t2 ON m.team_2_id = t2.id
        WHERE m.id = ?
    """, (match_id,))
    match = cursor.fetchone()

    if not match:
        conn.close()
        return "Match not found", 404

    match_id, team_1_name, team_2_name, start_time, duration = match

    # Retrieve events
    cursor.execute("""
        SELECT me.event_type, me.event_time,
               (SELECT team_name FROM teams WHERE id = me.team_id),
               (SELECT name || ' ' || surname FROM players WHERE id = me.player_id)
        FROM match_events me
        WHERE me.match_id = ?
        ORDER BY me.event_time ASC
    """, (match_id,))
    events = cursor.fetchall()

    conn.close()
    return render_template('match_statistics/view_match.html',
                           match_id=match_id,
                           team_1_name=team_1_name,
                           team_2_name=team_2_name,
                           start_time=start_time,
                           duration=duration,
                           events=events)


###############################################################################
#                      SERVE UPLOADED FILES
###############################################################################
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded images from the static/uploads folder."""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


###############################################################################
#                              RUN THE APP
###############################################################################
if __name__ == '__main__':
    app.run(debug=True)
