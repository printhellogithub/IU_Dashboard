from __future__ import annotations
from email_validator import validate_email, EmailNotValidError
from database import DatabaseManager
from models import (
    Student,
)

import csv
from dateutil.relativedelta import relativedelta


class Controller:
    def __init__(self):
        self.db = DatabaseManager()
        self.student: Student | None = None

    # --- Account & Login ---
    def login(self, email: str, password: str):
        student = self.db.lade_student_mit_beziehungen(email)
        if student and student.verify_password(password):
            self.student = student
            return True
        else:
            return False

    def erstelle_account(self, cache: dict):
        self.cache = cache
        self.student = self.db.add_student(
            name=self.cache["name"],
            matrikelnummer=self.cache["matrikelnummer"],
            email=self.cache["email"],
            password=self.cache["password"],
            semester_anzahl=self.cache["semesteranzahl"],
            start_datum=self.cache["startdatum"],
            ziel_datum=self.cache["zieldatum"],
            ziel_note=self.cache["zielnote"],
        )
        self.erstelle_semester_fuer_student(self.student)
        self.add_hochschule_zu_student(student=self.student, cache=self.cache)
        self.add_studiengang_zu_student(student=self.student, cache=self.cache)
        # if not studiengang in hochschule.studiengaenge:
        self.add_studiengang_zu_hochschule(cache=cache)
        # self.db.session.flush()
        # self.db.session.refresh(self.student)

        self.db.session.commit()

    # Relationships bei neuem Account
    def add_hochschule_zu_student(self, student: Student, cache):
        hs = self.db.lade_hochschule_mit_id(int(cache["hochschuleid"]))
        if hs is None:
            raise ValueError(
                f"Hochschule ({cache['hochschuleid']}) wurde nicht gefunden!"
            )
        student.hochschule = hs
        # session.flush() ?

    def add_studiengang_zu_student(self, student: Student, cache):
        sg = self.db.lade_studiengang_mit_id(int(cache["studiengang_id"]))
        if sg is None:
            raise ValueError(
                f"Studiengang ({cache['studiengang_id']}) wurde nicht gefunden!"
            )
        student.studiengang = sg
        # session.flush()

    def add_studiengang_zu_hochschule(self, cache):
        hs = self.db.lade_hochschule_mit_id(int(cache["hochschuleid"]))
        sg = self.db.lade_studiengang_mit_id(int(cache["studiengang_id"]))
        if not hs:
            raise ValueError(
                f"Hochschule ({cache['hochschuleid']}) wurde nicht gefunden! command: controller.add_studiengang_zu_hochschule"
            )
        if not sg:
            raise ValueError(
                f"Studiengang ({cache['studiengang_id']}) wurde nicht gefunden! command: controller.add_studiengang_zu_hochschule"
            )
        if sg not in hs.studiengaenge:
            hs.studiengaenge.append(sg)

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
        # TODO: unvollständig, muss neu gecoded werden

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
        # TODO: teste diese funktion!

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
        studiengang = self.db.add_studiengang(studiengang_name, gesamt_ects_punkte)
        return {studiengang.id: studiengang.name}

    def erstelle_semester_fuer_student(self, student: Student):
        """Erstellt aus Startdatum und Semesteranzahl einzelne Semesterobjekte"""
        # TODO
        for i in range(student.semester_anzahl):
            beginn = student.start_datum + relativedelta(months=6 * i)
            ende = (beginn + relativedelta(months=6)) - relativedelta(days=1)
            nummer = i + 1
            self.db.add_semester(
                student=student, nummer=nummer, ende=ende, beginn=beginn
            )

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
