from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
import datetime

class Worker(Base):
    __tablename__ = "workers"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    
    events = relationship("Event", back_populates="worker")

class Workstation(Base):
    __tablename__ = "workstations"

    id = Column(String, primary_key=True, index=True)
    type = Column(String)
    
    events = relationship("Event", back_populates="workstation")

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    worker_id = Column(String, ForeignKey("workers.id"))
    workstation_id = Column(String, ForeignKey("workstations.id"))
    event_type = Column(String) # working, idle, absent, product_count
    confidence = Column(Float)
    count = Column(Integer, default=0) # For product_count events

    worker = relationship("Worker", back_populates="events")
    workstation = relationship("Workstation", back_populates="events")
