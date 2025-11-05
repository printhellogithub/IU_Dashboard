from __future__ import annotations
import customtkinter as ctk
import datetime
import tkinter as tk
from tkcalendar import Calendar
from email_validator import EmailNotValidError

from main import Controller


# EXTRA-Klasse: Searchable Combobox
class SearchableComboBox(ctk.CTkComboBox):
    """Erbt von ComboBox: nimmt statt values, options als inputparameter.
    Options muss type(dict) sein.
    mit jedem Keystroke wird die Auswahl des dicts gefiltert.
    Falls eine der Options ausgewählt wird, kann die id mit .get_id() abgerufen werden.
    Den Wert erhält man mit .get_value()
    """

    def __init__(self, master, options: dict[int, str], **kwargs):
        # dict speichern
        self._options_dict = options
        self._all_values = list(options.values())

        super().__init__(master, values=self._all_values, **kwargs)

        # Auf Änderungen im Entry reagieren
        self.bind("<KeyRelease>", self._on_key_release)

    def _on_key_release(self, event):
        text = self.get()
        if not text:
            # nichts eingegeben -> alles anzeigen
            self.configure(values=self._all_values)
            return
        # filtern (case-insensitive)
        filtered = [
            value for value in self._all_values if text.lower() in value.lower()
        ]
        # Liste im Dropdown aktualisieren
        # (wenn leer, trotzdem mindestens den aktuellen Text drin lassen)
        self.configure(values=filtered or [text])

    def get_value(self) -> str:
        # gibt sichtbaren text zurück
        return self.get()

    def get_id(self) -> int | None:
        # gibt id zurück, falls Value bekannt, sonst None
        value = self.get()
        for k, v in self._options_dict.items():
            if v == value:
                return k
        return None


# EXTRA-Klasse: EnrollmentIcon
class EnrollmentIcon(ctk.CTkButton):
    pass


# EXTRA-Klasse: SemesterIcon
class SemesterIcon(ctk.CTkButton):
    pass


class LoginFrame(ctk.CTkFrame):
    def __init__(self, master, controller: Controller, go_to_dashboard, go_to_new_user):
        super().__init__(master)

        self.controller = controller
        self.go_to_dashboard = go_to_dashboard
        self.go_to_new_user = go_to_new_user

        ctk.CTkLabel(self, text="Login", font=ctk.CTkFont(size=18, weight="bold")).pack(
            pady=20
        )

        self.entry_email = ctk.CTkEntry(self, placeholder_text="Email-Adresse")
        self.entry_email.focus()
        self.entry_email.pack(pady=5)

        self.entry_pw = ctk.CTkEntry(self, placeholder_text="Passwort", show="●")
        self.entry_pw.pack(pady=5)

        self.label_info = ctk.CTkLabel(self, text="", text_color="red")
        self.label_info.pack(pady=5)

        ctk.CTkButton(self, text="Login", command=self.check_login).pack(pady=10)

        self.button_to_new_user = ctk.CTkButton(
            self, text="Neuen Account anlegen", command=self.go_to_new_user
        )
        self.button_to_new_user.pack(pady=20)

    def check_login(self):
        email = self.entry_email.get()
        password = self.entry_pw.get()
        if self.controller.login(email, password):
            self.go_to_dashboard(self.controller)
        else:
            self.label_info.configure(text="Login fehlgeschlagen")


