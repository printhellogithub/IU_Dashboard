from __future__ import annotations
import customtkinter as ctk
import datetime
import tkinter as tk
from tkinter import ttk
from tkcalendar import Calendar

from main import Controller

# EXTRA-Klasse: Searchable Combobox


class SearchableComboBox(ctk.CTkComboBox):
    def __init__(self, master, values: list[str], **kwargs):
        super().__init__(master, values=values, **kwargs)
        # Alle Originalwerte merken
        self._all_values = list(values)

        # Auf Änderungen im Entry reagieren
        self.bind("<KeyRelease>", self._on_key_release)

    def _on_key_release(self, event):
        text = self.get()
        if not text:
            # nichts eingegeben -> alles anzeigen
            self.configure(values=self._all_values)
            return
        # filtern (case-insensitive)
        filtered = [v for v in self._all_values if text.lower() in v.lower()]
        # Liste im Dropdown aktualisieren
        # (wenn leer, trotzdem mindestens den aktuellen Text drin lassen)
        self.configure(values=filtered or [text])

    def get_value(self) -> str:
        return self.get()


class LoginFrame(ctk.CTkFrame):
    def __init__(self, main, controller, go_to_dashboard, go_to_new_user):
        super().__init__(main)

        self.controller = controller
        self.go_to_dashboard = go_to_dashboard
        self.go_to_make_new_account = go_to_new_user

        ctk.CTkLabel(self, text="Login", font=ctk.CTkFont(size=18, weight="bold")).pack(
            pady=20
        )

        self.entry_user = ctk.CTkEntry(self, placeholder_text="Email-Adresse")
        self.entry_user.focus()
        self.entry_user.pack(pady=5)

        self.entry_pw = ctk.CTkEntry(self, placeholder_text="Passwort", show="●")
        self.entry_pw.pack(pady=5)

        self.label_info = ctk.CTkLabel(self, text="", text_color="red")
        self.label_info.pack(pady=5)

        ctk.CTkButton(self, text="Login", command=self.check_login).pack(pady=10)

    def check_login(self):
        user = self.entry_user.get()
        password = self.entry_user.get()
        if self.controller.login(user, password):
            self.go_to_dashboard(user)
        else:
            self.label_info.configure(text="Login fehlgeschlagen")


class NewUserFrame(ctk.CTkFrame):
    def __init__(self, main, controller, go_to_dashboard, go_to_login):
        super().__init__(main)

        self.controller = controller
        self.go_to_dashboard = go_to_dashboard
        self.go_to_login = go_to_login

        ctk.CTkLabel(
            self,
            text="Deinen Account anlegen",
            font=ctk.CTkFont(size=18, weight="bold"),
        ).pack(pady=20)

        self.entry_name = ctk.CTkEntry(self, placeholder_text="Dein Name")
        self.entry_name.pack(pady=5)

        self.entry_matrikelnummer = ctk.CTkEntry(
            self, placeholder_text="Deine Matrikelnummer"
        )
        self.entry_matrikelnummer.pack(pady=5)

        self.label_semesteranzahl = ctk.CTkLabel(
            self, text="Wie viele Semester hast du?"
        )
        self.label_semesteranzahl.pack(pady=5)
        self.entry_semesteranzahl = ctk.CTkOptionMenu(
            self,
            values=["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", 12],
        )
        self.entry_semesteranzahl.pack(pady=5)

        self.label_startdatum = ctk.CTkLabel(self, text="Wann ist/war Dein Startdatum?")
        self.label_startdatum.pack(pady=5)

        self.entry_startdatum = ttk.Button(
            self, text="Startdatum", command=self.start_datum_calendar
        )

        self.label_zieldatum = ctk.CTkLabel(
            self, text="Bis wann möchtest Du Dein Studium beenden?"
        )
        self.label_zieldatum.pack(pady=5)

        self.entry_zieldatum = ttk.Button(
            self, text="Zieldatum", command=self.ziel_datum_calendar
        )

        self.entry_zielnote: float = 0.0
        self.slider_zielnote = ctk.CTkSlider(
            self, from_=1, to=4, number_of_steps=30, command=self.slider_zielnote_event
        )
        self.slider_zielnote.pack(pady=5)
        self.label_zielnote = ctk.CTkLabel(
            self, text=f"Deine Zielnote: {round(self.slider_zielnote.get(), 1)}"
        )
        self.label_zielnote.pack(pady=5)

        # Hochschule
        self.hochschulen_liste = controller.get_hochschulen_liste()
        self.label_hochschule = ctk.CTkLabel(self, text="Wie heißt deine Hochschule?")
        self.label_hochschule.pack(pady=10)
        self.search_combo = SearchableComboBox(self, values=self.hochschulen_liste)
        self.search_combo.pack(pady=20)
        self.button_hochschule = ctk.CTkButton(self, text="Ok", command=self.on_submit)

    def on_submit(self):
        self.entry_hochschule = self.search_combo.get_value()

        # Studiengang

        self.entry_user = ctk.CTkEntry(self, placeholder_text="Email-Adresse")
        self.entry_user.pack(pady=5)

        self.entry_pw = ctk.CTkEntry(self, placeholder_text="Passwort", show="●")
        self.entry_pw.pack(pady=5)

    def start_datum_calendar(self):
        top = tk.Toplevel(self)
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
            disabledforeground="red",
            showweeknumbers=False,
        )

        cal_start.pack(fill="both", expand=True)
        ttk.Button(top, text="ok").pack()
        return cal_start.selection_get()

    def ziel_datum_calendar(self):
        top = tk.Toplevel(self)
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
            disabledforeground="red",
            showweeknumbers=False,
        )

        cal_ziel.pack(fill="both", expand=True)
        ttk.Button(top, text="ok").pack()
        return cal_ziel.selection_get()

    def slider_zielnote_event(self, value: float):
        self.entry_zielnote = round(float(value), 1)
        self.label_zielnote.configure(text=f"Deine Zielnote: {round(float(value), 1)}")


class DashboardFrame(ctk.CTkFrame):
    def __init__(self, main, user, go_to_login):
        super().__init__(main)


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
            self, self.controller, self.show_dashboard, self.show_new_user
        )
        self.current_frame.pack(fill="both", expand=True)

    def show_new_user(self):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = NewUserFrame(
            self, self.controller, self.show_dashboard, self.show_login
        )
        self.current_frame.pack(fill="both", expand=True)

    def show_dashboard(self, user):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_frame = DashboardFrame(self, user, self.show_login)
        self.current_frame.pack(fill="both", expand=True)


if __name__ == "__main__":
    app = App()
    app.mainloop()
