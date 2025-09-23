from __future__ import annotations
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.hybrid import hybrid_property
from typing import List
from enum import Enum, auto
from email_validator import validate_email, EmailNotValidError
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from dataclasses import dataclass

# PasswordHasher
ph = PasswordHasher()


# Basisklasse
class Base(DeclarativeBase):
    pass


class Status(Enum):
    OFFEN = auto()
    IN_BEARBEITUNG = auto()
    ABGESCHLOSSEN = auto()


class Student(Base):
    __tablename__ = "student"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    _name: Mapped[str] = mapped_column(String)
    _matrikelnummer: Mapped[str] = mapped_column(String)
    _email_address: Mapped[str] = mapped_column(String)
    _password: Mapped[str] = mapped_column("password", String)

    hochschule_id = mapped_column(ForeignKey("hochschule.id"))
    hochschule: Mapped[Hochschule] = relationship(back_populates="students")

    enrollments: Mapped[List["Enrollment"]] = relationship(back_populates="student")

    def __init__(
        self,
        name: str,
        matrikelnummer: str,
        email_address: str,
        password: str,
        hochschule: "Hochschule" = None,
    ):
        self.name = name
        self.matrikelnummer = matrikelnummer
        self.email_address = email_address
        self.password = password  # läuft über Setter → Hashing
        if hochschule:
            self.hochschule = hochschule

    def __repr__(self) -> str:
        return f"Student: {self.name}"

    @hybrid_property
    def name(self):
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    @hybrid_property
    def matrikelnummer(self):
        return self._matrikelnummer

    @matrikelnummer.setter
    def matrikelnummer(self, matrikelnummer):
        self._matrikelnummer = matrikelnummer

    #    @hybrid_property
    #    def hochschule(self):
    #        return self.hochschule

    @hybrid_property
    def email_address(self):
        return self._email_address

    @email_address.setter
    def email_address(self, value: str):
        try:
            new_address = validate_email(value).email
            self._email_address = new_address
        except EmailNotValidError as e:
            raise ValueError(f"Ungültige Email: {e}")

    @hybrid_property
    def password(self):
        raise AttributeError("Passwort ist geschützt")

    @password.setter
    def password(self, klartext: str) -> None:
        self._password = ph.hash(klartext)

    def verify_password(self, passworteingabe: str) -> bool:
        try:
            return ph.verify(self._password, passworteingabe)
        except VerifyMismatchError:
            return False


class Hochschule(Base):
    __tablename__ = "hochschule"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    _hochschul_name: Mapped[str] = mapped_column(String)

    students: Mapped[List[Student]] = relationship(back_populates="hochschule")

    def __repr__(self):
        return f"Hochschule: {self.hochschul_name}"

    @hybrid_property
    def hochschul_name(self):
        return self._hochschul_name

    @hochschul_name.setter
    def hochschul_name(self, value: str):
        self._hochschul_name = value

    # @hybrid_property
    # def students(self):
    #     return self.students


class Kurs(Base):
    __tablename__ = "kurs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    _kurs_name: Mapped[str] = mapped_column(String)
    _kurs_nummer: Mapped[str] = mapped_column(String)

    enrollments: Mapped[List["Enrollment"]] = relationship(back_populates="kurs")

    def __repr__(self) -> str:
        return f"Kurs: {self.kurs_name}"

    @hybrid_property
    def kurs_name(self):
        return self._kurs_name

    @kurs_name.setter
    def kurs_name(self, value: str):
        self._kurs_name = value

    @hybrid_property
    def kurs_nummer(self):
        return self._kurs_nummer

    @kurs_nummer.setter
    def kurs_nummer(self, value: str):
        self._kurs_nummer = value


class Enrollment(Base):
    __tablename__ = "enrollment"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    student_id: Mapped[int] = mapped_column(ForeignKey("student.id"))
    kurs_id: Mapped[int] = mapped_column(ForeignKey("kurs.id"))

    _status: Mapped[Status] = mapped_column(SQLEnum(Status))

    student: Mapped["Student"] = relationship(back_populates="enrollments")
    kurs: Mapped["Kurs"] = relationship(back_populates="enrollments")

    def __repr__(self) -> str:
        return f"Kurs: {self.kurs_id}, Status: {self.status.name.replace('_', ' ')}"

    @hybrid_property
    def status(self):
        return self._status

    @status.setter
    def status(self, value: Status):
        self._status = value


@dataclass
class EnrollmentDTO:
    student_name: str
    kurs_name: str
    status: str

    @classmethod
    def make_dto(cls, enrollment: Enrollment) -> "EnrollmentDTO":
        return cls(
            student_name=enrollment.student.name,
            kurs_name=enrollment.kurs.kurs_name,
            status=enrollment.status.name,
        )
