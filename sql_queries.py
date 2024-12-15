import sqlite3

# Database file name
DATABASE = 'team.db'

# Function to initialize tables
def initialize_database():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Create teams table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS teams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    ''')

    # Create players table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            surname TEXT NOT NULL,
            jersey_number INTEGER NOT NULL,
            team_id INTEGER NOT NULL,
            image_path TEXT DEFAULT 'uploads/default_player.jpg',
            shots INTEGER DEFAULT 0,
            goals INTEGER DEFAULT 0,
            passes INTEGER DEFAULT 0,
            assists INTEGER DEFAULT 0,
            dribbles INTEGER DEFAULT 0,
            offsides INTEGER DEFAULT 0,
            fouls INTEGER DEFAULT 0,
            yellow_cards INTEGER DEFAULT 0,
            red_cards INTEGER DEFAULT 0,
            goals_conceded INTEGER DEFAULT 0,
            penalties INTEGER DEFAULT 0,
            FOREIGN KEY (team_id) REFERENCES teams (id)
        )
    ''')

    # Create matches table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_1_id INTEGER NOT NULL,
            team_2_id INTEGER NOT NULL,
            team_1_goals INTEGER DEFAULT 0,
            team_2_goals INTEGER DEFAULT 0,
            team_1_shots INTEGER DEFAULT 0,
            team_2_shots INTEGER DEFAULT 0,
            team_1_passes INTEGER DEFAULT 0,
            team_2_passes INTEGER DEFAULT 0,
            team_1_assists INTEGER DEFAULT 0,
            team_2_assists INTEGER DEFAULT 0,
            team_1_dribbles INTEGER DEFAULT 0,
            team_2_dribbles INTEGER DEFAULT 0,
            team_1_offsides INTEGER DEFAULT 0,
            team_2_offsides INTEGER DEFAULT 0,
            team_1_fouls INTEGER DEFAULT 0,
            team_2_fouls INTEGER DEFAULT 0,
            team_1_yellow_cards INTEGER DEFAULT 0,
            team_2_yellow_cards INTEGER DEFAULT 0,
            team_1_red_cards INTEGER DEFAULT 0,
            team_2_red_cards INTEGER DEFAULT 0,
            team_1_goals_conceded INTEGER DEFAULT 0,
            team_2_goals_conceded INTEGER DEFAULT 0,
            team_1_penalties INTEGER DEFAULT 0,
            team_2_penalties INTEGER DEFAULT 0,
            total_actions INTEGER DEFAULT 0,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()
    print("Database initialized successfully!")

def delete_table():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS players')
    conn.commit()
    conn.close()
    print("Tables deleted successfully!")

# Run the function to initialize the database
if __name__ == '__main__':
    initialize_database()
    #delete_table()
