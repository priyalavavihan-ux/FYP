from typing import List, Tuple, Optional, Dict, Any
from app.models.schemas import EntityResult
from app.services.campus_db import get_facility_hours

FACILITY_KEYWORDS = [
    "library", "gym", "cafe", "canteen", "sports centre", "sport central",
    "student union", "students union", "printing room", "student services",
    "computer lab", "coach lane", "ellison", "northumberland building",
    "city campus east", "squires", "lipman", "camden", "sutherland"
]

async def handle(query: str, entities: List[EntityResult]) -> Tuple[str, Optional[Dict[str, Any]], str]:
    # Try entity first
    facility_entity = next(
        (e for e in entities if e.label in ["CAMPUS_LOCATION", "FACILITY_TYPE"]), None
    )

    search_term = facility_entity.text if facility_entity else None

    # If no entity extracted, search query text directly for known keywords
    if not search_term:
        query_lower = query.lower()
        for keyword in FACILITY_KEYWORDS:
            if keyword in query_lower:
                search_term = keyword
                break

    if not search_term:
        return (
            "Which facility are you asking about? E.g. the library, sports centre, or student union.",
            None,
            "fallback"
        )

    hours_result = get_facility_hours(search_term)
    if hours_result:
        hours_text = ", ".join([f"{day}: {time}" for day, time in hours_result["hours"].items()])
        return (
            f"{hours_result['name']} opening hours: {hours_text}.",
            hours_result,
            "database"
        )

    return (
        f"I don't have opening hours for {search_term}. Please check northumbria.ac.uk.",
        None,
        "fallback"
    )