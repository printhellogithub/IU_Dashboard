import os

from database import DatabaseManager
from models_test import Status, Student, Enrollment, EnrollmentDTO

from email_validator import validate_email, EmailNotValidError
from rich.table import Table
from rich.console import Console

console = Console()


class DashboardCLI:
    def __init__(self):
        self.db = DatabaseManager()
        self.student: Student | None = None

    def run(self):
        """Programm wird gestartet"""
        self.login()
        while True:
            os.system("clear") # WINDOWS!!! -> "cls"
            self.show_enrollments()
            self.choose_action()

    def greet(self, student):
        print(f"Hallo, {student.name}.")
        
    def login(self):
        while True:
            raw_email = input("Deine Email: ")
            try:
                email = validate_email(raw_email).email
                break
            except EmailNotValidError:
                print("Ungültige Email")
        
        while True:
            password = input("Passwort: ")
            student = self.db.lade_student(email)

            if not student:
                print("Kein Account gefunden. Erstelle einen Account.")
                self.erstelle_account(email, password)
                return

            if student.verify_password(password):
                self.student = student
                self.greet(self.student)
                return
            else:
                print("Falsches Passwort.")

    def erstelle_account(self, email: str, password: str):
        name = input("Dein Name: ")
        matrikelnummer = input("Deine Matrikelnummer: ")
        self.student = self.db.erstelle_student(
            name=name,
            matrikelnummer=matrikelnummer,
            email_address=email,
            password=password
        )
        self.greet(self.student)

    def show_enrollments(self):
        enrollments = self.db.lade_enrollments_von_student(self.student.id)

        dtos = [EnrollmentDTO.make_dto(enr) for enr in enrollments]

        if dtos:
            table = Table(title="Deine Kurse")
            table.add_column("#", justify="right", style="cyan", no_wrap=True)
            table.add_column("Kurs", style="magenta")
            table.add_column("Status")

            status_farben = {
                Status.OFFEN.name: "blue",
                Status.IN_BEARBEITUNG.name: "yellow",
                Status.ABGESCHLOSSEN.name: "green",
            }

            for i, dto in enumerate(dtos, start=1):
                color = status_farben.get(dto.status, "white")
                table.add_row(str(i), dto.kurs_name, f"[{color}]{dto.status}[/{color}]")

            console.print(table)
        else:
            console.print("[bold red]Noch keine Kurse. [/bold red]")


    def choose_action(self):
        print("\n1: Kurs hinzufügen    2: Status ändern    3: Beenden\n")
        while True:
            action = input("Wähle Aktion ")
            if action == "1":
                self.add_enrollment()
                break
            elif action == "2":
                self.change_status()
                break
            elif action == "3":
                print("Programm wird beendet.")
                exit()
            else:
                pass

    def add_enrollment(self):
        kursname = input("Kursname: ")
        kursnummer = input("Kursnummer: ")
        kurs = self.db.lade_kurs(kursnummer)
        if not kurs:
            kurs = self.db.erstelle_kurs(kursname, kursnummer)
        enr = self.db.erstelle_enrollment(self.student, kurs, Status.OFFEN)
        # print(f"Eingeschrieben in {kurs.name} (Status {enr.status.name})")
        return enr

    def change_status(self):
        enrollments = self.db.lade_enrollments_von_student(self.student.id)
        if not enrollments:
            print("Keine Kurse vorhanden.")
            return
        
        while True:
            try:
                kursauswahl = int(input("Wähle Kursnummer: ")) - 1
                enrollment = enrollments[kursauswahl]
                break
            except (ValueError, IndexError):
                print("Ungültige Auswahl.")

        print("Neuer Status: 1=OFFEN, 2=IN_BEARBEITUNG, 3=ABGESCHLOSSEN\n")
        statusauswahl = input("... ")
        mapping = {"1": Status.OFFEN, "2": Status.IN_BEARBEITUNG, "3": Status.ABGESCHLOSSEN}
        neuer_status = mapping.get(statusauswahl)

        if neuer_status:
            self.db.change_enrollment_status(enrollment, neuer_status)
            print(f"Status geändert: {enrollment.kurs.kurs_name} -> {neuer_status.name}")


if __name__ == "__main__":
    app = DashboardCLI()
    app.run()

        