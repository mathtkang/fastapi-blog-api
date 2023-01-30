from pydantic import BaseSettings, PostgresDsn, Field

class AppSettings(BaseSettings):
    DATABASE_URI: PostgresDsn = Field(
        default="postgresql+asyncpg://practice:devpassword@localhost:35000/fastapi-practice",
        description="PosstgreSQL connection URI.",
    )

    AWS_ACCESS_KEY_ID: str = Field(default="", description="aws access key id")
    AWS_SECRET_ACCESS_KEY: str = Field(default="", description="aws secret access key")

    class Config:
        env_file = ".env"
        env_prefix = "app_"