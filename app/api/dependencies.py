from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session
from jose import jwt, JWTError
from uuid import UUID

from app.core.config import settings
from app.core.db import engine
from app.domain.models.user import User
from app.domain.services import UserService
from app.domain.services import LotteryService
from app.domain.services import BallotService
from app.domain.exceptions import UserNotFound


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# database session dependency
def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session

# service dependencies
def get_user_service(session: Session = Depends(get_session)) -> UserService:
    return UserService(session)

def get_lottery_service(session: Session = Depends(get_session)) -> LotteryService:
    return LotteryService(session)

def get_ballot_service(session: Session = Depends(get_session)) -> BallotService:
    return BallotService(session)

# current user dependency
def get_current_user(
    token: str = Depends(oauth2_scheme),
    service: UserService = Depends(get_user_service),
) -> User:
    """
    Get the current user from the token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if not user_id:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    try:
        user = service.get_user(UUID(user_id))
    except UserNotFound:
        raise credentials_exception

    return user

# admin dependency
def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency to require admin privileges.
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    return current_user
