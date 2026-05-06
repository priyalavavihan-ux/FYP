import httpx
import os
from typing import Optional

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")

NORTHUMBRIA_ORIGIN = "Northumbria University, Newcastle upon Tyne, UK"


async def get_directions(destination: str) -> Optional[dict]:
    return {
        "destination": destination,
        "note": "For directions to " + destination + ", please use Google Maps or visit northumbria.ac.uk/campus-map",
        "source": "fallback"
    }


async def get_nearby_places(location: str, place_type: str = "establishment") -> Optional[dict]:
    return None