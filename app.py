from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = "trainpulse_secret_key"
DB = "database.db"

def init_db():
    conn = sqlite3.connect(DB)
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

    c.execute("""CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        train_no TEXT,
        train_name TEXT,
        destination TEXT,
        eta TEXT,
        status TEXT,
        duration_distance TEXT
    )""")

    # Ensure sample trains exist in the database
    trains = [
        ("12694", "Pearl City Express", "Thirumangalam", "Madurai Junction",
         "03:10", "03:27", "17 mins", "18 km", "PF 2",
         "Tirupparankundram", "Running On Time", "8 Mins"),
        ("12649", "Cheran Express", "Chennai Egmore", "Madurai Junction",
         "04:00", "08:20", "4h 20m", "497 km", "PF 7",
         "Dindigul", "Running On Time", "50 Mins"),
        ("16237", "Tuticorin Express", "Tirunelveli", "Madurai Junction",
         "02:30", "05:15", "2h 45m", "204 km", "PF 5",
         "Virudhunagar", "Running On Time", "40 Mins"),
        ("16724", "Anantapuri Express", "Kanyakumari", "Madurai Junction",
         "01:20", "05:35", "4h 15m", "248 km", "PF 6",
         "Vilakudi", "Delayed 10 mins", "65 Mins"),
        ("56701", "Punalur Passenger", "Kollam", "Madurai Junction",
         "01:55", "04:10", "2h 15m", "165 km", "PF 2",
         "Kallupatti", "Running On Time", "20 Mins"),
    ]
    c.executemany("INSERT OR REPLACE INTO trains VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", trains)

    c.execute("SELECT COUNT(*) FROM history")
    if c.fetchone()[0] == 0:
        history = [
            ("12694", "Pearl City Express", "Madurai Junction", "8 Mins", "Running On Time", "17 mins . 18 km"),
            ("16237", "Tuticorin Express", "Madurai Junction", "12 Mins", "Running On Time", "20 mins . 18 km"),
            ("16724", "Anantapuri Express", "Madurai Junction", "30 Mins", "Delayed 10 mins", "20 mins . 18 km"),
            ("56701", "Punalur Passenger", "Madurai Junction", "15 Mins", "Running On Time", "23 mins . 18 km"),
        ]
        c.executemany("INSERT INTO history (train_no, train_name, destination, eta, status, duration_distance) VALUES (?,?,?,?,?,?)", history)

    conn.commit()
    conn.close()


@app.route("/", methods=["GET"])
def index():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT train_no, train_name FROM trains")
    available = c.fetchall()
    conn.close()
    return render_template("index.html", available_trains=available, error=None, username=session.get("username"))


@app.route("/verify", methods=["GET", "POST"])
def verify():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    if request.method == "POST":
        train_no = request.form["train_no"]
        departure = request.form["departure"]
        destination = request.form["destination"]
    else:
        train_no = request.args.get("train_no")
        departure = request.args.get("departure")
        destination = request.args.get("destination")

    return render_template("verify.html",
                            train_no=train_no,
                            departure=departure,
                            destination=destination)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        session.pop("logged_in", None)
        session.pop("username", None)
        return render_template("login.html", error=None)

    error = None
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()
    normalized = username.lower()
    if (normalized in ["admin", "aarthee"] and password == "admin") or (normalized == "aarthee" and password == "eeswari"):
        session["logged_in"] = True
        session["username"] = username
        return redirect(url_for("index"))
    error = "Invalid username or password. Try admin/admin or aarthee/eeswari."

    return render_template("login.html", error=error)


@app.route("/logout", methods=["GET"])
def logout():
    session.pop("logged_in", None)
    session.pop("username", None)
    return redirect(url_for("login"))


@app.route("/dashboard", methods=["GET"])
def dashboard():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    train_no = request.args.get("train_no")
    departure = request.args.get("departure")
    destination = request.args.get("destination")

    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT * FROM trains WHERE train_no=?", (train_no,))
    train = c.fetchone()

    c.execute("SELECT * FROM history")
    history = c.fetchall()

    if not train:
        c.execute("SELECT train_no, train_name FROM trains")
        available = c.fetchall()
        conn.close()
        return render_template(
            "index.html",
            available_trains=available,
            error=f"Train {train_no} not found. Please choose one of the available train numbers.",
            username=session.get("username")
        )

    conn.close()

    train_data = {
        "train_no": train[0],
        "train_name": train[1],
        "source": train[2],
        "destination": train[3],
        "departure": train[4],
        "arrival": train[5],
        "duration": train[6],
        "distance": train[7],
        "platform": train[8],
        "current_location": train[9],
        "status": train[10],
        "eta": train[11],
    }

    return render_template("dashboard.html",
                            train=train_data,
                            history=history,
                            journey_date=departure,
                            station=destination,
                            username=session.get("username"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)