from __future__ import annotations
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.hybrid import hybrid_property
from typing import List, Optional
from enum import Enum, auto
from email_validator import validate_email, EmailNotValidError
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from dataclasses import dataclass
from datetime import date

# PasswordHasher
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
#Student
class Student(Base):
    __tablename__ = "student"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    matrikelnummer: Mapped[str] = mapped_column(String)
    email_address: Mapped[str] = mapped_column(String)    
    password: Mapped[str] = mapped_column("password", String)

    hochschule_id = mapped_column(ForeignKey("hochschule.id"))
    hochschule: Mapped[Hochschule] = relationship(back_populates="students")

    studiengang_id: mapped_column(ForeignKey("studiengang.id"))
    studiengang: Mapped[Studiengang] = relationship(back_populates="students")

    semester_anzahl: Mapped[int] = mapped_column(Integer)
    semester: Mapped[List["Semester"]] = relationship(back_populates="student")

    start_datum: Mapped[date] = mapped_column(Date)
    ziel_datum: Mapped[date] = mapped_column(Date)

    ziel_note: Mapped[float] = mapped_column(Float)

    exmatrikulationsdatum: Mapped [date] = mapped_column(Date)

    enrollments: Mapped[List["Enrollment"]] = relationship(back_populates="student")

    def __init__(
        self,
        name: str,
        matrikelnummer: str,
        email_address: str,
        password: str,
        semester_anzahl: int,
        start_datum: date,
        ziel_datum: date,
        ziel_note: float,
        hochschule: Optional["Hochschule"] = None,
        studiengang: Optional["Studiengang"] = None,
        exmatrikulationsdatum: Optional[date] = None,
    ):
        self.name = name
        self.matrikelnummer = matrikelnummer
        self.email_address = email_address
        self.password = password  # läuft über Setter → Hashing

        self.semester_anzahl = semester_anzahl
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
    def name(self):
        return self.name

    @name.setter
    def name(self, value: str):
        self.name = value

    @hybrid_property
    def matrikelnummer(self):
        return self.matrikelnummer

    @matrikelnummer.setter
    def matrikelnummer(self, matrikelnummer):
        self.matrikelnummer = matrikelnummer

    #    @hybrid_property
    #    def hochschule(self):
    #        return self.hochschule

    @hybrid_property
    def email_address(self):
        return self.email_address

    @email_address.setter
    def email_address(self, value: str):
        try:
            new_address = validate_email(value).email
            self.email_address = new_address
        except EmailNotValidError as e:
            raise ValueError(f"Ungültige Email: {e}")

    @hybrid_property
    def password(self):
        raise AttributeError("Passwort ist geschützt")

    @password.setter
    def password(self, klartext: str) -> None:
        self.password = ph.hash(klartext)

    def verify_password(self, passworteingabe: str) -> bool:
        try:
            return ph.verify(self._password, passworteingabe)
        except VerifyMismatchError:
            return False
    
    @hybrid_property
    def semester_anzahl(self):
        return self.semester_anzahl

    @semester_anzahl.setter
    def semester_anzahl(self, value)
        self.semester_anzahl = value

    @hybrid_property
    def start_datum(self):
        return self.start_datum

    @start_datum.setter
    def start_datum(self, value)
        self.start_datum = value

    @hybrid_property
    def ziel_datum(self):
        return self.ziel_datum

    @ziel_datum.setter
    def ziel_datum(self, value)
        self.ziel_datum = value

    @hybrid_property
    def ziel_note(self):
        return self.ziel_note

    @ziel_note.setter
    def ziel_note(self, value)
        self.ziel_note = value

# Getter / Setter für hochschule, studiengang, enrollments, semester(?), ?

# Methoden von Student
    def verify_password(self):
        pass
    
    def erstelle_enrollment(self):
        pass

    def berechne_gesamt_ects(self):
        pass

    def berechne_durchschnittsnote(self):
        pass
    
    def werde_exmatrikuliert(self):
        pass


#Hochschule
class Hochschule(Base):
    pass

    def erstelle_studiengang(self):
        pass

#Studiengang
class Studiengang(Base):
    pass

    def erstelle_modul(self):
        pass

    def fuege_kurs_zu_modul_hinzu(self):
        pass

#Modul
class Modul(Base):
    pass

#Kurs
class Kurs(Base):
    pass

#Enrollment
class Enrollment(Base):
    pass

    def add_pruefungsleistung(self):
        pass
    
    def check_status(self)
        pass

#Prüfungsleistung
class Pruefungsleistung(Base):
    pass

    def bestanden(self):
        pass

#Semester
class Semester(Base):
    pass

    def get_semester_status(self):
        pass
