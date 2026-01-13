from typing import List, Optional
from pydantic import BaseModel


class Entity(BaseModel):
    type: str
    value: str
    start: int
    end: int


class Content(BaseModel):
    text: str
    entities: List[Entity]


class RedactRequest(BaseModel):
    customer_id: str
    policy_version: Optional[str] = None
    content: Content


class ActionResult(BaseModel):
    entity_type: str
    original_value: str
    applied_action: str
    policy_source: str
    justification: str


class RedactResponse(BaseModel):
    original_text_length: int
    redacted_text: str
    actions: List[ActionResult]



class PolicyRequest(BaseModel):
    customer_id: str
    policy_version: Optional[str] = None
    entity_type: str
        
    
class PolicyResponse(BaseModel):
    applied_action: str
    policy_source: str
    justification: str