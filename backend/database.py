import sqlite3
import json

DB_PATH ="marathi.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.executescript("""

        CREATE TABLE IF NOT EXISTS sheets (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            filename    TEXT NOT NULL,
            columns     TEXT NOT NULL,
            uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS records (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            sheet_id    INTEGER REFERENCES sheets(id),
            data        TEXT NOT NULL,
            search_text TEXT NOT NULL
        );

        CREATE VIRTUAL TABLE IF NOT EXISTS records_fts
        USING fts5(
            search_text,
            content='records',
            content_rowid='id',
            tokenize='unicode61'
        );

        CREATE TRIGGER IF NOT EXISTS records_ai
        AFTER INSERT ON records BEGIN
            INSERT INTO records_fts(rowid, search_text)
            VALUES (new.id, new.search_text);
        END;

    """)

    conn.commit()
    conn.close()