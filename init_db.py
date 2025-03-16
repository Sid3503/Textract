import sqlite3

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('employees.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        employee_id TEXT NOT NULL,
        password TEXT NOT NULL,
        email TEXT NOT NULL
    )
''')

employees = [
    ('emp1', '001', 'pass123', 'emp1@example.com'),
    ('emp2', '002', 'pass456', 'emp2@example.com'),
    ('emp3', '003', 'pass789', 'emp3@example.com'),
    ('emp4', '004', 'pass012', 'emp4@example.com'),
    ('emp5', '005', 'pass345', 'emp5@example.com')
]

cursor.executemany('''
    INSERT INTO employees (username, employee_id, password, email)
    VALUES (?, ?, ?, ?)
''', employees)

conn.commit()
conn.close()

print("Database 'employees.db' created and populated with dummy data.")
