import asyncio
import httpx
import sys
sys.path.insert(0, '.')

async def test():
    async with httpx.AsyncClient() as client:
        for query in ["When is the freshers fair?", "When is the next careers event?"]:
            r = await client.post("http://127.0.0.1:8000/api/v1/query", json={"query": query}, timeout=10.0)
            data = r.json()
            print(f"\nQuery: {query}")
            print(f"Response: {data.get('response')}")
            print(f"Intent: {data.get('intent')}")
            print(f"Entities: {data.get('entities')}")

asyncio.run(test())