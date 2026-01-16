# Integration/backend/main.py
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from models import SessionLocal, ViolationEvent  # <--- FIXED IMPORT
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/logs")
def get_logs(db: Session = Depends(get_db)):
    # Query the 'ViolationEvent' table, not 'Log'
    return db.query(ViolationEvent).order_by(ViolationEvent.timestamp.desc()).limit(10).all()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)