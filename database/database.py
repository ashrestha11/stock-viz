import sqlite3

conn = sqlite3.connect('memes.db')

cursor = conn.cursor()
cursor.execute("CREATE TABLE reddit(id TEXT, symbol TEXT, title TEXT, timestamp DATETIME, upvotes INT, comments INT)")

