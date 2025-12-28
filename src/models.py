from __future__ import annotations
from sqlalchemy import Integer, String, Float, Date, ForeignKey
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.hybrid import hybrid_property
from typing import List, Optional
from enum import Enum, auto
from email_validator import validate_email, EmailNotValidError
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from datetime import date

TODAY = date.today()

ph = PasswordHasher()


# Basisklasse
class Base(DeclarativeBase):
    pass


# ENUM-Klassen
class EnrollmentStatus(Enum):
    IN_BEARBEITUNG = auto()
    ABGESCHLOSSEN = auto()
    NICHT_BESTANDEN = auto()


class SemesterStatus(Enum):
    ZURUECKLIEGEND = auto()
    AKTUELL = auto()
    ZUKUENFTIG = auto()


# Entity-Klassen
class Student(Base):
    __tablename__ = "student"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    _name: Mapped[str] = mapped_column(String)
    _matrikelnummer: Mapped[str] = mapped_column(String)
    _email: Mapped[str] = mapped_column(String, unique=True)
    _password: Mapped[str] = mapped_column("password", String)

    _ziel_note: Mapped[float] = mapped_column(Float)
    _start_datum: Mapped[date] = mapped_column(Date)
    _ziel_datum: Mapped[date] = mapped_column(Date)
    _exmatrikulationsdatum: Mapped[Optional[date]] = mapped_column(
        Date, nullable=True, default=None
    )

    hochschule_id = mapped_column(ForeignKey("hochschule.id"))
    hochschule: Mapped[Hochschule] = relationship(back_populates="studenten")

    studiengang_id = mapped_column(ForeignKey("studiengang.id"))
    studiengang: Mapped[Studiengang] = relationship(back_populates="studenten")

    _semester_anzahl: Mapped[int] = mapped_column(Integer)
    semester: Mapped[List["Semester"]] = relationship(
        back_populates="student",
        cascade="all, delete-orphan",
    )

    _modul_anzahl: Mapped[int] = mapped_column(Integer)

    enrollments: Mapped[List["Enrollment"]] = relationship(
        back_populates="student",
        cascade="all, delete-orphan",
    )

    def __init__(
        self,
        name: str,
        matrikelnummer: str,
        email: str,
        password: str,
        semester_anzahl: int,
        modul_anzahl: int,
        start_datum: date,
        ziel_datum: date,
        ziel_note: float,
        hochschule: Optional["Hochschule"] = None,
        studiengang: Optional["Studiengang"] = None,
        exmatrikulationsdatum: Optional[date] = None,
    ):
        self.name = name
        self.matrikelnummer = matrikelnummer
        self.email = email
        self.password = password

        self.semester_anzahl = semester_anzahl
        self.modul_anzahl = modul_anzahl
        self.start_datum = start_datum
        self.ziel_datum = ziel_datum
        self.ziel_note = ziel_note
        if hochschule:
            self.hochschule = hochschule
        if studiengang:
            self.studiengang = studiengang
        if exmatrikulationsdatum:
            self.exmatrikulationsdatum = exmatrikulationsdatum

    def __repr__(self) -> str:
        return f"Student: {self.name}"

    @hybrid_property
    def name(self):  # type: ignore[reportRedeclaration]
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    @hybrid_property
    def matrikelnummer(self):  # type: ignore[reportRedeclaration]
        return self._matrikelnummer

    @matrikelnummer.setter
    def matrikelnummer(self, value):
        self._matrikelnummer = value

    @hybrid_property
    def email(self) -> str:  # type: ignore[reportRedeclaration]
        return self._email

    @email.setter
    def email(self, value: str) -> None:
        try:
            new_address = validate_email(value).email
            self._email = new_address
        except EmailNotValidError as e:
            raise ValueError(f"Ungültige Email: {e}")

    @hybrid_property
    def password(self):  # type: ignore[reportRedeclaration]
        raise AttributeError("Passwort ist geschützt")

    @password.setter
    def password(self, value: str) -> None:
        self._password = ph.hash(value)

    def verify_password(self, passworteingabe: str) -> bool:
        try:
            return ph.verify(self._password, passworteingabe)
        except VerifyMismatchError:
            return False

    @hybrid_property
    def semester_anzahl(self):  # type: ignore[reportRedeclaration]
        return self._semester_anzahl

    @semester_anzahl.setter
    def semester_anzahl(self, value):
        self._semester_anzahl = value

    @hybrid_property
    def modul_anzahl(self):  # type: ignore[reportRedeclaration]
        return self._modul_anzahl

    @modul_anzahl.setter
    def modul_anzahl(self, value):
        self._modul_anzahl = value

    @hybrid_property
    def start_datum(self):  # type: ignore[reportRedeclaration]
        return self._start_datum

    @start_datum.setter
    def start_datum(self, value):
        self._start_datum = value

    @hybrid_property
    def ziel_datum(self):  # type: ignore[reportRedeclaration]
        return self._ziel_datum

    @ziel_datum.setter
    def ziel_datum(self, value):
        self._ziel_datum = value

    @hybrid_property
    def ziel_note(self):  # type: ignore[reportRedeclaration]
        return self._ziel_note

    @ziel_note.setter
    def ziel_note(self, value):
        self._ziel_note = value

    @hybrid_property
    def exmatrikulationsdatum(self):  # type: ignore[reportRedeclaration]
        return self._exmatrikulationsdatum

    @exmatrikulationsdatum.setter
    def exmatrikulationsdatum(self, value):
        self._exmatrikulationsdatum = value


