import datetime
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.sql import expression as sql_exp
from sqlalchemy.sql import func as sql_func
from starlette.status import HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND, HTTP_409_CONFLICT

from app.database import models as m
from app.utils.auth import resolve_access_token, validate_user_role
from app.utils.ctx import Context

router = APIRouter(prefix="/boards", tags=["boards"])


class GetBoardResponse(BaseModel):
    id: int
    title: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    written_user_id: int | None

    class Config:
        orm_mode = True

    """
    [데이터의 구조를 정의하는 (사용자)인터페이스]
    1. 보여주면 안되는 필드 있을 수 있음
    2. 새로운 필드를 넣어주기도 함
    3. 1:1 매칭이 되지 않을 수 있다.
    """


@router.get("/{board_id}")
async def get_board(board_id: int):
    board: m.Board = await Context.current.db.session.scalar(
        sql_exp.select(m.Board).where(m.Board.id == board_id)
    )

    if board is None:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail=f"Board ID as {board_id} is not found.",
        )

    return GetBoardResponse.from_orm(board)


class SearchBoardRequest(BaseModel):
    # filter (query parameters)
    written_user_id: int | None
    title: str | None
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
async def search_board(q: SearchBoardRequest):
    board_query = sql_exp.select(m.Board)

    if q.written_user_id is not None:
        board_query = board_query.where(m.Board.written_user_id == q.written_user_id)
    if q.title is not None:
        board_query = board_query.where(m.Board.title.ilike(q.title))

    board_cnt: int = await Context.current.db.session.scalar(
        # sql_exp.select(sql_func.count()).select_from(board_query)
        sql_exp.select(sql_func.count()).select_from(board_query.subquery())  # after
    )

    board_query = board_query.order_by(
        getattr(getattr(m.Board, q.sort_by), q.sort_direction)()
    )
    if q.sort_direction == "asc":
        board_query = board_query.order_by(getattr(m.Board, q.sort_by).asc())
    else:  # "desc"
        board_query = board_query.order_by(getattr(m.Board, q.sort_by).desc())

    board_query = board_query.offset(q.offset).limit(q.count)
    boards = (await Context.current.db.session.scalars(board_query)).all()

    return SearchBoardResponse(
        boards=[GetBoardResponse.from_orm(board) for board in boards],
        count=board_cnt,
    )


class PostBoardRequest(BaseModel):
    title: str


class PostBoardResponse(BaseModel):
    board_id: int


@router.post("/")
async def create_board(
    q: PostBoardRequest,
    user_id: int = Depends(resolve_access_token),
):
    await validate_user_role(user_id, m.UserRoleEnum.Admin)

    board = m.Board(
        title=q.title,
        written_user_id=user_id,
    )

    is_title_exist = await Context.current.db.session.scalar(
        sql_exp.exists().where(m.Board.title == q.title).select()
    )
    if is_title_exist:
        raise HTTPException(
            status_code=HTTP_409_CONFLICT, detail="This board title already exists."
        )

    Context.current.db.session.add(board)
    await Context.current.db.session.commit()

    return PostBoardResponse(board_id=board.id)


@router.put("/{board_id:int}")
async def update_board(
    board_id: int,
    q: PostBoardRequest,
    user_id: int = Depends(resolve_access_token),
):
    await validate_user_role(user_id, m.UserRoleEnum.Admin)

    board: m.Board | None = (
        await Context.current.db.session.execute(
            sql_exp.select(m.Board).where(m.Board.id == board_id)
        )
    ).scalar_one_or_none()

    if board is None:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="Board not found.",
        )

    if board.written_user_id != user_id:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="This is not your board. Therefore, it cannot be updated.",
        )

    board.title = q.title

    Context.current.db.session.add(board)
    await Context.current.db.session.commit()


@router.delete("/{board_id:int}")
async def delete_board(
    board_id: int,
    user_id: int = Depends(resolve_access_token),
):
    await validate_user_role(user_id, m.UserRoleEnum.Admin)

    board: m.Board | None = (
        await Context.current.db.session.execute(
            sql_exp.select(m.Board).where(m.Board.id == board_id)
        )
    ).scalar_one_or_none()

    if board is None:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="Board not found.",
        )

    if board.written_user_id != user_id:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="This is not your board. Therefore, it cannot be deleted.",
        )

    await Context.current.db.session.delete(board)
    await Context.current.db.session.commit()