class NewUserFrame(ctk.CTkScrollableFrame):
    def __init__(
        self, master, controller: Controller, go_to_login, go_to_StudiengangAuswahl
    ):
        super().__init__(master)

        self.controller = controller
        self.go_to_login = go_to_login
        self.go_to_StudiengangAuswahl = go_to_StudiengangAuswahl

        ctk.CTkLabel(
            self,
            text="Deinen Account anlegen",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).pack(pady=20)

        # Name
        self.entry_name = ctk.CTkEntry(self, placeholder_text="Dein Name")
        self.entry_name.pack(pady=5)

        # Matrikelnummer
        self.entry_matrikelnummer = ctk.CTkEntry(
            self, placeholder_text="Deine Matrikelnummer"
        )
        self.entry_matrikelnummer.pack(pady=5)

        # Semesteranzahl
        self.label_semesteranzahl = ctk.CTkLabel(
            self, text="Wie viele Semester hat Dein Studiengang?"
        )
        self.label_semesteranzahl.pack(pady=5)
        self.entry_semesteranzahl = ctk.CTkOptionMenu(
            self,
            values=["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"],
        )
        self.entry_semesteranzahl.pack(pady=5)

        # Start-Datum
        self.selected_startdatum = tk.StringVar(value="Noch kein Datum ausgewählt")

        self.label_startdatum = ctk.CTkLabel(self, text="Wann war Dein Studienstart?")
        self.label_startdatum.pack(pady=5)

        self.label_startdatum_variable = ctk.CTkLabel(
            self, textvariable=self.selected_startdatum
        )
        self.label_startdatum_variable.pack(pady=10)

        self.button_startdatum = ctk.CTkButton(
            self, text="Startdatum auswählen", command=self.start_datum_calendar
        )
        self.button_startdatum.pack(pady=10)

        # Ziel-Datum
        self.selected_zieldatum = tk.StringVar(value="Noch kein Datum ausgewählt")

        self.label_zieldatum = ctk.CTkLabel(
            self, text="Bis wann möchtest Du Dein Studium beenden?"
        )
        self.label_zieldatum.pack(pady=5)

        self.label_zieldatum_variable = ctk.CTkLabel(
            self, textvariable=self.selected_zieldatum
        )
        self.label_zieldatum_variable.pack(pady=10)

        self.button_zieldatum = ctk.CTkButton(
            self, text="Zieldatum auswählen", command=self.ziel_datum_calendar
        )
        self.button_zieldatum.pack(pady=5)

        # Ziel-Note
        self.entry_zielnote: float = 0.0
        self.slider_zielnote = ctk.CTkSlider(
            self, from_=1, to=4, number_of_steps=30, command=self.slider_zielnote_event
        )
        self.slider_zielnote.pack(pady=5)
        self.label_zielnote = ctk.CTkLabel(
            self,
            text=f"Deine Wunsch-Abschlussnote: {round(self.slider_zielnote.get(), 1)}",
        )
        self.label_zielnote.pack(pady=5)

        # Hochschule
        self.hochschulen_dict = self.controller.get_hochschulen_dict()
        self.label_hochschule = ctk.CTkLabel(self, text="Wie heißt deine Hochschule?")
        self.label_hochschule.pack(pady=10)
        self.search_combo = SearchableComboBox(self, options=self.hochschulen_dict)
        self.search_combo.pack(pady=20)

        # User-Email
        self.entry_email = ctk.CTkEntry(self, placeholder_text="Email-Adresse")
        self.entry_email.pack(pady=5)
        self.label_email_not_valid = ctk.CTkLabel(self, text="", text_color="red")
        self.label_email_not_valid.pack(pady=5)

        # PW
        self.entry_pw = ctk.CTkEntry(self, placeholder_text="Passwort", show="●")
        self.entry_pw.pack(pady=5)

        # Submit-Button
        self.button_submit = ctk.CTkButton(self, text="Weiter", command=self.on_submit)
        self.button_submit.pack(pady=20)
        self.label_leere_felder = ctk.CTkLabel(self, text="", text_color="red")
        self.label_leere_felder.pack(pady=5)

    def on_submit(self):
        # validiere Email
        valid = self.controller.validate_email_for_new_account(
            str(self.entry_email.get())
        )
        if isinstance(valid, EmailNotValidError):
            error = str(valid)
            self.label_email_not_valid.configure(text=error)
            return
        else:
            self.selected_email = valid

        # validiere user-input
        self.list_for_validation = [
            self.entry_pw.get(),
            self.entry_name.get(),
            self.entry_matrikelnummer.get(),
            self.entry_semesteranzahl.get(),
            self.search_combo.get_value(),
        ]

        if not self.validate_entries(liste=self.list_for_validation):
            return
        # user-input validiert, speicher eingaben
        self.selected_password = self.entry_pw.get()
        self.selected_name = self.entry_name.get()
        self.selected_matrikelnummer = self.entry_matrikelnummer.get()
        self.selected_semesteranzahl = self.entry_semesteranzahl.get()
        self.selected_zielnote = self.entry_zielnote
        self.selected_hochschule_name = self.search_combo.get_value()
        self.selected_hochschule_id = self.search_combo.get_id()

        # Lege hochschule an, falls noch nicht in db
        if self.selected_hochschule_id is None:
            hochschule = self.controller.erstelle_hochschule(
                self.selected_hochschule_name
            )
            for k, v in hochschule.items():
                if v == self.selected_hochschule_name:
                    self.selected_hochschule_id = k
                else:
                    raise ValueError(
                        "Datenbankrückgabe entspricht nicht Eingabewert: Hochschule"
                    )

        # lege cache an, um über Daten in anderem Frame zu verfügen
        cache = {
            "email": self.selected_email,
            "password": self.selected_password,
            "name": self.selected_name,
            "matrikelnummer": self.selected_matrikelnummer,
            "semesteranzahl": self.selected_semesteranzahl,
            "startdatum": self.selected_startdatum,
            "zieldatum": self.selected_zieldatum,
            "zielnote": self.selected_zielnote,
            "hochschulname": self.selected_hochschule_name,
            "hochschulid": self.selected_hochschule_id,
        }
        # Zur Studiengangauswahl
        self.go_to_StudiengangAuswahl(cache=cache)

    def start_datum_calendar(self):
        top = ctk.CTkToplevel(self)
        mindate_start = datetime.date(year=2010, month=1, day=1)
        maxdate_start = datetime.date.today()

        cal_start = Calendar(
            top,
            font="Arial 14",
            selectmode="day",
            locale="de_DE",
            date_patern="dd.mm.y",
            mindate=mindate_start,
            maxdate=maxdate_start,
            # disabledforeground="red",
            showweeknumbers=False,
        )

        cal_start.pack(fill="both", expand=True)

        def save():
            self.selected_startdatum.set(cal_start.get_date())
            top.destroy()

        self.save_button_start = ctk.CTkButton(top, text="ok", command=save)
        self.save_button_start.pack(pady=10)

    def ziel_datum_calendar(self):
        top = ctk.CTkToplevel(self)
        mindate_ziel = datetime.date.today()
        maxdate_ziel = datetime.date(year=2200, month=12, day=31)

        cal_ziel = Calendar(
            top,
            font="Arial 14",
            selectmode="day",
            locale="de_DE",
            date_patern="dd.mm.y",
            mindate=mindate_ziel,
            maxdate=maxdate_ziel,
            # disabledforeground="red",
            showweeknumbers=False,
        )

        cal_ziel.pack(fill="both", expand=True)

        def save():
            self.selected_zieldatum.set(cal_ziel.get_date())
            top.destroy()

        self.save_button_ziel = ctk.CTkButton(top, text="ok", command=save)
        self.save_button_ziel.pack(pady=10)

    def slider_zielnote_event(self, value: float):
        self.entry_zielnote = round(float(value), 1)
        self.label_zielnote.configure(text=f"Deine Zielnote: {round(float(value), 1)}")

    # checken ob alle Felder ausgefüllt sind!!!
    def validate_entries(self, liste):
        for value in liste:
            if str(value).strip() == "":
                self.label_leere_felder.configure(text="Etwas ist nicht ausgefüllt.")
                return False
            else:
                pass
        return True


