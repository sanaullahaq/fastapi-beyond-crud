from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRY_SECONDS: int
    REFRESH_TOKEN_EXPIRY_DAYS: int
    REDIS_URL:str
    JTI_EXPIRY_SECONDS: int
    DB_ECHO: bool
    """
        This should match (or slightly exceed) your JWT's access-token expiry time.
        Once the original token would have expired anyway, there's no point keeping it in the blocklist — it's already invalid on its own.
        This keeps Redis memory from growing forever with stale entries.
    """

    MAIL_USERNAME: str
    MAIL_PASSWORD: SecretStr
    MAIL_FROM: str
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_FROM_NAME: str
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True
    DOMAIN: str
    
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"      #ignore any extra attributes provided within our Settings class.
    )

Config = Settings()