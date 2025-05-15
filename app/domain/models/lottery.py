from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID, uuid4
from datetime import datetime, date, timezone


class Lottery(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field()
    closure_date: date = Field(index=True, unique=True)
    is_closed: bool = Field(default=False)
    winning_ballot_id: UUID | None = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    ballots: list["Ballot"] = Relationship(back_populates="lottery")

# cross-reference resolution
from .ballot import Ballot