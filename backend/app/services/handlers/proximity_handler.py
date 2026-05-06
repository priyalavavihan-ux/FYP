from typing import List, Tuple, Optional, Dict, Any
from app.models.schemas import EntityResult
from app.services.campus_db import get_nearby_facilities, CAMPUS_LOCATIONS

FACILITY_RESPONSES = {
    "cafe": "There is a campus cafe located in the Ellison Building and in the Students' Union on Sandyford Road.",
    "coffee shop": "There is a campus cafe located in the Ellison Building and in the Students' Union on Sandyford Road.",
    "gym": "The nearest gym is Sport Central on Northumberland Road, NE1 8ST.",
    "library": "The nearest library is City Campus Library on Sandyford Road, NE1 8ST.",
    "atm": "There are ATMs available near the Students' Union on Sandyford Road.",
    "cash machine": "There are ATMs available near the Students' Union on Sandyford Road.",
    "printer": "Printing facilities are available in City Campus Library and the Ellison Building.",
    "printing room": "The printing room is located in City Campus Library on Sandyford Road.",
    "toilet": "Toilets are available in all campus buildings including Ellison Building, Northumberland Building, and City Campus Library.",
    "pharmacy": "The nearest pharmacy is on Northumberland Street, a 5-minute walk from City Campus.",
    "canteen": "The student canteen is located in the Students' Union on Sandyford Road.",
    "food": "Food is available at the Students' Union canteen and campus cafes in Ellison Building and City Campus East.",
    "study room": "Study rooms are available in City Campus Library on Sandyford Road.",
    "car park": "The nearest car park is on Sandyford Road adjacent to City Campus.",
    "bike": "Bike storage is available at the main City Campus entrance on Sandyford Road.",
    "vending machine": "Vending machines are located in Ellison Building and Northumberland Building.",
    "water fountain": "Water fountains are available in all main campus buildings.",
    "prayer room": "The prayer room is located in the Northumberland Building.",
    "meditation room": "The meditation and prayer room is located in the Northumberland Building.",
    "first aid": "First aid facilities are available at the Campus Security office in Ellison Building.",
    "shower": "Shower facilities are available at Sport Central on Northumberland Road.",
}

async def handle(query: str, entities: List[EntityResult]) -> Tuple[str, Optional[Dict[str, Any]], str]:
    location_entity = next((e for e in entities if e.label == "CAMPUS_LOCATION"), None)
    facility_entity = next((e for e in entities if e.label == "FACILITY_TYPE"), None)

    # If asking about a specific facility type, return direct response
    if facility_entity:
        facility_text = facility_entity.text.lower()
        for keyword, response in FACILITY_RESPONSES.items():
            if keyword in facility_text or facility_text in keyword:
                return (response, None, "database")

    # If asking about nearby facilities to a location
    reference_location = location_entity.text if location_entity else None
    facility_type = facility_entity.text if facility_entity else None

    nearby = get_nearby_facilities(reference_location, facility_type)
    if nearby:
        names = ", ".join([f["name"] for f in nearby[:3]])
        return (
            f"Nearby {'facilities' if not facility_type else facility_type} "
            + (f"to {reference_location}" if reference_location else "on campus")
            + f": {names}.",
            {"facilities": nearby},
            "database"
        )

    # Fallback — return all campus locations
    all_locations = list(CAMPUS_LOCATIONS.values())[:3]
    names = ", ".join([l["name"] for l in all_locations])
    return (
        f"Main campus facilities include: {names}. Visit northumbria.ac.uk for the full campus map.",
        {"facilities": all_locations},
        "database"
    )