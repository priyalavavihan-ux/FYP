import os
import httpx
from typing import Optional, Dict, Any

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")
DIRECTIONS_URL = "https://maps.googleapis.com/maps/api/directions/json"
GEOCODE_URL = "https://maps.googleapis.com/maps/api/geocode/json"

async def get_directions(destination: str, origin: str = "Northumbria University, Newcastle") -> Optional[Dict[str, Any]]:
    if not GOOGLE_MAPS_API_KEY:
        return None
    params = {"origin": origin, "destination": destination, "key": GOOGLE_MAPS_API_KEY, "mode": "walking"}
    async with httpx.AsyncClient() as client:
        response = await client.get(DIRECTIONS_URL, params=params)
        data = response.json()
    if data.get("status") == "OK":
        route = data["routes"][0]
        leg = route["legs"][0]
        return {
            "summary": route.get("summary", ""),
            "distance": leg["distance"]["text"],
            "duration": leg["duration"]["text"],
            "start_address": leg["start_address"],
            "end_address": leg["end_address"],
            "steps": [step["html_instructions"] for step in leg["steps"][:5]]
        }
    return None