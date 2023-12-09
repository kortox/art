import sqlite3

conn = sqlite3.connect("data/frame_player")
cursor = conn.cursor()

cursor.execute(
"""
CREATE TABLE IF NOT EXISTS last_frame_played(
    directory TEXT NOT NULL PRIMARY KEY, 
    frame_file_name TEXT NOT NULL, 
    iso_datetime_played TEXT NOT NULL
)
""")
