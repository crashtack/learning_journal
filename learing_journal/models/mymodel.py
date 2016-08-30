from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
    UnicodeText,
    Unicode,
    Date,
)

from .meta import Base


class MyModel(Base):
    __tablename__ = 'models'
    id = Column(Integer, primary_key=True)
    title = Column(Unicode)
    date = Column(Unicode)
    body = Column(UnicodeText)


# TODO: test the unique=True statement
Index('my_index', MyModel.title, unique=True, mysql_length=255)
