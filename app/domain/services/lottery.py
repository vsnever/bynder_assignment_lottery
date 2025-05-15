from datetime import date
from sqlmodel import Session, select
from typing import Sequence
import random
from uuid import UUID
import namer

from app.domain.models import Lottery, Ballot
from app.schemas.lottery import LotteryCreate
from app.domain.exceptions import (
    LotteryAlreadyExists,
    LotteryNotFound,
    LotteryAlreadyClosed,
    LotteryNotClosed,
    LotteryInvalidClosureDate,
    LotteryNoWinnerDrawn
)


class LotteryService:
    """
    Service class to create, retrieve, and close lotteries and draw winners.
    """

    def __init__(self, session: Session):
        self.session = session
    
    def create_lottery(self, lottery_data: LotteryCreate) -> Lottery:

        closure_date = lottery_data.closure_date

        if closure_date < date.today():
            raise LotteryInvalidClosureDate("Cannot create a lottery in the past.")
        
        # check if a lottery already exists for the given date
        stmt = select(Lottery).where(Lottery.closure_date == closure_date)
        existing_lottery = self.session.exec(stmt).first()
        if existing_lottery:
            raise LotteryAlreadyExists(f"A lottery already exists for {closure_date}.")

        # assign a random name if not provided, e.g. "tan octopus lottery"
        name = lottery_data.name or namer.generate().replace('-', ' ') + ' lottery'

        lottery = Lottery(name=name, closure_date=closure_date)

        self.session.add(lottery)
        self.session.commit()
        self.session.refresh(lottery)

        return lottery

    def get_lottery(self, lottery_id: UUID) -> Lottery:

        lottery = self.session.get(Lottery, lottery_id)

        if not lottery:
            raise LotteryNotFound(f"Lottery with id {lottery_id} not found.")

        return lottery

    def get_lottery_by_date(self, closure_date: date) -> Lottery | None:

        stmt = select(Lottery).where(Lottery.closure_date == closure_date)
    
        lottery = self.session.exec(stmt).first()

        if not lottery:
            raise LotteryNotFound(f"Lottery with closure date {closure_date} not found.")

        return lottery

    def get_open_lotteries(self) -> Sequence[Lottery]:

        stmt = select(Lottery).where(Lottery.is_closed == False)

        return self.session.exec(stmt).all()
    
    def close_and_draw_winner(self, lottery: Lottery) -> Lottery:
        """
        Close the lottery and randomly select a winning ballot.
        """
        
        if lottery.is_closed:
            raise LotteryAlreadyClosed("Lottery is already closed.")
        
        lottery.is_closed = True

        lottery_ballots = lottery.ballots

        if lottery_ballots:
            # randomly select a ballot
            winning_ballot = random.choice(lottery_ballots)
            lottery.winning_ballot_id = winning_ballot.id
        
        self.session.add(lottery)
        self.session.commit()
        self.session.refresh(lottery)

        return lottery
    
    def get_winning_ballot(self, lottery: Lottery) -> Ballot:
        """
        Get the winning ballot for the lottery.
        If the lottery has no winning ballot, raise.
        """
        
        if not lottery.is_closed:
            raise LotteryNotClosed("Lottery is not closed.")

        if not lottery.winning_ballot_id:
            raise LotteryNoWinnerDrawn("No ballots were submitted - no winner.")

        return self.session.get(Ballot, lottery.winning_ballot_id)
    