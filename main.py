# main.py
import threading
import uvicorn
from simulate_radar import run_simulation
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from datetime import datetime
from math import sqrt

from database import engine, Base, seed_data, SessionLocal, BaseStation, Interceptor

app = FastAPI()

# Serve static files (map)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Store last result for map
last_result = {}


# -----------------------------
# Radar Input Schema
# -----------------------------
class RadarData(BaseModel):
    speed_ms: float
    altitude_m: float
    heading_deg: float
    latitude: float
    longitude: float
    report_time: datetime


# -----------------------------
# Threat classification
# -----------------------------
def classify_threat(speed, altitude):
    """
    AI assisted: structured logic based on assignment rules
    """

    if speed < 15 or altitude < 200:
        return "no threat"
    elif speed > 150:
        return "threat"
    elif speed > 15:
        return "caution"
    else:
        return "potential threat"


# -----------------------------
# Distance calculation
# -----------------------------
def calculate_distance(x1, z1, x2, z2):
    """
    Euclidean distance (flat earth assumption)
    """
    return sqrt((x2 - x1) ** 2 + (z2 - z1) ** 2)


# -----------------------------
# Get closest base
# -----------------------------
def get_closest_base(db, x, z):
    bases = db.query(BaseStation).all()

    def distance(b):
        return sqrt((b.x - x) ** 2 + (b.z - z) ** 2)

    return min(bases, key=distance)


# -----------------------------
# Choose interceptor
# -----------------------------
def choose_interceptor(db, distance, altitude):
    """
    Select cheapest interceptor that can reach target

    AI assisted: filtering + min selection
    """

    interceptors = db.query(Interceptor).all()

    possible = []

    for i in interceptors:
        if distance <= i.range and altitude <= i.altitude:
            possible.append(i)

    if not possible:
        return None

    return min(possible, key=lambda x: x.cost)


# -----------------------------
# API endpoint
# -----------------------------
@app.post("/radar")
def process_radar(data: RadarData):

    global last_result

    db = SessionLocal()

    threat = classify_threat(data.speed_ms, data.altitude_m)

    if threat == "no threat":
        db.close()
        result = {"threat": threat, "action": "ignore"}
        last_result = result
        return result

    base = get_closest_base(db, data.latitude, data.longitude)

    distance = calculate_distance(
        base.x,
        base.z,
        data.latitude,
        data.longitude
    )

    interceptor = choose_interceptor(db, distance, data.altitude_m)

    if not interceptor:
        db.close()
        result = {
            "threat": threat,
            "action": "no available interceptor"
        }
        last_result = result
        return result

    result = {
        "threat": threat,
        "base": base.name,
        "interceptor": interceptor.name,
        "intercept_coordinates": {
            "x": data.latitude,
            "z": data.longitude
        }
    }

    db.close()
    last_result = result
    return result


# -----------------------------
# Get last result (for map)
# -----------------------------
@app.get("/last")
def get_last():
    return last_result


# -----------------------------
# Serve map
# -----------------------------
@app.get("/")
def root():
    return FileResponse("static/index.html")

if __name__ == "__main__":
    # 1. Initialize DB
    Base.metadata.create_all(bind=engine)
    seed_data()

    # 2. Start the simulator in a background thread
    # This prevents the simulator from "blocking" the server
    sim_thread = threading.Thread(target=run_simulation, daemon=True)
    sim_thread.start()

    # 3. Start the Web Server
    uvicorn.run(app, host="127.0.0.1", port=8000)