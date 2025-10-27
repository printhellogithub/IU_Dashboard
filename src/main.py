from database import DatabaseManager
from models import (
    Student,
)


class Controller:
    def __init__(self, db: DatabaseManager):
        self.db = db
        self.student: Student | None = None

    # --- Account & Login ---
    def login(self, email: str, password: str) -> Student | None:
        student = self.db.lade_student(email)
        if student and student.verify_password(password):
            self.student = student
            return student
        return None

    def erstelle_account(
        self,
        name: str,
        matrikelnummer: str,
        email: str,
        password: str,
        semester_anzahl,
        start_datum,
        ziel_datum,
        ziel_note,
    ):
        # self.student = self.db.add_student(
        #     name=name,
        #     matrikelnummer=matrikelnummer,
        #     email=email,
        #     password=password,
        #     semester_anzahl=semester_anzahl,
        #     start_datum=start_datum,
        #     ziel_datum=ziel_datum,
        #     ziel_note=ziel_note
        #     )
        # return self.student
        pass

    # # --- Enrollment-Operationen ---
    # def enrollments(self) -> list[Enrollment]:
    #     return self.db.lade_enrollments_von_student(self.student.id)

    # def add_enrollment(self, kursname: str, kursnummer: str) -> Enrollment:
    #     kurs = self.db.lade_kurs(kursnummer) or self.db.add_kurs(
    #         kursname, kursnummer
    #     )
    #     return self.db.add_enrollment(self.student, kurs, EnrollmentStatus.IN_BEARBEITUNG)

    # def change_enrollment_status(self, enrollment: Enrollment, status: EnrollmentStatus):
    #     self.db.change_enrollment_status(enrollment, status)
