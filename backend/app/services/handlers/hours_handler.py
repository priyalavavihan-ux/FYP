from typing import List, Tuple, Optional, Dict, Any
from app.models.schemas import EntityResult
from app.services.campus_db import get_facility_hours

async def handle(query: str, entities: List[EntityResult]) -> Tuple[str, Optional[Dict[str, Any]], str]:
    facility_entity = next((e for e in entities if e.label in ["CAMPUS_LOCATION", "FACILITY_TYPE"]), None)
    if not facility_entity:
        return ("Which facility are you asking about? E.g. the library, sports centre, or student union.", None, "fallback")
    
    hours_result = get_facility_hours(facility_entity.text)
    if hours_result:
        hours_text = ", ".join([f"{day}: {time}" for day, time in hours_result["hours"].items()])
        return (f"{hours_result['name']} opening hours: {hours_text}.", hours_result, "database")
    
    return (f"I don't have opening hours for {facility_entity.text}. Check northumbria.ac.uk.", None, "fallback")