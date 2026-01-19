"""SQLAlchemy ORM-Modelle für das Dashboard.

Enthält Entity-Klassen (Student, Hochschule, Studiengang, Modul, Kurs, Enrollment,
Pruefungsleistung, Semester) sowie Enums für Statuswerte.
"""

from __future__ import annotations
from sqlalchemy import Integer, String, Float, Date, ForeignKey
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.hybrid import hybrid_property
from typing import List, Optional, NoReturn
from enum import Enum, auto
from email_validator import validate_email, EmailNotValidError
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
import datetime

ph = PasswordHasher()


class Base(DeclarativeBase):
    """SQLAlchemy Declarative Base für alle ORM-Modelle."""

    pass


# ENUM-Klassen
class EnrollmentStatus(Enum):
    """Status eines Enrollments (Moduleinschreibung)."""

    IN_BEARBEITUNG = auto()
    ABGESCHLOSSEN = auto()
    NICHT_BESTANDEN = auto()


class SemesterStatus(Enum):
    """Zeitlicher Status eines Semesters relativ zu heute oder dem Exmatrikulationsdatum."""

    ZURUECKLIEGEND = auto()
    AKTUELL = auto()
    ZUKUENFTIG = auto()


# Entity-Klassen
class Student(Base):
    """Repräsentiert einen User/Studenten des Dashboards.

    Properties:
        name (str): Name.
        matrikelnummer (str): Matrikelnummer.
        email (str): Email-Adresse (Validierung über setter).
        password (str): Passwort (Hashing über setter, nicht auslesbar!).
        semester_anzahl (int): Anzahl der Semester.
        modul_anzahl (int): Anzahl der Module.
        start_datum (datetime.date): Studienstartdatum.
        ziel_datum (datetime.date): Wunsch-Abschlussdatum.
        ziel_note (float): gewünschte Durchschnittsnote.
        exmatrikulationsdatum (Optional[datetime.date] = None): Exmatrikulationsdatum, falls vorhanden.
    """

    __tablename__ = "student"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    _name: Mapped[str] = mapped_column(String)
    _matrikelnummer: Mapped[str] = mapped_column(String)
    _email: Mapped[str] = mapped_column(String, unique=True)
    _password: Mapped[str] = mapped_column("password", String)

    _ziel_note: Mapped[float] = mapped_column(Float)
    _start_datum: Mapped[datetime.date] = mapped_column(Date)
    _ziel_datum: Mapped[datetime.date] = mapped_column(Date)
    _exmatrikulationsdatum: Mapped[Optional[datetime.date]] = mapped_column(
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
        start_datum: datetime.date,
        ziel_datum: datetime.date,
        ziel_note: float,
        hochschule: Optional["Hochschule"] = None,
        studiengang: Optional["Studiengang"] = None,
        exmatrikulationsdatum: Optional[datetime.date] = None,
    ) -> None:
        """Konstruktor eines Studenten.

        Args:
            name (str): Name.
            matrikelnummer (str): Matrikelnummer.
            email (str): Email-Adresse (Validierung über setter).
            password (str): Passwort (Hashing über setter).
            semester_anzahl (int): Anzahl der Semester.
            modul_anzahl (int): Anzahl der Module.
            start_datum (datetime.date): Studienstartdatum.
            ziel_datum (datetime.date): Wunsch-Abschlussdatum.
            ziel_note (float): gewünschte Durchschnittsnote.
            hochschule (Optional["Hochschule"] = None): Hochschule.
            studiengang (Optional["Studiengang"] = None): Studiengang.
            exmatrikulationsdatum (Optional[datetime.date] = None): Exmatrikulationsdatum, falls vorhanden.
        """
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
    def name(self) -> str:  # type: ignore[reportRedeclaration]
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @hybrid_property
    def matrikelnummer(self) -> str:  # type: ignore[reportRedeclaration]
        return self._matrikelnummer

    @matrikelnummer.setter
    def matrikelnummer(self, value: str) -> None:
        self._matrikelnummer = value

    @hybrid_property
    def email(self) -> str:  # type: ignore[reportRedeclaration]
        return self._email

    @email.setter
    def email(self, value: str) -> None:
        # Überprüft die Syntax und Zustellbarkeit.
        # Speichert normalisierte Email bei erfolgreicher Prüfung.
        try:
            new_address = validate_email(value, check_deliverability=True).email
            self._email = new_address
        except EmailNotValidError as e:
            raise ValueError(f"Ungültige Email: {e}")

    @hybrid_property
    def password(self) -> NoReturn:  # type: ignore[reportRedeclaration]
        raise AttributeError("Passwort ist geschützt")

    @password.setter
    def password(self, value: str) -> None:
        if value.startswith("$argon2"):
            # Double-Hashing vermeiden, Argon2-Hashes beginnen typischerweise mit "$argon2".
            self._password = value
        else:
            self._password = ph.hash(value)

    def verify_password(self, passworteingabe: str) -> bool:
        """Prüft eine Passworteingabe gegen den gespeicherten Argon2-Hash.

        Args:
            passworteingabe (str): Passwort im Klartext (User-Eingabe).

        Returns:
            bool: True, wenn das Passwort korrekt ist, sonst False.
        """
        try:
            return ph.verify(self._password, passworteingabe)
        except VerifyMismatchError:
            return False

    @hybrid_property
    def semester_anzahl(self) -> int:  # type: ignore[reportRedeclaration]
        return self._semester_anzahl

    @semester_anzahl.setter
    def semester_anzahl(self, value: int) -> None:
        self._semester_anzahl = value

    @hybrid_property
    def modul_anzahl(self) -> int:  # type: ignore[reportRedeclaration]
        return self._modul_anzahl

    @modul_anzahl.setter
    def modul_anzahl(self, value: int) -> None:
        self._modul_anzahl = value

    @hybrid_property
    def start_datum(self) -> datetime.date:  # type: ignore[reportRedeclaration]
        return self._start_datum

    @start_datum.setter
    def start_datum(self, value: datetime.date) -> None:
        self._start_datum = value

    @hybrid_property
    def ziel_datum(self) -> datetime.date:  # type: ignore[reportRedeclaration]
        return self._ziel_datum

    @ziel_datum.setter
    def ziel_datum(self, value: datetime.date) -> None:
        self._ziel_datum = value

    @hybrid_property
    def ziel_note(self) -> float:  # type: ignore[reportRedeclaration]
        return self._ziel_note

    @ziel_note.setter
    def ziel_note(self, value: float) -> None:
        self._ziel_note = value

    @hybrid_property
    def exmatrikulationsdatum(self) -> datetime.date | None:  # type: ignore[reportRedeclaration]
        return self._exmatrikulationsdatum

    @exmatrikulationsdatum.setter
    def exmatrikulationsdatum(self, value: datetime.date | None) -> None:
        self._exmatrikulationsdatum = value


