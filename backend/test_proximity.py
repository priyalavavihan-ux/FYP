import asyncio
import sys
sys.path.insert(0, '.')

from app.services.handlers.proximity_handler import handle
from app.models.schemas import EntityResult

async def test():
    entities = [EntityResult(text='cafe', label='FACILITY_TYPE', start=16, end=20)]
    try:
        result = await handle('Where is the nearest cafe?', entities)
        print(result)
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

asyncio.run(test())