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

import logging
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "data.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)
DB_URL = f"sqlite+pysqlite:///{DB_PATH}"

logger = logging.getLogger(__name__)


class DatabaseManager:
    def __init__(self):
        try:
            # Verbindung zur Datenbank
            self.engine = create_engine(DB_URL, echo=False)
            logger.info("Datenbank-Engine erstellt: %s", self.engine.url)
            # Alle Tabellen erzeugen
            Base.metadata.create_all(self.engine)
            logger.info("Tabellen erstellt (create_all).")
            self.SessionLocal = sessionmaker(bind=self.engine, expire_on_commit=False)
            self.session = self.SessionLocal()
            logger.debug("Erste DB-Session geöffnet.")
        except Exception:
            logger.critical("Datenbank-Initialisierung fehlgeschlagen.", exc_info=True)
            raise RuntimeError("Datenbank-Initialisierung fehlgeschlagen.")

    def recreate_session(self):
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

    def add_student(
        self,
        name: str,
        matrikelnummer: str,
        email: str,
        password: str,
        semester_anzahl: int,
        modul_anzahl: int,
        start_datum,
        ziel_datum,
        ziel_note: float,
    ) -> Student:
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
        self.session.commit()
        return student

    def add_enrollment(
        self,
        student: Student,
        modul: Modul,
        status: EnrollmentStatus,
        einschreibe_datum,
        anzahl_pruefungsleistungen,
    ) -> Enrollment:
        enrollment = Enrollment(
            student=student,
            modul=modul,
            status=status,
            einschreibe_datum=einschreibe_datum,
            anzahl_pruefungsleistungen=anzahl_pruefungsleistungen,
        )
        self.session.add(enrollment)
        self.session.commit()
        return enrollment

    def add_pruefungsleistung(
        self, teilpruefung, teilpruefung_gewicht, versuch, note, datum
    ):
        pruefungsleistung = Pruefungsleistung(
            teilpruefung=teilpruefung,
            teilpruefung_gewicht=teilpruefung_gewicht,
            versuch=versuch,
            note=note,
            datum=datum,
        )
        self.session.add(pruefungsleistung)
        self.session.commit()
        return pruefungsleistung

    def add_kurs(self, name: str, nummer: str) -> Kurs:
        kurs = Kurs(name=name, nummer=nummer)
        self.session.add(kurs)
        self.session.commit()
        return kurs

    def add_modul(
        self,
        name: str,
        modulcode: str,
        ects_punkte: int,
        studiengang_id: int,
    ):
        modul = Modul(
            name=name,
            modulcode=modulcode,
            ects_punkte=ects_punkte,
            studiengang_id=studiengang_id,
        )
        self.session.add(modul)
        self.session.commit()
        return modul

    def add_semester(self, student: Student, nummer, beginn, ende):
        semester = Semester(nummer=nummer, beginn=beginn, ende=ende, student=student)
        self.session.add(semester)
        self.session.commit()
        return semester

    def add_studiengang(self, name, gesamt_ects_punkte):
        studiengang = Studiengang(name=name, gesamt_ects_punkte=gesamt_ects_punkte)
        self.session.add(studiengang)
        self.session.commit()
        return studiengang

    def add_hochschule(self, name):
        hochschule = Hochschule(name=name)
        self.session.add(hochschule)
        self.session.commit()
        return hochschule

    def lade_student(self, email: str) -> Student | None:
        stmt = select(Student).where(Student.email == email)
        return self.session.scalars(stmt).first()

    def lade_student_mit_beziehungen(self, email: str) -> Student | None:
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
        return self.session.scalar(stmt)

    def lade_kurs(self, kursnummer) -> Kurs | None:
        stmt = select(Kurs).where(Kurs.nummer == kursnummer)
        return self.session.scalars(stmt).first()

    def lade_modul(self, modulcode) -> Modul | None:
        stmt = select(Modul).where(Modul.modulcode == modulcode)
        return self.session.scalars(stmt).first()

    def lade_studiengang_mit_id(self, id):
        stmt = select(Studiengang).where(Studiengang.id == id)
        return self.session.scalars(stmt).first()

    def lade_studiengang_mit_name(self, hochschule_id, studiengang_name):
        stmt = (
            select(Studiengang)
            .where(Studiengang.hochschule_id == hochschule_id)
            .where(Studiengang.name == studiengang_name)
        )
        return self.session.scalars(stmt).first()

    def lade_alle_studiengaenge_von_hochschule(self, hochschule: Hochschule):
        stmt = (
            select(Studiengang)
            .join(Hochschule)
            .where(Studiengang.hochschule_id == hochschule.id)
        )
        result = self.session.scalars(stmt)
        return result.all()

    def lade_hochschule_mit_id(self, id):
        stmt = select(Hochschule).where(Hochschule.id == id)
        return self.session.scalars(stmt).first()

    def lade_alle_hochschulen(self):
        stmt = select(Hochschule)
        result = self.session.scalars(stmt)
        return result.all()
