
from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os
import requests
from datetime import date, datetime, timedelta

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "trainpulse-dev-secret")
DB = "database.db"

# Read credentials from environment variables so the app uses the new API key/secret.
# PowerShell example:
#   $env:TRAINPULSE_API_KEY="your_real_key_here"
#   $env:TRAINPULSE_API_SECRET="your_real_secret_here"
# CMD example:
#   set TRAINPULSE_API_KEY=your_real_key_here
#   set TRAINPULSE_API_SECRET=your_real_secret_here
API_KEY = "rg_c778e6583943451aba41f7dda8477be4"
  
API_CALL_LIMIT = int(os.getenv("TRAINPULSE_API_CALL_LIMIT", os.getenv("API_CALL_LIMIT", "20")))
# If a key is present, enable live API automatically unless explicitly disabled.
env_use_api = os.getenv("TRAINPULSE_USE_API", "").lower()
USE_LIVE_API = (env_use_api in ("1", "true", "yes", "on")) or (bool(API_KEY) and env_use_api != "false")
API_CACHE_SECONDS = int(os.getenv("TRAINPULSE_API_CACHE_SECONDS", "300"))
# RailRadar API: GET https://api.railradar.in/v1/trains/{number}/live?date=YYYY-MM-DD
API_URL_TEMPLATE = "https://api.railradar.in/v1/trains/{train_no}/live"
api_cache = {}
api_call_stats = {"count": 0}


def get_journey_date_str(departure):
    # RailRadar expects "YYYY-MM-DD"
    if departure and departure.lower() == "tomorrow":
        target_date = date.today() + timedelta(days=1)
    else:
        target_date = date.today()
    return target_date.strftime("%Y-%m-%d")


def parse_api_response(payload):
    current_location = (
        payload.get("position", {}).get("station", {}).get("name")
        or payload.get("current_location")
        or payload.get("current_station")
        or "Unknown"
    )
    status = (
        payload.get("position", {}).get("status")
        or payload.get("running_status")
        or payload.get("status")
        or payload.get("response_message")
        or "Live status unavailable"
    )
    delay = (
        payload.get("delay")
        or payload.get("delay_minutes")
        or payload.get("late_by")
        or payload.get("estimated_delay")
        or "N/A"
    )
    message = payload.get("message") or payload.get("response_message") or "Live API data received"
    return {
        "current_location": current_location,
        "status": status,
        "delay": delay,
        "message": message,
    }


def build_api_headers():
    headers = {}
    if API_KEY:
        headers["Authorization"] = f"Bearer {API_KEY}"
    return headers