class Hochschule(Base):
    """Repräsentiert eine Hochschule.

    Properties:
        name (str): Name der Hochschule.
    """

    __tablename__ = "hochschule"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    _name: Mapped[str] = mapped_column(String, unique=True)

    studenten: Mapped[List[Student]] = relationship(back_populates="hochschule")

    studiengaenge: Mapped[List[Studiengang]] = relationship(back_populates="hochschule")

    def __repr__(self) -> str:
        return f"Hochschule: {self.name}"

    @hybrid_property
    def name(self) -> str:  # type: ignore[reportRedeclaration]
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value


class Studiengang(Base):
    """Repräsentiert einen Studiengang einer Hochschule.

    Properties:
        name (str): Studiengangsname.
        gesamt_ects_punkte (int): Anzahl der ECTS-Punkte.
    """

    __tablename__ = "studiengang"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    _name: Mapped[str] = mapped_column(String)
    _gesamt_ects_punkte: Mapped[int] = mapped_column(Integer)

    hochschule_id = mapped_column(ForeignKey("hochschule.id"))
    hochschule: Mapped[Hochschule] = relationship(back_populates="studiengaenge")

    module: Mapped[List[Modul]] = relationship(back_populates="studiengang")

    studenten: Mapped[List[Student]] = relationship(back_populates="studiengang")

    @hybrid_property
    def name(self) -> str:  # type: ignore[reportRedeclaration]
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @hybrid_property
    def gesamt_ects_punkte(self) -> int:  # type: ignore[reportRedeclaration]
        return self._gesamt_ects_punkte

    @gesamt_ects_punkte.setter
    def gesamt_ects_punkte(self, value: int) -> None:
        self._gesamt_ects_punkte = value


