from __future__ import annotations
from email_validator import validate_email, EmailNotValidError
from database import DatabaseManager
from models import (
    Student,
)

import csv

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

    def erstelle_account(self, cache):
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

    # gibt dict mit Hochschul-Namen zurück, die in csv sind + id als key
    def get_hochschulen_dict(self) -> dict[int, str]:
        try:
            with open("data/LISTE_Hochschulen_Hochschulkompass.csv") as file:
                reader = csv.DictReader(file)
                hs_namen_liste = [row["Hochschulname"] for row in reader]
                alle_hs = self.db.lade_alle_hochschulen()
                hs_dict = {}
                for value in alle_hs:
                    if value.name in hs_namen_liste:
                        hs_dict[value.id] = value.name
            return hs_dict
        except FileNotFoundError:
            return {}

    def get_studiengaenge_von_hs_dict(self, hochschule_id) -> dict[int, str]:
        hochschule = self.db.lade_hochschule_mit_id(hochschule_id)
        if hochschule:
            studiengaenge = self.db.lade_alle_studiengaenge_von_hochschule(hochschule)
            studiengaenge_dict = {}
            for studiengang in studiengaenge:
                studiengaenge_dict[studiengang.id] = studiengang.name
            return studiengaenge_dict
        else:
            return {}

    def erstelle_hochschule(self, hochschul_name) -> dict[int, str]:
        hochschule = self.db.add_hochschule(hochschul_name)
        return {hochschule.id: hochschule.name}

    def erstelle_studiengang(self, studiengang_name, gesamt_ects_punkte):
        # To-Do
        pass

    def validate_email_for_new_account(self, value: str):
        try:
            emailinfo = validate_email(value, check_deliverability=True)
            email = emailinfo.normalized
            return email
        except EmailNotValidError as e:
            return e

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