class Hochschule(Base):
    __tablename__ = "hochschule"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    _name: Mapped[str] = mapped_column(String, unique=True)

    studenten: Mapped[List[Student]] = relationship(back_populates="hochschule")

    studiengaenge: Mapped[List[Studiengang]] = relationship(back_populates="hochschule")

    def __repr__(self):
        return f"Hochschule: {self.name}"

    @hybrid_property
    def name(self):  # type: ignore[reportRedeclaration]
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value


class Studiengang(Base):
    __tablename__ = "studiengang"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    _name: Mapped[str] = mapped_column(String)
    _gesamt_ects_punkte: Mapped[int] = mapped_column(Integer)

    hochschule_id = mapped_column(ForeignKey("hochschule.id"))
    hochschule: Mapped[Hochschule] = relationship(back_populates="studiengaenge")

    module: Mapped[List[Modul]] = relationship(back_populates="studiengang")

    studenten: Mapped[List[Student]] = relationship(back_populates="studiengang")

    @hybrid_property
    def name(self):  # type: ignore[reportRedeclaration]
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    @hybrid_property
    def gesamt_ects_punkte(self):  # type: ignore[reportRedeclaration]
        return self._gesamt_ects_punkte

    @gesamt_ects_punkte.setter
    def gesamt_ects_punkte(self, value: int):
        self._gesamt_ects_punkte = value


class Modul(Base):
    __tablename__ = "modul"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    _name: Mapped[str] = mapped_column(String)
    _modulcode: Mapped[str] = mapped_column(String, unique=True)
    _ects_punkte: Mapped[int] = mapped_column(Integer)

    studiengang_id = mapped_column(ForeignKey("studiengang.id"))
    studiengang: Mapped[Studiengang] = relationship(back_populates="module")

    enrollments: Mapped[List["Enrollment"]] = relationship(back_populates="modul")
    kurse: Mapped[List[Kurs]] = relationship(back_populates="modul")

    @hybrid_property
    def name(self):  # type: ignore[reportRedeclaration]
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    @hybrid_property
    def modulcode(self):  # type: ignore[reportRedeclaration]
        return self._modulcode

    @modulcode.setter
    def modulcode(self, value: str):
        self._modulcode = value

    @hybrid_property
    def ects_punkte(self):  # type: ignore[reportRedeclaration]
        return self._ects_punkte

    @ects_punkte.setter
    def ects_punkte(self, value: int):
        self._ects_punkte = value