def fetch_train_live_status(train_no, departure):
    if not USE_LIVE_API:
        return None, "api_disabled"

    headers = build_api_headers()
    if not headers:
        return None, "missing_api_key"

    # FIX 3: Check cache BEFORE spending an API call. This stops every page
    # refresh from burning through the daily/hourly call limit.
    cache_key = (train_no, departure)
    cached = api_cache.get(cache_key)
    if cached and (datetime.now() - cached["time"]).total_seconds() < API_CACHE_SECONDS:
        return cached["data"], "api"

    if api_call_stats["count"] >= API_CALL_LIMIT:
        return None, "limit_reached"

    url = API_URL_TEMPLATE.format(train_no=train_no)
    params = {"date": get_journey_date_str(departure)}

    api_call_stats["count"] += 1
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        print(f"[DEBUG] API status_code={response.status_code}")
        print(f"[DEBUG] API raw response={response.text[:1000]}")
        payload = response.json()

        if response.status_code == 401 or response.status_code == 403:
            return None, "unauthorized"

        if response.status_code != 200 or not isinstance(payload, dict):
            return None, "request_failed"

        if not payload.get("success"):
            error_message = payload.get("error", {}).get("message") or payload.get("message") or "API request failed"
            print(f"[DEBUG] API error={error_message}")
            return None, "request_failed"

        data = payload.get("data", {})
        current_location = data.get("currentLocation")
        if isinstance(current_location, dict):
            current_location = (
                current_location.get("stationName")
                or current_location.get("stationCode")
                or current_location.get("status")
            )

        delay_value = data.get("delayMinutes") or data.get("delay") or data.get("delayInMinutes") or "0"
        if isinstance(delay_value, (int, float)):
            delay_value = f"{delay_value} mins"
        elif isinstance(delay_value, str) and delay_value.isdigit():
            delay_value = f"{delay_value} mins"

        next_halt = data.get("nextHalt") or {}
        previous_halt = data.get("previousHalt") or {}
        train_info = data.get("train", {}) or {}
        route_source = train_info.get("source", {}).get("name")
        route_destination = train_info.get("destination", {}).get("name")

        result = {
            "current_location": (
                current_location
                or data.get("currentStation")
                or "Unknown"
            ),
            "status": (
                data.get("status")
                or data.get("currentStatus")
                or (data.get("currentLocation", {}).get("status") if isinstance(data.get("currentLocation"), dict) else None)
                or "Running"
            ),
            "delay": delay_value,
            "message": "Live API Data Updated!",
            "next_halt": (
                next_halt.get("stationName")
                or next_halt.get("stationCode")
                or None
            ),
            "previous_halt": (
                previous_halt.get("stationName")
                or previous_halt.get("stationCode")
                or None
            ),
            "tracking_mode": data.get("trackingMode") or "real-time",
            "is_live": data.get("isLive", False),
            "route_source": route_source,
            "route_destination": route_destination,
            "last_updated": data.get("lastUpdatedAt"),
        }
        api_cache[cache_key] = {"data": result, "time": datetime.now()}
        return result, "api"
    except requests.exceptions.RequestException:
        return None, "request_failed"
    except ValueError:
        return None, "request_failed"


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

    # Real trains covering: Thirumangalam-Madurai, Madurai-Virudhunagar,
    # Chennai-Madurai, Coimbatore-Chennai.
    real_trains = [
        (
            "12693", "Pearl City Express",
            "Thirumangalam", "Madurai Junction",
            "06:10", "06:45", "0h 35m", "18 km",
            "PF 1", "Thirumangalam", "Running On Time", "Madurai Junction",
        ),
        (
            "12631", "Nellai SF Express",
            "Madurai Junction", "Virudhunagar Junction",
            "05:15", "05:50", "0h 35m", "44 km",
            "PF 2", "Madurai Junction", "Running On Time", "Virudhunagar Junction",
        ),
        (
            "12635", "Vaigai SF Express",
            "Chennai Egmore", "Madurai Junction",
            "13:15", "20:35", "7h 20m", "497 km",
            "PF 3", "Chennai Egmore", "Running On Time", "Madurai Junction",
        ),
        (
            "12676", "Kovai Express",
            "Coimbatore Junction", "Chennai Central",
            "15:15", "23:00", "7h 45m", "496 km",
            "PF 4", "Coimbatore Junction", "Running On Time", "Chennai Central",
        ),
    ]
    c.executemany(
        """INSERT OR IGNORE INTO trains
           (train_no, train_name, source, destination, departure, arrival,
            duration, distance, platform, current_location, status, eta)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        real_trains,
    )

    conn.commit()
    conn.close()
    init_db()


@app.route("/", methods=["GET"])
def index():
    if not session.get("logged_in"):
        return redirect(url_for("login"))

    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT train_no, train_name FROM trains")
    available = c.fetchall()
    conn.close()
    return render_template(
        "index.html",
        available_trains=available,
        error=None,
        username=session.get("username"),
        live_api_enabled=USE_LIVE_API,
    )


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
    # Fetch recent history only for this train (most recent first)
    c.execute("SELECT * FROM history WHERE train_no=? ORDER BY id DESC LIMIT 10", (train_no,))
    history = c.fetchall()
    conn.close()

    if not train:
        # Error handling fix: Sariyaana render_template format
        return render_template("index.html", error=f"Train {train_no} not found.", available_trains=[], username=session.get("username"))

    # API call
    api_data, api_source = fetch_train_live_status(train_no, departure)
    
    # Fallback-kku default dict
    if not api_data:
        api_data = {"current_location": "N/A", "status": "No live data", "delay": "N/A"}

    # Define api_info to fix UndefinedError
    api_info = {
        "calls_remaining": max(API_CALL_LIMIT - api_call_stats["count"], 0),
        "source": api_source if api_source else "Unknown"
    }

    train_data = {
        "train_no": train[0], "train_name": train[1], "source": train[2],
        "destination": train[3], "departure": train[4], "arrival": train[5],
        "platform": train[8],
        "current_location": api_data.get("current_location", train[9]),
        "status": api_data.get("status", train[10]),
        "eta": api_data.get("delay", "N/A")
    }

    # Insert a history record only when we have live data and it changed
    try:
        if api_source == "api" and api_data.get("is_live"):
            conn_h = sqlite3.connect(DB)
            c_h = conn_h.cursor()
            c_h.execute("SELECT status, eta FROM history WHERE train_no=? ORDER BY id DESC LIMIT 1", (train_data["train_no"],))
            last = c_h.fetchone()
            last_status = last[0] if last else None
            last_eta = last[1] if last else None
            current_status = train_data.get("status")
            current_eta = train_data.get("eta")
            # If no previous history exists, insert an initial record so recent history shows up
            c_h.execute("SELECT COUNT(1) FROM history WHERE train_no=?", (train_data["train_no"],))
            count = c_h.fetchone()[0]
            duration_distance = f"{train_data.get('duration','')} / {train_data.get('distance','')}"
            if count == 0:
                # insert initial snapshot
                c_h.execute(
                    "INSERT INTO history (train_no, train_name, destination, eta, status, duration_distance) VALUES (?, ?, ?, ?, ?, ?)",
                    (train_data["train_no"], train_data["train_name"], train_data["destination"], current_eta, current_status, duration_distance),
                )
                conn_h.commit()
            else:
                if current_status != last_status or current_eta != last_eta:
                    c_h.execute(
                        "INSERT INTO history (train_no, train_name, destination, eta, status, duration_distance) VALUES (?, ?, ?, ?, ?, ?)",
                        (train_data["train_no"], train_data["train_name"], train_data["destination"], current_eta, current_status, duration_distance),
                    )
                    conn_h.commit()
            conn_h.close()
    except Exception as e:
        print(f"[DEBUG] history insert failed: {e}")

    return render_template(
        "dashboard.html",
        train=train_data,
        api_data=api_data,
        api_info=api_info,
        history=history,
        username=session.get("username"))
