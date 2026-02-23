from typing import List, Tuple, Optional, Dict, Any
from app.models.schemas import EntityResult
from app.services.campus_db import get_nearby_facilities

async def handle(query: str, entities: List[EntityResult]) -> Tuple[str, Optional[Dict[str, Any]], str]:
    location_entity = next((e for e in entities if e.label == "CAMPUS_LOCATION"), None)
    facility_entity = next((e for e in entities if e.label == "FACILITY_TYPE"), None)
    
    reference_location = location_entity.text if location_entity else None
    facility_type = facility_entity.text if facility_entity else None
    
    nearby = get_nearby_facilities(reference_location, facility_type)
    if nearby:
        names = ", ".join([f['name'] for f in nearby[:3]])
        return (f"Nearby {facility_type or 'facilities'}" + (f" to {reference_location}" if reference_location else "") + f": {names}.", {"facilities": nearby}, "database")
    
    return ("I couldn't find nearby facilities. Try the campus map at northumbria.ac.uk.", None, "fallback")