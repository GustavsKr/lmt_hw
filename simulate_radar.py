# simulate.py
import time
import requests
import random
from datetime import datetime

URL = "http://127.0.0.1:8000/radar"

def run_simulation():
    print("--- Simulator Started ---")
    # Wait a moment for the server to actually boot up
    time.sleep(2) 
    
    while True:
        data = {
            "speed_ms": random.uniform(10, 1000),
            "altitude_m": random.uniform(100, 5000),
            "heading_deg": random.uniform(0, 360),
            "latitude": 56.9 + random.uniform(-0.5, 0.5),
            "longitude": 24.1 + random.uniform(-3, 3),
            "report_time": datetime.now().isoformat()      
        }
        try:
            response = requests.post(URL, json=data)
            print(f"Target Detected | Action: {response.json().get('action') or response.json().get('interceptor')}")
        except Exception as e:
            print(f"Simulator Connection Error: {e}")

        time.sleep(2)