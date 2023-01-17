from fastapi import Depends, HTTPException, APIRouter
from db.db import get_session
from utils.auth import resolve_access_token, validate_user_role
from sqlalchemy.ext.asyncio import AsyncSession as Session
import db.models as m
from sqlalchemy.sql import expression as sql_exp
from pydantic import BaseModel
import datetime
from starlette.status import HTTP_404_NOT_FOUND, HTTP_403_FORBIDDEN
from typing import Literal

router = APIRouter(prefix="/boards", tags=["boards"])


class GetBoardResponse(BaseModel):
    id: int
    name: str
    created_at: datetime.datetime
    updated_at: datetime.datetime

    """
    데이터의 구조를 정의하는 (사용자)인터페이스
    1. 보여주면 안되는 필드 있을 수 있음
    2. 새로운 필드를 넣어주기도 함
    3. 1:1 매칭이 되지 않을 수 있다.
    """


@router.get("/")
def read_board(session: Session = Depends(get_session)):
    boards: list[m.Board] = (session.scalars(sql_exp.select(m.Board))).all()

    # return [
    #     GetBoardResponse(
    #         id=board.id,
    #         name=board.name,
    #         created_at=board.created_at,
    #         updated_at=board.updated_at,
    #     )
    #     for board in boards
    # ]
    return [GetBoardResponse.from_orm(board) for board in boards]


@router.get("/{board_id}")
def get_board(
    board_id: int,
    session: Session = Depends(get_session),
):
    board: m.Board = session.scalar(
        sql_exp.select(m.Board).where(m.Board.id == board_id)
    )

    if board is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="post not found")

    return GetBoardResponse.from_orm(board)


class SearchBoardRequest(BaseModel):
    # filter (query parameters)
    like_user_id: int | None
    written_user_id: int | None
    board_id: int | None
    # sort
    sort_by: Literal["created_at"] | Literal["updated_at"] | Literal[
        "written_user_id"
    ] = "created_at"
    sort_direction: Literal["asc"] | Literal["desc"] = "asc"
    # pagination
    offset: int = 0
    count: int = 20


class SearchBoardResponse(BaseModel):
    posts: list[GetBoardResponse]
    count: int


# TODO: search board
@router.post("/search")
def search_board(
    q: SearchBoardRequest,
    session: Session = Depends(get_session),
):
    pass



class PostBoardRequest(BaseModel):
    name: str


@router.post("/")
async def create_board(
    q: PostBoardRequest,
    session: Session = Depends(get_session),
    user_id: int = Depends(resolve_access_token),
):
    validate_user_role(user_id, m.UserRoleEnum.Admin, session)

    board = m.Board(
        name=q.name,
    )

    session.add(board)
    await session.commit()


@router.put("/{board_id:int}")
async def update_board(
    board_id: int,
    q: PostBoardRequest,
    session: Session = Depends(get_session),
    user_id: int = Depends(resolve_access_token),
):
    validate_user_role(user_id, m.UserRoleEnum.Admin, session)

    board: m.Board | None = (
        await session.execute(
            sql_exp.select(m.Board).where(m.Board.id == board_id)
        )
    ).scalar_one_or_none()

    if board is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="board not found")

    board.name = q.name

    session.add(board)
    await session.commit()


@router.delete("/{board_id:int}")
async def delete_board(
    board_id: int,
    session: Session = Depends(get_session),
    user_id: int = Depends(resolve_access_token),
):
    validate_user_role(user_id, m.UserRoleEnum.Admin, session)

    board: m.Board | None = (
        await session.execute(
            sql_exp.select(m.Board).where(m.Board.id == board_id)
        )
    ).scalar_one_or_none()

    if board is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="board not found")

    await session.delete(board)
    await session.commit()
