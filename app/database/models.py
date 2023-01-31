import enum
import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, TIMESTAMP
from sqlalchemy import text as sql_text
from sqlalchemy import orm as sql_orm
from sqlalchemy.schema import FetchedValue
from sqlalchemy.orm import ColumnProperty, column_property, relationship, backref
from sqlalchemy.sql import expression as sa_exp
from sqlalchemy.sql import func as sa_func
from sqlalchemy.ext.declarative import declarative_base


from .base_ import ModelBase


# class Base:
#     __allow_unmapped__ = True

# Base = declarative_base(cls=Base)

# orm 매핑 함수 선언
Base = declarative_base()

TZ_UTC = datetime.timezone.utc


class UserRoleEnum(int, enum.Enum):
    Owner = 50
    Admin = 25
    User = 0


class Board(Base):
    __tablename__ = "board"


    id = Column(Integer, primary_key=True)
    title = Column(String(150), nullable=False)
    written_user_id = Column(Integer, ForeignKey("user.id"), index=True)
    written_user = relationship("User", uselist=False)  # orm 에서만, db에 들어가지 않음
    posts = relationship("Post", uselist=True, back_populates="board", cascade="all")
    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=sql_text("CURRENT_TIMESTAMP"),
        nullable=False,
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=sql_text("CURRENT_TIMESTAMP"),
        server_onupdate=FetchedValue(),
    )

    def __repr__(self):
        # `Board(id={self.id}, board_name={self.board_name}, )`
        result = f"Board(id={self.id!r}, board_name={self.board_name!r}, )"
        return result


class Post(Base):
    __tablename__ = "post"

    id = Column(Integer, primary_key=True)
    title = Column(String(150), nullable=False)
    content = Column(Text, nullable=True, default=None)
    like_cnt: ColumnProperty
    written_user_id = Column(Integer, ForeignKey("user.id"), index=True)
    written_user = relationship("User", uselist=False)  # orm 에서만, db에 들어가지 않음
    board_id = Column(Integer, ForeignKey("board.id"), index=True)
    board = relationship("Board", uselist=False)
    likes = relationship("Like", uselist=True, back_populates="post", cascade="all")
    comments = relationship(
        "Comment", uselist=True, back_populates="post", cascade="all"
    )
    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=sql_text("CURRENT_TIMESTAMP"),
        nullable=False,
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=sql_text("CURRENT_TIMESTAMP"),
        server_onupdate=FetchedValue(),
    )
    # hashtags = relationship("Hasttag", uselist=False, back_populates="post", cascade="all")


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    email = Column(String(150), nullable=False)
    password = Column(String(256), nullable=False)
    role = Column(Integer, nullable=False, default=UserRoleEnum.User)
    profile_file_key = Column(String(255), nullable=True)
    posts = relationship(
        "Post", uselist=True, back_populates="written_user", cascade="all"
    )
    likes = relationship("Like", uselist=True, back_populates="user", cascade="all")
    comments = relationship(
        "Comment", uselist=True, back_populates="user", cascade="all"
    )
    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=sql_text("CURRENT_TIMESTAMP"),
        nullable=False,
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=sql_text("CURRENT_TIMESTAMP"),
        server_onupdate=FetchedValue(),
    )


class Like(Base):
    __tablename__ = "like"

    post_id = Column(Integer, ForeignKey("post.id"), primary_key=True)
    post = relationship("Post", uselist=False)
    user_id = Column(Integer, ForeignKey("user.id"), primary_key=True)
    user = relationship("User", uselist=False)


class Comment(Base):
    __tablename__ = "comment"

    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=True, default=None)
    user_id = Column(Integer, ForeignKey("user.id"), index=True)
    user = relationship("User", uselist=False)
    post_id = Column(Integer, ForeignKey("post.id"), index=True)
    post = relationship("Post", uselist=False)
    parent_comment_id = Column(Integer, ForeignKey("comment.id"), index=True)
    # parent_comment = relationship("Comment", uselist=False)
    children_comment = relationship(
        "Comment", uselist=True, backref=backref("parent_comment", remote_side=[id]), cascade="all"
    )
    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=sql_text("CURRENT_TIMESTAMP"),
        nullable=False,
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=sql_text("CURRENT_TIMESTAMP"),
        server_onupdate=FetchedValue(),
    )


class Hashtag(Base):
    __tablename__ = "hashtag"

    name = Column(String, primary_key=True)
    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=sql_text("CURRENT_TIMESTAMP"),
        nullable=False,
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=sql_text("CURRENT_TIMESTAMP"),
        server_onupdate=FetchedValue(),
    )


class PostHashTag(Base):
    __tablename__ = "connect_post_hashtag"

    post_id = Column(Integer, ForeignKey("post.id"), primary_key=True)
    post = relationship("Post", uselist=False)
    hashtag_name = Column(String, ForeignKey("hashtag.name"), primary_key=True)
    hashtag = relationship("Hashtag", uselist=False)


Post.like_cnt = sql_orm.column_property(
    sa_exp.select(sa_func.count(Like.user_id))
    .where(Like.post_id == Post.id)
    .correlate_except(Like)
    .scalar_subquery()
)