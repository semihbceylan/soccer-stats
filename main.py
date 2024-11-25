import sqlite3
from tkinter import Tk, Label, Entry, Button, Listbox, Scrollbar, END, Toplevel, messagebox

# Database setup
conn = sqlite3.connect("football_stats.db")
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS players (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    scores INTEGER,
                    fouls INTEGER,
                    offsides INTEGER,
                    substitutions INTEGER)''')
conn.commit()


# Add new player
def add_player():
    name = entry_name.get()
    scores = entry_scores.get()
    fouls = entry_fouls.get()
    offsides = entry_offsides.get()
    substitutions = entry_subs.get()

    if name and scores.isdigit() and fouls.isdigit() and offsides.isdigit() and substitutions.isdigit():
        cursor.execute("INSERT INTO players (name, scores, fouls, offsides, substitutions) VALUES (?, ?, ?, ?, ?)",
                       (name, scores, fouls, offsides, substitutions))
        conn.commit()
        entry_name.delete(0, END)
        entry_scores.delete(0, END)
        entry_fouls.delete(0, END)
        entry_offsides.delete(0, END)
        entry_subs.delete(0, END)
        refresh_list()
    else:
        messagebox.showerror("Input Error", "Please enter valid data for all fields.")


# Refresh the player list
def refresh_list():
    listbox_players.delete(0, END)
    cursor.execute("SELECT * FROM players")
    for row in cursor.fetchall():
        listbox_players.insert(END, f"{row[0]}: {row[1]} - Scores: {row[2]}, Fouls: {row[3]}, Offsides: {row[4]}, Subs: {row[5]}")


# Delete selected player
def delete_player():
    selected = listbox_players.curselection()
    if selected:
        player_id = listbox_players.get(selected[0]).split(":")[0]
        cursor.execute("DELETE FROM players WHERE id = ?", (player_id,))
        conn.commit()
        refresh_list()
    else:
        messagebox.showwarning("Selection Error", "Please select a player to delete.")


# Update player data
def update_player():
    selected = listbox_players.curselection()
    if selected:
        player_id = listbox_players.get(selected[0]).split(":")[0]
        edit_window = Toplevel(root)
        edit_window.title("Update Player Data")

        Label(edit_window, text="Scores:").grid(row=0, column=0)
        Label(edit_window, text="Fouls:").grid(row=1, column=0)
        Label(edit_window, text="Offsides:").grid(row=2, column=0)
        Label(edit_window, text="Substitutions:").grid(row=3, column=0)

        entry_scores_edit = Entry(edit_window)
        entry_fouls_edit = Entry(edit_window)
        entry_offsides_edit = Entry(edit_window)
        entry_subs_edit = Entry(edit_window)

        entry_scores_edit.grid(row=0, column=1)
        entry_fouls_edit.grid(row=1, column=1)
        entry_offsides_edit.grid(row=2, column=1)
        entry_subs_edit.grid(row=3, column=1)

        def save_update():
            scores = entry_scores_edit.get()
            fouls = entry_fouls_edit.get()
            offsides = entry_offsides_edit.get()
            substitutions = entry_subs_edit.get()

            if scores.isdigit() and fouls.isdigit() and offsides.isdigit() and substitutions.isdigit():
                cursor.execute("UPDATE players SET scores = ?, fouls = ?, offsides = ?, substitutions = ? WHERE id = ?",
                               (scores, fouls, offsides, substitutions, player_id))
                conn.commit()
                edit_window.destroy()
                refresh_list()
            else:
                messagebox.showerror("Input Error", "Please enter valid numbers for all fields.")

        Button(edit_window, text="Save", command=save_update).grid(row=4, columnspan=2)

    else:
        messagebox.showwarning("Selection Error", "Please select a player to update.")


# GUI setup
root = Tk()
root.title("Football Player Stats")

Label(root, text="Name:").grid(row=0, column=0)
entry_name = Entry(root)
entry_name.grid(row=0, column=1)

Label(root, text="Scores:").grid(row=1, column=0)
entry_scores = Entry(root)
entry_scores.grid(row=1, column=1)

Label(root, text="Fouls:").grid(row=2, column=0)
entry_fouls = Entry(root)
entry_fouls.grid(row=2, column=1)

Label(root, text="Offsides:").grid(row=3, column=0)
entry_offsides = Entry(root)
entry_offsides.grid(row=3, column=1)

Label(root, text="Substitutions:").grid(row=4, column=0)
entry_subs = Entry(root)
entry_subs.grid(row=4, column=1)

Button(root, text="Add Player", command=add_player).grid(row=5, column=0, columnspan=2)

listbox_players = Listbox(root, width=60)
listbox_players.grid(row=6, column=0, columnspan=2)

scrollbar = Scrollbar(root, orient="vertical", command=listbox_players.yview)
scrollbar.grid(row=6, column=2, sticky="ns")
listbox_players.config(yscrollcommand=scrollbar.set)

Button(root, text="Delete Player", command=delete_player).grid(row=7, column=0)
Button(root, text="Update Player", command=update_player).grid(row=7, column=1)

refresh_list()
root.mainloop()
