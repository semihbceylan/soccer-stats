from flask import Flask, render_template, request, jsonify, redirect, url_for
import sqlite3

app = Flask(__name__)
DATABASE = 'team.db'

# Fetch teams for selection
@app.route('/select-teams', methods=['GET'])
def select_teams():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM teams")
    teams = cursor.fetchall()
    conn.close()
    return render_template('match_track/select_teams.html', teams=teams)

# Show players from selected teams
@app.route('/view-players', methods=['POST'])
def view_players():
    team_1_id = request.form['team_1']
    team_2_id = request.form['team_2']

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Fetch team names
    cursor.execute("SELECT name FROM teams WHERE id = ?", (team_1_id,))
    team_1_name = cursor.fetchone()[0]

    cursor.execute("SELECT name FROM teams WHERE id = ?", (team_2_id,))
    team_2_name = cursor.fetchone()[0]

    # Fetch players
    cursor.execute("SELECT * FROM players WHERE team_id = ?", (team_1_id,))
    team_1_players = cursor.fetchall()

    cursor.execute("SELECT * FROM players WHERE team_id = ?", (team_2_id,))
    team_2_players = cursor.fetchall()

    # Insert a new match
    cursor.execute(
        "INSERT INTO matches (team_1_id, team_2_id) VALUES (?, ?)",
        (team_1_id, team_2_id)
    )
    match_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return render_template(
        'match_track/view_players.html',
        team_1={"id": team_1_id, "name": team_1_name, "players": team_1_players},
        team_2={"id": team_2_id, "name": team_2_name, "players": team_2_players},
        match_id=match_id
    )

# Handle player actions
@app.route('/log-action', methods=['POST'])
def log_action():
    data = request.json
    player_id = data['player_id']
    action = data['action']
    timestamp = data['timestamp']
    match_id = data['match_id']

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Fetch the player's team
    cursor.execute("SELECT team_id FROM players WHERE id = ?", (player_id,))
    team_id = cursor.fetchone()[0]

    # Update player stats
    cursor.execute(f"UPDATE players SET {action} = {action} + 1 WHERE id = ?", (player_id,))

    # Update match stats
    team_column_prefix = "team_1" if team_id == get_team_id(cursor, match_id, "team_1_id") else "team_2"
    if action in ['goals', 'shots', 'passes', 'assists', 'dribbles', 'offsides', 'fouls', 'yellow_cards', 'red_cards', 'goal_conceded', 'penalties']:
        column_to_update = f"{team_column_prefix}_{action}"
        cursor.execute(f"UPDATE matches SET {column_to_update} = {column_to_update} + 1 WHERE id = ?", (match_id,))

    conn.commit()
    conn.close()

    return jsonify({"status": "success", "message": f"Action '{action}' logged for player {player_id} at {timestamp}."})

def get_team_id(cursor, match_id, column):
    cursor.execute(f"SELECT {column} FROM matches WHERE id = ?", (match_id,))
    return cursor.fetchone()[0]

@app.route('/end-match', methods=['POST'])
def end_match():
    data = request.json
    match_id = data['match_id']

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Fetch match stats
    cursor.execute('''
        SELECT team_1_id, team_2_id, team_1_goals, team_2_goals, team_1_shots, team_2_shots,
               team_1_passes, team_2_passes, team_1_yellow_cards, team_2_yellow_cards,
               team_1_red_cards, team_2_red_cards, total_actions
        FROM matches WHERE id = ?
    ''', (match_id,))
    match_stats = cursor.fetchone()

    # Fetch team names
    cursor.execute("SELECT name FROM teams WHERE id = ?", (match_stats[0],))
    team_1_name = cursor.fetchone()[0]

    cursor.execute("SELECT name FROM teams WHERE id = ?", (match_stats[1],))
    team_2_name = cursor.fetchone()[0]

    conn.close()

    stats = {
        "team_1": {
            "name": team_1_name,
            "goals": match_stats[2],
            "shots": match_stats[4],
            "passes": match_stats[6],
            "yellow_cards": match_stats[8],
            "red_cards": match_stats[10],
        },
        "team_2": {
            "name": team_2_name,
            "goals": match_stats[3],
            "shots": match_stats[5],
            "passes": match_stats[7],
            "yellow_cards": match_stats[9],
            "red_cards": match_stats[11],
        },
        "total_actions": match_stats[12]
    }

    return jsonify(stats)


@app.route('/')
def home():
    return "Flask is running!"

if __name__ == '__main__':
    app.run(debug=True)