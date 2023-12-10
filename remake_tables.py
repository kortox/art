import sqlite3
import sys

conn = sqlite3.connect("data/frame_player")
cursor = conn.cursor()

answer = input(f"THIS WILL DELETE ALL DATA in last_frame_played\n\ttype yes to continue: ")

if answer != 'yes':
    print(f"Didn't receive yes, got {answer} aborting")
    sys.exit(1)

cursor.execute(
    """
DROP TABLE IF EXISTS last_frame_played
"""
)
print("Dropped table: last_frame_played")

cursor.execute(
"""
CREATE TABLE IF NOT EXISTS last_frame_played(
    directory TEXT NOT NULL PRIMARY KEY, 
    frame_file_name TEXT NOT NULL, 
    iso_datetime_played TEXT NOT NULL
)
""")
print("Created table: last_frame_played")
