from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
import models, schemas, services
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, specfiy the frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    # Seed data on startup
    db = next(get_db())
    services.seed_data(db)

@app.get("/metrics")
def get_metrics(db: Session = Depends(get_db)):
    return services.get_db_metrics(db)

@app.post("/events", response_model=schemas.Event)
def create_event(event: schemas.EventCreate, db: Session = Depends(get_db)):
    db_event = models.Event(**event.dict())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

@app.post("/seed")
def seed_manual(db: Session = Depends(get_db)):
    services.seed_data(db)
    return {"message": "Data seeded (if empty)"}
