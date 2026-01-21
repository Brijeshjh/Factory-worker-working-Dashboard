from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# Event Schemas
class EventBase(BaseModel):
    timestamp: datetime
    worker_id: str
    workstation_id: str
    event_type: str
    confidence: float
    count: Optional[int] = 0

class EventCreate(EventBase):
    pass

class Event(EventBase):
    id: int

    class Config:
        orm_mode = True

# Worker Schemas
class WorkerBase(BaseModel):
    id: str
    name: str

class Worker(WorkerBase):
    class Config:
        orm_mode = True

# Workstation Schemas
class WorkstationBase(BaseModel):
    id: str
    type: str

class Workstation(WorkstationBase):
    class Config:
        orm_mode = True

# Response Schemas for Metrics
class WorkerMetric(BaseModel):
    worker_id: str
    name: str
    total_active_time_seconds: float
    total_idle_time_seconds: float
    utilization_percent: float
    total_units_produced: int
    units_per_hour: float

class WorkstationMetric(BaseModel):
    workstation_id: str
    type: str
    occupancy_time_seconds: float
    utilization_percent: float
    total_units_produced: int
    throughput_rate: float

class FactoryMetrics(BaseModel):
    total_productive_time_seconds: float
    total_production_count: int
    avg_production_rate: float
    avg_utilization_percent: float
