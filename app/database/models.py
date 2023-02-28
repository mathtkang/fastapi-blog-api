import enum
import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, TIMESTAMP
from sqlalchemy import text as sql_text
from sqlalchemy import orm as sql_orm
from sqlalchemy.schema import FetchedValue
from sqlalchemy.orm import ColumnProperty, relationship, backref
from sqlalchemy.sql import expression as sa_exp
from sqlalchemy.sql import func as sa_func
from sqlalchemy.ext.declarative import declarative_base
from app.utils.blob import get_image_url
import asyncio
from async_property import async_property

from app.database.base_ import ModelBase


# orm 매핑 함수 선언
# Base = declarative_base()  # (sqlalchemy==1.4)

# class Base:
#     __allow_unmapped__ = True

# Base = declarative_base(cls=Base)  # (sqlalchemy==2.0) ref.https://docs.sqlalchemy.org/en/14/changelog/migration_20.html


TZ_UTC = datetime.timezone.utc


class UserRoleEnum(int, enum.Enum):
    Owner = 50
    Admin = 25
    User = 0


class Board(ModelBase):
    __tablename__ = "board"

    id = Column(Integer, primary_key=True)
    title = Column(String(150), nullable=False, unique=True)
    written_user_id = Column(Integer, ForeignKey("user.id"), index=True, nullable=False)
    written_user = relationship("User", uselist=False)  # relationship: orm 에서만, db에 들어가지 않음
    posts = relationship("Post", uselist=True, back_populates="board", cascade="all")

    def __repr__(self):
        # `Board(id={self.id}, board_name={self.board_name}, )`
        result = f"Board(id={self.id!r}, board_name={self.board_name!r}, )"
        return result


class Post(ModelBase):
    __tablename__ = "post"

    id = Column(Integer, primary_key=True)
    title = Column(String(150), nullable=False)
    content = Column(Text, nullable=True, default=None)
    written_user_id = Column(Integer, ForeignKey("user.id"), index=True, nullable=False)
    written_user = relationship("User", uselist=False)
    board_id = Column(Integer, ForeignKey("board.id"), index=True)
    board = relationship("Board", uselist=False)
    likes = relationship("Like", uselist=True, back_populates="post", cascade="all")
    comments = relationship(
        "Comment", uselist=True, back_populates="post", cascade="all"
    )
    # hashtags = relationship("Hashtag", uselist=False, back_populates="post", cascade="all")

    like_cnt: int


class User(ModelBase):
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
        "Comment", uselist=True, back_populates="written_user", cascade="all"
    )
    
    # 만약 profile_file_url 가져와지지 않으면 'async_property' 적용

    # @async_property
    # async def profile_file_url(self) -> str | None:
    #     if self.profile_file_key is None:
    #         return None
    #     return asyncio.run(
    #         await get_image_url(self.profile_file_key)
    #     )
        # return await get_image_url(self.profile_file_key)
    
    # @property
    # def profile_file_url(self) -> str | None:
    #     if self.profile_file_key is None:
    #         return None
    #     return get_image_url(self.profile_file_key)


class Like(ModelBase):
    __tablename__ = "like"

    post_id = Column(Integer, ForeignKey("post.id"), primary_key=True)
    post = relationship("Post", uselist=False)
    user_id = Column(Integer, ForeignKey("user.id"), primary_key=True)
    user = relationship("User", uselist=False)


class Comment(ModelBase):
    __tablename__ = "comment"

    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False, default=None)
    written_user_id = Column(Integer, ForeignKey("user.id"), index=True, nullable=False)
    written_user = relationship("User", uselist=False)
    post_id = Column(Integer, ForeignKey("post.id"), index=True)
    post = relationship("Post", uselist=False)
    parent_comment_id = Column(Integer, ForeignKey("comment.id"), index=True)
    # parent_comment = relationship("Comment", uselist=False)
    children_comment = relationship(
        "Comment", 
        uselist=True, 
        backref=backref("parent_comment", remote_side=[id]), 
        cascade="all"
    )


class Hashtag(ModelBase):
    __tablename__ = "hashtag"

    name = Column(String, primary_key=True)


class PostHashTag(ModelBase):
    __tablename__ = "connect_post_hashtag"

    post_id = Column(Integer, ForeignKey("post.id"), primary_key=True)
    post = relationship("Post", uselist=False)
    hashtag_name = Column(String, ForeignKey("hashtag.name"), primary_key=True)
    hashtag = relationship("Hashtag", uselist=False)


'''
[board 오브젝트를 부를때 실행]
저장했다가 board.id로 부를때 암시적으로 board에 대한 쿼리가 실행됨
(쿼리가 실행될 때 column_property에 대한)
암시적으로 실행될 경우, column_property에 대한 쿼리는 await이 안 붙음
따라서 암시적으로 가져올때, 명시적으로 부르지 않는이상 이 값을 가져오지 않도록 하면 됨 (deferred=True,)
'''
Post.like_cnt = sql_orm.column_property(
    (
        sa_exp.select(sa_func.count(Like.user_id))
        .where(Like.post_id == Post.id)
        .correlate_except(Like)
        .scalar_subquery()
    ),
    deferred=True,
)