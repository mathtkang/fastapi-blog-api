from fastapi import Depends, HTTPException, APIRouter
from db.db import get_session
from utils.auth import resolve_access_token
from sqlalchemy.orm import Session
import db.models as m
from sqlalchemy.sql import expression as sql_exp
from pydantic import BaseModel
import datetime
from starlette.status import HTTP_404_NOT_FOUND, HTTP_403_FORBIDDEN

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


class PostBoardRequest(BaseModel):
    name: str


@router.get("/")
def read_board(session: Session = Depends(get_session)):
    boards: list[m.Board] = session.execute(sql_exp.select(m.Board)).scalars().all()

    return [
        GetBoardResponse(
            id=board.id,
            name=board.name,
            created_at=board.created_at,
            updated_at=board.updated_at,
        )
        for board in boards
    ]


@router.post("/")
def create_board(
    q: PostBoardRequest, 
    session: Session = Depends(get_session), 
    user_id: int = Depends(resolve_access_token),
):
    user: m.User | None = session.execute(
        sql_exp.select(m.User).where(m.User.id == user_id)
    ).scalar_one_or_none()
    if user is None :
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="user not found")

    if user.role < m.UserRoleEnum.Admin:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, 
            detail="this user has not permission to create board"
        )

    board = m.Board(
        name=q.name,
    )

    session.add(board)
    session.commit()


@router.put("/{board_id:int}")
def update_board(
    board_id: int, q: PostBoardRequest, session: Session = Depends(get_session)
):


    board: m.Board | None = session.execute(
        sql_exp.select(m.Board).where(m.Board.id == board_id)
    ).scalar_one_or_none()

    if board is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="board not found")

    board.name = q.name

    session.add(board)
    session.commit()


@router.delete("/{board_id:int}")
def delete_board(board_id: int, session: Session = Depends(get_session)):
    board: m.Board | None = session.execute(
        sql_exp.select(m.Board).where(m.Board.id == board_id)
    ).scalar_one_or_none()

    if board is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="board not found")

    session.delete(board)
    session.commit()
