from pydantic import BaseModel
from typing import List, Optional, Any, Dict

class QueryRequest(BaseModel):
    query: str
    user_id: Optional[int] = None

class QueryResponse(BaseModel):
    sql: Optional[str] = None
    results: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None
    clarification_needed: bool = False
    clarification_question: Optional[str] = None

class ClarificationResponse(BaseModel):
    query_id: int
    user_response: str