class Modul(Base):
    """Repräsentiert ein Modul.

    Properties:
        name (str): Modulname.
        modulcode (str): Modulcode.
        ects_punkte (int): Anzahl der ECTS-Punkte, die mit Abschluss des Moduls erreicht werden.
    """

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
    def name(self) -> str:  # type: ignore[reportRedeclaration]
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @hybrid_property
    def modulcode(self) -> str:  # type: ignore[reportRedeclaration]
        return self._modulcode

    @modulcode.setter
    def modulcode(self, value: str) -> None:
        self._modulcode = value

    @hybrid_property
    def ects_punkte(self) -> int:  # type: ignore[reportRedeclaration]
        return self._ects_punkte

    @ects_punkte.setter
    def ects_punkte(self, value: int) -> None:
        self._ects_punkte = value


class Kurs(Base):
    """Repräsentiert einen Kurs als Teil eines Moduls.
    Properties:
        name (str): Kursname.
        nummer (str): Kursnummer.
    """

    __tablename__ = "kurs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    _name: Mapped[str] = mapped_column(String)
    _nummer: Mapped[str] = mapped_column(String, unique=True)

    modul_id = mapped_column(ForeignKey("modul.id"))
    modul: Mapped[Modul] = relationship(back_populates="kurse")

    @hybrid_property
    def name(self) -> str:  # type: ignore[reportRedeclaration]
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @hybrid_property
    def nummer(self) -> str:  # type: ignore[reportRedeclaration]
        return self._nummer

    @nummer.setter
    def nummer(self, value: str) -> None:
        self._nummer = value


