from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID, uuid4
from datetime import datetime, timezone


class User(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    username: str = Field(index=True, nullable=False)
    email: str = Field(unique=True, index=True, nullable=False)
    hashed_password: str
    is_admin: bool = Field(default=False)
    registered_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    ballots: list["Ballot"] = Relationship(back_populates="user")

# cross-reference resolution
from .ballot import Ballot
