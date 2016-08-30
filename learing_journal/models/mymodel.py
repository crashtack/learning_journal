from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
    UnicodeText,
    Unicode,
    Date,
    DateTime,
)

from .meta import Base


# TODO: change the DATETIME type to a time format
class MyModel(Base):
    __tablename__ = 'models'
    id = Column(Integer, primary_key=True)
    title = Column(Unicode)
    date = Column(DateTime)      # date = Column(DATETIME)
    body = Column(UnicodeText)
    date_last_updated = Column(DateTime)


# TODO: test the unique=True statement
Index('my_index', MyModel.date, unique=True, mysql_length=255)
