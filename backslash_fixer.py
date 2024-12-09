import sqlite3

# Connect to the database
conn = sqlite3.connect('team.db')
cursor = conn.cursor()

# Update paths in the database
cursor.execute("SELECT id, image_path FROM players")
for row in cursor.fetchall():
    corrected_path = row[1].replace("\\", "/")  # Fix backslashes
    cursor.execute("UPDATE players SET image_path = ? WHERE id = ?", (corrected_path, row[0]))

conn.commit()
conn.close()