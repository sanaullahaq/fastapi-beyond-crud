from datetime import datetime
from typing import List
import uuid

from pydantic import BaseModel


class TagOut(BaseModel):
    uid: uuid.UUID
    name: str
    created_at: datetime


class TagCreate(BaseModel):
    name: str


class TagAdd(BaseModel):
    tags: List[TagCreate]