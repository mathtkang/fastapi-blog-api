from pydantic import BaseSettings, Field, PostgresDsn

class AppSettings(BaseSettings):
    DATABASE_URL: PostgresDsn = Field(
        default="postgresql+asyncpg://practice:devpassword@localhost:35000/fastapi-practice",
        description="PosstgreSQL connection URL.",
    )
    DEBUG_ALLOW_CORS_ALL_ORIGIN: bool = Field(
        default=True,
        description="If True, allow origins for CORS requests.",
    )

    AWS_ACCESS_KEY_ID: str = Field(default="", description="aws access key id")
    AWS_SECRET_ACCESS_KEY: str = Field(default="", description="aws secret access key")

    class Config:
        env_file = ".env"
        env_prefix = "app_"