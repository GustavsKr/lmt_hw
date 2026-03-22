# database.py
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///./app.db"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()


# -------------------------
# Models
# -------------------------
class BaseStation(Base):
    __tablename__ = "bases"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    x = Column(Float)
    y = Column(Float)
    range_radius_m = Column(Float)


class Interceptor(Base):
    __tablename__ = "interceptors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    speed = Column(Float)
    range = Column(Float)
    altitude = Column(Float)
    cost = Column(Float)

class DB:
    def __init__(self):
        self.db = SessionLocal()

    def close(self):
        self.db.close()

    def get_bases(self):
        return self.db.query(BaseStation).all()

    def get_interceptors(self):
        return self.db.query(Interceptor).all()


def seed_data():
    db = SessionLocal()

    if db.query(BaseStation).first():
        db.close()
        return

    db.add_all([
        BaseStation(name="Riga", y=56.97475845607155, x=24.1670070219384, range_radius_m=100000)
    ])

    db.add_all([
        Interceptor(name="drone", speed=80, range=30000, altitude=2000, cost=10000),
        Interceptor(name="jet", speed=700, range=3500000, altitude=15000, cost=1000),
        Interceptor(name="rocket", speed=1500, range=10000000, altitude=300000, cost=300000),
        Interceptor(name="50cal", speed=900, range=2000, altitude=2000, cost=1),
    ])

    db.commit()
    db.close()