class StudiengangAuswahlFrame(ctk.CTkFrame):
    def __init__(
        self,
        master,
        controller: Controller,
        cache,
        go_to_dashboard,
        go_to_login,
        go_to_new_user,
    ):
        super().__init__(master)

        self.controller = controller
        self.cache = cache
        self.go_to_dashboard = go_to_dashboard
        self.go_to_login = go_to_login
        self.go_to_new_user = go_to_new_user

        ctk.CTkLabel(
            self,
            text="Deinen Account anlegen",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).pack(pady=20)

        # Studiengang
        self.label_studiengang = ctk.CTkLabel(self, text="Wie heißt Dein Studiengang?")
        self.label_studiengang.pack(pady=5)

        self.studiengaenge_dict = self.controller.get_studiengaenge_von_hs_dict(
            self.cache["hochschulid"]
        )
        self.search_combo_studiengang = SearchableComboBox(
            self, options=self.studiengaenge_dict
        )
        self.search_combo_studiengang.pack(pady=20)

        # Gesamt-ECTS-Punkte
        self.entry_ects = ctk.CTkEntry(
            self, placeholder_text="Gesamt ECTS-Punkte Deines Studiums"
        )
        self.entry_ects.pack(pady=10)
        self.label_no_int = ctk.CTkLabel(self, text="", text_color="red")
        self.label_no_int.pack(pady=5)

        # Submit-Button
        self.button_submit = ctk.CTkButton(self, text="Weiter", command=self.on_submit)
        self.button_submit.pack(pady=20)
        self.label_leere_felder = ctk.CTkLabel(self, text="", text_color="red")
        self.label_leere_felder.pack(pady=5)

    def validate_ects(self, ects):
        try:
            number = int(ects)
        except ValueError:
            self.label_no_int.configure(text="Muss eine (Ganz-) Zahl sein")
            return False

        if number:
            if number > 0 and number <= 500:
                return True
        else:
            self.label_no_int.configure(text="Zahl muss zwischen 1 und 500 liegen")
            return False

    def on_submit(self):
        # validiere ECTS-Feld
        if self.validate_ects(self.entry_ects.get().strip()):
            self.selected_ects = int(self.entry_ects.get().strip())
        else:
            return

        # bekomme values von searchableCombobox
        self.selected_studiengang_name = self.search_combo_studiengang.get_value()
        self.selected_studiengang_id = self.search_combo_studiengang.get_id()

        # checke ob Feld leer oder fange ab,
        # falls keine id aus searchableComboBox
        if self.selected_studiengang_name.strip() == "":
            self.label_leere_felder.configure(text="Etwas ist nicht ausgefüllt.")
            return

        if self.selected_studiengang_id is None:
            studiengang = self.controller.erstelle_studiengang(
                studiengang_name=self.selected_studiengang_name,
                gesamt_ects_punkte=self.selected_ects,
            )
            for k, v in studiengang.items():
                if v == self.selected_studiengang_name:
                    self.selected_studiengang_id = k
                else:
                    raise ValueError(
                        "Datenbankrückgabe entspricht nicht Eingabewert: Hochschule"
                    )

        # Fuege values zum Cache hinzu
        self.cache["studiengang_ects"] = self.selected_ects
        self.cache["studiengang_name"] = self.selected_studiengang_name
        self.cache["studiengang_id"] = self.selected_studiengang_id

        # erstelle Account
        self.controller.erstelle_account(self.cache)
        # wechsle Fenster
        self.go_to_dashboard(self.controller)

        # TODO
        # ändere new_user_frame zu Grid!

        # SearchableComboBox funktioniert nicht, checke ob es an dict liegt?!
        # außerdem zeigt default CTKComboBox an, checke ob hochschulen in sql vorliegen
        # bzw. ob csv-reader funktioniert.


