import sqlite3
import uuid

conn = sqlite3.connect('db.sqlite3')
cur = conn.cursor()

cur.execute('DELETE FROM events_registration')
cur.execute('ALTER TABLE events_registration ADD COLUMN name varchar(100) NOT NULL DEFAULT \"\"')
cur.execute('ALTER TABLE events_registration ADD COLUMN email varchar(254) NOT NULL DEFAULT \"\"')
cur.execute('ALTER TABLE events_registration ADD COLUMN check_in_id char(32) NOT NULL DEFAULT \"\"')
cur.execute('ALTER TABLE events_registration DROP COLUMN user_id')

conn.commit()