class Kurs(Base):
    __tablename__ = "kurs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    _name: Mapped[str] = mapped_column(String)
    _nummer: Mapped[str] = mapped_column(String, unique=True)

    modul_id = mapped_column(ForeignKey("modul.id"))
    modul: Mapped[Modul] = relationship(back_populates="kurse")

    @hybrid_property
    def name(self):  # type: ignore[reportRedeclaration]
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    @hybrid_property
    def nummer(self):  # type: ignore[reportRedeclaration]
        return self._nummer

    @nummer.setter
    def nummer(self, value: str):
        self._nummer = value


class Enrollment(Base):
    __tablename__ = "enrollment"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, unique=True)
    _einschreibe_datum: Mapped[date] = mapped_column(Date)
    _end_datum: Mapped[Optional[date]] = mapped_column(
        Date, nullable=True, default=None
    )
    _status: Mapped[EnrollmentStatus] = mapped_column(SQLEnum(EnrollmentStatus))

    student_id = mapped_column(ForeignKey("student.id"))
    student: Mapped["Student"] = relationship(back_populates="enrollments")

    modul_id = mapped_column(ForeignKey("modul.id"))
    modul: Mapped["Modul"] = relationship(back_populates="enrollments")

    _anzahl_pruefungsleistungen: Mapped[int] = mapped_column(Integer)
    pruefungsleistungen: Mapped[List[Pruefungsleistung]] = relationship(
        back_populates="enrollment", cascade="all, delete-orphan"
    )

    @hybrid_property
    def einschreibe_datum(self):  # type: ignore[reportRedeclaration]
        return self._einschreibe_datum

    @einschreibe_datum.setter
    def einschreibe_datum(self, value):
        self._einschreibe_datum = value

    @hybrid_property
    def end_datum(self):  # type: ignore[reportRedeclaration]
        return self._end_datum

    @end_datum.setter
    def end_datum(self, value):
        self._end_datum = value

    @hybrid_property
    def status(self):  # type: ignore[reportRedeclaration]
        return self._status

    @status.setter
    def status(self, value: EnrollmentStatus):
        self._status = value

    @hybrid_property
    def anzahl_pruefungsleistungen(self):  # type: ignore[reportRedeclaration]
        return self._anzahl_pruefungsleistungen

    @anzahl_pruefungsleistungen.setter
    def anzahl_pruefungsleistungen(self, value):
        self._anzahl_pruefungsleistungen = value

    def add_pruefungsleistung(
        self,
        teilpruefung,
        teilpruefung_gewicht,
        versuch,
        note: float | None,
        datum: date | None,
    ):
        self.pruefungsleistungen.append(
            Pruefungsleistung(
                teilpruefung=teilpruefung,
                teilpruefung_gewicht=teilpruefung_gewicht,
                versuch=versuch,
                note=note,
                datum=datum,
            )
        )
        self.check_status()

    def check_status(self):
        abgeschlossene_pls = [
            pl for pl in self.pruefungsleistungen if pl.note is not None
        ]
        bestandene_pls = [pl for pl in abgeschlossene_pls if pl.ist_bestanden()]
        if len(bestandene_pls) == self.anzahl_pruefungsleistungen:
            self.status = EnrollmentStatus.ABGESCHLOSSEN
            self.end_datum = self.set_end_date()
            return
        for pl in abgeschlossene_pls:
            if pl.versuch == 3 and not pl.ist_bestanden():
                self.status = EnrollmentStatus.NICHT_BESTANDEN
                return
        self.status = EnrollmentStatus.IN_BEARBEITUNG

    def berechne_enrollment_note(self) -> float | None:
        abgeschlossene_pls = [
            pl for pl in self.pruefungsleistungen if pl.note is not None
        ]
        bestandene_pls = [pl for pl in abgeschlossene_pls if pl.ist_bestanden()]
        if bestandene_pls != []:
            # noten_summe wird gewichtet -> durchschnitt
            noten_summe = 0
            gewicht_summe = 0
            for pruefungsleistung in bestandene_pls:
                noten_summe += (
                    pruefungsleistung.note * pruefungsleistung.teilpruefung_gewicht  # type: ignore
                )
                gewicht_summe += pruefungsleistung.teilpruefung_gewicht
            ds_note = noten_summe / gewicht_summe
            enrollment_note = float(round(ds_note, 2))
            return enrollment_note
        else:
            return None

    def set_end_date(self):
        abgeschlossene_pls = [
            pl for pl in self.pruefungsleistungen if pl.note is not None
        ]
        bestandene_pls = [pl for pl in abgeschlossene_pls if pl.ist_bestanden()]
        last_date = None
        for pl in bestandene_pls:
            if last_date is None:
                last_date = pl.datum
            elif last_date < pl.datum:  # type: ignore
                last_date = pl.datum
            else:
                continue
        return last_date


