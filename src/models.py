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
from datetime import date, datetime

TODAY = datetime.today()

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

# Es wäre klug gewesen, eine User-Klasse zu machen, von der Student erbt,
# dadurch wäre es möglich weitere User wie Hochschulmitarbeiter, Admins oder Ähnliche hinzuzufügen,
# die auch von User (z.b. email/password/name/Hochschule) erben. Somit könnte man den
# Hochschulmitarbeitern z.b. Statistiken zu kursen oder deren Prüfungen geben, z.b. Durchfallquote,
# Anzahl d. Studierenden, durchschnittliche Anzahl der Prüfungsversuche, dursch. Bearbeitungszeit...


# Student
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
    _exmatrikulationsdatum: Mapped[date] = mapped_column(Date)

    hochschule_id = mapped_column(ForeignKey("hochschule.id"))
    hochschule: Mapped[Hochschule] = relationship(back_populates="studenten")

    studiengang_id = mapped_column(ForeignKey("studiengang.id"))
    studiengang: Mapped[Studiengang] = relationship(back_populates="studenten")

    _semester_anzahl: Mapped[int] = mapped_column(Integer)
    semester: Mapped[List["Semester"]] = relationship(back_populates="student")

    enrollments: Mapped[List["Enrollment"]] = relationship(back_populates="student")

    def __init__(
        self,
        name: str,
        matrikelnummer: str,
        email: str,
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
        self.email = email
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

    # Methoden von Student
    def erstelle_enrollment(self):
        # verlegen nach controller? student müsste db parameter haben, oder?
        pass

    def berechne_gesamt_ects(self):
        gesamt_ects_punkte = 0
        for enrollment in self.enrollments:
            if enrollment.check_status():
                gesamt_ects_punkte += enrollment.kurs.ects_punkte
        return gesamt_ects_punkte

    def berechne_durchschnittsnote(self):
        noten = []
        for enrollment in self.enrollments:
            for pruefungsleistung in enrollment.pruefungsleistungen:
                if pruefungsleistung.ist_bestanden():
                    noten.append(pruefungsleistung.note)
                else:
                    pass
        durchschnittsnote = sum(noten) / len(noten)
        return durchschnittsnote

    @hybrid_property
    def exmatrikulationsdatum(self):
        return self._exmatrikulationsdatum

    def werde_exmatrikuliert(self, exmatrikulationsdatum: date):
        self._exmatrikulationsdatum = exmatrikulationsdatum


# Hochschule
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

    def erstelle_studiengang(self):
        # -> controller?
        pass


# Studiengang
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

    def erstelle_modul(self):
        # verlegen nach controller?
        pass

    def fuege_kurs_zu_modul_hinzu(self):
        # heißt Kurs braucht .modul und andersherum, evtl. schon durch programierung erzwungen?
        pass


# Modul
class Modul(Base):
    __tablename__ = "modul"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    _name: Mapped[str] = mapped_column(String)

    studiengang_id = mapped_column(ForeignKey("studiengang.id"))
    studiengang: Mapped[Studiengang] = relationship(back_populates="module")

    kurse: Mapped[List[Kurs]] = relationship(back_populates="modul")

    @hybrid_property
    def name(self):  # type: ignore[reportRedeclaration]
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value


# Kurs
class Kurs(Base):
    __tablename__ = "kurs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    _name: Mapped[str] = mapped_column(String)
    _nummer: Mapped[str] = mapped_column(String)
    _ects_punkte: Mapped[int] = mapped_column(Integer)

    modul_id = mapped_column(ForeignKey("modul.id"))
    modul: Mapped[Modul] = relationship(back_populates="kurs")

    enrollments: Mapped[List["Enrollment"]] = relationship(back_populates="kurs")

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

    @hybrid_property
    def ects_punkte(self):  # type: ignore[reportRedeclaration]
        return self._ects_punkte

    @ects_punkte.setter
    def ects_punkte(self, value: int):
        self._ects_punkte = value


# Enrollment
class Enrollment(Base):
    __tablename__ = "enrollment"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    _einschreibe_datum: Mapped[date] = mapped_column(Date)
    _end_datum: Mapped[date] = mapped_column(Date)
    _status: Mapped[EnrollmentStatus] = mapped_column(SQLEnum(EnrollmentStatus))

    student_id = mapped_column(ForeignKey("student.id"))
    student: Mapped["Student"] = relationship(back_populates="enrollments")
    kurs_id = mapped_column(ForeignKey("kurs.id"))
    kurs: Mapped["Kurs"] = relationship(back_populates="enrollments")

    pruefungsleistungen: Mapped[List[Pruefungsleistung]] = relationship(
        back_populates="enrollment"
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

    def add_pruefungsleistung(self, note: float, datum: date):
        if len(self.pruefungsleistungen) > 3:
            raise ValueError(
                "Ein Enrollment darf höchstens 3 Prüfungsleistungen haben."
            )
        versuch = int(len(self.pruefungsleistungen) + 1)
        self.pruefungsleistungen.append(Pruefungsleistung(versuch, note, datum))
        self.check_status()

    def check_status(self):
        if self.pruefungsleistungen:
            for pruefungsleistung in self.pruefungsleistungen:
                if pruefungsleistung.ist_bestanden():
                    self.status = EnrollmentStatus.ABGESCHLOSSEN
            if (
                len(self.pruefungsleistungen) == 3
                and self.status is not EnrollmentStatus.ABGESCHLOSSEN
            ):
                self.status = EnrollmentStatus.NICHT_BESTANDEN


# Prüfungsleistung
class Pruefungsleistung(Base):
    __tablename__ = "pruefungsleistung"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    _versuch: Mapped[int] = mapped_column(Integer)
    _note: Mapped[float] = mapped_column(Float)
    _datum: Mapped[date] = mapped_column(Date)

    enrollment_id: Mapped[int] = mapped_column(
        ForeignKey("enrollment.id"), nullable=False
    )
    enrollment: Mapped[Enrollment] = relationship(back_populates="pruefungsleistungen")

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
    def note(self, value: float):
        self._note = value

    @hybrid_property
    def datum(self):  # type: ignore[reportRedeclaration]
        return self._datum

    @datum.setter
    def datum(self, value: date):
        self._datum = value

    def __init__(self, versuch, note, datum):
        self.versuch = versuch
        self.note = note
        self.datum = datum

    def ist_bestanden(self):
        if self.note > 4.0:
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

    def get_semester_status(self):
        if TODAY < self.beginn:
            return SemesterStatus.ZUKUENFTIG
        elif TODAY >= self.beginn and TODAY <= self.ende:
            return SemesterStatus.AKTUELL
        else:
            return SemesterStatus.ZURUECKLIEGEND
