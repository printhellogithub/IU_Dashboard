from sqlalchemy.orm import sessionmaker, selectinload
from models import (
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

import csv


class DatabaseManager:
    def __init__(self):
        # Verbindung zur Datenbank
        self.engine = create_engine("sqlite+pysqlite:///data.db", echo=False)
        # Alle Tabellen erzeugen
        Base.metadata.create_all(self.engine)
        SessionLocal = sessionmaker(bind=self.engine, expire_on_commit=False)
        self.session = SessionLocal()

    def add_student(
        self,
        name: str,
        matrikelnummer: str,
        email_address: str,
        password: str,
        semester_anzahl: int,
        start_datum,
        ziel_datum,
        ziel_note: float,
    ) -> Student:
        student = Student(
            name=name,
            matrikelnummer=matrikelnummer,
            email=email_address,
            password=password,
            semester_anzahl=semester_anzahl,
            start_datum=start_datum,
            ziel_datum=ziel_datum,
            ziel_note=ziel_note,
        )
        self.session.add(student)
        self.session.commit()
        # session.refresh(student)
        return student

    def add_enrollment(
        self, student: Student, kurs: Kurs, status: EnrollmentStatus
    ) -> Enrollment:
        enrollment = Enrollment(student=student, kurs=kurs, status=status)
        self.session.add(enrollment)
        self.session.commit()
        # session.refresh(enrollment)
        return enrollment

    # siehe models.py -> class Enrollment -> add_pruefungsleistung
    def add_pruefungsleistung(self, versuch, note, datum):
        pruefungsleistung = Pruefungsleistung(versuch=versuch, note=note, datum=datum)
        self.session.add(pruefungsleistung)
        self.session.commit()
        return pruefungsleistung

    def add_kurs(self, name: str, nummer: str, ects_punkte: int) -> Kurs:
        kurs = Kurs(name=name, nummer=nummer, ects_punkte=ects_punkte)
        self.session.add(kurs)
        self.session.commit()
        # session.refresh(kurs)
        return kurs

    def add_modul(self, name: str, studiengang: Studiengang, kurs: Kurs):
        modul = Modul(name=name)
        self.session.add(modul)
        self.session.commit()
        return modul

    def add_semester(self, nummer, beginn, ende):
        semester = Semester(nummer=nummer, beginn=beginn, ende=ende)
        self.session.add(semester)
        self.session.commit()
        return semester

    def add_studiengang(self, name, gesamt_ects_punkte):
        studiengang = Studiengang(name=name, gesamt_ects_punkte=gesamt_ects_punkte)
        self.session.add(studiengang)
        self.session.commit()
        return studiengang

    def add_hochschulen_von_csv(self):
        with self.session as session:
            with open("data/LISTE_Hochschulen_Hochschulkompass.csv") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    stmt = select(Hochschule).where(
                        Hochschule.name == row["Hochschulname"]
                    )
                    if not session.scalars(stmt).first():
                        hochschule = Hochschule(name=row["Hochschulname"])
                        session.add(hochschule)
                    session.commit()

    def add_hochschule(self, name):
        hochschule = Hochschule(name=name)
        self.session.add(hochschule)
        self.session.commit()
        return hochschule

    def lade_student(self, email: str) -> Student | None:
        stmt = select(Student).where(Student.email == email)
        return self.session.scalars(stmt).first()

    def lade_enrollment(self, student: Student, kurs: Kurs) -> Enrollment | None:
        stmt = (
            select(Enrollment)
            .where(Enrollment.student_id == student.id)
            .where(Enrollment.kurs_id == kurs.id)
        )
        return self.session.scalars(stmt).first()

    def lade_pruefungsleistung(self, enrollment: Enrollment):
        stmt = select(Pruefungsleistung).where(
            Pruefungsleistung.enrollment_id == enrollment.id
        )
        return self.session.scalars(stmt).first()

    def lade_kurs(self, kursnummer) -> Kurs | None:
        stmt = select(Kurs).where(Kurs.nummer == kursnummer)
        return self.session.scalars(stmt).first()

    def lade_modul(self, student: Student):
        stmt = select(Modul).where(Modul.studiengang_id == student.studiengang_id)
        return self.session.scalars(stmt).first()

    def lade_semester(self, student: Student):
        stmt = select(Semester).where(Semester.student_id == student.id)
        return self.session.scalars(stmt).first()

    # where-stmt wird fehlschlagen
    def lade_studiengang(self, student: Student):
        stmt = select(Studiengang).where(Studiengang.id == student.studiengang.id)
        return self.session.scalars(stmt).first()

    # where-stmt wird fehlschlagen
    def lade_hochschule(self, student: Student):
        stmt = select(Hochschule).where(Hochschule.id == student.hochschule_id)
        return self.session.scalars(stmt).first()

    def lade__alle_hochschulen(self):
        stmt = select(Hochschule)
        result = self.session.scalars(stmt)
        return result.all()

    def lade_enrollments_von_student(self, student_id: int) -> list[Enrollment]:
        stmt = (
            select(Enrollment)
            .options(
                selectinload(Enrollment.kurs),
                selectinload(Enrollment.student),
            )
            .where(Enrollment.student_id == student_id)
        )
        return list(self.session.scalars(stmt))

    def lade_kurse_von_student(self, student: Student) -> list[Kurs]:
        stmt = select(Kurs).join(Enrollment).where(Enrollment.student_id == student.id)
        return list(self.session.scalars(stmt))

    def lade_module_von_student(self, student: Student):
        stmt = select(Modul).where(Modul.studiengang_id == student.studiengang_id)
        return list(self.session.scalars(stmt))

    def lade_semester_von_student(self, student: Student):
        stmt = select(Semester).where(Semester.student_id == student.id)
        return list(self.session.scalars(stmt))

    def change_student(self, student: Student):
        pass

    def change_enrollment(self, enrollment: Enrollment):
        pass

    def change_pruefungsleistung(self, pruefungsleistung: Pruefungsleistung):
        pass

    def change_kurs(self, kurs: Kurs):
        pass

    def change_modul(self, modul: Modul):
        pass

    def change_semester(self, semester: Semester):
        pass

    def change_studiengang(self, studiengang: Studiengang):
        pass

    def change_hochschule(self, hochschule: Hochschule):
        pass

    # wurde ersetzt durch enrollment.check_status()

    # def change_enrollment_status(
    #     self, enrollment: Enrollment, neuer_status: EnrollmentStatus
    # ) -> None:
    #     enrollment.status = neuer_status
    #     self.session.commit()
