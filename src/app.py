# from models import *
# from database import *
# from main import *


# class DashboardCLI:
#     def __init__(self):
#         self.console = Console()
#         self.controller = Controller(DatabaseManager())

# def run(self):
#     """Programm wird gestartet"""
#     self.login_flow()
#     while True:
#         os.system("clear")  # Windows: "cls"
#         self.show_enrollments()
#         self.choose_action()


#    # --- UI: Begrüßung ---
#     def greet(self, student: Student):
#         print(f"Hallo, {student.name}.")

#     # --- UI: Login Flow ---
#     def login_flow(self):
#         while True:
#             raw_email = input("Deine Email: ")
#             try:
#                 email = validate_email(raw_email).email
#                 break
#             except EmailNotValidError:
#                 print("Ungültige Email")

#         while True:
#             password = input("Passwort: ")
#             student = self.controller.login(email, password)

#             if not student:
#                 print("Kein Account gefunden. Erstelle einen Account.")
#                 self.create_account_flow(email, password)
#                 return

#             self.greet(student)
#             return

#     def create_account_flow(self, email: str, password: str):
#         name = input("Dein Name: ")
#         matrikelnummer = input("Deine Matrikelnummer: ")
#         student = self.controller.create_account(name, matrikelnummer, email, password)
#         self.greet(student)

#     # --- UI: Enrollments anzeigen ---
#     def show_enrollments(self):
#         enrollments = self.controller.enrollments()
#         dtos = [EnrollmentDTO.make_dto(e) for e in enrollments]

#         if dtos:
#             table = Table(title="Deine Kurse")
#             table.add_column("#", justify="right", style="cyan", no_wrap=True)
#             table.add_column("Kurs", style="magenta")
#             table.add_column("Status")

#             status_farben = {
#                 Status.OFFEN.name: "blue",
#                 Status.IN_BEARBEITUNG.name: "yellow",
#                 Status.ABGESCHLOSSEN.name: "green",
#             }

#             for i, dto in enumerate(dtos, start=1):
#                 color = status_farben.get(dto.status, "white")
#                 table.add_row(str(i), dto.kurs_name, f"[{color}]{dto.status}[/{color}]")

#             self.console.print(table)
#         else:
#             self.console.print("[bold red]Noch keine Kurse. [/bold red]")

#     # --- UI: Menü ---
#     def choose_action(self):
#         print("\n1: Kurs hinzufügen    2: Status ändern    3: Beenden\n")
#         action = input("Wähle Aktion: ")

#         if action == "1":
#             self.add_enrollment_flow()
#         elif action == "2":
#             self.change_status_flow()
#         elif action == "3":
#             print("Programm wird beendet.")
#             exit()

#     # --- UI: Kurs hinzufügen ---
#     def add_enrollment_flow(self):
#         kursname = input("Kursname: ")
#         kursnummer = input("Kursnummer: ")
#         self.controller.add_enrollment(kursname, kursnummer)

#     # --- UI: Status ändern ---
#     def change_status_flow(self):
#         enrollments = self.controller.enrollments()
#         if not enrollments:
#             print("Keine Kurse vorhanden.")
#             return

#         while True:
#             try:
#                 kursauswahl = int(input("Wähle Kursnummer: ")) - 1
#                 enrollment = enrollments[kursauswahl]
#                 break
#             except (ValueError, IndexError):
#                 print("Ungültige Auswahl.")

#         print("Neuer Status: 1=OFFEN, 2=IN_BEARBEITUNG, 3=ABGESCHLOSSEN\n")
#         statusauswahl = input("... ")
#         mapping = {
#             "1": Status.OFFEN,
#             "2": Status.IN_BEARBEITUNG,
#             "3": Status.ABGESCHLOSSEN,
#         }
#         neuer_status = mapping.get(statusauswahl)

#         if neuer_status:
#             self.controller.change_enrollment_status(enrollment, neuer_status)
#             print(
#                 f"Status geändert: {enrollment.kurs.kurs_name} -> {neuer_status.name}"
#             )


# -----------------------------
# Startpunkt
# -----------------------------
# if __name__ == "__main__":
#     app = DashboardCLI()
#     # app.run()
