from __future__ import annotations
from database import DatabaseManager
from models import (
    Student,
)

# pseudo-code: wie ich mir einen Controller OOP-based vorstellen kann:
# class Controller:
#     def __init__(self, db: DatabaseManager,):
#         self.db = db
#         self.student: Student | None = None

#     def after_log_in_init(self, logged_in, student: Student):
#         if login() == True:
#             pass


class Controller:
    def __init__(self):
        self.db = DatabaseManager()
        self.student: Student | None = None

    # --- Account & Login ---
    def login(self, email: str, password: str):
        student = self.db.lade_student(email)
        if student and student.verify_password(password):
            self.student = student
            return True
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

    def load_dashboard_data(self):
        if not self.student:
            raise RuntimeError("Nicht eingeloggt")
        return {
            "email": self.student.email,
            "name": self.student.name,
            "hochschule": self.student.hochschule.name,
            "studiengang": self.student.studiengang.name,
            "gesamt_ects": self.student.studiengang.gesamt_ects_punkte,
        }

    # ist ohne SQL!!!! -> macht nur Namen in Liste!
    # def get_hochschulen_liste(self):
    #     with open("data/LISTE_Hochschulen_Hochschulkompass.csv") as file:
    #         reader = csv.DictReader(file)
    #         hs_namen_liste = [row["Hochschulname"] for row in reader]
    #     return hs_namen_liste
    def get_hochschulen_liste(self):
        return self.db.lade__alle_hochschulen()

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
