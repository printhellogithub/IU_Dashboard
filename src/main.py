from __future__ import annotations
from email_validator import validate_email, EmailNotValidError
from src.database import DatabaseManager
from src.models import Enrollment, EnrollmentStatus, Student, Modul, Pruefungsleistung
from data.hochschulen import hs_dict
from data.hs_dict_kurz import hs_dict_kurz

import datetime
from dateutil.relativedelta import relativedelta
import logging

logger = logging.getLogger(__name__)


class Controller:
    def __init__(self, db: DatabaseManager | None = None, seed: bool = True):
        self.db = db or DatabaseManager()

        self.student: Student | None = None
        if seed:
            self.erstelle_hochschulen_von_hs_dict()
            logger.debug("Hochschulen aus hs_dict erstellt, falls nicht vorhanden.")
        logger.debug("Controller initialisiert")

    # --- Account & Login ---
    def login(self, email: str, password: str):
        verified_email = self.validate_email_for_login(email)
        if isinstance(verified_email, EmailNotValidError):
            logger.debug(f"EmailNotValidError: {verified_email}")
            return False
        logger.debug(f"Login-Versuch mit {verified_email}")
        student = self.db.lade_student_mit_beziehungen(verified_email)
        if student and student.verify_password(password):
            self.student = student
            logger.info("Login erfolgreich: %s", self.student.email)
            return True
        else:
            logger.info("Login fehlgeschlagen: %s", verified_email)
            return False

    def erstelle_account(self, cache: dict):
        start_datum = datetime.date.fromisoformat(cache["startdatum"])
        zieldatum = datetime.date.fromisoformat(cache["zieldatum"])

        self.student = self.db.add_student(
            name=cache["name"],
            matrikelnummer=cache["matrikelnummer"],
            email=cache["email"],
            password=cache["password"],
            semester_anzahl=cache["semesteranzahl"],
            modul_anzahl=cache["modulanzahl"],
            start_datum=start_datum,
            ziel_datum=zieldatum,
            ziel_note=cache["zielnote"],
        )
        logger.info("Student erstellt: %s", self.student.email)
        self.erstelle_semester_fuer_student(self.student)
        self.add_hochschule_zu_student(student=self.student, cache=cache)
        self.add_studiengang_zu_student(student=self.student, cache=cache)
        # if not studiengang in hochschule.studiengaenge:
        self.add_studiengang_zu_hochschule(cache=cache)
        # self.db.session.flush()
        # self.db.session.refresh(self.student)

        self.db.session.commit()
        logger.info("Account mit Beziehungen erstellt: %s", self.student.email)

    # Relationships bei neuem Account
    def add_hochschule_zu_student(self, student: Student, cache):
        hs = self.db.lade_hochschule_mit_id(int(cache["hochschulid"]))
        if hs is None:
            logger.warning("Hochschule nicht gefunden: id=%s", cache["hochschulid"])
            raise ValueError(
                f"Hochschule ({cache['hochschulid']}) wurde nicht gefunden!"
            )
        student.hochschule = hs
        self.db.session.commit()
        logger.info("Hochschule %s Student %s zugeordnet", hs.name, student.email)
        # session.flush() ?

    def add_studiengang_zu_student(self, student: Student, cache):
        sg = self.db.lade_studiengang_mit_id(int(cache["studiengang_id"]))
        if sg is None:
            logger.warning("Studiengang nicht gefunden: id=%s", cache["studiengang_id"])
            raise ValueError(
                f"Studiengang ({cache['studiengang_id']}) wurde nicht gefunden!"
            )
        student.studiengang = sg
        self.db.session.commit()
        logger.info("Studiengang %s Student %s zugeordnet", sg.name, student.email)
        # session.flush()

    def add_studiengang_zu_hochschule(self, cache):
        hs = self.db.lade_hochschule_mit_id(int(cache["hochschulid"]))
        sg = self.db.lade_studiengang_mit_id(int(cache["studiengang_id"]))
        if not hs:
            logger.warning("Hochschule nicht gefunden: id=%s", cache["hochschulid"])
            raise ValueError(
                f"Hochschule ({cache['hochschulid']}) wurde nicht gefunden! command: controller.add_studiengang_zu_hochschule"
            )
        if not sg:
            logger.warning("Studiengang nicht gefunden: id=%s", cache["studiengang_id"])
            raise ValueError(
                f"Studiengang ({cache['studiengang_id']}) wurde nicht gefunden! command: controller.add_studiengang_zu_hochschule"
            )
        if sg not in hs.studiengaenge:
            hs.studiengaenge.append(sg)
            self.db.session.commit()
            logger.info("Studiengang %s Hochschule %s zugeordnet", sg.name, hs.name)

    def load_dashboard_data(self):
        if not self.student:
            logger.warning("Nicht eingeloggt: load_dashboard_data aufgerufen.")
            raise RuntimeError("Nicht eingeloggt")
        return {
            "email": self.student.email,
            "name": self.student.name,
            "matrikelnummer": self.student.matrikelnummer,
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
            logger.warning("Nicht eingeloggt: get_time_progress aufgerufen.")
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
        logger.debug("get_time_progress ausgeführt")
        return progress

    def get_semester_amount(self):
        if not self.student:
            logger.warning("Nicht eingeloggt: get_semester_amount aufgerufen.")
            raise RuntimeError("Nicht eingeloggt")

        for semester in self.student.semester:
            if semester.nummer == self.student.semester_anzahl:
                dauer_aller_semester = (semester.ende - self.student.start_datum).days
                dauer_start_ziel = (
                    self.student.ziel_datum - self.student.start_datum
                ).days
                amount = round(
                    # max(0, min(dauer_aller_semester / dauer_start_ziel, 1)), 3
                    max(0, (dauer_aller_semester / dauer_start_ziel)),
                    3,
                )
                logger.debug("get_semester_amount ausgeführt")
                return amount

    def get_number_of_enrollments_with_status(self, status: EnrollmentStatus) -> int:
        if not self.student:
            logger.warning(
                "Nicht eingeloggt: get_number_of_enrollments_with_status aufgerufen."
            )
            raise RuntimeError("Nicht eingeloggt")
        liste = [
            enrollment
            for enrollment in self.student.enrollments
            if enrollment.status == status
        ]
        logger.debug("get_number_of_enrollments_with_status %s ausgeführt", str(status))
        return len(liste)

    def get_number_of_enrollments_with_status_ausstehend(self) -> int:
        if not self.student:
            logger.warning(
                "Nicht eingeloggt: get_number_of_enrollments_with_status_ausstehend aufgerufen."
            )
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
        logger.debug("get_number_of_enrollments_with_status_ausstehend ausgeführt")
        return ausstehende

    def get_erarbeitete_ects(self) -> int:
        if not self.student:
            logger.warning("Nicht eingeloggt: get_erarbeitete_ects aufgerufen.")
            raise RuntimeError("Nicht eingeloggt")
        liste = [
            enrollment.modul.ects_punkte
            for enrollment in self.student.enrollments
            if enrollment.status == EnrollmentStatus.ABGESCHLOSSEN
        ]
        logger.debug("get_erarbeitete_ects ausgeführt")
        return sum(liste)

    def get_notendurchschnitt(self) -> float | str:
        if not self.student:
            logger.warning("Nicht eingeloggt: get_notendurchschnitt aufgerufen.")
            raise RuntimeError("Nicht eingeloggt")
        liste = [
            enrollment.berechne_enrollment_note()
            for enrollment in self.student.enrollments
            if enrollment.status == EnrollmentStatus.ABGESCHLOSSEN
        ]
        if liste != []:
            logger.debug("get_notendurchschnitt ausgeführt")
            return float(round((sum(liste) / len(liste)), 2))  # type: ignore
        else:
            logger.debug("get_notendurchschnitt ausgeführt")
            return "--"

    def get_list_of_semester(self) -> list:
        if not self.student:
            logger.warning("Nicht eingeloggt: get_list_of_semester aufgerufen.")
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
        logger.debug("get_list_of_semester ausgeführt")
        return semester_list

    def get_list_of_enrollments(self) -> list:
        if not self.student:
            logger.warning("Nicht eingeloggt: get_list_of_enrollments aufgerufen.")
            raise RuntimeError("Nicht eingeloggt")
        enrollment_list = []
        enrollment_dict = {}
        for enrollment in self.student.enrollments:
            enrollment_dict = self.get_enrollment_data(enrollment.id)
            enrollment_list.append(enrollment_dict)
        logger.debug("get_list_of_enrollments ausgeführt")
        return enrollment_list

    def get_list_of_kurse(self, modul: Modul) -> list:
        if not self.student:
            logger.warning("Nicht eingeloggt: get_list_of_kurse aufgerufen.")
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
        logger.debug("get_list_of_kurse ausgeführt")
        return kurse_list

    def get_list_of_pruefungsleistungen(self, enrollment: Enrollment) -> list:
        if not self.student:
            logger.warning(
                "Nicht eingeloggt: get_list_of_pruefungsleistungen aufgerufen."
            )
            raise RuntimeError("Nicht eingeloggt")
        pruefungsleistungen_list = []
        pruefungsleistungen_dict = {}
        for pl in enrollment.pruefungsleistungen:
            pruefungsleistungen_dict = self.get_pl_dict(pl)
            pruefungsleistungen_list.append(pruefungsleistungen_dict)
        logger.debug("get_list_of_pruefungsleistungen ausgeführt")
        return pruefungsleistungen_list

    def get_pl_dict(self, pl: Pruefungsleistung):
        logger.debug("get_pl_dict ausgeführt")
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
            logger.warning("Nicht eingeloggt: get_pl_with_id aufgerufen.")
            raise RuntimeError("Nicht eingeloggt")
        for enrollment in self.student.enrollments:
            if enrollment.id == enrollment_id:
                for pl in enrollment.pruefungsleistungen:
                    if pl.id == pl_id:
                        logger.debug("get_pl_with_id ausgeführt")
                        return self.get_pl_dict(pl)
        return {}

    def get_enrollment_data(self, id):
        if not self.student:
            logger.warning("Nicht eingeloggt: get_enrollment_data aufgerufen.")
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
            logger.debug("get_enrollment_data ausgeführt")
            return enrollment_dict
        return {}

    def erstelle_hochschulen_von_hs_dict(self):
        hochschul_namen = {h.name for h in self.db.lade_alle_hochschulen()}
        for name in hs_dict.values():
            if not name:
                continue
            if name not in hochschul_namen:
                self.erstelle_hochschule(hochschul_name=name)

    def get_hs_kurzname_if_notwendig(self, name):
        if len(name) > 50:
            for dictionary in hs_dict_kurz.values():
                for long, short in dictionary.items():
                    if long == name:
                        logger.debug(
                            "get_hs_kurzname_if_notwendig ausgeführt: Name lang - Kurz zurück"
                        )
                        return short
                    else:
                        pass

            return name
        else:
            logger.debug("get_hs_kurzname_if_notwendig ausgeführt: Name kurz")
            return name

    def get_hochschulen_dict(self) -> dict[int, str]:
        hochschulen = self.db.lade_alle_hochschulen()
        hochschulen_dict: dict[int, str] = {}
        hs_namen_set = set(hs_dict.values())
        for hochschule in hochschulen:
            if hochschule.name in hs_namen_set:
                hochschulen_dict[hochschule.id] = hochschule.name
        logger.debug("get_hochschulen_dict ausgeführt")
        return hochschulen_dict

    def get_studiengaenge_von_hs_dict(self, hochschule_id) -> dict[int, str]:
        hochschule = self.db.lade_hochschule_mit_id(hochschule_id)
        if hochschule:
            studiengaenge = self.db.lade_alle_studiengaenge_von_hochschule(hochschule)
            studiengaenge_dict = {}
            for studiengang in studiengaenge:
                studiengaenge_dict[studiengang.id] = studiengang.name
            logger.debug("get_studiengaenge_von_hs_dict ausgeführt")
            return studiengaenge_dict
        else:
            logger.debug("get_studiengaenge_von_hs_dict ausgeführt - keine gefunden")
            return {0: ""}

    def get_studiengang_id(self, studiengang_name, hochschule_id) -> dict[int, str]:
        hochschule = self.db.lade_hochschule_mit_id(hochschule_id)
        if hochschule:
            studiengang = self.db.lade_studiengang_mit_name(
                hochschule_id=hochschule.id, studiengang_name=studiengang_name
            )
            if studiengang:
                logger.debug(
                    "get_studiengang_id ausgeführt: %s: %s",
                    studiengang.id,
                    studiengang.name,
                )
                return {studiengang.id: studiengang.name}
            else:
                logger.debug("get_studiengang_id ausgeführt: {0: }")
                return {0: ""}
        else:
            logger.debug("get_studiengang_id ausgeführt: {0: }")
            return {0: ""}

    def erstelle_hochschule(self, hochschul_name) -> dict[int, str]:
        hochschule = self.db.add_hochschule(hochschul_name)
        self.db.session.commit()
        logger.info("Hochschule erstellt: %s", hochschule.id)
        return {hochschule.id: hochschule.name}

    def erstelle_studiengang(self, studiengang_name, gesamt_ects_punkte):
        studiengang = self.db.add_studiengang(studiengang_name, gesamt_ects_punkte)
        self.db.session.commit()
        logger.info("Studiengang erstellt: %s", studiengang.id)
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
        self.db.session.commit()
        logger.info("Semester wurden erstellt: %s", student.email)

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

    def check_if_email_exists(self, email):
        if self.db.lade_student(email=email):
            return True
        else:
            return False

    def check_if_already_enrolled(self, enrollment_cache):
        if self.student:
            for enrollment in self.student.enrollments:
                if enrollment_cache["modul_code"] == enrollment.modul.modulcode:
                    return True
                else:
                    continue
            return False
        else:
            logger.warning("Nicht eingeloggt: check_if_already_enrolled aufgerufen.")
            raise RuntimeError("Nicht eingeloggt")

    def get_startdatum(self):
        if not self.student:
            logger.warning("Nicht eingeloggt: get_startdatum aufgerufen.")
            raise RuntimeError("Nicht eingeloggt")
        return self.student.start_datum

    def erstelle_enrollment(self, enrollment_cache):
        if not self.student:
            logger.warning("Nicht eingeloggt: erstelle_enrollment aufgerufen.")
            raise RuntimeError("Nicht eingeloggt")

        # Einschreibedatum setzen
        einschreibe_datum_str = enrollment_cache["startdatum"]
        try:
            einschreibe_datum = datetime.date.fromisoformat(einschreibe_datum_str)
        except ValueError:
            logger.warning(
                "Ungültiges Startdatum in erstelle_enrollment: %s",
                einschreibe_datum_str,
            )
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
            logger.info("Modul erstellt: %s", modul.id)
        # Kurse erstellen, falls nicht vorhanden
        for key, value in enrollment_cache["kurse_list"].items():
            kursnummer = key
            kurs = self.db.lade_kurs(kursnummer=kursnummer)
            if kurs is None:
                kurs = self.db.add_kurs(name=value, nummer=kursnummer)
                logger.info("Kurs erstellt: %s", kurs.id)
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
        logger.info(
            "Enrollment %s erstellt: Student: %s, Modul: %s",
            enrollment.id,
            self.student.email,
            modul.id,
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
        logger.info(
            "Prüfungsleistungen für Enrollment %s erstellt",
            enrollment.id,
        )
        # erzeugte Objekte bekommen IDs von DB.
        self.db.session.flush()

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
            logger.warning("Nicht eingeloggt: change_pl aufgerufen.")
            raise RuntimeError("Nicht eingeloggt")

        # Einschreibedatum setzen
        pl_datum_str = pl_dict["datum"]
        try:
            pl_datum = datetime.date.fromisoformat(pl_datum_str)
        except ValueError:
            logger.warning("Ungültiges Startdatum in change_pl: %s", pl_datum_str)
            raise ValueError(f"Ungültiges Startdatum: {pl_datum_str}")

        for enrollment in self.student.enrollments:
            if enrollment.id == enrollment_id:
                for pl in enrollment.pruefungsleistungen:
                    if pl.id == pl_dict["id"]:
                        pl.datum = pl_datum
                        pl.note = pl_dict["note"]
                        logger.info(
                            "Prüfungsleistungen für Enrollment %s geändert: PL-ID=%s",
                            enrollment.id,
                            pl.id,
                        )
                        self.db.session.commit()
                        enrollment.check_status()

    def change_email(self, new_email: str):
        if not self.student:
            logger.warning("Nicht eingeloggt: change_email aufgerufen.")
            raise RuntimeError("Nicht eingeloggt")
        self.student.email = new_email
        self.db.session.commit()
        logger.info("change_email: s.id=%s, email=%s", self.student.id, new_email)

    def change_password(self, new_password: str):
        if not self.student:
            logger.warning("Nicht eingeloggt: change_password aufgerufen.")
            raise RuntimeError("Nicht eingeloggt")
        self.student.password = new_password
        self.db.session.commit()
        logger.info("change_password: s.id=%s", self.student.id)

    def change_name(self, new_name: str):
        if not self.student:
            logger.warning("Nicht eingeloggt: change_name aufgerufen.")
            raise RuntimeError("Nicht eingeloggt")
        self.student.name = new_name
        self.db.session.commit()
        logger.info("change_name: s.id=%s, name=%s", self.student.id, new_name)

    def change_matrikelnummer(self, value: str):
        if not self.student:
            logger.warning("Nicht eingeloggt: change_matrikelnummer aufgerufen.")
            raise RuntimeError("Nicht eingeloggt")
        self.student.matrikelnummer = value
        self.db.session.commit()
        logger.info("changed_matrikelnummer: s.id=%s, m.nr=%s", self.student.id, value)

    def change_semester_anzahl(self, value: int):
        if not self.student:
            logger.warning("Nicht eingeloggt: change_semester_anzahl aufgerufen.")
            raise RuntimeError("Nicht eingeloggt")
        self.student.semester_anzahl = value
        self.student.semester.clear()
        self.erstelle_semester_fuer_student(self.student)
        self.db.session.commit()
        logger.info(
            "change_semester_anzahl: s.id=%s to %s semester", self.student.id, value
        )

    def change_startdatum(self, value: datetime.date):
        if not self.student:
            logger.warning("Nicht eingeloggt: change_startdatum aufgerufen.")
            raise RuntimeError("Nicht eingeloggt")
        self.student.start_datum = value
        self.student.semester.clear()
        self.erstelle_semester_fuer_student(self.student)
        self.db.session.commit()
        logger.info("change_startdatum: s.id=%s to %s", self.student.id, value)

    def change_gesamt_ects(self, value: int):
        if not self.student:
            logger.warning("Nicht eingeloggt: change_gesamt_ects aufgerufen.")
            raise RuntimeError("Nicht eingeloggt")
        self.student.studiengang.gesamt_ects_punkte = value
        self.db.session.commit()
        logger.info("change_gesamt_ects: s.id=%s to %s", self.student.id, value)

    def change_modul_anzahl(self, value: int):
        if not self.student:
            logger.warning("Nicht eingeloggt: change_modul_anzahl aufgerufen.")
            raise RuntimeError("Nicht eingeloggt")
        self.student.modul_anzahl = value
        self.db.session.commit()
        logger.info("change_modul_anzahl: s.id=%s to %s", self.student.id, value)

    def change_hochschule(self, id, hs):
        if not self.student:
            logger.warning("Nicht eingeloggt: change_hochschule aufgerufen.")
            raise RuntimeError("Nicht eingeloggt")
        cache = {
            "hochschulid": id,
            "hochschulname": hs,
            "studiengang_id": self.student.studiengang_id,
        }
        self.add_hochschule_zu_student(student=self.student, cache=cache)
        self.change_studiengang(value=self.student.studiengang.name)
        self.db.session.commit()
        logger.info("change_hochschule: s.id=%s to hs.id=%s", self.student.id, id)

    def change_studiengang(self, value):
        if not self.student:
            logger.warning("Nicht eingeloggt: change_studiengang aufgerufen.")
            raise RuntimeError("Nicht eingeloggt")
        studiengang = [
            studiengang
            for studiengang in self.student.hochschule.studiengaenge
            if studiengang.name == value
        ]
        self.student.enrollments.clear()
        if studiengang:
            self.student.studiengang = studiengang[0]
        else:
            studiengang = self.erstelle_studiengang(
                value,
                self.student.studiengang.gesamt_ects_punkte,
            )
            for k, v in studiengang.items():
                neu_cache = {
                    "hochschulid": self.student.hochschule_id,
                    "hochschulname": self.student.hochschule.name,
                    "studiengang_id": k,
                }
                self.add_studiengang_zu_hochschule(cache=neu_cache)

                self.add_studiengang_zu_student(student=self.student, cache=neu_cache)
        self.db.session.commit()
        logger.info("change_studiengang: s.id=%s to sg=%s", self.student.id, value)

    def change_zieldatum(self, value: datetime.date):
        if not self.student:
            logger.warning("Nicht eingeloggt: change_zieldatum aufgerufen.")
            raise RuntimeError("Nicht eingeloggt")
        self.student.ziel_datum = value
        self.db.session.commit()
        logger.info("change_zieldatum: s.id=%s to %s", self.student.id, value)

    def change_zielnote(self, value):
        if not self.student:
            logger.warning("Nicht eingeloggt: change_zielnote aufgerufen.")
            raise RuntimeError("Nicht eingeloggt")
        self.student.ziel_note = value
        self.db.session.commit()
        logger.info("change_zielnote: s.id=%s to %s", self.student.id, value)

    def change_exmatrikulationsdatum(self, value):
        if not self.student:
            logger.warning("Nicht eingeloggt: change_exmatrikulationsdatum aufgerufen.")
            raise RuntimeError("Nicht eingeloggt")
        self.student.exmatrikulationsdatum = value
        self.db.session.commit()
        logger.info(
            "change_exmatrikulationsdatum: s.id=%s to %s", self.student.id, value
        )

    def logout(self) -> None:
        if not self.student:
            logger.warning("Nicht eingeloggt: logout aufgerufen.")
            raise RuntimeError("Nicht eingeloggt")
        logger.info("Logout: %s - %s", self.student.id, self.student.email)
        try:
            if self.db.session.is_active:
                self.db.session.expire_all()
        except Exception:
            logger.exception("expire_all fehlgeschlagen.")
        try:
            self.db.session.close()
        except Exception:
            logger.exception("Session close fehlgeschlagen.")
        self.student = None
        try:
            self.db.recreate_session()
        except Exception:
            logger.exception("recreate_session fehlgeschlagen.")
            raise RuntimeError(
                "Es konnte keine neue Datenbank-Session eröffnet werden."
            )

    def delete_student(self):
        if not self.student:
            logger.warning("Nicht eingeloggt: delete_student aufgerufen.")
            raise RuntimeError("Nicht eingeloggt")
        logger.info("delete_student: %s - %s", self.student.id, self.student.email)
        try:
            self.db.session.delete(self.student)
            self.db.session.commit()
        except Exception:
            logger.exception("Student löschen fehlgeschlagen.")
            raise RuntimeError("Student löschen fehlgeschlagen.")
        self.logout()
