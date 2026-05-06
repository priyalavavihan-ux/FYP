from typing import List, Tuple, Optional, Dict, Any
from app.models.schemas import EntityResult
from app.services.campus_db import get_events, CAMPUS_EVENTS

CAREERS_KEYWORDS = ["careers", "career", "job", "jobs", "employment", "recruitment"]
FRESHERS_KEYWORDS = ["freshers", "fresher", "welcome week", "freshers fair", "freshers week"]

async def handle(query: str, entities: List[EntityResult]) -> Tuple[str, Optional[Dict[str, Any]], str]:
    time_entity = next((e for e in entities if e.label == "TIME_REFERENCE"), None)
    event_entity = next((e for e in entities if e.label == "EVENT_TYPE"), None)
    location_entity = next((e for e in entities if e.label == "CAMPUS_LOCATION"), None)

    time_ref = time_entity.text if time_entity else "today"
    location = location_entity.text if location_entity else None
    query_lower = query.lower()

    # Check for specific event type keywords directly in query
    if any(kw in query_lower for kw in FRESHERS_KEYWORDS):
        freshers = [e for e in CAMPUS_EVENTS if "fresher" in e["name"].lower()]
        if freshers:
            e = freshers[0]
            return (
                f"{e['name']} is on {e['date']} at {e['time']} in {e['location']}.",
                {"events": freshers}, "database"
            )

    if any(kw in query_lower for kw in CAREERS_KEYWORDS):
        careers = [e for e in CAMPUS_EVENTS if "career" in e["name"].lower()]
        if careers:
            e = careers[0]
            return (
                f"{e['name']} is on {e['date']} at {e['time']} in {e['location']}.",
                {"events": careers}, "database"
            )

    # General event lookup
    events = get_events(time_ref, location)
    if events:
        event_list = "; ".join([f"{e['name']} at {e['time']} in {e['location']}" for e in events[:3]])
        return (f"Upcoming events ({time_ref}): {event_list}.", {"events": events}, "database")

    return (f"No events found for {time_ref}. Check northumbria.ac.uk/events.", None, "fallback")