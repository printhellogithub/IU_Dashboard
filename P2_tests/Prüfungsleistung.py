from __future__ import annotations
from sqlalchemy import Integer, Float, ForeignKey, Date
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.hybrid import hybrid_property
from enum import Enum, auto
import datetime
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine


# Basisklasse
class Base(DeclarativeBase):
    pass


class Status(Enum):
    EINGESCHRIEBEN = auto()
    ABGESCHLOSSEN = auto()
    NICHT_BESTANDEN = auto()


class DatabaseManager:
    def __init__(self):
        # Verbindung zur Datenbank
        self.engine = create_engine("sqlite+pysqlite:///test.db", echo=False)
        # Alle Tabellen erzeugen
        Base.metadata.create_all(self.engine)
        SessionLocal = sessionmaker(bind=self.engine, expire_on_commit=False)
        self.session = SessionLocal()

    def erstelle_enrollment(self) -> Enrollment:
        enrollment = Enrollment(status=Status.EINGESCHRIEBEN)
        self.session.add(enrollment)
        self.session.commit()
        # session.refresh(enrollment)
        return enrollment


class Enrollment(Base):
    __tablename__ = "enrollment"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    _status: Mapped[Status] = mapped_column(SQLEnum(Status))

    pruefungsleistungen: Mapped[list["Pruefungsleistung"]] = relationship(
        back_populates="enrollment"
    )

    @hybrid_property
    def status(self):
        return self._status

    @status.setter
    def status(self, value: Status):
        self._status = value

    def add_pruefungsleistung(self, note: float, datum: datetime.date):
        if len(self.pruefungsleistungen) > 3:
            raise ValueError(
                "Ein Enrollment darf höchstens 3 Prüfungsleistungen haben."
            )
        versuch = int(len(self.pruefungsleistungen) + 1)
        self.pruefungsleistungen.append(Pruefungsleistung(versuch, note, datum))
        self.change_status()

    def change_status(self):
        if self.pruefungsleistungen:
            for pruefungsleistung in self.pruefungsleistungen:
                if pruefungsleistung.pruefung_bestanden():
                    self.status = Status.ABGESCHLOSSEN
            if (
                len(self.pruefungsleistungen) == 3
                and self.status is not Status.ABGESCHLOSSEN
            ):
                self.status = Status.NICHT_BESTANDEN


class Pruefungsleistung(Base):
    __tablename__ = "pruefungsleistung"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    versuch: Mapped[int] = mapped_column(Integer)
    note: Mapped[float] = mapped_column(Float)
    datum: Mapped[datetime.date] = mapped_column(Date)

    enrollment_id: Mapped[int] = mapped_column(
        ForeignKey("enrollment.id"), nullable=False
    )

    enrollment: Mapped[Enrollment] = relationship(back_populates="pruefungsleistungen")

    def __init__(self, versuch, note, datum):
        self.versuch = versuch
        self.note = note
        self.datum = datum

    def pruefung_bestanden(self):
        if self.note > 4.0:
            return False
        else:
            return True

    def __repr__(self) -> str:
        return f"PL Versuch {self.versuch}, Note {self.note}, Datum {self.datum}"


class Test:
    def __init__(self):
        self.db = DatabaseManager()

    def run(self):
        enroll1 = self.db.erstelle_enrollment()
        print(enroll1.pruefungsleistungen)
        print(f"enroll1 status ohne PL == {enroll1.status}")
        enroll1.add_pruefungsleistung(2.3, datetime.date(2025, 3, 13))
        print(f"enroll1 status nach PL == {enroll1.status}")
        print(enroll1.pruefungsleistungen)

        enroll2 = self.db.erstelle_enrollment()
        print(f"enroll2: {enroll2.pruefungsleistungen}")
        print(f"enroll2 status vor PL == {enroll2.status}")
        enroll2.add_pruefungsleistung(5.0, datetime.date(2025, 4, 25))
        print(f"enroll2 status nach PL mit 5.0 == {enroll2.status}")
        enroll2.add_pruefungsleistung(3.4, datetime.date(2025, 6, 21))
        print(f"enroll2 status nach V2 mit 3.4 == {enroll2.status}")
        print(enroll2.pruefungsleistungen)

        enroll3 = self.db.erstelle_enrollment()
        print(f"enroll3: {enroll3.pruefungsleistungen}")
        print(f"enroll3 status vor PL == {enroll3.status}")
        enroll3.add_pruefungsleistung(5.0, datetime.date(2025, 4, 25))
        print(f"enroll3 status nach PL mit 5.0 == {enroll3.status}")
        enroll3.add_pruefungsleistung(4.3, datetime.date(2025, 6, 21))
        print(f"enroll3 status nach V2 mit 4.3 == {enroll3.status}")
        enroll3.add_pruefungsleistung(4.1, datetime.date(2025, 6, 25))
        print(f"enroll3 status nach V3 mit 4.1 == {enroll3.status}")
        # Teste ob 4. PL hinzugefügt werden kann - ValueError erfolgreich raised.
        # enroll3.add_pruefungsleistung(4.8, datetime.date(2025, 6, 21))
        # print(f"enroll3 status nach V4 mit 4.8 == {enroll3.status}")
        print(enroll3.pruefungsleistungen)


if __name__ == "__main__":
    app = Test()
    app.run()
