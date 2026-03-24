# main.py
import threading
import uvicorn
from geopy.distance import geodesic
from simulate_radar import run_simulation
from fastapi import FastAPI, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from datetime import datetime
from math import radians, cos, sin, sqrt, atan2, degrees

from database import engine, Base, seed_data, SessionLocal, BaseStation, Interceptor

app = FastAPI()

app.mount("/templates", StaticFiles(directory="templates"), name="templates")

last_result = {}

class RadarData(BaseModel):
    speed_ms: float
    altitude_m: float
    heading_deg: float
    latitude: float
    longitude: float
    report_time: datetime

class BaseData(BaseModel):
    name: str
    x: float
    y: float
    range_radius_m: float

class InterceptorData(BaseModel):
    name: str
    speed: float
    range: float
    altitude: float
    cost: float

def latlon_to_meters_distance(base_lat: float, base_lon: float, target_lat: float, target_lon: float):
    """
    Converts the difference between base and target latitude/longitude coordinates
    into distance in meters
    """
    base = (base_lat, base_lon)
    target = (target_lat, target_lon)
    
    # Returns distance in meters
    return geodesic(base, target).meters

def classify_threat(speed: float, altitude: float):
    """
    Classify threat level based off speed and altitude
    """
    if speed < 15 or altitude < 200:
        return "no threat"
    elif speed > 150:
        return "threat"
    elif speed > 15:
        return "caution"
    else:
        return "potential threat"

def get_closest_base(db, target_lat: float, target_lon: float):
    """
    Returns the closest base to the target **within its operational range**.
    Coordinates are assumed to be in degrees, so we convert to meters.
    """
    bases = db.query(BaseStation).all()
    candidates = []

    for b in bases:
        # b.y is Latitude, b.x is Longitude
        distance = latlon_to_meters_distance(b.y, b.x, target_lat, target_lon)

        if distance <= b.range_radius_m:
            candidates.append((b, distance))
    
    return min(candidates, key=lambda x: x[1])[0] if candidates else None

def choose_interceptor(interceptors, base: BaseData, data: RadarData, threat: str):
    candidates = []

    target_distance = latlon_to_meters_distance(base.y, base.x, data.latitude, data.longitude)
    dy = data.latitude - base.y
    dx = data.longitude - base.x
    angle_to_target_deg = degrees(atan2(dy, dx))
    angle_diff_rad = radians(data.heading_deg - angle_to_target_deg)

    for i in interceptors:
        if target_distance > i.range or data.altitude_m > i.altitude:
            continue

        target_v_away = data.speed_ms * cos(angle_diff_rad)
        relative_speed = i.speed - target_v_away

        if relative_speed <= 0:
            continue

        intercept_time = target_distance / relative_speed

        candidates.append({
            "obj": i,
            "cost": i.cost,
            "time": intercept_time,
            "speed": i.speed
        })

    if not candidates:
        return None

    candidates.sort(key=lambda x: (x['cost'], x['time']))

    return candidates[0]['obj']

@app.post("/radar")
def process_radar(data: RadarData):
    global last_result

    db = SessionLocal()
    try:
        base = get_closest_base(db, data.latitude, data.longitude)
        if not base:
            # No base in range 404 Not Found
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No base in range of the target"
            )

        interceptors = db.query(Interceptor).all()

        threat = classify_threat(data.speed_ms, data.altitude_m)

        if threat == "no threat":
            result = {
                "threat": threat, 
                "base": base.name, 
                "action": "ignore",
                "target_coordinates": {"x": data.longitude, "y": data.latitude}
            }
            last_result = result
            return result  # 200

        interceptor = choose_interceptor(interceptors, base, data, threat)

        if not interceptor:
            # Interceptor can't reach target 400 Bad Request
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No available interceptor can reach the target"
            )

        result = {
            "threat": threat,
            "base": base.name,
            "interceptor": interceptor.name,
            "target_coordinates": {
                "x": data.longitude,
                "y": data.latitude
            },
            "speed": data.speed_ms,
            "altitude": data.altitude_m,
            "heading": data.heading_deg,
            "time": data.report_time.strftime("%H:%M:%S")
        }

        last_result = result
        return result  # 200

    finally:
        db.close()

@app.get("/last")
def get_last():
    return last_result

@app.get("/map-data")
def get_map_data():
    db = SessionLocal()
    try:
        bases = db.query(BaseStation).all()
        interceptors = db.query(Interceptor).all()
        
        return {
            "bases": [{"name": b.name, "x": b.x, "y": b.y, "range": b.range_radius_m} for b in bases],
            "interceptors": [{"name": i.name, "range": i.range} for i in interceptors]
        }
    finally:
        db.close()

@app.get("/")
def root():
    return FileResponse("templates/index.html")

if __name__ == "__main__":
    # 1. Initialize DB
    Base.metadata.create_all(bind=engine)
    seed_data()

    # 2. Start the simulator in a background thread
    # This prevents the simulator from "blocking" the server
    sim_thread = threading.Thread(target=run_simulation, daemon=True)
    sim_thread.start()

    # 3. Start the Web Server
    uvicorn.run(app, host="0.0.0.0", port=8000)