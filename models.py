import sqlite3
from flask import current_app

DATABASE = 'team.db'

def get_db():
    """Get a connection to the database."""
    conn = sqlite3.connect(current_app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database (create tables)."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS players (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        surname TEXT NOT NULL,
        jersey_number INTEGER NOT NULL,
        image_path TEXT NOT NULL)''')
    conn.commit()
    conn.close()

def create_player(name, surname, jersey_number, image_path):
    """Insert a new player into the database."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO players (name, surname, jersey_number, image_path)
    VALUES (?, ?, ?, ?)''', (name, surname, jersey_number, image_path))
    conn.commit()
    conn.close()

def get_all_players():
    """Get all players from the database."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM players')
    players = cursor.fetchall()
    conn.close()
    return players

def get_player_by_id(player_id):
    """Get a player by their ID."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM players WHERE id = ?', (player_id,))
    player = cursor.fetchone()
    conn.close()
    return player

def update_player(player_id, name, surname, jersey_number, image_path=None):
    """Update a player's details."""
    conn = get_db()
    cursor = conn.cursor()
    if image_path:
        cursor.execute('''
        UPDATE players SET name = ?, surname = ?, jersey_number = ?, image_path = ? WHERE id = ?''',
        (name, surname, jersey_number, image_path, player_id))
    else:
        cursor.execute('''
        UPDATE players SET name = ?, surname = ?, jersey_number = ? WHERE id = ?''',
        (name, surname, jersey_number, player_id))
    conn.commit()
    conn.close()

def delete_player(player_id):
    """Delete a player from the database."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM players WHERE id = ?', (player_id,))
    conn.commit()
    conn.close()
