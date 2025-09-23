from sqlalchemy.orm import Session, sessionmaker, selectinload
from models_test import Base, Student, Enrollment, Kurs, Hochschule, Status
from sqlalchemy import create_engine, select


class DatabaseManager:
    def __init__(self):
        # Verbindung zur Datenbank
        self.engine = create_engine("sqlite+pysqlite:///test.db", echo=False)
        # Alle Tabellen erzeugen
        Base.metadata.create_all(self.engine)
        SessionLocal = sessionmaker(bind=self.engine, expire_on_commit=False)
        self.session = SessionLocal()
        
        

    def erstelle_student(self, name: str, matrikelnummer: str, email_address: str, password: str) -> Student:
        student = Student(name=name, matrikelnummer=matrikelnummer, email_address=email_address, password=password)
        self.session.add(student)
        self.session.commit()
        # session.refresh(student)
        return student

    def lade_student(self, email: str) -> Student | None:
        stmt = select(Student).where(Student.email_address == email)
        return self.session.scalars(stmt).first()
        
    def erstelle_kurs(self, name: str, nummer: str) -> Kurs:
        kurs = Kurs(kurs_name=name, kurs_nummer=nummer)
        self.session.add(kurs)
        self.session.commit()
        # session.refresh(kurs)
        return kurs
    
    def lade_kurs(self, kursnummer) -> Kurs | None:
        stmt = select(Kurs).where(Kurs.kurs_nummer == kursnummer)
        return self.session.scalars(stmt).first()
    
    def lade_kurse_von_student(self, student: Student) -> list[Kurs]:
        stmt = (
            select(Kurs)
            .join(Enrollment)
            .where(Enrollment.student_id == student.id)
        )
        return list(self.session.scalars(stmt))

    def erstelle_enrollment(self, student: Student, kurs: Kurs, status: Status) -> Enrollment:
        enrollment = Enrollment(student=student, kurs=kurs, status=status)
        self.session.add(enrollment)
        self.session.commit()
        # session.refresh(enrollment)
        return enrollment
    
    def lade_enrollment(self, student:Student, kurs: Kurs) -> Enrollment | None:
        stmt = (
            select(Enrollment)
            .where(Enrollment.student_id == student.id)
            .where(Enrollment.kurs_id == kurs.id)
        )
        return self.session.scalars(stmt).first()
        
    def lade_enrollments_von_student(self, student_id: int) -> list[Enrollment]:
            stmt = (select(Enrollment)
            .options(
                selectinload(Enrollment.kurs),
                selectinload(Enrollment.student),
            )
            .where(Enrollment.student_id == student_id))
            return list(self.session.scalars(stmt))


    def change_enrollment_status(self, enrollment: Enrollment, neuer_status: Status) -> None:
            enrollment.status = neuer_status
            self.session.commit()