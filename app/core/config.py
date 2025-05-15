from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Settings for the application.
    """
    model_config = {"env_prefix": "",}

    # database setting
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: str = "5432"
    
    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    # OAuth2 security settings
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    # Lottery admin settings
    LOTTERY_ADMIN_USERNAME: str
    LOTTERY_ADMIN_EMAIL: str
    LOTTERY_ADMIN_PASSWORD: str

    # metadata
    PROJECT_NAME: str = "Bynder Lottery Service"
    VERSION: str

settings = Settings()