class Enrollment(Base):
    """Repräsentiert eine Einschreibung eines Studenten in ein Modul.

    Properties:
        einschreibe_datum (datetime.date): Datum der Einschreibung.
        end_datum (datetime.date): Datum der Prüfungsleistung, mit der das Modul abgeschlossen wurde.
        status (EnrollmentStatus): Status des Enrollments (Abgeschlossen, nicht bestanden, in Bearbeitung).
        anzahl_pruefungsleistungen: Anzahl der erforderlichen Teilprüfungen, um das Modul abzuschließen.
    """

    __tablename__ = "enrollment"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, unique=True)
    _einschreibe_datum: Mapped[datetime.date] = mapped_column(Date)
    _end_datum: Mapped[Optional[datetime.date]] = mapped_column(
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
    def einschreibe_datum(self) -> datetime.date:  # type: ignore[reportRedeclaration]
        return self._einschreibe_datum

    @einschreibe_datum.setter
    def einschreibe_datum(self, value: datetime.date) -> None:
        self._einschreibe_datum = value

    @hybrid_property
    def end_datum(self) -> datetime.date | None:  # type: ignore[reportRedeclaration]
        return self._end_datum

    @end_datum.setter
    def end_datum(self, value: datetime.date | None) -> None:
        self._end_datum = value

    @hybrid_property
    def status(self) -> EnrollmentStatus:  # type: ignore[reportRedeclaration]
        return self._status

    @status.setter
    def status(self, value: EnrollmentStatus) -> None:
        self._status = value

    @hybrid_property
    def anzahl_pruefungsleistungen(self) -> int:  # type: ignore[reportRedeclaration]
        return self._anzahl_pruefungsleistungen

    @anzahl_pruefungsleistungen.setter
    def anzahl_pruefungsleistungen(self, value: int) -> None:
        self._anzahl_pruefungsleistungen = value

    def add_pruefungsleistung(
        self,
        teilpruefung,
        teilpruefung_gewicht,
        versuch,
        note: float | None,
        datum: datetime.date | None,
    ) -> None:
        """Fügt dem Enrollment einen Versuch einer Prüfungsleistung hinzu.

        Args:
            teilpruefung (int): Nummer der Teilprüfung (z.B. Prüfung 2 des Moduls)
            teilpruefung_gewicht (float): Gewichtung der Note in der Modulnote.
            versuch (int): Erster, zweiter oder Dritter Versuch (1, 2, 3).
            note (float | None): Note des Versuchs.
            datum (datetime.date | None): Datum der Abgabe.
        """
        self.pruefungsleistungen.append(
            Pruefungsleistung(
                teilpruefung=teilpruefung,
                teilpruefung_gewicht=teilpruefung_gewicht,
                versuch=versuch,
                note=note,
                datum=datum,
            )
        )
        self.aktualisiere_status()

    def aktualisiere_status(self) -> None:
        """Aktualisiert den Enrollment-Status basierend auf den Prüfungsleistungen.

        Regeln:
            - ABGESCHLOSSEN: Pro Teilprüfung existiert ein bestandener Versuch.
            - NICHT_BESTANDEN: Das Modul ist nicht bestanden, wenn auch der dritte Versuch einer Teilprüfung nicht bestanden wurde.
            - IN_BEARBEITUNG: sonst.
        """
        abgeschlossene_pls = [
            pl for pl in self.pruefungsleistungen if pl.note is not None
        ]
        bestandene_pls = [pl for pl in abgeschlossene_pls if pl.ist_bestanden()]
        if len(bestandene_pls) == self.anzahl_pruefungsleistungen:
            # wenn für jede Teilprüfung eine bestandene Prüfungsleistung existiert -> Status: Abgeschlossen
            self.status = EnrollmentStatus.ABGESCHLOSSEN
            self.end_datum = self.set_end_date()
            return
        for pl in abgeschlossene_pls:
            # wenn für eine Teilprüfung auch der dritte Versuch nicht bestanden wurde -> Status: Nicht bestanden
            if pl.versuch == 3 and not pl.ist_bestanden():
                self.status = EnrollmentStatus.NICHT_BESTANDEN
                return
        # wenn weder "abgeschlossen" noch "Nicht bestanden" -> Status: In Bearbeitung
        self.status = EnrollmentStatus.IN_BEARBEITUNG

    def berechne_enrollment_note(self) -> float | None:
        """Berechnet die Modulnote als gewichteten Durchschnitt der bestandenen Versuche.

        Nicht bestandene und nicht bewertete Versuche werden ignoriert.

        Returns:
            Gewichtete Durchschnittsnote (float, gerundet auf 2 Nachkommastellen) oder None, falls keine bestandenen
            Prüfungsleistungen vorhanden sind.
        """
        abgeschlossene_pls = [
            pl for pl in self.pruefungsleistungen if pl.note is not None
        ]
        bestandene_pls = [pl for pl in abgeschlossene_pls if pl.ist_bestanden()]
        if bestandene_pls != []:
            # noten_summe wird gewichtet -> Durchschnitt
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

    def set_end_date(self) -> datetime.date | None:
        """Gibt das größte Datum aller bestandenen Prüfungsleistungen des Enrollments zurück,
        oder ``None`` falls keine bestandenen Prüfungsleistungen vorliegen."""
        abgeschlossene_pls = [
            pl for pl in self.pruefungsleistungen if pl.note is not None
        ]
        bestandene_pls = [pl for pl in abgeschlossene_pls if pl.ist_bestanden()]
        return max(
            (pl.datum for pl in bestandene_pls if pl.datum is not None), default=None
        )


class Pruefungsleistung(Base):
    """Ein Prüfungsversuch innerhalb einer (Teil-) Prüfung.

    Properties:
        teilpruefung (int): Nummer der Teilprüfung (z.B. Prüfung 2 des Moduls)
        teilpruefung_gewicht (float): Gewichtung der Note in der Modulnote.
        versuch (int): Erster, zweiter oder Dritter Versuch (1, 2, 3).
        note (float | None): Note des Versuchs.
        datum (datetime.date | None): Datum der Abgabe.
    """

    __tablename__ = "pruefungsleistung"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    # Teilpruefung nr. von insgesamt enrollment.anzahl_pruefungsleistungen
    _teilpruefung: Mapped[int] = mapped_column(Integer)
    # bei mehreren Teilprüfungen -> Gewicht pro note
    _teilpruefung_gewicht: Mapped[float] = mapped_column(Float)
    _versuch: Mapped[int] = mapped_column(Integer)

    _note: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    _datum: Mapped[Optional[datetime.date]] = mapped_column(Date, nullable=True)

    enrollment_id: Mapped[int] = mapped_column(
        ForeignKey("enrollment.id"), nullable=False
    )
    enrollment: Mapped[Enrollment] = relationship(back_populates="pruefungsleistungen")

    @hybrid_property
    def teilpruefung(self) -> int:  # type: ignore[reportRedeclaration]
        return self._teilpruefung

    @teilpruefung.setter
    def teilpruefung(self, value: int) -> None:
        self._teilpruefung = value

    @hybrid_property
    def teilpruefung_gewicht(self) -> float:  # type: ignore[reportRedeclaration]
        return self._teilpruefung_gewicht

    @teilpruefung_gewicht.setter
    def teilpruefung_gewicht(self, value: float) -> None:
        self._teilpruefung_gewicht = value

    @hybrid_property
    def versuch(self) -> int:  # type: ignore[reportRedeclaration]
        return self._versuch

    @versuch.setter
    def versuch(self, value: int) -> None:
        self._versuch = value

    @hybrid_property
    def note(self) -> float | None:  # type: ignore[reportRedeclaration]
        return self._note

    @note.setter
    def note(self, value: float | None) -> None:
        self._note = value

    @hybrid_property
    def datum(self) -> datetime.date | None:  # type: ignore[reportRedeclaration]
        return self._datum

    @datum.setter
    def datum(self, value: datetime.date | None) -> None:
        self._datum = value

    # def __init__(self, teilpruefung, teilpruefung_gewicht, versuch, note, datum) -> None:
    #     """Konstruktor einer Prüfungsleistung."""
    #     self.teilpruefung = teilpruefung
    #     self.teilpruefung_gewicht = teilpruefung_gewicht
    #     self.versuch = versuch
    #     self.note = note
    #     self.datum = datum

    def ist_bestanden(self) -> bool:
        """Gibt zurück, ob die Prüfungsleistung bestanden wurde.

        Returns:
            bool: ``False``, wenn die Note nicht existiert oder > 4.0 ist, sonst ``True``.
        """
        return False if self.note is None or self.note > 4.0 else True

    def __repr__(self) -> str:
        return f"PL Versuch {self.versuch}, Note {self.note}, Datum {self.datum}"


class Semester(Base):
    """Ein Semester eines Studenten mit Start- und Enddatum.

    Properties:
        nummer (int): Nummer des Semesters (z.B. Semester Nr.3).
        beginn (datetime.date): Startdatum des Semesters.
        ende (datetime.date): Enddatum des Semesters.
    """

    __tablename__ = "semester"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    _nummer: Mapped[int] = mapped_column(Integer)
    _beginn: Mapped[datetime.date] = mapped_column(Date)
    _ende: Mapped[datetime.date] = mapped_column(Date)

    student_id = mapped_column(ForeignKey("student.id"))
    student: Mapped["Student"] = relationship(back_populates="semester")

    @hybrid_property
    def nummer(self) -> int:  # type: ignore[reportRedeclaration]
        return self._nummer

    @nummer.setter
    def nummer(self, value: int) -> None:
        self._nummer = value

    @hybrid_property
    def beginn(self) -> datetime.date:  # type: ignore[reportRedeclaration]
        return self._beginn

    @beginn.setter
    def beginn(self, value: datetime.date) -> None:
        self._beginn = value

    @hybrid_property
    def ende(self) -> datetime.date:  # type: ignore[reportRedeclaration]
        return self._ende

    @ende.setter
    def ende(self, value: datetime.date) -> None:
        self._ende = value

    def get_semester_status(
        self, exmatrikulationsdatum: datetime.date | None
    ) -> SemesterStatus:
        """Bestimmt den zeitlichen Status des Semesters relativ zu heute oder dem Exmatrikulationsdatum.

        Wenn der Student exmatrikuliert wurde, wird dieses Datum verwendet, damit die Semester-Ansicht in der GUI "einfriert".

        Args:
            exmatrikulationsdatum: Falls nicht ``None``, wird dieser Tag als Stichtag verwendet.
            Sonst wird das heutige Datum genutzt.

        Returns:
            SemesterStatus (ZUKUENFTIG, AKTUELL, ZURUECKLIEGEND).
        """
        today = datetime.date.today()
        if exmatrikulationsdatum is not None:
            today = exmatrikulationsdatum

        if today < self.beginn:
            return SemesterStatus.ZUKUENFTIG
        elif self.beginn <= today <= self.ende:
            return SemesterStatus.AKTUELL
        else:
            return SemesterStatus.ZURUECKLIEGEND
