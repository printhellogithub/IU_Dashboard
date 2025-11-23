from __future__ import annotations
from email_validator import validate_email, EmailNotValidError
from database import DatabaseManager
from models import Enrollment, EnrollmentStatus, Student, Modul, Pruefungsleistung
from hochschulen import hs_dict

# import csv
import datetime
from dateutil.relativedelta import relativedelta


class Controller:
    def __init__(self):
        self.db = DatabaseManager()
        self.student: Student | None = None

        self.erstelle_hochschulen_von_hs_dict()

    # --- Account & Login ---
    def login(self, email: str, password: str):
        verified_email = self.validate_email_for_login(email)
        if isinstance(verified_email, EmailNotValidError):
            return False

        student = self.db.lade_student_mit_beziehungen(verified_email)
        if student and student.verify_password(password):
            self.student = student
            return True
        else:
            return False

    def erstelle_account(self, cache: dict):
        self.cache = cache

        start_datum = datetime.date.fromisoformat(cache["startdatum"])
        zieldatum = datetime.date.fromisoformat(cache["zieldatum"])

        self.student = self.db.add_student(
            name=self.cache["name"],
            matrikelnummer=self.cache["matrikelnummer"],
            email=self.cache["email"],
            password=self.cache["password"],
            semester_anzahl=self.cache["semesteranzahl"],
            modul_anzahl=self.cache["modulanzahl"],
            start_datum=start_datum,
            ziel_datum=zieldatum,
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
        hs = self.db.lade_hochschule_mit_id(int(cache["hochschulid"]))
        if hs is None:
            raise ValueError(
                f"Hochschule ({cache['hochschulid']}) wurde nicht gefunden!"
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
        hs = self.db.lade_hochschule_mit_id(int(cache["hochschulid"]))
        sg = self.db.lade_studiengang_mit_id(int(cache["studiengang_id"]))
        if not hs:
            raise ValueError(
                f"Hochschule ({cache['hochschulid']}) wurde nicht gefunden! command: controller.add_studiengang_zu_hochschule"
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
            "name": self.student.name,
            "studiengang": self.student.studiengang.name,
            "hochschule": self.student.hochschule.name,
            "startdatum": self.student.start_datum,
            "zieldatum": self.student.ziel_datum,
            "zielnote": self.student.ziel_note,
            "modulanzahl": self.student.modul_anzahl,
            "gesamt_ects": self.student.studiengang.gesamt_ects_punkte,
            "semester": self.get_list_of_semester(),
            "enrollments": self.get_list_of_enrollments(),
            "heute": datetime.date.today(),
            "time_progress": self.get_time_progress(),
            "abgeschlossen": self.get_number_of_enrollments_with_status(
                EnrollmentStatus.ABGESCHLOSSEN
            ),
            "in_bearbeitung": self.get_number_of_enrollments_with_status(
                EnrollmentStatus.IN_BEARBEITUNG
            ),
            "nicht_bestanden": self.get_number_of_enrollments_with_status(
                EnrollmentStatus.NICHT_BESTANDEN
            ),
            "ausstehend": self.get_number_of_enrollments_with_status_ausstehend(),
            "erarbeitete_ects": self.get_erarbeitete_ects(),
            "notendurchschnitt": self.get_notendurchschnitt(),
            "exmatrikulationsdatum": self.student.exmatrikulationsdatum,
        }

    def get_time_progress(self):
        if not self.student:
            raise RuntimeError("Nicht eingeloggt")

        dauer = (self.student.ziel_datum - self.student.start_datum).days
        if self.student.exmatrikulationsdatum is not None:
            # Status: Exmatrikuliert
            bisher = (
                self.student.exmatrikulationsdatum - self.student.start_datum
            ).days
            progress = round(max(0, min(bisher / dauer, 1)), 3)
        else:
            bisher = (datetime.date.today() - self.student.start_datum).days
            progress = round(max(0, min(bisher / dauer, 1)), 3)
        return progress

    def get_number_of_enrollments_with_status(self, status: EnrollmentStatus) -> int:
        if not self.student:
            raise RuntimeError("Nicht eingeloggt")
        liste = [
            enrollment
            for enrollment in self.student.enrollments
            if enrollment.status == status
        ]
        return len(liste)

    def get_number_of_enrollments_with_status_ausstehend(self) -> int:
        if not self.student:
            raise RuntimeError("Nicht eingeloggt")
        ausstehende = self.student.modul_anzahl - (
            self.get_number_of_enrollments_with_status(EnrollmentStatus.ABGESCHLOSSEN)
            + self.get_number_of_enrollments_with_status(
                EnrollmentStatus.IN_BEARBEITUNG
            )
            + self.get_number_of_enrollments_with_status(
                EnrollmentStatus.NICHT_BESTANDEN
            )
        )
        return ausstehende

    def get_erarbeitete_ects(self) -> int:
        if not self.student:
            raise RuntimeError("Nicht eingeloggt")
        liste = [
            enrollment.modul.ects_punkte
            for enrollment in self.student.enrollments
            if enrollment.status == EnrollmentStatus.ABGESCHLOSSEN
        ]
        return sum(liste)

    def get_notendurchschnitt(self) -> float | str:
        if not self.student:
            raise RuntimeError("Nicht eingeloggt")
        liste = [
            enrollment.berechne_enrollment_note()
            for enrollment in self.student.enrollments
            if enrollment.status == EnrollmentStatus.ABGESCHLOSSEN
        ]
        if liste != []:
            return float(round((sum(liste) / len(liste)), 2))  # type: ignore
        else:
            return "--"

    def get_list_of_semester(self) -> list:
        if not self.student:
            raise RuntimeError("Nicht eingeloggt")
        semester_list = []
        semester_dict = {}
        for semester in self.student.semester:
            semester_dict = {
                "id": semester.id,
                "nummer": semester.nummer,
                "beginn": semester.beginn,
                "ende": semester.ende,
                "status": str(
                    semester.get_semester_status(self.student.exmatrikulationsdatum)
                ),
            }
            semester_list.append(semester_dict)
        return semester_list

    def get_list_of_enrollments(self) -> list:
        if not self.student:
            raise RuntimeError("Nicht eingeloggt")
        enrollment_list = []
        enrollment_dict = {}
        for enrollment in self.student.enrollments:
            enrollment_dict = self.get_enrollment_data(enrollment.id)
            enrollment_list.append(enrollment_dict)
        return enrollment_list

    def get_list_of_kurse(self, modul: Modul) -> list:
        if not self.student:
            raise RuntimeError("Nicht eingeloggt")
        kurse_list = []
        kurse_dict = {}
        for kurs in modul.kurse:
            kurse_dict = {
                "id": kurs.id,
                "name": kurs.name,
                "nummer": kurs.nummer,
            }
            kurse_list.append(kurse_dict)
        return kurse_list

    def get_list_of_pruefungsleistungen(self, enrollment: Enrollment) -> list:
        if not self.student:
            raise RuntimeError("Nicht eingeloggt")
        pruefungsleistungen_list = []
        pruefungsleistungen_dict = {}
        for pl in enrollment.pruefungsleistungen:
            pruefungsleistungen_dict = self.get_pl_dict(pl)
            pruefungsleistungen_list.append(pruefungsleistungen_dict)
        return pruefungsleistungen_list

    def get_pl_dict(self, pl: Pruefungsleistung):
        return {
            "id": pl.id,
            "teilpruefung": pl.teilpruefung,
            "teilpruefung_gewicht": pl.teilpruefung_gewicht,
            "versuch": pl.versuch,
            "note": pl.note,
            "datum": pl.datum,
            "ist_bestanden": pl.ist_bestanden(),
        }

    def get_pl_with_id(self, enrollment_id, pl_id):
        if not self.student:
            raise RuntimeError("Nicht eingeloggt")
        for enrollment in self.student.enrollments:
            if enrollment.id == enrollment_id:
                for pl in enrollment.pruefungsleistungen:
                    if pl.id == pl_id:
                        return self.get_pl_dict(pl)
        return {}

    def get_enrollment_data(self, id):
        if not self.student:
            raise RuntimeError("Nicht eingeloggt")
        for enrollment in self.student.enrollments:
            if enrollment.id == id:
                enrollment.check_status()
                enrollment_dict = {
                    "id": enrollment.id,
                    "einschreibe_datum": enrollment.einschreibe_datum,
                    "end_datum": enrollment.end_datum,
                    "status": str(enrollment.status).strip("EnrollmentStatus."),
                    "modul_id": enrollment.modul_id,
                    "modul_name": enrollment.modul.name,
                    "modul_code": enrollment.modul.modulcode,
                    "modul_ects": enrollment.modul.ects_punkte,
                    "kurse": self.get_list_of_kurse(enrollment.modul),
                    "anzahl_pruefungsleistungen": enrollment.anzahl_pruefungsleistungen,
                    "pruefungsleistungen": self.get_list_of_pruefungsleistungen(
                        enrollment,
                    ),
                    "enrollment_note": enrollment.berechne_enrollment_note(),
                }
            else:
                continue
            return enrollment_dict
        return {}

    def erstelle_hochschulen_von_hs_dict(self):
        hochschul_namen = {h.name for h in self.db.lade_alle_hochschulen()}
        for name in hs_dict.values():
            if not name:
                continue
            if name not in hochschul_namen:
                self.erstelle_hochschule(hochschul_name=name)

    # gibt dict mit Hochschul-Namen zurück, die in csv sind + id als key
    def get_hochschulen_dict(self) -> dict[int, str]:
        hochschulen = self.db.lade_alle_hochschulen()
        hochschulen_dict: dict[int, str] = {}
        hs_namen_set = set(hs_dict.values())
        for hochschule in hochschulen:
            if hochschule.name in hs_namen_set:
                hochschulen_dict[hochschule.id] = hochschule.name
        return hochschulen_dict

    def get_studiengaenge_von_hs_dict(self, hochschule_id) -> dict[int, str]:
        hochschule = self.db.lade_hochschule_mit_id(hochschule_id)
        if hochschule:
            studiengaenge = self.db.lade_alle_studiengaenge_von_hochschule(hochschule)
            studiengaenge_dict = {}
            for studiengang in studiengaenge:
                studiengaenge_dict[studiengang.id] = studiengang.name
            return studiengaenge_dict
        else:
            return {0: ""}

    def erstelle_hochschule(self, hochschul_name) -> dict[int, str]:
        hochschule = self.db.add_hochschule(hochschul_name)
        return {hochschule.id: hochschule.name}

    def erstelle_studiengang(self, studiengang_name, gesamt_ects_punkte):
        studiengang = self.db.add_studiengang(studiengang_name, gesamt_ects_punkte)
        return {studiengang.id: studiengang.name}

    def erstelle_semester_fuer_student(self, student: Student):
        """Erstellt aus Startdatum und Semesteranzahl einzelne Semesterobjekte."""

        assert isinstance(student.start_datum, datetime.date)
        assert isinstance(student.ziel_datum, datetime.date)
        assert isinstance(student.semester_anzahl, int) and student.semester_anzahl > 0

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

    def validate_email_for_login(self, value: str):
        try:
            emailinfo = validate_email(value, check_deliverability=False)
            email = emailinfo.normalized
            return email
        except EmailNotValidError as e:
            return e

    def get_enrollment_status(self, enrollment_id: int) -> str | None:
        if self.student:
            for enrollment in self.student.enrollments:
                if enrollment_id == enrollment.id:
                    enrollment.check_status()
                    return str(enrollment.status)
        else:
            return None

    def check_if_already_enrolled(self, enrollment_cache):
        if self.student:
            for enrollment in self.student.enrollments:
                if enrollment_cache["modul_code"] == enrollment.modul.modulcode:
                    return True
                else:
                    continue
            return False

    def erstelle_enrollment(self, enrollment_cache):
        if not self.student:
            raise RuntimeError("Nicht eingeloggt")

        # Einschreibedatum setzen
        einschreibe_datum_str = enrollment_cache["startdatum"]
        try:
            einschreibe_datum = datetime.date.fromisoformat(einschreibe_datum_str)
        except ValueError:
            raise ValueError(f"Ungültiges Startdatum: {einschreibe_datum_str}")

        # Modul erstellen, falls nicht vorhanden
        modul = self.db.lade_modul(enrollment_cache["modul_code"])
        if modul is None:
            modul = self.db.add_modul(
                name=enrollment_cache["modul_name"],
                modulcode=enrollment_cache["modul_code"],
                ects_punkte=enrollment_cache["modul_ects"],
                studiengang_id=self.student.studiengang_id,
            )
        # Kurse erstellen, falls nicht vorhanden
        for kurs_dict in enrollment_cache["kurse_list"]:
            for key, value in kurs_dict.items():
                kursnummer = key
                kurs = self.db.lade_kurs(kursnummer=kursnummer)
                if kurs is None:
                    kurs = self.db.add_kurs(name=value, nummer=kursnummer)
                if kurs not in modul.kurse:
                    modul.kurse.append(kurs)
        # enrollment erstellen
        enrollment = self.db.add_enrollment(
            student=self.student,
            modul=modul,
            status=EnrollmentStatus.IN_BEARBEITUNG,
            einschreibe_datum=einschreibe_datum,
            anzahl_pruefungsleistungen=enrollment_cache["pl_anzahl"],
        )
        # Prüfungsleistungen erstellen:
        for i in range(enrollment.anzahl_pruefungsleistungen):
            for v in range(1, 4, 1):
                enrollment.add_pruefungsleistung(
                    teilpruefung=i,
                    teilpruefung_gewicht=round(
                        float(1 / enrollment.anzahl_pruefungsleistungen), ndigits=2
                    ),
                    versuch=v,
                    note=None,
                    datum=None,
                )

        enrollment_dict = {
            "id": enrollment.id,
            "einschreibe_datum": enrollment.einschreibe_datum,
            "end_datum": enrollment.end_datum,
            "status": str(enrollment.status).strip("EnrollmentStatus."),
            "modul_id": enrollment.modul_id,
            "modul_name": enrollment.modul.name,
            "modul_code": enrollment.modul.modulcode,
            "modul_ects": enrollment.modul.ects_punkte,
            "kurse": self.get_list_of_kurse(enrollment.modul),
            "anzahl_pruefungsleistungen": enrollment.anzahl_pruefungsleistungen,
            "pruefungsleistungen": self.get_list_of_pruefungsleistungen(enrollment),
        }
        self.db.session.commit()
        return enrollment_dict

    def change_pl(self, enrollment_id, pl_dict):
        if not self.student:
            raise RuntimeError("Nicht eingeloggt")

        # Einschreibedatum setzen
        pl_datum_str = pl_dict["datum"]
        try:
            pl_datum = datetime.date.fromisoformat(pl_datum_str)
        except ValueError:
            raise ValueError(f"Ungültiges Startdatum: {pl_datum_str}")

        for enrollment in self.student.enrollments:
            if enrollment.id == enrollment_id:
                for pl in enrollment.pruefungsleistungen:
                    if pl.id == pl_dict["id"]:
                        pl.datum = pl_datum
                        pl.note = pl_dict["note"]
                        self.db.session.commit()
                        enrollment.check_status()

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
