from sqlmodel import Session, select
from uuid import UUID

from app.domain.models.user import User
from app.schemas.user import UserCreate
from app.core.security import hash_password, verify_password
from app.domain.exceptions import (
    UserAlreadyExists,
    UserInvalidCredentials,
    UserNotFound,
)


class UserService:
    """
    Service class to create, retrieve, and authenticate users.
    """
    
    def __init__(self, session: Session):
        self.session = session

    def register_user(self, user_data: UserCreate) -> User:

        # check if the user already exist
        stmt = select(User).where(User.email == user_data.email)
        existing_user = self.session.exec(stmt).first()
        if existing_user:
            raise UserAlreadyExists("User with this email already exists.")

        hashed_password = hash_password(user_data.password)
        user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password
        )

        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)

        return user

    def authenticate_user(self, user_email: str, user_password: str) -> User:

        user = self.get_user_by_email(user_email)

        if not user or not verify_password(user_password, user.hashed_password):
            raise UserInvalidCredentials("Invalid username/email or password.")

        return user
    
    def get_user(self, user_id: UUID) -> User:

        user = self.session.get(User, user_id)
        if not user:
            raise UserNotFound("User not found.")

        return user

    def get_user_by_email(self, email: str) -> User:

        stmt = select(User).where(User.email == email)

        result = self.session.exec(stmt).first()
        if not result:
            raise UserNotFound("User not found.")

        return result

