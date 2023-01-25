from sqlalchemy import Column, Text, Float, SmallInteger, BigInteger, Date, \
    DateTime, VARCHAR, CHAR, Time, Boolean
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship

from pydatabasecli.const import PYDBCLI_DATABASE_URL

Base = declarative_base()


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    name = Column(String(30))
    fullname = Column(String)
    addresses = relationship(
        "Address", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"User(id={self.id!r}, name={self.name!r}, fullname={self.fullname!r})"


class Address(Base):
    __tablename__ = "address"
    id = Column(Integer, primary_key=True)
    email_address = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    user = relationship("User", back_populates="addresses")

    def __repr__(self):
        return f"Address(id={self.id!r}, email_address={self.email_address!r})"


class BasicTypes(Base):
    __tablename__ = "basic_type"
    id = Column(Integer, primary_key=True)  # autoincrement
    int = Column(Integer)
    # smallint, bigint?
    smallint = Column(SmallInteger)
    bigint = Column(BigInteger)
    float = Column(Float)  # real
    double = Column(Float)  # TODO: Double type in sqlalchemy == ???
    text = Column(Text)
    char = Column(CHAR(8))
    varchar = Column(VARCHAR(8))
    # charN varcharN ?
    date = Column(Date)
    time = Column(Time)
    datetime = Column(DateTime)
    # TODO: also with timezones?
    bool = Column(Boolean)


engine = create_engine(PYDBCLI_DATABASE_URL, echo=True, future=True)

Base.metadata.create_all(engine)
