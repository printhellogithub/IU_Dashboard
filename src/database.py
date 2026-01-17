from sqlalchemy.orm import sessionmaker, selectinload
from src.models import (
    Base,
    EnrollmentStatus,
    Student,
    Hochschule,
    Studiengang,
    Modul,
    Kurs,
    Enrollment,
    Pruefungsleistung,
    Semester,
)
from sqlalchemy import create_engine, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

import logging
from pathlib import Path
from typing import Sequence
import datetime

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "data.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)
DB_URL = f"sqlite+pysqlite:///{DB_PATH}"

logger = logging.getLogger(__name__)


class DBTransactionError(Exception):
    """Fehler beim Persistieren, Transaktion wurde zurückgerollt."""


class DatabaseManager:
    """Kapselt SQLAlchemy Engine, Session und CRUD-Zugriffe für das Dashboard.

    Verantwortlichkeiten:
        - Initialisiert die SQLite-Datenbank und erzeugt Tabellen (create_all).
        - Verwaltet eine Session für Datenzugriffe.
        - Stellt CRUD-Methoden für zentrale Domänenobjekte bereit.
        - Vereinheitlicht Commit/Rollback-Handling über ``commit_or_rollback``.

    Hinweis:
        Die Klasse nutzt aktuell eine langlebige Session (``self.session``).
    """

    def __init__(self) -> None:
        """Initialisiert Engine, erstellt Tabellen und öffnet eine erste Session.

        Raises:
            RuntimeError: Wenn die Datenbank nicht initialisiert werden kann (Engine/Tabellen/Session).
        """
        try:
            self.engine = create_engine(DB_URL, echo=False)
            logger.info("Datenbank-Engine erstellt: %s", self.engine.url)
            Base.metadata.create_all(self.engine)
            logger.info("Tabellen vorhanden oder erstellt (create_all).")
            self.SessionLocal = sessionmaker(
                bind=self.engine, expire_on_commit=False
            )  # expire_on_commit=False: Attribute der Objekte bleiben auch nach Commit verfügbar.
            self.session = self.SessionLocal()
            logger.debug("Erste DB-Session geöffnet.")
        except Exception:
            logger.critical("Datenbank-Initialisierung fehlgeschlagen.", exc_info=True)
            raise RuntimeError("Datenbank-Initialisierung fehlgeschlagen.")

    def recreate_session(self) -> None:
        """Schließt die aktuelle Session und erzeugt eine neue.

        Wird beim Logout-Vorgang aufgerufen.
        """
        try:
            self.session.close()
        except Exception:
            logger.exception("Session konnte nicht geschlossen werden.")
        try:
            self.session = self.SessionLocal()
            logger.debug("Neue DB-Session erstellt.")
        except Exception:
            logger.exception("Neue DB-Session konnte nicht erstellt werden.")
            raise RuntimeError("Neue DB-Session konnte nicht erstellt werden.")

    def commit_or_rollback(self, action: str | None = None) -> None:
        """Versucht, die aktuelle Transaktion zu committen, sonst Rollback.

        Args:
            action:
                Optionaler Kontext-String für Logging (z. B. "add_student", "add_enrollment").

        Raises:
            DBTransactionError: Bei Integritätsverletzungen oder allgemeinen DB-Fehlern.
        """
        try:
            self.session.commit()
        except IntegrityError as e:
            logger.exception("IntegrityError beim Commit: %s", action)
            self.session.rollback()
            raise DBTransactionError(
                "Transaktion wurde zurückgerollt. Datenbank-Integrität verletzt."
            ) from e
        except SQLAlchemyError as e:
            logger.exception("SQLAlchemyError beim Commit: %s", action)
            self.session.rollback()
            raise DBTransactionError(
                "Transaktion wurde zurückgerollt. Technischer DB-Fehler."
            ) from e

    def add_student(
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
    ) -> Student:
        """Legt einen Student in der Datenbank an.

        Args:
            name: Name des Studenten.
            matrikelnummer: Matrikelnummer (str).
            email: E-Mail, muss eindeutig sein.
            password: Passwort (wird im Model (Property-Setter) gehasht).
            semester_anzahl: Anzahl der Semester.
            modul_anzahl: Gesamtanzahl der Module im Studiengang.
            start_datum: Studienbeginn.
            ziel_datum: Geplantes Studienenddatum.
            ziel_note: Wunsch-Abschlussnote.

        Returns:
            Das persistierte Student-Objekt.

        Raises:
            DBTransactionError: Wenn Commit/Rollback fehlschlägt (z. B. Unique-Verletzung bei E-Mail).
        """
        student = Student(
            name=name,
            matrikelnummer=matrikelnummer,
            email=email,
            password=password,
            semester_anzahl=semester_anzahl,
            modul_anzahl=modul_anzahl,
            start_datum=start_datum,
            ziel_datum=ziel_datum,
            ziel_note=ziel_note,
        )
        self.session.add(student)
        self.commit_or_rollback(action="add_student")
        return student

    def add_enrollment(
        self,
        student: Student,
        modul: Modul,
        status: EnrollmentStatus,
        einschreibe_datum: datetime.date,
        anzahl_pruefungsleistungen: int,
    ) -> Enrollment:
        """Legt ein Enrollment in der Datenbank an.

        Args:
            student: Student-Objekt (User).
            modul: zugehöriges Modul-Objekt.
            status: Status des Enrollments (bei Erstellung ``in Bearbeitung``.).
            einschreibe_datum: Datum der Moduleinschreibung.
            anzahl_pruefungsleistungen: Anzahl erforderlicher Prüfungsleistungen, um Modul abzuschließen.

        Returns:
            Das persistierte Enrollment-Objekt.

        Raises:
            DBTransactionError: Wenn Commit/Rollback fehlschlägt.
        """
        enrollment = Enrollment(
            student=student,
            modul=modul,
            status=status,
            einschreibe_datum=einschreibe_datum,
            anzahl_pruefungsleistungen=anzahl_pruefungsleistungen,
        )
        self.session.add(enrollment)
        self.commit_or_rollback(action="add_enrollment")
        return enrollment

    def add_pruefungsleistung(
        self,
        teilpruefung: int,
        teilpruefung_gewicht: float,
        versuch: int,
        note: float | None,
        datum: datetime.date | None,
    ) -> Pruefungsleistung:
        """Legt eine Prüfungsleistung in der Datenbank an.

        Args:
            teilpruefung: Nummer X von insgesammt Y erforderlichen Prüfungsleistungen.
            teilpruefung_gewicht: Gewichtung der Prüfungsleistung im Modul.
            versuch: Nummer des Versuchs (max. 3 Versuche pro Teilprüfung).
            note: Note des Prüfungsleistungsversuch.
            datum: Abgabedatum der Prüfungsleistung.

        Returns:
            Das persistierte Prüfungsleistungs-Objekt.

        Raises:
            DBTransactionError: Wenn Commit/Rollback fehlschlägt.
        """
        pruefungsleistung = Pruefungsleistung(
            teilpruefung=teilpruefung,
            teilpruefung_gewicht=teilpruefung_gewicht,
            versuch=versuch,
            note=note,
            datum=datum,
        )
        self.session.add(pruefungsleistung)
        self.commit_or_rollback(action="add_pruefungsleistung")
        return pruefungsleistung

    def add_kurs(self, name: str, nummer: str) -> Kurs:
        """Legt einen Kurs in der Datenbank an.

        Args:
            name: Name des Kurses.
            nummer: Eindeutige Kursnummer (str).

        Returns:
            Das persistierte Kurs-Objekt.

        Raises:
            DBTransactionError: Wenn Commit/Rollback fehlschlägt.
        """
        kurs = Kurs(name=name, nummer=nummer)
        self.session.add(kurs)
        self.commit_or_rollback(action="add_kurs")
        return kurs

    def add_modul(
        self,
        name: str,
        modulcode: str,
        ects_punkte: int,
        studiengang_id: int,
    ) -> Modul:
        """Legt ein Modul in der Datenbank an.

        Args:
            name: Name des Moduls.
            modulcode: Eindeutiger Modulcode (str).
            ects_punkte: Anzahl der erreichten ECTS-Punkte bei Abschluss des Moduls.
            studiengang_id: ID des zugehörigen Studiengangs.

        Returns:
            Das persistierte Modul-Objekt.

        Raises:
            DBTransactionError: Wenn Commit/Rollback fehlschlägt.
        """
        modul = Modul(
            name=name,
            modulcode=modulcode,
            ects_punkte=ects_punkte,
            studiengang_id=studiengang_id,
        )
        self.session.add(modul)
        self.commit_or_rollback(action="add_modul")
        return modul

    def add_semester(
        self, student: Student, nummer: int, beginn: datetime.date, ende: datetime.date
    ) -> Semester:
        """Legt ein Semester in der Datenbank an.

        Args:
            student: Objekt des Studenten (User).
            nummer: Nummer X von insgesamt Y Semestern.
            beginn: Startdatum des jeweiligen Semesters.
            ende: Enddatum des jeweiligen Semesters.

        Returns:
            Das persistierte Semester-Objekt.

        Raises:
            DBTransactionError: Wenn Commit/Rollback fehlschlägt.
        """
        semester = Semester(nummer=nummer, beginn=beginn, ende=ende, student=student)
        self.session.add(semester)
        self.commit_or_rollback(action="add_semester")
        return semester

    def add_studiengang(self, name: str, gesamt_ects_punkte: int) -> Studiengang:
        """Legt einen Studiengang in der Datenbank an.

        Args:
            name: Name des Studiengangs.
            gesamt_ects_punkte: Anzahl der zu erarbeitenden ECTS-Punkte des Studiengangs.

        Returns:
            Das persistierte Studiengang-Objekt.

        Raises:
            DBTransactionError: Wenn Commit/Rollback fehlschlägt.
        """
        studiengang = Studiengang(name=name, gesamt_ects_punkte=gesamt_ects_punkte)
        self.session.add(studiengang)
        self.commit_or_rollback(action="add_studiengang")
        return studiengang

    def add_hochschule(self, name: str) -> Hochschule:
        """Legt eine Hochschule in der Datenbank an.

        Args:
            name: Name der Hochschule.

        Returns:
            Das persistierte Hochschul-Objekt.

        Raises:
            DBTransactionError: Wenn Commit/Rollback fehlschlägt.
        """
        hochschule = Hochschule(name=name)
        self.session.add(hochschule)
        self.commit_or_rollback(action="add_hochschule")
        return hochschule

    def lade_student(self, email: str) -> Student | None:
        """Lädt einen Student anhand der E-Mail.

        Args:
            email: Email-Adresse des Studenten (User).

        Returns:
            Student oder ``None``, wenn keine passende E-Mail existiert.
        """
        stmt = select(Student).where(Student.email == email)
        return self.session.scalars(stmt).first()

    def lade_student_mit_beziehungen(self, email: str) -> Student | None:
        """Lädt einen Student anhand der E-Mail inkl. häufiger Beziehungen.

        Args:
            email: Email-Adresse des Studenten (User).

        Nutzt ``selectinload`` um N+1-Queries zu vermeiden.

        Returns:
            Student oder ``None``, wenn keine passende E-Mail existiert.
        """
        stmt = (
            select(Student)
            .options(
                selectinload(Student.hochschule),
                selectinload(Student.studiengang),
                selectinload(Student.enrollments),
                selectinload(Student.semester),
            )
            .where(Student.email == email)
        )
        return self.session.scalars(stmt).first()

    def lade_kurs(self, kursnummer: str) -> Kurs | None:
        """Lädt einen Kurs anhand der Kursnummer.

        Args:
            kursnummer (str): Eindeutige Kursnummer.

        Returns:
            Kurs oder ``None``, wenn keine passende Kursnummer existiert.
        """
        stmt = select(Kurs).where(Kurs.nummer == kursnummer)
        return self.session.scalars(stmt).first()

    def lade_modul(self, modulcode: str) -> Modul | None:
        """Lädt ein Modul anhand des Modulcodes.

        Args:
            modulcode (str): Eindeutiger Modulcode.

        Returns:
            Modul oder ``None``, wenn kein passender Modulcode existiert.
        """
        stmt = select(Modul).where(Modul.modulcode == modulcode)
        return self.session.scalars(stmt).first()

    def lade_studiengang_mit_id(self, studiengang_id: int) -> Studiengang | None:
        """Lädt einen Studiengang anhand seiner ID.

        Args:
            studiengang_id (int): ID des Studiengangs

        Returns:
            Studiengang oder ``None``, wenn keine passende ID existiert.
        """
        stmt = select(Studiengang).where(Studiengang.id == studiengang_id)
        return self.session.scalars(stmt).first()

    def lade_studiengang_mit_name(
        self, hochschule_id: int, studiengang_name: str
    ) -> Studiengang | None:
        """Lädt einen Studiengang einer Hochschule anhand des Namens.

        Args:
            hochschule_id (int): ID der Hochschule.
            studiengang_name (str): Name des Studiengangs.

        Returns:
            Studiengang oder ``None``, wenn kein passender Studiengang existiert.
        """
        stmt = (
            select(Studiengang)
            .where(Studiengang.hochschule_id == hochschule_id)
            .where(Studiengang.name == studiengang_name)
        )
        return self.session.scalars(stmt).first()

    def lade_alle_studiengaenge_von_hochschule(
        self, hochschule: Hochschule
    ) -> Sequence[Studiengang]:
        """Lädt alle Studiengänge, die einer Hochschule zugeordnet sind.

        Args:
            hochschule: Hochschul-Objekt (ID wird verwendet).

        Returns:
            Sequenz aller Studiengänge dieser Hochschule.
        """
        stmt = select(Studiengang).where(Studiengang.hochschule_id == hochschule.id)
        result = self.session.scalars(stmt)
        return result.all()

    def lade_hochschule_mit_id(self, hochschule_id: int) -> Hochschule | None:
        """Lädt eine Hochschule anhand ihrer ID.

        Args:
            hochschule_id (int): ID der Hochschule.

        Returns:
            Hochschule oder ``None``, wenn keine passende ID existiert.
        """
        stmt = select(Hochschule).where(Hochschule.id == hochschule_id)
        return self.session.scalars(stmt).first()

    def lade_alle_hochschulen(self) -> Sequence[Hochschule]:
        """Lädt alle Hochschulen, die in der Datenbank sind.

        Returns:
            Sequenz aller Hochschulen.
        """
        stmt = select(Hochschule)
        result = self.session.scalars(stmt)
        return result.all()
