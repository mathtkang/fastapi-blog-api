from fastapi import Depends, HTTPException, APIRouter
from app.database.db import get_session
from app.utils.auth import resolve_access_token, validate_user_role
from sqlalchemy.ext.asyncio import AsyncSession as Session
from app.database import models as m
from sqlalchemy.sql import expression as sql_exp
from pydantic import BaseModel
import datetime
from starlette.status import HTTP_404_NOT_FOUND, HTTP_403_FORBIDDEN
from typing import Literal
from sqlalchemy.sql import func as sql_func

router = APIRouter(prefix="/boards", tags=["boards"])


class GetBoardResponse(BaseModel):
    id: int
    title: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    written_user_id: int

    class Config:
        orm_mode = True

    """
    [데이터의 구조를 정의하는 (사용자)인터페이스]
    1. 보여주면 안되는 필드 있을 수 있음
    2. 새로운 필드를 넣어주기도 함
    3. 1:1 매칭이 되지 않을 수 있다.
    """


@router.get("/{board_id}")
async def get_board(
    board_id: int,
    session: Session = Depends(get_session),
):
    board: m.Board = await session.scalar(
        sql_exp.select(m.Board).where(m.Board.id == board_id)
    )

    if board is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="post not found")

    return GetBoardResponse.from_orm(board)


class SearchBoardRequest(BaseModel):
    # filter (query parameters)
    written_user_id: int | None
    # sort
    sort_by: Literal["created_at"] | Literal["updated_at"] | Literal[
        "written_user_id"
    ] = "created_at"
    sort_direction: Literal["asc"] | Literal["desc"] = "asc"
    # pagination
    offset: int = 0
    count: int = 20


class SearchBoardResponse(BaseModel):
    boards: list[GetBoardResponse]
    count: int


@router.post("/search")
async def search_board(
    q: SearchBoardRequest,
    session: Session = Depends(get_session),
):
    board_query = sql_exp.select(m.Board)

    if q.written_user_id is not None:
        board_query = board_query.where(m.Board.written_user_id == q.written_user_id)

    board_cnt: int = await session.scalar(
        sql_exp.select(sql_func.count()).select_from(board_query)
    )

    board_query = board_query.order_by(
        getattr(getattr(m.Board, q.sort_by), q.sort_direction)()
    )
    if q.sort_direction is "asc":
        board_query = board_query.order_by(getattr(m.Board, q.sort_by).asc())
    else:  # "desc"
        board_query = board_query.order_by(getattr(m.Board, q.sort_by).desc())

    board_query = board_query.offset(q.offset).limit(q.count)

    boards = (await session.scalars(board_query)).all()

    return SearchBoardResponse(
        boards=[GetBoardResponse.from_orm(board) for board in boards],
        count=board_cnt,
    )


class PostBoardRequest(BaseModel):
    title: str


@router.post("/")
async def create_board(
    q: PostBoardRequest,
    session: Session = Depends(get_session),
    user_id: int = Depends(resolve_access_token),
):
    validate_user_role(user_id, m.UserRoleEnum.Admin, session)

    board = m.Board(
        title=q.title,
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

    board.title = q.title

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
