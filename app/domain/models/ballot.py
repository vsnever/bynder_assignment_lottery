from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime, timezone
from uuid import UUID, uuid4


class Ballot(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="user.id")
    lottery_id: UUID = Field(foreign_key="lottery.id")
    submitted_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    user: "User" = Relationship(back_populates="ballots")
    lottery: "Lottery" = Relationship(back_populates="ballots")

# cross-reference resolution
from .user import User
from .lottery import Lottery