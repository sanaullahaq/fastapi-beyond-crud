import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ReviewBase(BaseModel):
    rating: int = Field(le=5)
    review_text: str


class ReviewOut(ReviewBase):
    uid: uuid.UUID
    user_uid: Optional[uuid.UUID]
    book_uid: Optional[uuid.UUID]
    created_at: datetime
    updated_at: datetime


class ReviewCreate(ReviewBase):
    pass
