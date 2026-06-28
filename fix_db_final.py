import sqlite3

conn = sqlite3.connect('db.sqlite3')
cur = conn.cursor()

cur.execute('DROP TABLE IF EXISTS events_registration')
cur.execute('CREATE TABLE "events_registration" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "name" varchar(100) NOT NULL, "email" varchar(254) NOT NULL, "check_in_id" char(32) NOT NULL UNIQUE, "registered_at" datetime NOT NULL, "attended" bool NOT NULL, "event_id" bigint NOT NULL REFERENCES "events_event" ("id") DEFERRABLE INITIALLY DEFERRED)')
cur.execute('CREATE UNIQUE INDEX "events_registration_event_id_email_bb6b6f27_uniq" ON "events_registration" ("event_id", "email")')
cur.execute('CREATE INDEX "events_registration_event_id_75b6f198" ON "events_registration" ("event_id")')

conn.commit()
