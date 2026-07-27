from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, AliasChoices

class Settings(BaseSettings):
    API_PORT: int = 8000
    SECRET_KEY: str = "supersecretkey-change-in-production"

    POSTGRES_USER: str = Field(default="openintel", validation_alias=AliasChoices("POSTGRES_USER", "PGUSER"))
    POSTGRES_PASSWORD: str = Field(default="openintel_pass", validation_alias=AliasChoices("POSTGRES_PASSWORD", "PGPASSWORD"))
    POSTGRES_DB: str = Field(default="openintel", validation_alias=AliasChoices("POSTGRES_DB", "PGDATABASE"))
    POSTGRES_PORT: int = Field(default=5432, validation_alias=AliasChoices("POSTGRES_PORT", "PGPORT"))
    POSTGRES_HOST: str = Field(default="postgres", validation_alias=AliasChoices("POSTGRES_HOST", "PGHOST"))
    DATABASE_URL: str | None = None

    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str | None = None
    REDIS_URL_ENV: str | None = Field(default=None, alias="REDIS_URL")

    ELASTIC_HOST: str = "elasticsearch"
    ELASTIC_PORT: int = 9200
    ELASTIC_PASSWORD: str = "elastic_pass"

    NEO4J_HOST: str = "neo4j"
    NEO4J_PORT: int = 7687
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "neo4j_pass"

    RABBITMQ_HOST: str = "rabbitmq"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "guest"
    RABBITMQ_PASSWORD: str = "guest"

    SHODAN_API_KEY: str | None = None
    HUNTER_API_KEY: str | None = None

    # Telegram Bot
    TELEGRAM_BOT_TOKEN: str = "8889115534:AAFRU4OrqpYQkqlrsSbb3eL3IsTPmUFvHk4"
    TELEGRAM_ADMIN_ID: int = 1669340183
    API_URL_FOR_BOT: str = "http://localhost:8000" # Internal URL when running in the same stack

    @property
    def async_database_url(self) -> str:
        if self.DATABASE_URL:
            # Railway provides DATABASE_URL starting with postgresql:// or postgres://
            url = self.DATABASE_URL
            if url.startswith("postgres://"):
                url = url.replace("postgres://", "postgresql+asyncpg://", 1)
            elif url.startswith("postgresql://"):
                url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
            return url
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def redis_url(self) -> str:
        if self.REDIS_URL_ENV:
            return self.REDIS_URL_ENV
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/0"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"

    @property
    def elastic_url(self) -> str:
        return f"http://{self.ELASTIC_HOST}:{self.ELASTIC_PORT}"

    @property
    def neo4j_uri(self) -> str:
        return f"bolt://{self.NEO4J_HOST}:{self.NEO4J_PORT}"

    @property
    def celery_broker_url(self) -> str:
        return f"amqp://{self.RABBITMQ_USER}:{self.RABBITMQ_PASSWORD}@{self.RABBITMQ_HOST}:{self.RABBITMQ_PORT}//"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
