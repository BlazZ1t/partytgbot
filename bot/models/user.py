from pydantic import BaseModel, Field
from typing import List
from datetime import datetime

class User(BaseModel):
    id: int = Field(..., alias="_id")
    name: str
    surname: str
    registered_at: datetime
    invited_by: int | None
    hosted_events: List[str] = []
    signed_events: List[str] = []
    invite_links: List[str] = []

    class Config:
        validate_by_name = True
    