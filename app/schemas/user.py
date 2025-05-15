from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Annotated
from uuid import UUID
from datetime import datetime


class UserCreate(BaseModel):
    email: Annotated[EmailStr, Field(title='Email address')]
    username: Annotated[str, Field(min_length=3, max_length=50, title='User name')]
    password: Annotated[str, Field(min_length=8, title='User password')]


class UserRead(BaseModel):
    id: UUID
    email: EmailStr
    username: str
    registered_at: datetime

    model_config = ConfigDict(from_attributes=True)
