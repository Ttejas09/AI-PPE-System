from sqlalchemy import Column, Integer, String, DateTime, LargeBinary, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

# Database file location
DATABASE_URL = "sqlite:///./safety_system.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ViolationEvent(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.now)
    person_name = Column(String, default="Unknown")
    violation_type = Column(String) # e.g. "No Helmet"
    snapshot_path = Column(String)  # Path to image evidence

class Employee(Base):
    __tablename__ = "employees"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    face_encoding = Column(LargeBinary)

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)