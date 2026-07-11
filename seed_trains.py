import sqlite3

conn = sqlite3.connect("database.db")
c = conn.cursor()

c.execute("""CREATE TABLE IF NOT EXISTS trains (
    train_no TEXT PRIMARY KEY,
    train_name TEXT,
    source TEXT,
    destination TEXT,
    departure TEXT,
    arrival TEXT,
    duration TEXT,
    distance TEXT,
    platform TEXT,
    current_location TEXT,
    status TEXT,
    eta TEXT
)""")

real_trains = [
    ("12693", "Pearl City Express", "Thirumangalam", "Madurai Junction",
     "06:10", "06:45", "0h 35m", "18 km", "PF 1",
     "TMM", "Running On Time", "MDU"),

    ("12631", "Nellai SF Express", "Madurai Junction", "Virudhunagar Junction",
     "05:15", "05:50", "0h 35m", "44 km", "PF 2",
     "MDU", "Running On Time", "VPT"),

    ("12635", "Vaigai SF Express", "Chennai Egmore", "Madurai Junction",
     "13:15", "20:35", "7h 20m", "497 km", "PF 3",
     "MAS", "Running On Time", "MDU"),

    ("12676", "Kovai Express", "Coimbatore Junction", "Chennai Central",
     "15:15", "23:00", "7h 45m", "496 km", "PF 4",
     "CBE", "Running On Time", "MAS"),
]

c.executemany(
    """INSERT OR REPLACE INTO trains
       (train_no, train_name, source, destination, departure, arrival,
        duration, distance, platform, current_location, status, eta)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
    real_trains,
)

conn.commit()

c.execute("SELECT train_no, train_name FROM trains")
print("Trains now in database:", c.fetchall())

conn.close()