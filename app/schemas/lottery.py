from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime, date
from typing import Annotated
from uuid import UUID


class LotteryCreate(BaseModel):
    closure_date: Annotated[date, Field(..., title='Lottery closure date')]
    name: Annotated[str | None, Field(default=None, title='Lottery name')]


class LotteryRead(BaseModel):
    id: UUID
    name: str
    closure_date: date
    is_closed: bool
    created_at: datetime
    winning_ballot_id: UUID | None

    model_config = ConfigDict(from_attributes=True)
