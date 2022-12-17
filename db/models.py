from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, TIMESTAMP
from sqlalchemy import text as sql_text
from sqlalchemy.orm import sessionmaker
import datetime
from sqlalchemy.schema import FetchedValue
import enum


# orm 매핑 함수 선언
Base = declarative_base()

TZ_UTC = datetime.timezone.utc


# TODO -> 1:1 or n:m 
# https://docs.sqlalchemy.org/en/20/orm/basic_relationships.html#one-to-many

class UserRoleEnum(int, enum.Enum):
    Owner = 50
    Admin = 25
    User = 0



class Board(Base):
    __tablename__ = "board"

    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=sql_text("CURRENT_TIMESTAMP"),
        nullable=False, 
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=sql_text("CURRENT_TIMESTAMP"),
        server_onupdate=FetchedValue()
    )

    # created_user_id = Column(Integer, ForeignKey("user.id"), index=True)

    def __repr__(self):
        # `Board(id={self.id}, board_name={self.board_name}, )`
        result = f"Board(id={self.id!r}, board_name={self.board_name!r}, )"
        return result


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    email = Column(String(150), nullable=False)
    password = Column(String(256), nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=sql_text("CURRENT_TIMESTAMP"),
        nullable=False, 
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=sql_text("CURRENT_TIMESTAMP"),
        server_onupdate=FetchedValue()
    )
    role = Column(Integer, nullable=False, default=UserRoleEnum.User)
    



# class Post(Base):
#     __tablename__ = "post"
#     title = Column(String(150), nullable=False)
#     content = Column(Text, nullable=True, default=None)
#     created_at = Column(
#         DateTime, nullable=False, default=lambda: datetime.datetime.now(TZ_UTC)
#     )
#     updated_at = Column(
#         DateTime,
#         nullable=False,
#         default=lambda: datetime.datetime.now(TZ_UTC),
#         onupdate=lambda: datetime.datetime.now(TZ_UTC),
#     )

#     written_user_id = Column(Integer, ForeignKey("user.id"), index=True)
#     board_id = Column(Integer, ForeignKey("board.id"), index=True)


# class Like(Base):
#     __tablename__ = "like"

#     post_id = Column(Integer, ForeignKey("post.id"), index=True)
#     user_id = Column(Integer, ForeignKey("user.id"), index=True)


# class Comment(Base):
#     __tablename__ = "comment"

#     content = Column(Text, nullable=True)

#     user_id = Column(Integer, ForeignKey("user.id"), index=True)
#     post_id = Column(Integer, ForeignKey("post.id"), index=True)
#     parent_comment_id = Column(Integer, ForeignKey("post.id"), index=True)
#     # TODO: 재귀 FK search
#     # models.ForeignKey(
#     #     "self",
#     #     on_delete=models.CASCADE,
#     #     blank=True,
#     #     null=True,  # nullable
#     # )
#     created_at = Column(DateTime, nullable=False)
#     updated_at = Column(DateTime, nullable=False)


