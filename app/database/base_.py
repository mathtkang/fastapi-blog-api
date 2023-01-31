from typing import TYPE_CHECKING
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import Column, FetchedValue, Sequence
from sqlalchemy.sql import sqltypes
from sqlalchemy import text as sql_text
from sqlalchemy.orm import object_session



# if TYPE_CHECKING:
from sqlalchemy.sql.schema import ColumnCollectionConstraint, MetaData, Table
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm.session import Session


# orm 매핑 함수 선언
ModelMeta: DeclarativeMeta = declarative_base()


'''
(models.py -> base)
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
'''


class ModelBase(ModelMeta):
    __abstract__ = True

    __table__: Table
    metadata: MetaData

    created = Column(
        sqltypes.TIMESTAMP(timezone=True),
        nullable=False,
        server_default=sql_text("CURRENT_TIMESTAMP"),
    )
    updated = Column(
        sqltypes.TIMESTAMP(timezone=True),
        nullable=False,
        server_default=sql_text("CURRENT_TIMESTAMP"),
        server_onupdate=FetchedValue(),
    )

    @property
    def object_session(self) -> Session:
        return object_session(self)  # type: ignore
