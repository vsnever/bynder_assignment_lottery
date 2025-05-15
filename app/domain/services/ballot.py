from uuid import UUID
from sqlmodel import Session, select

from app.domain.models import User, Lottery, Ballot
from app.domain.exceptions import (
    LotteryAlreadyClosed,
    BallotNotFound,
)


class BallotService:
    """
    Service class to handle ballot operations.
    This includes submitting a ballot, retrieving a ballot, and
    retrieving ballots by user or lottery.
    """

    def __init__(self, session: Session):
        self.session = session

    def submit_ballot(self, user: User, lottery: Lottery) -> Ballot:

        if lottery.is_closed:
            raise LotteryAlreadyClosed("Cannot submit ballot to a closed lottery.")

        ballot = Ballot(user_id=user.id, lottery_id=lottery.id)
        self.session.add(ballot)
        self.session.commit()
        self.session.refresh(ballot)

        return ballot

    def get_ballot(self, ballot_id: UUID) -> Ballot:

        ballot = self.session.get(Ballot, ballot_id)
        if not ballot:
            raise BallotNotFound(f"Ballot with id {ballot_id} not found.")

        return ballot
    
    def get_ballots_by_user(self, user: User) -> list[Ballot]:

        statement = select(Ballot).where(Ballot.user_id == user.id)

        return self.session.exec(statement).all()

    def get_ballots_by_lottery(self, lottery: Lottery) -> list[Ballot]:

        statement = select(Ballot).where(Ballot.lottery_id == lottery.id)

        return self.session.exec(statement).all()

