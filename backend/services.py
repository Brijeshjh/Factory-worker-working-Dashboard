from sqlalchemy.orm import Session
from sqlalchemy import func
import models, schemas
import random
from datetime import datetime, timedelta

def get_db_metrics(db: Session):
    # This is a placeholde for complex aggregations.
    # In a real heavy-load system, we might use SQL aggregations or a time-series DB.
    # Here, for the assessment, we will fetch events and process them in Python for flexibility 
    # as the logic (state-based duration) is easier to implement in code than SQL for a small dataset.
    
    workers = db.query(models.Worker).all()
    workstations = db.query(models.Workstation).all()
    
    worker_metrics = []
    factory_active_time = 0
    factory_idle_time = 0
    factory_production_count = 0
    
    # 1. Worker Metrics
    for worker in workers:
        events = db.query(models.Event).filter(models.Event.worker_id == worker.id).order_by(models.Event.timestamp).all()
        
        total_active_seconds = 0.0
        total_idle_seconds = 0.0
        total_units = 0
        
        if events:
            # Calculate durations based on time between events
            for i in range(len(events) - 1):
                current_event = events[i]
                next_event = events[i+1]
                
                # Cap duration to avoid huge gaps (e.g. overnight) counting as work/idle if the system was off
                # Assuming max meaningful gap is 1 hour for this context
                duration = (next_event.timestamp - current_event.timestamp).total_seconds()
                if duration > 3600: 
                    duration = 0 # Ignore large gaps
                    
                if current_event.event_type == "working":
                    total_active_seconds += duration
                elif current_event.event_type == "idle":
                    total_idle_seconds += duration
                    
                if current_event.event_type == "product_count":
                    total_units += current_event.count

            # Handle last event (assume valid for a short duration or ignore)
            # For simplicity, we ignore duration after the very last event unless we have a "shift end"
            # But we must count the production of the last event if it exists
            if events[-1].event_type == "product_count":
                total_units += events[-1].count

        total_time = total_active_seconds + total_idle_seconds
        utilization = (total_active_seconds / total_time * 100) if total_time > 0 else 0
        
        # Estimate shift duration roughly as total_time for "Units per Hour"
        # Or just use the total_time span.
        hours = total_time / 3600.0
        units_per_hour = (total_units / hours) if hours > 0 else 0
        
        w_metric = schemas.WorkerMetric(
            worker_id=worker.id,
            name=worker.name,
            total_active_time_seconds=total_active_seconds,
            total_idle_time_seconds=total_idle_seconds,
            utilization_percent=round(utilization, 2),
            total_units_produced=total_units,
            units_per_hour=round(units_per_hour, 2)
        )
        worker_metrics.append(w_metric)
        
        factory_active_time += total_active_seconds
        factory_idle_time += total_idle_seconds
        factory_production_count += total_units

    # 2. Workstation Metrics
    workstation_metrics = []
    for station in workstations:
        events = db.query(models.Event).filter(models.Event.workstation_id == station.id).order_by(models.Event.timestamp).all()
        
        occupancy_seconds = 0.0
        total_units = 0
        
        if events:
            for i in range(len(events) - 1):
                current_event = events[i]
                next_event = events[i+1]
                duration = (next_event.timestamp - current_event.timestamp).total_seconds()
                if duration > 3600: duration = 0
                
                # Any event at a workstation implies occupancy except maybe "absent" 
                # But "absent" is usually worker status. Let's assume if a worker is "working" or "idle" at a station, it's occupied.
                if current_event.event_type in ["working", "idle", "product_count"]:
                    occupancy_seconds += duration

                if current_event.event_type == "product_count":
                    total_units += current_event.count
            
            if events[-1].event_type == "product_count":
                total_units += events[-1].count
                
        # Utilization for station: time occupied / total observed time range? 
        # Or simple ratio of specific statuses. Let's reuse the logic: Occupied vs Empty (no event? or specific empty event?)
        # For simplicity, let's assume utilization = occupancy / total time of all events for that station
        # Finding total time range is valid
        start_time = events[0].timestamp if events else datetime.now()
        end_time = events[-1].timestamp if events else datetime.now()
        total_range = (end_time - start_time).total_seconds()
        
        utilization = (occupancy_seconds / total_range * 100) if total_range > 0 else 0
        throughput = (total_units / (occupancy_seconds/3600)) if occupancy_seconds > 0 else 0
        
        s_metric = schemas.WorkstationMetric(
            workstation_id=station.id,
            type=station.type,
            occupancy_time_seconds=occupancy_seconds,
            utilization_percent=round(utilization, 2),
            total_units_produced=total_units,
            throughput_rate=round(throughput, 2)
        )
        workstation_metrics.append(s_metric)

    # 3. Factory Metrics
    total_factory_time = factory_active_time + factory_idle_time
    avg_utilization = (factory_active_time / total_factory_time * 100) if total_factory_time > 0 else 0
    avg_prod_rate = factory_production_count / (total_factory_time/3600) if total_factory_time > 0 else 0 # Units per factory-hour

    factory_metrics = schemas.FactoryMetrics(
        total_productive_time_seconds=factory_active_time,
        total_production_count=factory_production_count,
        avg_production_rate=round(avg_prod_rate, 2),
        avg_utilization_percent=round(avg_utilization, 2)
    )

    return {
        "factory": factory_metrics,
        "workers": worker_metrics,
        "workstations": workstation_metrics
    }

def seed_data(db: Session):
    # Check if data exists
    if db.query(models.Worker).first():
        return # Already seeded

    # Seed Workers
    workers = [
        models.Worker(id=f"W{i}", name=f"Worker {i}") for i in range(1, 7)
    ]
    db.add_all(workers)

    # Seed Workstations
    stations = [
        models.Workstation(id=f"S{i}", type=f"Assembly Station {i}") for i in range(1, 7)
    ]
    db.add_all(stations)
    db.commit()

    # Seed Events (Simulate a shift today)
    # Start at 8:00 AM today
    base_time = datetime.utcnow().replace(hour=8, minute=0, second=0, microsecond=0)
    
    events = []
    for w in workers:
        # Assign each worker to a station (W1 -> S1, etc)
        s_id = w.id.replace("W", "S")
        
        current_time = base_time
        # Generate events for 4 hours
        for _ in range(20): # 20 segments
            # Random duration 5-15 mins
            duration_mins = random.randint(5, 15)
            
            # 80% chance working, 10% idle, 10% product
            r = random.random()
            if r < 0.7:
                e_type = "working"
                count = 0
            elif r < 0.8:
                e_type = "idle"
                count = 0
            else:
                e_type = "product_count"
                count = random.randint(1, 5)
                # Production shouldn't take time in our "state" logic usually, 
                # but let's assume it's an instantaneous event that happens WHILE working.
                # To make the loop logic simple, if we hit product count, we just insert it
                # and don't advance time much, or we assume it replaces a state.
                # Let's say product count is a point event. 
                # We will insert a "working" event immediately after to resume state.
            
            events.append(models.Event(
                timestamp=current_time,
                worker_id=w.id,
                workstation_id=s_id,
                event_type=e_type,
                confidence=random.uniform(0.8, 0.99),
                count=count
            ))
            
            current_time += timedelta(minutes=duration_mins)

    db.add_all(events)
    db.commit()
