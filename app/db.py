import os
import sqlite3
from flask import current_app


def get_db():
    db_path = current_app.config["DATABASE"]
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    db = get_db()

    db.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT DEFAULT 'member'
    );

    CREATE TABLE IF NOT EXISTS companies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        expected_amount REAL DEFAULT 0,
        weekly INTEGER DEFAULT 0,
        weekday INTEGER DEFAULT 0,
        active INTEGER DEFAULT 1
    );

    CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_id INTEGER,
        payment_date TEXT NOT NULL,
        expected REAL DEFAULT 0,
        paid REAL DEFAULT 0,
        note TEXT,
        FOREIGN KEY(company_id) REFERENCES companies(id)
    );

    CREATE TABLE IF NOT EXISTS settings (
        id INTEGER PRIMARY KEY CHECK (id = 1),
        business_name TEXT DEFAULT 'Payment Manager',
        report_title TEXT DEFAULT 'Payment Report',
        phone TEXT DEFAULT '',
        footer TEXT DEFAULT 'Software Developed by Arslan.Ak | Contact: 03200199895'
    );
    """)

    db.execute(
        "INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)",
        ("admin", "admin123", "admin")
    )

    db.execute(
        "INSERT OR IGNORE INTO settings (id) VALUES (1)"
    )

    db.commit()
    db.close()
