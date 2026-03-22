# simulate_radar.py
import time
import requests
import random
from datetime import datetime

URL = "http://127.0.0.1:8000/radar"

def run_simulation():
    print("--- Tactical Simulator Started ---")
    time.sleep(2) 
    
    # Define profiles that match your interceptor capabilities
    threat_profiles = [
        {"type": "Small Drone", "speed": (15, 60), "alt": (200, 1500), "lat_off": 0.1, "lon_off": 0.2},
        {"type": "Fighter Jet", "speed": (250, 600), "alt": (5000, 12000), "lat_off": 0.5, "lon_off": 1.0},
        {"type": "Ballistic Missile", "speed": (1000, 2500), "alt": (20000, 50000), "lat_off": 1.5, "lon_off": 3.0},
        {"type": "Low-Flyer", "speed": (300, 800), "alt": (50, 500), "lat_off": 0.05, "lon_off": 0.1}
    ]

    while True:
        # Pick a random profile
        profile = random.choice(threat_profiles)
        
        data = {
            "speed_ms": random.uniform(*profile["speed"]),
            "altitude_m": random.uniform(*profile["alt"]),
            "heading_deg": random.uniform(0, 360),
            # Narrower lat/lon for drones, wider for missiles
            "latitude": 56.9 + random.uniform(-profile["lat_off"], profile["lat_off"]),
            "longitude": 24.1 + random.uniform(-profile["lon_off"], profile["lon_off"]),
            "report_time": datetime.now().isoformat()      
        }
        
        try:
            response = requests.post(URL, json=data)
            res_json = response.json()
            
            # Print feedback to see which interceptor was chosen
            threat_type = profile["type"]
            interceptor = res_json.get("interceptor", "NONE")
            print(f"[{threat_type}] Spd: {data['speed_ms']:.0f}m/s | Alt: {data['altitude_m']:.0f}m -> Assigned: {interceptor}")
            
        except Exception as e:
            print(f"Simulator Connection Error: {e}")

        time.sleep(1)