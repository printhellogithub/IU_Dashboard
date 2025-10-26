# Testprogramm zum Testen der Datenbankspeicherung
# ? python.analysis.typeCheckingMode ?

from sqlalchemy import ForeignKey, create_engine
from sqlalchemy import text

engine = create_engine("sqlite+pysqlite:///:memory:", echo=True)

# "commit as you go"
with engine.connect() as conn:
    result = conn.execute(text("CREATE TABLE some_table (x int, y int)"))
    conn.execute(
        text("INSERT INTO some_table (x, y) VALUES (:x, :y)"),
        [{"x": 1, "y": 1}, {"x": 2, "y": 4}],
    )
    conn.commit()


# "begin once"
with engine.begin() as conn:
    conn.execute(
        text("INSERT INTO some_table (x, y) VALUES (:x, :y)"),
        [{"x": 6, "y": 8}, {"x": 9, "y": 10}],
    )

# Zeilen abrufen
with engine.connect() as conn:
    result = conn.execute(text("SELECT x, y FROM some_table"))
    for row in result:
        print(f"x: {row.x}  y: {row.y}")


# ORM
from sqlalchemy.orm import Session

stmt = text("SELECT x, y FROM some_table WHERE y > :y ORDER BY x, y")
with Session(engine) as session:
    result = session.execute(stmt, {"y": 6})
    for row in result:
        print(f"x: {row.x}  y: {row.y}")


with Session(engine) as session:
    result = session.execute(
        text("UPDATE some_table SET y=:y WHERE x=:x"),
        [{"x": 9, "y": 11}, {"x": 13, "y": 15}],
    )
    session.commit()

from sqlalchemy import MetaData

metadata_obj = MetaData()

from sqlalchemy import String
# user_table = Table(
#    "user_account",
#    metadata_obj,
#    Column("id", Integer, primary_key=True),
#    Column("name", String(30)),
#    Column("fullname", String),
# )

# from sqlalchemy import ForeignKey
# address_table = Table(#
#    "address",
#    metadata_obj,
#    Column("id", Integer, primary_key=True),
#    Column("user_id", ForeignKey("user_account.id"), nullable=False),
#    Column("email_address", String, nullable=False),
# )
#
# metadata_obj.create_all(engine)

# ORM

from sqlalchemy.orm import DeclarativeBase
from typing import List, Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user_account"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    fullname: Mapped[Optional[str]]

    addresses: Mapped[List["Address"]] = relationship(back_populates="user")

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, name={self.name!r}, fullname={self.fullname!r})"


class Address(Base):
    __tablename__ = "address"

    id: Mapped[int] = mapped_column(primary_key=True)
    email_address: Mapped[str]
    user_id = mapped_column(ForeignKey("user_account.id"), nullable=False)

    user: Mapped[User] = relationship(back_populates="addresses")

    def __repr__(self):
        return f"Address(id={self.id!r}, email_address={self.email_address!r})"


Base.metadata.create_all(engine)
