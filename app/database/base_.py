from typing import TYPE_CHECKING
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import Column, FetchedValue, Sequence
from sqlalchemy import text as sql_text
from sqlalchemy import Column, TIMESTAMP
from sqlalchemy.orm import object_session



# if TYPE_CHECKING:
from sqlalchemy.sql.schema import ColumnCollectionConstraint, MetaData, Table
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm.session import Session


# ModelMeta 사용하려면, alembic > env.py 에서 설정 해줘야함
ModelMeta: DeclarativeMeta = declarative_base()


class ModelBase(ModelMeta):
    __abstract__ = True

    __table__: Table
    metadata: MetaData

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

    @property
    def object_session(self) -> Session:
        return object_session(self)  # type: ignore
