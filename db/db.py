from sqlalchemy import create_engine
from sqlalchemy.sql import expression as sa_exp
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
)

engine = create_async_engine(
    "postgresql+asyncpg://practice:devpassword@localhost:35000/fastapi-practice"
)  # 연결완료 (Singleton pattern)
# <user>:<password>@<localhost>:<port>:<databaseName>


# with engine.connect() as conn:
#     # result = conn.execute(sa_exp.select([1]))
#     # print(result.scalar())

#     # conn.execute(text("CREATE TABLE some_table (x int, y int)"))

#     # conn.execute(
#     #     text("INSERT INTO some_table (x, y) VALUES (:x, :y)"),
#     #     [{"x": 1, "y": 1}, {"x": 2, "y": 4}],
#     # )
#     # conn.commit()

#     result = conn.execute(text("SELECT x, y FROM some_table"))
#     for row in result:
#         print(f"x: {row.x}  y: {row.y}")


async def get_session() -> AsyncSession:
    async with AsyncSession(engine) as session:
        yield session