class DashboardFrame(ctk.CTkFrame):
    def __init__(
        self,
        master,
        controller: Controller,
        go_to_login,
        go_to_enrollement,
        go_to_settings,
    ):
        super().__init__(master)
        # TODO
        self.controller = controller
        self.go_to_login = go_to_login
        self.go_to_enrollment = go_to_enrollement
        self.go_to_settings = go_to_settings

        # Grid / Place ausprobieren
        # Enrollment-Test hinzuziehen.


class EnrollmentFrame(ctk.CTkFrame):
    def __init__(self, master, controller: Controller, go_to_dashboard):
        super().__init__(master)
        # TODO


class SettingsFrame(ctk.CTkFrame):
    def __init__(self, master, controller: Controller, go_to_dashboard):
        super().__init__(master)
        # TODO


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.controller = Controller()
        self.title("Dashboard")
        self.geometry("960x540")
        self.current_frame = None
        self.show_login()

    def show_login(self):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = LoginFrame(
            self,
            controller=self.controller,
            go_to_dashboard=self.show_dashboard,
            go_to_new_user=self.show_new_user,
        )
        self.current_frame.pack(fill="both", expand=True)

    def show_new_user(self):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = NewUserFrame(
            self,
            controller=self.controller,
            go_to_login=self.show_login,
            go_to_StudiengangAuswahl=self.show_studiengang_auswahl,
        )
        self.current_frame.pack(fill="both", expand=True)

    def show_studiengang_auswahl(self, hochschule_id, cache):
        self.cache = cache
        self.hochschule_id = hochschule_id
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = StudiengangAuswahlFrame(
            self,
            controller=self.controller,
            cache=self.cache,
            go_to_dashboard=self.show_dashboard,
            go_to_login=self.show_login,
            go_to_new_user=self.show_new_user,
        )
        self.current_frame.pack(fill="both", expand=True)

    def show_dashboard(self, user):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = DashboardFrame(
            self,
            controller=self.controller,
            go_to_login=self.show_login,
            go_to_enrollement=self.show_enrollment,
            go_to_settings=self.show_settings,
        )
        self.current_frame.pack(fill="both", expand=True)

    def show_enrollment(self):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = EnrollmentFrame(
            self, controller=self.controller, go_to_dashboard=self.show_dashboard
        )
        self.current_frame.pack(fill="both", expand=True)

    def show_settings(self):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = SettingsFrame(
            self, controller=self.controller, go_to_dashboard=self.show_dashboard
        )
        self.current_frame.pack(fill="both", expand=True)


if __name__ == "__main__":
    app = App()
    app.mainloop()
