# Integration/backend/models.py
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

# NOTE: We use an absolute path so both scripts find the SAME file
# Update this to your exact path if needed, or keep as is for relative pathing
DATABASE_URL = "sqlite:///../safety_system.db" 

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ViolationEvent(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.now)
    person_name = Column(String)
    violation_type = Column(String)
    snapshot_path = Column(String)

# Create tables
Base.metadata.create_all(bind=engine)