import sqlite3

conn = sqlite3.connect("bookings.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    time TEXT,
    name TEXT,
    phone TEXT
)
""")
conn.commit()

def add_booking(date, time, name, phone):
    if hasattr(date, "strftime"):
        date = date.strftime("%Y-%m-%d")  # только дата
    cursor.execute("INSERT INTO bookings (date, time, name, phone) VALUES (?, ?, ?, ?)", (date, time, name, phone))
    conn.commit()



def get_booked_times(date):
    cursor.execute("SELECT time FROM bookings WHERE date = ?", (date,))
    return [row[0] for row in cursor.fetchall()]

def get_bookings_by_date(date):
    cursor.execute("SELECT time, name, phone FROM bookings WHERE date = ?", (date,))
    return cursor.fetchall()


def get_all_bookings():
    cursor.execute("SELECT date, time, name, phone FROM bookings")
    return cursor.fetchall()

def clear_bookings():
    cursor.execute("DELETE FROM bookings")
    conn.commit()