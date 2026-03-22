from main import choose_interceptor, classify_threat, BaseData, RadarData, Interceptor
from datetime import datetime

def test_classify_threat():
    assert classify_threat(2000, 100) == "no threat"
    assert classify_threat(10, 500) == "no threat"
    assert classify_threat(50, 100) == "no threat"
    assert classify_threat(200, 500) == "threat"
    assert classify_threat(50, 500) == "caution"


class Interceptor:
    def __init__(self, name, speed, range, altitude, cost):
        self.name = name
        self.speed = speed
        self.range = range
        self.altitude = altitude
        self.cost = cost

def test_choose_interceptor():
    # Define the interceptor fleet
    interceptors = [
        Interceptor(name="rocket", speed=1500, range=10000000, altitude=300000, cost=300000),
        Interceptor(name="jet", speed=700, range=3500000, altitude=15000, cost=1000),
        Interceptor(name="drone", speed=80, range=30000, altitude=2000, cost=10000),
        Interceptor(name="50cal", speed=900, range=2000, altitude=2000, cost=1),
    ]
    
    # Static base for all tests (X=Lon, Y=Lat)
    base = BaseData(name="TestBase", x=0.0, y=0.0, range_radius_m=10000000)

    # --- BASIC RANGE & COST TESTS ---
    # 1. Cheapest valid: 1000m away, 500m high, slow speed (50cal is $1)
    assert choose_interceptor(interceptors, base, RadarData(speed_ms=50, altitude_m=500, heading_deg=0, latitude=1000/111000, longitude=0, report_time=datetime.now()), "caution").name == "50cal"

    # 2. Out of 50cal range: 5000m away (max range 2000m), next cheapest is Jet ($1000)
    assert choose_interceptor(interceptors, base, RadarData(speed_ms=50, altitude_m=500, heading_deg=0, latitude=5000/111000, longitude=0, report_time=datetime.now()), "caution").name == "jet"

    # 3. Altitude limit: 1000m away but 3000m high (Drone/50cal limit is 2000m)
    assert choose_interceptor(interceptors, base, RadarData(speed_ms=10, altitude_m=3000, heading_deg=0, latitude=1000/111000, longitude=0, report_time=datetime.now()), "caution").name == "jet"

    # --- VECTOR & ANGLE TESTS (The Heading Logic) ---
    # 4. Facing AWAY: Target at 100m/s moving away from base. Drone (80m/s) cannot catch it.
    assert choose_interceptor(interceptors, base, RadarData(speed_ms=100, altitude_m=1000, heading_deg=0, latitude=1000/111000, longitude=0, report_time=datetime.now()), "threat").name != "drone"

    # 5. Facing BASE: Target at 100m/s moving TOWARD base. 50cal (80m/s) CAN catch it now.
    assert choose_interceptor(interceptors, base, RadarData(speed_ms=100, altitude_m=1000, heading_deg=180, latitude=1000/111000, longitude=0, report_time=datetime.now()), "threat").name == "50cal"

    # 6. Faster but Facing Base: Target at 800m/s flying at base. 50cal is valid and faster than Jet.
    assert choose_interceptor(interceptors, base, RadarData(speed_ms=800, altitude_m=1000, heading_deg=180, latitude=1000/111000, longitude=0, report_time=datetime.now()), "threat").name == "50cal"

    # --- THREAT LEVEL SORTING ---
    # 7. Urgent Threat: Pick fastest (50cal: 900m/s) over Jet (700m/s) despite cost
    assert choose_interceptor(interceptors, base, RadarData(speed_ms=100, altitude_m=1000, heading_deg=180, latitude=500/111000, longitude=0, report_time=datetime.now()), "threat").name == "50cal"

    # 8. Not Urgent: Target is 15km away, pick cheapest (Jet: $1000) over Drone ($10000)
    assert choose_interceptor(interceptors, base, RadarData(speed_ms=20, altitude_m=1000, heading_deg=0, latitude=15000/111000, longitude=0, report_time=datetime.now()), "caution").name == "jet"

    # --- EXTREME LIMITS ---
    # 9. High Altitude: 200km up. Only Rocket can reach.
    assert choose_interceptor(interceptors, base, RadarData(speed_ms=100, altitude_m=200000, heading_deg=0, latitude=1000/111000, longitude=0, report_time=datetime.now()), "threat").name == "rocket"

    # 10. Too Fast: 2000m/s moving away. Even Rocket (1500m/s) can't catch it.
    assert choose_interceptor(interceptors, base, RadarData(speed_ms=2000, altitude_m=1000, heading_deg=0, latitude=1000/111000, longitude=0, report_time=datetime.now()), "threat") in interceptors
