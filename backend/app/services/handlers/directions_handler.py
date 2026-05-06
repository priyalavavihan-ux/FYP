from typing import List, Tuple, Optional, Dict, Any
from app.models.schemas import EntityResult
from app.services.campus_db import get_location
from app.services.maps_service import get_directions

async def handle(query: str, entities: List[EntityResult]) -> Tuple[str, Optional[Dict[str, Any]], str]:
    location_entity = next((e for e in entities if e.label in ["CAMPUS_LOCATION", "FACILITY_TYPE"]), None)
    if not location_entity:
        return ("Could you clarify which location you're looking for?", None, "fallback")

    location_name = location_entity.text
    campus_result = get_location(location_name)
    if campus_result:
        return (
            f"{campus_result['name']} is located at {campus_result['address']}. {campus_result.get('directions_hint', '')}",
            campus_result,
            "database"
        )

    maps_result = await get_directions(location_name)
    if maps_result:
        note = maps_result.get('note', f"Please use Google Maps to find {location_name}.")
        return (note, maps_result, "fallback")

    return (
        f"Sorry, I couldn't find directions to {location_name}. Try northumbria.ac.uk/campus-map.",
        None,
        "fallback"
    )