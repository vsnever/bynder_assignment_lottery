from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime, date


class BallotRead(BaseModel):
    id: UUID
    user_id: UUID
    lottery_id: UUID
    submitted_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BallotLotteryInfo(BaseModel):
    id: UUID
    name: str
    closure_date: date

    model_config = ConfigDict(from_attributes=True)


class BallotUserInfo(BaseModel):
    id: UUID
    username: str

    model_config = ConfigDict(from_attributes=True)


class WinnerBallotRead(BaseModel):
    id: UUID
    user: BallotUserInfo
    lottery: BallotLotteryInfo
    submitted_at: datetime

    model_config = ConfigDict(from_attributes=True)
