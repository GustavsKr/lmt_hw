from main import choose_interceptor
from main import classify_threat, calculate_distance, choose_interceptor

def test_classify_threat():
    assert classify_threat(2000, 100) == "no threat"
    assert classify_threat(10, 500) == "no threat"
    assert classify_threat(50, 100) == "no threat"
    assert classify_threat(200, 500) == "threat"
    assert classify_threat(50, 500) == "caution"


def test_distance_zero():
    assert calculate_distance(0, 0, 0, 0) == 0
    assert calculate_distance(0, 0, 3, 4) == 5  # 3-4-5 triangle


class Interceptor:
    def __init__(self, name, speed, range, altitude, cost):
        self.name = name
        self.speed = speed
        self.range = range
        self.altitude = altitude
        self.cost = cost

def test_choose_interceptor():
    interceptors = [
        Interceptor("rocket", speed=1500, range=10000000, altitude=300000, cost=300000),
        Interceptor("jet", speed=700, range=3500000, altitude=15000, cost=1000),
        Interceptor("drone", speed=80, range=30000, altitude=2000, cost=10000),
        Interceptor("50cal", speed=900, range=2000, altitude=2000, cost=1),
    ]

    # Cheapest valid
    chosen = choose_interceptor(interceptors, 1000, 1000, 100)
    assert chosen.name == "50cal"

    # Out of range
    chosen = choose_interceptor(interceptors, 5000, 1000, 100)
    assert chosen.name != "50cal"

    # Too slow
    chosen = choose_interceptor(interceptors, 1000, 1000, 950)
    assert chosen.name != "50cal"

    # Valid but not cheapest
    chosen = choose_interceptor(interceptors, 20000, 1000, 50)
    assert chosen.name == "jet"

    # Too slow
    chosen = choose_interceptor(interceptors, 1000, 1000, 100)
    assert chosen.name != "drone"

    # Altitude limit exceeded
    chosen = choose_interceptor(interceptors, 1000, 3000, 50)
    assert chosen.name != "drone"

    # Mid-range typical case
    chosen = choose_interceptor(interceptors, 50000, 1000, 100)
    assert chosen.name == "jet"

    # Too slow for fast target
    chosen = choose_interceptor(interceptors, 1000, 1000, 800)
    assert chosen.name != "jet"

    # Altitude too high
    chosen = choose_interceptor(interceptors, 1000, 20000, 100)
    assert chosen.name != "jet"

    # High altitude target
    chosen = choose_interceptor(interceptors, 1000, 200000, 100)
    assert chosen.name == "rocket"

    # Only option for very fast target
    chosen = choose_interceptor(interceptors, 1000, 1000, 1000)
    assert chosen.name == "rocket"

    # Not chosen when cheaper options exist
    chosen = choose_interceptor(interceptors, 1000, 1000, 100)
    assert chosen.name != "rocket"

    # Target too fast for all
    chosen = choose_interceptor(interceptors, 1000, 1000, 2000)
    assert chosen is None

    # Target too high for all
    chosen = choose_interceptor(interceptors, 1000, 500000, 100)
    assert chosen is None

    # Target too far for all
    chosen = choose_interceptor(interceptors, 20000000, 1000, 100)
    assert chosen is None
