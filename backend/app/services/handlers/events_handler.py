from typing import List, Tuple, Optional, Dict, Any
from app.models.schemas import EntityResult
from app.services.campus_db import get_events

async def handle(query: str, entities: List[EntityResult]) -> Tuple[str, Optional[Dict[str, Any]], str]:
    time_entity = next((e for e in entities if e.label == "TIME_REFERENCE"), None)
    location_entity = next((e for e in entities if e.label == "CAMPUS_LOCATION"), None)
    
    time_ref = time_entity.text if time_entity else "today"
    location = location_entity.text if location_entity else None
    
    events = get_events(time_ref, location)
    if events:
        event_list = "; ".join([f"{e['name']} at {e['time']} in {e['location']}" for e in events[:3]])
        return (f"Upcoming events ({time_ref}): {event_list}.", {"events": events}, "database")
    
    return (f"No events found for {time_ref}. Check northumbria.ac.uk/events.", None, "fallback")