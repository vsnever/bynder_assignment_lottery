from sqlmodel import SQLModel, create_engine, Session, select
from app.core.config import settings
from app.core.security import hash_password
from app.domain.models import User

engine = create_engine(settings.DATABASE_URL, echo=False)

def init_db():
    """
    Initialize the database and create tables.
    Adds a lottery admin user if it doesn't exist.
    """
    SQLModel.metadata.create_all(engine)

    # Add admin user if not exist
    with Session(engine) as session:
        stmt = select(User).where(User.email == settings.LOTTERY_ADMIN_EMAIL)
        existing_user = session.exec(stmt).first()
        if not existing_user:
            admin_user = User(
                username=settings.LOTTERY_ADMIN_USERNAME,
                email=settings.LOTTERY_ADMIN_EMAIL,
                hashed_password=hash_password(settings.LOTTERY_ADMIN_PASSWORD),
                is_admin=True
            )
            session.add(admin_user)
            session.commit()
            session.refresh(admin_user)