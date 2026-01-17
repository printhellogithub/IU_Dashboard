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
    """Kapselt die Geschäftslogik und kommuniziert zwischen Model und UI.

    Wird von der UI aufgerufen und kümmert sich um Umsetzun, Persistenz im Model und Rückgaben.

    Verantwortlichkeiten:
        - Authentifizierung bei Login.
        - Erstellen von Accounts, anderen Objekten und deren Beziehungen.
        - Läd aktuelle Daten für UI.
        -
    """

    def __init__(self, db: DatabaseManager | None = None, seed: bool = True):
        """Initialisiert den Controller mit Instanz für Datenbankzugriffe.

        Args:
            db: DatabaseManager-Instanz, default: None.
            seed (bool): default: True. Sorgt für automatische Bereitstellung aller deutschen Hochschulen, die in hs_dict vorhanden sind.

        Attribute:
            db: DatabaseManager-Instanz, für Datenbankzugriffe.
            student: Student-Instanz, User-Objekt wird bei Login oder Registrierung zugewiesen.
        """
        self.db = db or DatabaseManager()

        self.student: Student | None = None
        if seed:
            self.erstelle_hochschulen_von_hs_dict()
            logger.debug("Hochschulen aus hs_dict erstellt, falls nicht vorhanden.")
        logger.debug("Controller initialisiert")

    # --- Account & Login ---
    def login(self, email: str, password: str):
        """Authentifiziert einen Nutzer und setzt ``self.student`` bei Erfolg.

        Args:
            email (str): Email-Adresse.
            password (str): Passwort im Klartext.

        Ablauf:
            - E-Mail validieren/normalisieren.
            - Student inkl. Beziehungen aus DB laden.
            - Passwort gegen Argon2-Hash prüfen.

        Returns:
            True bei erfolgreichem Login, sonst False.
        """
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
        """Legt einen neuen Student inkl. Basis-Beziehungen und Semestern an.

        Args:
            cache (dict):
                - name, matrikelnummer, email, password
                - semesteranzahl, modulanzahl
                - startdatum, zieldatum (ISO-Strings)
                - hochschulid, studiengang_id

        Side Effects:
            - Erstellt DB-Datensätze und Beziehungen.
            - Setzt ``self.student`` auf den neu angelegten Student.
        """
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
        self.erstelle_semester_fuer_student()
        self.add_hochschule_zu_student(cache=cache)
        self.add_studiengang_zu_student(cache=cache)
        self.add_studiengang_zu_hochschule(cache=cache)

        self.db.session.commit()
        logger.info("Account mit Beziehungen erstellt: %s", self.student.email)

    # Relationships bei neuem Account
    def add_hochschule_zu_student(self, cache: dict):
        """Fügt dem Student eine Hochschule zu.

        Args:
            cache (dict): erwartet ``hochschulid`` Eintrag
        """
        if not self.student:
            logger.warning("Nicht eingeloggt: add_hochschule_zu_student aufgerufen.")
            raise RuntimeError("Nicht eingeloggt")

        hs = self.db.lade_hochschule_mit_id(int(cache["hochschulid"]))
        if hs is None:
            logger.warning("Hochschule nicht gefunden: id=%s", cache["hochschulid"])
            raise ValueError(
                f"Hochschule ({cache['hochschulid']}) wurde nicht gefunden!"
            )
        self.student.hochschule = hs
        self.db.session.commit()
        logger.info("Hochschule %s Student %s zugeordnet", hs.name, self.student.email)

    def add_studiengang_zu_student(self, cache):
        """Fügt einem Student einen Studiengang hinzu.

        Args:
            cache (dict): erwartet ``studiengang_id`` Eintrag
        """
        if not self.student:
            logger.warning("Nicht eingeloggt: add_hochschule_zu_student aufgerufen.")
            raise RuntimeError("Nicht eingeloggt")

        sg = self.db.lade_studiengang_mit_id(int(cache["studiengang_id"]))
        if sg is None:
            logger.warning("Studiengang nicht gefunden: id=%s", cache["studiengang_id"])
            raise ValueError(
                f"Studiengang ({cache['studiengang_id']}) wurde nicht gefunden!"
            )
        self.student.studiengang = sg
        self.db.session.commit()
        logger.info("Studiengang %s Student %s zugeordnet", sg.name, self.student.email)

    def add_studiengang_zu_hochschule(self, cache):
        """Fügt einer Hochschule einen Studiengang hinzu.

        Args:
            cache (dict): erwartet ``hochschulid`` und ``studiengang_id`` Eintrag.
        """
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
        """Gibt ein Dictionary mit allen benötigten Daten für die UI zurück.

        Returns:
            dict: Daten für das Dashboard (GUI).
        """
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
        """Gibt den zeitlichen Fortschritt des Studiums zwischen Beginn und Wunschdatum als float zurück.

        Falls ein Exmatrikulationsdatum vorhanden ist, wird dieses Datum,
        andernfalls das heutige Datum für die Berechnung verwendet.
        Ist das Wunschdatum des Studienendes schon überschritten wird 1 zurückgegeben.

        Returns:
            progress: Float zwischen 0 und 1, gerundet auf 3 Nachkommastellen.
        """
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
        """Gibt das Verhältnis der Dauer aller Semester zu der gewünschten Studiendauer zurück.

        Dieser Wert wird für die akurate Skallierung der grafischen Semesteranzeige in der GUI verwendet.
        Liegt der Wunschabschluss vor dem Ende des letzten Semesters ist der Wert kleiner 1, ansonsten größer.
        Stimmen die Daten überein, ist er genau 1.

        Returns:
            amount: Float, größer 0.
        """
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
        """Gibt die Anzahl der eingeschriebenen Module mit bestimmten Status zurück.

        Args:
            status (EnrollmentStatus): Möglichkeiten: IN_BEARBEITUNG, ABGESCHLOSSEN, NICHT_BESTANDEN

        Returns:
            int: Anzahl der entsprechenden Einschreibungen.
        """
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
        """Gibt die Anzahl der nicht eingeschriebenen Module zurück.

        Returns:
            int: Anzahl der ausstehenden Einschreibungen.
        """
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
        """Gibt die bisher vom Studenten erarbeiteten ECTS-Punkte als int zurück."""

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
        """Errechnet den Notendurchschnitt aller abgeschlossenen Module.

        Returns:
            float: Durchschnitt, falls Module abgeschlossen wurden.
            str: "--", falls kein Modul abgeschlossen wurde.
        """
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
        """Stellt alle Semester eines Studenten als dict dar und gibt eine Liste dieser Semester-Dictionaries zurück.

        Returns:
            list: Liste, mit Semester-Darstellungen in dict-Form.
        """
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
        """Gibt eine Liste mit allen Enrollments (als dict) eines Studenten zurück.

        Returns:
            list: Liste mit Enrollments in dict-Form.
        """
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
        """Stellt alle Kurse eines Moduls als dict dar und gibt eine Liste dieser Kurs-Dictionaries zurück.

        Args:
            modul (Modul): Modul-Objekt, welchem ein oder mehrere Kurse zugeordnet sind.

        Returns:
            list: Liste, mit Kurs-Darstellungen in dict-Form.
        """
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
        """Gibt eine Liste mit allen Prüfungsleistungen (als dict) eines Enrollments zurück.

        Args:
            enrollment (Enrollment): Enrollment-Objekt, welchem Prüfungsleistungen zugeordnet sind.

        Returns:
            list: Liste mit Prüfungsleistungen in dict-Form.
        """
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
        """Stellt eine Prüfungsleistung als dict dar und gibt dieses zurück.

        Args:
            pl (Prüfungsleistung): Prüfungsleistung, die als dict dargestellt werden soll.

        Returns:
            dict: dict, welches die Prüfungsleistung darstellt.
        """
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

    def get_pl_with_id(self, enrollment_id: int, pl_id: int) -> dict:
        """Gibt eine Prüfungsleistung als dict zurück, falls diese per Enrollment-ID und Prüfungsleistungs-ID gefunden wird.

        Args:
            enrollment_id (int): ID des Enrollments.
            pl_id (int): ID der Prüfungsleistung.

        Returns:
            dict: Rückgabe von ``self.get_pl_dict()``, wenn Prüfungsleistung gefunden wurde, sonst ``{}``.
        """
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

    def get_enrollment_data(self, enrollment_id: int) -> dict:
        """Gibt ein Enrollment in dict-Darstellung zurück, falls dieses per ID gefunden wurde.

        Args:
            enrollment_id (int): ID des Enrollments, welches als dict repräsentiert werden soll.

        Returns:
            dict: Darstellung eines Enrollments, falls dieses gefunden wurde, sonst ``{}``.
        """
        if not self.student:
            logger.warning("Nicht eingeloggt: get_enrollment_data aufgerufen.")
            raise RuntimeError("Nicht eingeloggt")
        for enrollment in self.student.enrollments:
            if enrollment.id == enrollment_id:
                enrollment.aktualisiere_status()
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
        """Erstellt Hochschulen, die in hs_dict (siehe import) gelistet sind."""
        hochschul_namen = {h.name for h in self.db.lade_alle_hochschulen()}
        for name in hs_dict.values():
            if not name:
                continue
            if name not in hochschul_namen:
                self.erstelle_hochschule(hochschul_name=name)

    def get_hs_kurzname_if_notwendig(self, name: str) -> str:
        """Gibt den Kurznamen einer Hochschule zurück, falls ihr Name zu lang ist.

        Falls der Name einer Hochschule länger ist als ``max_length``,
        wird die Kurzform aus hs_dict_kurz (siehe import) zurückgegeben.
        Falls die Hochschule nicht in ``hs_dict_kurz`` vorhanden ist oder
        kürzer ist als ``max_length``, wird der bisherige Name zurückgegeben.

        Args:
            name (str): Name der Hochschule.

        Returns:
            str: Name der Hochschule; Kurzname, wenn in ``hs_dict_kurz``.
        """
        max_length = 50
        if len(name) > max_length:
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
        """Gibt ein Dictionary mit allen Hochschulen in der Datenbank zurück.

        Der Schlüssel ist die jeweilige Datenbank-ID der Hochschule,
        der Name der Hochschule der zugehörige Wert.

        Returns:
            dict[int, str]: [Hochschul-ID, Hochschul-Name]
        """
        hochschulen = self.db.lade_alle_hochschulen()
        hochschulen_dict: dict[int, str] = {}
        hs_namen_set = set(hs_dict.values())
        for hochschule in hochschulen:
            if hochschule.name in hs_namen_set:
                hochschulen_dict[hochschule.id] = hochschule.name
        logger.debug("get_hochschulen_dict ausgeführt")
        return hochschulen_dict

    def get_studiengaenge_von_hs_dict(self, hochschule_id: int) -> dict[int, str]:
        """Gibt ein Dictionary mit allen Studiengängen einer Hochschule in der Datenbank zurück.

        Der Schlüssel ist die jeweilige Datenbank-ID des Studiengangs,
        der Name des Studiengangs der zugehörige Wert.
        Falls die Hochschule nicht gefunden wird, wird ``{0: ""}`` zurückgegeben.
        Falls keine Studiengänge angelegt sind, wird ``{}`` zurückgegeben

        Args:
            hochschule_id (int): ID der Hochschule.

        Returns:
            dict[int, str]: [Studiengang-ID, Studiengang-Name], falls Hochschule und Studiengänge gefunden wurden.
        """
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

    def get_studiengang_id(
        self, studiengang_name: str, hochschule_id: int
    ) -> dict[int, str]:
        """Gibt ein Dictionary mit der ID eines Studiengangs als Schlüssel und dem Namen als Wert zurück.

        Args:
            studiengang_name (str): Name des Studiengangs.
            hochschule_id (int): ID der Hochschule.

        Returns:
            dict[int, str]: [Studiengang-ID, Studiengang-Name], falls Hochschule und Studiengang gefunden wurde,
                            sonst ``{0: ""}``.
        """
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

    def erstelle_hochschule(self, hochschul_name: str) -> dict[int, str]:
        """Legt eine Hochschule in der Datenbank an und gibt ein Dictionary mit ID (Schlüssel) und Name (Wert) zurück.

        Args:
            hochschul_name (str): Name der Hochschule.

        Returns:
            dict[int, str]: [Hochschul-ID, Hochschul-Name]
        """
        hochschule = self.db.add_hochschule(hochschul_name)
        self.db.session.commit()
        logger.info("Hochschule erstellt: %s", hochschule.id)
        return {hochschule.id: hochschule.name}

    def erstelle_studiengang(
        self, studiengang_name: str, gesamt_ects_punkte: int
    ) -> dict[int, str]:
        """Legt einen Studiengang in der Datenbank an und gibt ein Dictionary mit ID (Schlüssel) und Name (Wert) zurück.

        Args:
            studiengang_name (str): Name des Studiengangs.
            gesamt_ects_punkte (int): Gesamtanzahl der ECTS-Punkte des Studiengangs.

        Returns:
            dict[int, str]: [Studiengang-ID, Studiengang-Name]
        """
        studiengang = self.db.add_studiengang(studiengang_name, gesamt_ects_punkte)
        self.db.session.commit()
        logger.info("Studiengang erstellt: %s", studiengang.id)
        return {studiengang.id: studiengang.name}

    def erstelle_semester_fuer_student(self) -> None:
        """Erstellt aus Startdatum und Semesteranzahl einzelne Semesterobjekte, zu je 6 Monaten,
        und legt sie in der Datenbank an.

        Das Enddatum berechnet sich: Enddatum = Beginn + 6 Monate - 1 Tag.
        """
        if not self.student:
            logger.warning("Nicht eingeloggt: add_hochschule_zu_student aufgerufen.")
            raise RuntimeError("Nicht eingeloggt")

        assert isinstance(self.student.start_datum, datetime.date)
        assert isinstance(self.student.ziel_datum, datetime.date)
        assert (
            isinstance(self.student.semester_anzahl, int)
            and self.student.semester_anzahl > 0
        )

        for i in range(self.student.semester_anzahl):
            beginn = self.student.start_datum + relativedelta(months=6 * i)
            ende = (beginn + relativedelta(months=6)) - relativedelta(days=1)
            nummer = i + 1
            self.db.add_semester(
                student=self.student, nummer=nummer, ende=ende, beginn=beginn
            )
        self.db.session.commit()
        logger.info("Semester wurden erstellt: %s", self.student.email)

    def validate_email_for_new_account(self, value: str) -> str | EmailNotValidError:
        """Validiert eine Email-Adresse bei Account-Registrierung.

        ``check_deliverability=True`` prüft per DNS-Abfrage,
        ob die Domain der Email-Adresse Emails empfangen kann.

        Args:
            value (str): Eingegebene Email-Adresse.

        Returns:
            str: Normalisierte Email-Adresse bei erfolgreicher Prüfung.
            EmailNotValidError: Infotext, weshalb die Prüfung fehlgeschlagen ist.
        """
        try:
            emailinfo = validate_email(value, check_deliverability=True)
            email = emailinfo.normalized
            return email
        except EmailNotValidError as e:
            return e

    def validate_email_for_login(self, value: str) -> str | EmailNotValidError:
        """Validiert eine Email-Adresse beim Login.

        Args:
            value (str): Eingegebene Email-Adresse.

        Returns:
            str: Normalisierte Email-Adresse bei erfolgreicher Prüfung.
            EmailNotValidError: Infotext, weshalb die Prüfung fehlgeschlagen ist.
        """
        try:
            emailinfo = validate_email(value, check_deliverability=False)
            email = emailinfo.normalized
            return email
        except EmailNotValidError as e:
            return e

    def check_if_email_exists(self, email: str) -> bool:
        """Prüft, ob die Email-Adresse in der Datenbank existiert.

        Args:
            email (str): Eingegebene Email-Adresse.

        Returns:
            bool: True, wenn Email-Adresse in Datenbank vorhanden ist, sonst False.
        """
        if self.db.lade_student(email=email):
            return True
        else:
            return False

    def check_if_already_enrolled(self, enrollment_cache: dict) -> bool:
        """Prüft, ob der Student schon in ein Modul eingeschrieben ist.

        Geprüft wird eine Übereinstimmung des Modulcodes.

        Args:
            enrollment_cache (dict): Erwartet ``["modul_code"]``.

        Returns:
            bool: True, wenn der Student schon in ein Modul mit
            gleichem Modulcode eingeschrieben ist, sonst False.
        """
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

    def get_startdatum(self) -> datetime.date:
        """Gibt das Studien-Startdatum des Studenten zurück.

        Returns:
            datetime.date: Studien-Startdatum des Studenten.
        """
        if not self.student:
            logger.warning("Nicht eingeloggt: get_startdatum aufgerufen.")
            raise RuntimeError("Nicht eingeloggt")
        return self.student.start_datum

    def erstelle_enrollment(self, enrollment_cache: dict) -> dict:
        """Legt ein Enrollment inklusive Modul, Kurse und Prüfungsleistungen in
        der Datenbank an und gibt die Daten als Dictionary für die GUI zurück.

        Ablauf:
            - Einschreibedatum parsen
            - Modul erstellen oder laden
            - Kurse erstellen oder laden
            - Enrollment erstellen
            - Prüfungsleistungen (Versuche 1-3) erstellen
            - Datenbank-Flush, damit IDs generiert werden
            - Rückgabe-Dictionary zusammenstellen
            - Datenbank-Commit
            - Rückgabe des Dictionary

        Args:
            enrollment_cache (dict): Liefert Eingabedaten des Users.

        Returns:
            dict: Gibt die Enrollment-Daten für die GUI zurück.
        """
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

    def change_pl(self, enrollment_id: int, pl_dict: dict) -> None:
        """Ergänzt bei einer Prüfungsleistung Daten für Note und Datum.

        Args:
            enrollment_id (int): ID des Enrollments.
            pl_dict (dict): Dictionary mit Eingabedaten (Note, Datum) und ID zur Prüfungsleistung.
        """
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
                        enrollment.aktualisiere_status()

    def change_email(self, value: str) -> None:
        """Weist dem Student eine neue Email-Adresse zu.

        Args:
            value (str): Neue Email-Adresse.
        """
        if not self.student:
            logger.warning("Nicht eingeloggt: change_email aufgerufen.")
            raise RuntimeError("Nicht eingeloggt")
        self.student.email = value
        self.db.session.commit()
        logger.info("change_email: s.id=%s, email=%s", self.student.id, value)

    def change_password(self, value: str) -> None:
        """Weist dem Student ein neues Passwort zu.

        Args:
            value (str): Neues Passwort.
        """
        if not self.student:
            logger.warning("Nicht eingeloggt: change_password aufgerufen.")
            raise RuntimeError("Nicht eingeloggt")
        self.student.password = value
        self.db.session.commit()
        logger.info("change_password: s.id=%s", self.student.id)

    def change_name(self, value: str) -> None:
        """Weist dem Student einen neuen Namen zu.

        Args:
            value (str): Neuer Name.
        """
        if not self.student:
            logger.warning("Nicht eingeloggt: change_name aufgerufen.")
            raise RuntimeError("Nicht eingeloggt")
        self.student.name = value
        self.db.session.commit()
        logger.info("change_name: s.id=%s, name=%s", self.student.id, value)

    def change_matrikelnummer(self, value: str) -> None:
        """Weist dem Student eine neue Matrikelnummer zu.

        Args:
            value (str): Neue Matrikelnummer.
        """
        if not self.student:
            logger.warning("Nicht eingeloggt: change_matrikelnummer aufgerufen.")
            raise RuntimeError("Nicht eingeloggt")
        self.student.matrikelnummer = value
        self.db.session.commit()
        logger.info("changed_matrikelnummer: s.id=%s, m.nr=%s", self.student.id, value)

    def change_semester_anzahl(self, value: int) -> None:
        """Weist dem Student eine neue Semesteranzahl zu, löscht alte und erzeugt neue Semester.

        Args:
            value (int): Neue Semesteranzahl.
        """
        if not self.student:
            logger.warning("Nicht eingeloggt: change_semester_anzahl aufgerufen.")
            raise RuntimeError("Nicht eingeloggt")
        self.student.semester_anzahl = value
        self.student.semester.clear()
        self.erstelle_semester_fuer_student()
        self.db.session.commit()
        logger.info(
            "change_semester_anzahl: s.id=%s to %s semester", self.student.id, value
        )

    def change_startdatum(self, value: datetime.date) -> None:
        """Weist dem Student ein neues Studienstartdatum zu, löscht alte und erzeugt neue Semester.

        Args:
            value (datetime.date): Neues Studienstartdatum.
        """
        if not self.student:
            logger.warning("Nicht eingeloggt: change_startdatum aufgerufen.")
            raise RuntimeError("Nicht eingeloggt")
        self.student.start_datum = value
        self.student.semester.clear()
        self.erstelle_semester_fuer_student()
        self.db.session.commit()
        logger.info("change_startdatum: s.id=%s to %s", self.student.id, value)

    def change_gesamt_ects(self, value: int) -> None:
        """Weist dem Studiengang des Studenten eine neue Gesamtanzahl an ECTS Punkten zu.

        Args:
            value (int): Neue Gesamtanzahl an ECTS Punkten des Studiengangs.
        """
        if not self.student:
            logger.warning("Nicht eingeloggt: change_gesamt_ects aufgerufen.")
            raise RuntimeError("Nicht eingeloggt")
        self.student.studiengang.gesamt_ects_punkte = value
        self.db.session.commit()
        logger.info("change_gesamt_ects: s.id=%s to %s", self.student.id, value)

    def change_modul_anzahl(self, value: int) -> None:
        """Weist dem Student eine neue Anzahl an Modulen zu.

        Args:
            value (int): Neue Anzahl an Modulen.
        """
        if not self.student:
            logger.warning("Nicht eingeloggt: change_modul_anzahl aufgerufen.")
            raise RuntimeError("Nicht eingeloggt")
        self.student.modul_anzahl = value
        self.db.session.commit()
        logger.info("change_modul_anzahl: s.id=%s to %s", self.student.id, value)

    def change_hochschule(self, hochschul_id: int, hochschul_name: str) -> None:
        """Weist dem Student eine neue Hochschule zu.

        Studiengangsänderungen werden über ``change_studiengang`` abgewickelt.

        Args:
            hochschul_id (int): ID der neuen Hochschule.
            hochschul_name (str): Name der neuen Hochschule.
        """
        if not self.student:
            logger.warning("Nicht eingeloggt: change_hochschule aufgerufen.")
            raise RuntimeError("Nicht eingeloggt")
        cache = {
            "hochschulid": hochschul_id,
            "hochschulname": hochschul_name,
            "studiengang_id": self.student.studiengang_id,
        }
        self.add_hochschule_zu_student(cache=cache)
        self.change_studiengang(value=self.student.studiengang.name)
        self.db.session.commit()
        logger.info("change_hochschule: s.id=%s to hs.id=%s", self.student.id, id)

    def change_studiengang(self, value: str) -> None:
        """Weist dem Student einen neuen Studiengang zu.

        Die Enrollments des Studenten werden gelöscht, da ein neuer Studiengang andere Module hat.
        Wird der neue Studiengang an der Hochschule des Studenten gefunden, wird er ihm zugewiesen.
        Sollte der neue Studiengang nicht in der Datenbank vorhanden sein, wird dieser erstellt und
        der Hochschule des Studenten hinzugefügt und dem Student zugewiesen.

        Args:
            value (str): Name des neuen Studiengangs.
        """
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

                self.add_studiengang_zu_student(cache=neu_cache)
        self.db.session.commit()
        logger.info("change_studiengang: s.id=%s to sg=%s", self.student.id, value)

    def change_zieldatum(self, value: datetime.date) -> None:
        """Weist dem Student ein neues Studienzieldatum zu.

        Args:
            value (datetime.date): Neues Studienzieldatum.
        """
        if not self.student:
            logger.warning("Nicht eingeloggt: change_zieldatum aufgerufen.")
            raise RuntimeError("Nicht eingeloggt")
        self.student.ziel_datum = value
        self.db.session.commit()
        logger.info("change_zieldatum: s.id=%s to %s", self.student.id, value)

    def change_zielnote(self, value: float) -> None:
        """Weist dem Student eine neue Studienzielnote zu.

        Args:
            value (float): Neue Studienzielnote.
        """
        if not self.student:
            logger.warning("Nicht eingeloggt: change_zielnote aufgerufen.")
            raise RuntimeError("Nicht eingeloggt")
        self.student.ziel_note = value
        self.db.session.commit()
        logger.info("change_zielnote: s.id=%s to %s", self.student.id, value)

    def change_exmatrikulationsdatum(self, value: datetime.date | None) -> None:
        """Weist dem Student ein (neues) Exmatrikulationsdatum zu oder setzt es auf ``None``.

        Args:
            value (datetime.date | None): (Neues) Exmatrikulationsdatum oder Überschreiben mit ``None``.
        """
        if not self.student:
            logger.warning("Nicht eingeloggt: change_exmatrikulationsdatum aufgerufen.")
            raise RuntimeError("Nicht eingeloggt")
        self.student.exmatrikulationsdatum = value
        self.db.session.commit()
        logger.info(
            "change_exmatrikulationsdatum: s.id=%s to %s", self.student.id, value
        )

    def logout(self) -> None:
        """Loggt den aktuellen Student aus und setzt die Datenbank-Session zurück.

        Raises:
            RuntimeError: Wenn keine neue Session erstellt werden kann oder der Student nicht eingeloggt ist.
        """
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

    def delete_student(self) -> None:
        """Löscht den Account des Studenten. Ruft Logout auf."""
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