# Prüfungsleistung
class Pruefungsleistung(Base):
    __tablename__ = "pruefungsleistung"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    # Teilpruefung nr. von insgesamt enrollment.anzahl_pruefungsleistungen
    _teilpruefung: Mapped[int] = mapped_column(Integer)
    # bei mehreren Teilprüfungen -> Gewicht pro note
    _teilpruefung_gewicht: Mapped[float] = mapped_column(Float)
    _versuch: Mapped[int] = mapped_column(Integer)

    _note: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    _datum: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    enrollment_id: Mapped[int] = mapped_column(
        ForeignKey("enrollment.id"), nullable=False
    )
    enrollment: Mapped[Enrollment] = relationship(back_populates="pruefungsleistungen")

    @hybrid_property
    def teilpruefung(self):  # type: ignore[reportRedeclaration]
        return self._teilpruefung

    @teilpruefung.setter
    def teilpruefung(self, value: int):
        self._teilpruefung = value

    @hybrid_property
    def teilpruefung_gewicht(self):  # type: ignore[reportRedeclaration]
        return self._teilpruefung_gewicht

    @teilpruefung_gewicht.setter
    def teilpruefung_gewicht(self, value: float):
        self._teilpruefung_gewicht = value

    @hybrid_property
    def versuch(self):  # type: ignore[reportRedeclaration]
        return self._versuch

    @versuch.setter
    def versuch(self, value: int):
        self._versuch = value

    @hybrid_property
    def note(self):  # type: ignore[reportRedeclaration]
        return self._note

    @note.setter
    def note(self, value: float | None):
        self._note = value

    @hybrid_property
    def datum(self):  # type: ignore[reportRedeclaration]
        return self._datum

    @datum.setter
    def datum(self, value: date | None):
        self._datum = value

    def __init__(self, teilpruefung, teilpruefung_gewicht, versuch, note, datum):
        self.teilpruefung = teilpruefung
        self.teilpruefung_gewicht = teilpruefung_gewicht
        self.versuch = versuch
        self.note = note
        self.datum = datum

    def ist_bestanden(self):
        if self.note is None:
            return False
        elif self.note > 4.0:
            return False
        else:
            return True

    def __repr__(self) -> str:
        return f"PL Versuch {self.versuch}, Note {self.note}, Datum {self.datum}"


# Semester
class Semester(Base):
    __tablename__ = "semester"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    _nummer: Mapped[int] = mapped_column(Integer)
    _beginn: Mapped[date] = mapped_column(Date)
    _ende: Mapped[date] = mapped_column(Date)

    student_id = mapped_column(ForeignKey("student.id"))
    student: Mapped["Student"] = relationship(back_populates="semester")

    @hybrid_property
    def nummer(self):  # type: ignore[reportRedeclaration]
        return self._nummer

    @nummer.setter
    def nummer(self, value: int):
        self._nummer = value

    @hybrid_property
    def beginn(self):  # type: ignore[reportRedeclaration]
        return self._beginn

    @beginn.setter
    def beginn(self, value: date):
        self._beginn = value

    @hybrid_property
    def ende(self):  # type: ignore[reportRedeclaration]
        return self._ende

    @ende.setter
    def ende(self, value: date):
        self._ende = value

    def get_semester_status(self, exmatrikulationsdatum):
        today = TODAY
        if exmatrikulationsdatum is not None:
            today = exmatrikulationsdatum

        if today < self.beginn:
            return SemesterStatus.ZUKUENFTIG
        elif today >= self.beginn and today <= self.ende:
            return SemesterStatus.AKTUELL
        else:
            return SemesterStatus.ZURUECKLIEGEND
