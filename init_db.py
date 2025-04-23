import sqlite3
from datetime import datetime, timedelta

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('employees.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        employee_id TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS otp_verification (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL,
        otp TEXT NOT NULL,
        expires_at TIMESTAMP NOT NULL,
        FOREIGN KEY (email) REFERENCES employees(email)
    )
''')

# Removed the is_verified field (the 5th element) from each tuple
employees = [
    ('emp1', '001', 'pass123', 'emp1@example.com'),
    ('emp2', '002', 'pass456', 'emp2@example.com'),
    ('emp3', '003', 'pass789', 'emp3@example.com'),
    ('emp4', '004', 'pass012', 'emp4@example.com')
]

cursor.executemany('''
    INSERT OR IGNORE INTO employees (username, employee_id, password, email)
    VALUES (?, ?, ?, ?)
''', employees)

conn.commit()
conn.close()

print("Database 'employees.db' created and populated with dummy data.")
