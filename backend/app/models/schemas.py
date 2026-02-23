from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class QueryRequest(BaseModel):
    query: str

class IntentResult(BaseModel):
    intent: str
    confidence: float

class EntityResult(BaseModel):
    text: str
    label: str
    start: int
    end: int

class QueryResponse(BaseModel):
    query: str
    intent: IntentResult
    entities: List[EntityResult]
    response: str
    data: Optional[Dict[str, Any]] = None
    source: Optional[str] = None