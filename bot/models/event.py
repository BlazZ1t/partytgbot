from pydantic import BaseModel, Field
from typing import List, Dict
from datetime import datetime

class GuestInfo(BaseModel):
    guest_id: int
    inviter_id: int
    joined_at: datetime

class InviteLink(BaseModel):
    link_code: str
    inviter_id: int
    created_at: datetime
    expires_at: datetime

class Event(BaseModel):
    id: str = Field(..., alias="_id")
    name: str
    description: str
    district: str
    event_datetime: datetime
    address: str
    created_at: datetime
    expired: bool
    canceled: bool
    capacity: int
    host_id: int
    guests: List[GuestInfo] = []
    invite_links: List[InviteLink] = []

    class Config:
        validate_by_name = True