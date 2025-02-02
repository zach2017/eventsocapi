
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, validator
from typing import List, Optional
from datetime import datetime
import json
import os

app = FastAPI(title="Events API", description="API for managing sports events")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


# File path for storing events
JSON_FILE = "events.json"

class EventBase(BaseModel):
    date: str
    title: str
    type: str
    location: str
    link: str
    description: str

    @validator('date')
    def validate_date_format(cls, v):
        try:
            datetime.strptime(v, '%m/%d/%Y')
            return v
        except ValueError:
            raise ValueError('Invalid date format. Use MM/DD/YYYY')

class Event(EventBase):
    id: int

class EventCreate(EventBase):
    pass

def load_events() -> List[dict]:
    """Load events from JSON file. Create file with empty array if it doesn't exist."""
    if not os.path.exists(JSON_FILE):
        with open(JSON_FILE, 'w') as f:
            json.dump([], f)
        return []
    
    try:
        with open(JSON_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def save_events(events: List[dict]):
    """Save events to JSON file."""
    with open(JSON_FILE, 'w') as f:
        json.dump(events, f, indent=2)

@app.get("/events", response_model=List[Event], tags=["Events"])
async def get_events():
    """
    Retrieve all events from the database.
    """
    return load_events()

@app.post("/events", response_model=Event, status_code=201, tags=["Events"])
async def create_event(event: EventCreate):
    """
    Create a new event.
    """
    events = load_events()
    
    # Generate new ID
    new_id = max([e['id'] for e in events], default=0) + 1
    
    # Create new event
    event_dict = event.dict()
    event_dict['id'] = new_id
    
    # Add and save
    events.append(event_dict)
    save_events(events)
    
    return event_dict

@app.get("/events/{event_id}", response_model=Event, tags=["Events"])
async def get_event(event_id: int):
    """
    Retrieve a specific event by ID.
    """
    events = load_events()
    event = next((e for e in events if e['id'] == event_id), None)
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return event

@app.delete("/events/{event_id}", status_code=204, tags=["Events"])
async def delete_event(event_id: int):
    """
    Delete a specific event by ID.
    """
    events = load_events()
    events_filtered = [e for e in events if e['id'] != event_id]
    
    if len(events) == len(events_filtered):
        raise HTTPException(status_code=404, detail="Event not found")
    
    save_events(events_filtered)
    return None
