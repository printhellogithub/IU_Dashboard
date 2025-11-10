from __future__ import annotations
from typing import Callable, Any
import customtkinter as ctk
import datetime
import tkinter as tk
from tkcalendar import Calendar
from email_validator import EmailNotValidError

from main import Controller

# GLOBAL
BACKGROUND = "#FFFFFF"


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


# EXTRA-Klasse: ToolTip:
class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip = None
        widget.bind("<Enter>", self._show)
        widget.bind("<Leave>", self._hide)

    def _show(self, ev):
        if self.tip:
            return
        x = ev.x_root + 10
        y = ev.y_root + 10
        self.tip = ctk.CTkToplevel()
        self.tip.overrideredirect(True)
        self.tip.geometry(f"+{x}+{y}")
        ctk.CTkLabel(
            self.tip,
            text=self.text,
            fg_color="gray95",
            text_color="black",
            corner_radius=6,
        ).pack(padx=6, pady=3)

    def _hide(self, ev):
        if self.tip:
            self.tip.destroy()
            self.tip = None


# EXTRA-Klasse: EnrollmentIcon
class EnrollmentIcon(ctk.CTkButton):
    STATUS_ICONS = {
        "offen": "radio_button_unchecked",  # leerer Kreis
        "in_bearbeitung": "pending",  # Kreis mit Punkt
        "abgeschlossen": "check_circle",  # Kreis mit Haken
        "nicht_bestanden": "cancel",  # Kreis mit Kreuz
    }
    # für hover --> "add_circle" bei unchecked

    STATUS_COLORS = {
        "offen": "#D9D9D9",
        "in_bearbeitung": "#FEC109",  # Kreis mit Punkt
        "abgeschlossen": "#29C731",  # Kreis mit Haken
        "nicht_bestanden": "#F20D0D",
    }

    def __init__(
        self,
        master,
        controller: Controller,
        enrollment_id: int | None,
        command: Callable[..., Any] | None = None,
        **kwargs,
    ):
        self.enrollment_id = enrollment_id
        self.controller = controller
        self._user_command = command
        MATERIAL_FONT = ctk.CTkFont(
            family="Material Symbols Sharp", size=28, weight="normal"
        )

        status = self._get_status()
        icon = self.STATUS_ICONS.get(status, self.STATUS_ICONS["offen"])
        color = self.STATUS_COLORS.get(status, self.STATUS_COLORS["offen"])

        def _invoke_command():
            if not callable(self._user_command):
                return
            try:
                self._user_command(self.enrollment_id)
            except TypeError:
                self._user_command()

        super().__init__(
            master,
            text=icon,
            font=MATERIAL_FONT,
            width=56,
            height=56,
            fg_color="transparent",
            text_color=color,
            command=_invoke_command if callable(self._user_command) else None,
            **kwargs,
        )
        # hovering
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        #
        self._base_icon = icon
        self._base_color = color

    def _get_status(self) -> str:
        if self.enrollment_id is None:
            return "offen"
        try:
            status = self.controller.get_enrollment_status(self.enrollment_id)
        except Exception:
            status = None

        if not status:
            return "offen"
        return status.lower()

    def _update_appearance(self):
        status = self._get_status()
        icon = self.STATUS_ICONS.get(status, self.STATUS_ICONS["offen"])
        color = self.STATUS_COLORS.get(status, self.STATUS_COLORS["offen"])
        self._base_icon = icon
        self._base_color = color
        self.configure(text=icon, text_color=color)

    def _on_enter(self, event=None):
        if self.enrollment_id is None:
            self.configure(text="add_circle", text_color="#0A64FF")
        else:
            pass

    def _on_leave(self, event=None):
        self._update_appearance()


# EXTRA-Klasse: SemesterIcon
class SemesterIcon(ctk.CTkButton):
    # TODO
    pass


class LoginFrame(ctk.CTkFrame):
    def __init__(self, master, controller: Controller, go_to_dashboard, go_to_new_user):
        super().__init__(master, fg_color="transparent")

        self.controller = controller
        self.go_to_dashboard = go_to_dashboard
        self.go_to_new_user = go_to_new_user

        H1 = ctk.CTkFont(family="Noto Sans", size=164, weight="normal", slant="italic")

        ctk.CTkLabel(self, text="DASHBOARD", font=H1).pack(pady=20)

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


class NewUserFrame(ctk.CTkFrame):
    def __init__(
        self, master, controller: Controller, go_to_login, go_to_StudiengangAuswahl
    ):
        super().__init__(master, fg_color="transparent")

        self.controller = controller
        self.go_to_login = go_to_login
        self.go_to_StudiengangAuswahl = go_to_StudiengangAuswahl

        H2 = ctk.CTkFont(family="Noto Sans", size=56, weight="normal", slant="italic")

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)
        self.grid_rowconfigure(4, weight=1)
        self.grid_rowconfigure(5, weight=1)
        self.grid_rowconfigure(6, weight=1)
        self.grid_rowconfigure(7, weight=1)
        self.grid_rowconfigure(8, weight=1)
        self.grid_rowconfigure(9, weight=1)
        self.grid_rowconfigure(10, weight=1)

        ctk.CTkLabel(
            self,
            text="Deinen Account anlegen",
            font=H2,
        ).grid(row=0, column=0, columnspan=2, sticky="we", padx=20, pady=20)

        # User-Email
        self.entry_email = ctk.CTkEntry(self, placeholder_text="Email-Adresse")
        self.entry_email.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.label_email_not_valid = ctk.CTkLabel(self, text="", text_color="red")
        self.label_email_not_valid.grid(row=2, column=0, sticky="nsew", padx=10, pady=0)

        # PW
        self.entry_pw = ctk.CTkEntry(self, placeholder_text="Passwort", show="●")
        self.entry_pw.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)

        # Name
        self.entry_name = ctk.CTkEntry(self, placeholder_text="Dein Name")
        self.entry_name.grid(row=3, column=0, sticky="nsew", padx=10, pady=10)

        # Matrikelnummer
        self.entry_matrikelnummer = ctk.CTkEntry(
            self, placeholder_text="Deine Matrikelnummer"
        )
        self.entry_matrikelnummer.grid(row=3, column=1, sticky="nsew", padx=10, pady=10)

        # Hochschule
        self.hochschulen_dict = self.controller.get_hochschulen_dict()
        self.label_hochschule = ctk.CTkLabel(self, text="Wie heißt deine Hochschule?")
        self.label_hochschule.grid(row=4, column=0, sticky="nsew", padx=10, pady=10)
        self.search_combo = SearchableComboBox(self, options=self.hochschulen_dict)
        self.search_combo.grid(row=4, column=1, sticky="nsew", padx=10, pady=10)

        # Semesteranzahl
        self.label_semesteranzahl = ctk.CTkLabel(
            self, text="Wie viele Semester hat Dein Studiengang?"
        )
        self.label_semesteranzahl.grid(row=5, column=0, sticky="nsew", padx=10, pady=10)
        self.entry_semesteranzahl = ctk.CTkOptionMenu(
            self,
            values=["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"],
        )
        self.entry_semesteranzahl.grid(row=5, column=1, sticky="nsew", padx=10, pady=10)

        # Ziel-Note
        self.entry_zielnote: float = 0.0
        self.slider_zielnote = ctk.CTkSlider(
            self, from_=1, to=4, number_of_steps=30, command=self.slider_zielnote_event
        )
        self.slider_zielnote.grid(row=6, column=1, sticky="nsew", padx=10, pady=10)
        self.label_zielnote = ctk.CTkLabel(
            self,
            text=f"Deine Wunsch-Abschlussnote: {round(self.slider_zielnote.get(), 1)}",
        )
        self.label_zielnote.grid(row=6, column=0, sticky="nsew", padx=10, pady=10)

        # Start-Datum
        self.selected_startdatum = tk.StringVar(value="Noch kein Datum ausgewählt")

        self.label_startdatum = ctk.CTkLabel(self, text="Wann war Dein Studienstart?")
        self.label_startdatum.grid(row=7, column=0, sticky="w", padx=10, pady=10)

        self.button_startdatum = ctk.CTkButton(
            self, text="Startdatum auswählen", command=self.start_datum_calendar
        )
        self.button_startdatum.grid(row=7, column=1, sticky="nsew", padx=10, pady=10)

        self.label_startdatum_variable = ctk.CTkLabel(
            self, textvariable=self.selected_startdatum
        )
        self.label_startdatum_variable.grid(
            row=7, column=0, sticky="e", padx=10, pady=10
        )

        self.selected_startdatum_real: str

        # Ziel-Datum
        self.selected_zieldatum = tk.StringVar(value="Noch kein Datum ausgewählt")

        self.label_zieldatum = ctk.CTkLabel(
            self, text="Bis wann möchtest Du Dein Studium beenden?"
        )
        self.label_zieldatum.grid(row=8, column=0, sticky="w", padx=10, pady=10)

        self.button_zieldatum = ctk.CTkButton(
            self, text="Zieldatum auswählen", command=self.ziel_datum_calendar
        )
        self.button_zieldatum.grid(row=8, column=1, sticky="nsew", padx=10, pady=10)

        self.label_zieldatum_variable = ctk.CTkLabel(
            self, textvariable=self.selected_zieldatum
        )
        self.label_zieldatum_variable.grid(
            row=8, column=0, sticky="e", padx=10, pady=10
        )

        self.selected_zieldatum_real: str

        # Submit-Button
        self.button_submit = ctk.CTkButton(self, text="Weiter", command=self.on_submit)
        self.button_submit.grid(row=9, column=0, sticky="nsew", padx=10, pady=10)
        self.label_leere_felder = ctk.CTkLabel(self, text="", text_color="red")
        self.label_leere_felder.grid(row=9, column=1, sticky="nsew", padx=10, pady=10)

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
        self.selected_semesteranzahl = int(self.entry_semesteranzahl.get())
        self.selected_zielnote = self.entry_zielnote
        self.selected_hochschule_name = self.search_combo.get_value()
        self.selected_hochschule_id = self.search_combo.get_id()
        self.selected_startdatum_str = self.selected_startdatum_real
        self.selected_zieldatum_str = self.selected_zieldatum_real

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
            "startdatum": self.selected_startdatum_str,
            "zieldatum": self.selected_zieldatum_str,
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
        top.title("Startdatum auswählen")

        cal_start = Calendar(
            top,
            font="Arial 14",
            selectmode="day",
            locale="de_DE",
            date_pattern="yyyy-mm-dd",
            mindate=mindate_start,
            maxdate=maxdate_start,
            # disabledforeground="red",
            showweeknumbers=False,
        )

        cal_start.pack(fill="both", expand=True)

        def save():
            self.selected_startdatum.set(cal_start.get_date())
            self.selected_startdatum_real = cal_start.get_date()
            top.destroy()

        self.save_button_start = ctk.CTkButton(top, text="ok", command=save)
        self.save_button_start.pack(pady=10)

    def ziel_datum_calendar(self):
        top = ctk.CTkToplevel(
            self,
        )
        mindate_ziel = datetime.date.today()
        maxdate_ziel = datetime.date(year=2200, month=12, day=31)
        top.title("Zieldatum auswählen")

        cal_ziel = Calendar(
            top,
            font="Arial 14",
            selectmode="day",
            locale="de_DE",
            date_pattern="yyyy-mm-dd",
            mindate=mindate_ziel,
            maxdate=maxdate_ziel,
            # disabledforeground="red",
            showweeknumbers=False,
        )

        cal_ziel.pack(fill="both", expand=True)

        def save():
            self.selected_zieldatum.set(cal_ziel.get_date())
            self.selected_zieldatum_real = cal_ziel.get_date()
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
        super().__init__(master, fg_color="transparent")

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


class DashboardFrame(ctk.CTkScrollableFrame):
    def __init__(
        self,
        master,
        controller: Controller,
        go_to_login,
        go_to_enrollement,
        go_to_settings,
    ):
        super().__init__(master, fg_color="transparent")
        # TODO
        self.controller = controller
        self.go_to_login = go_to_login
        self.go_to_enrollment = go_to_enrollement
        self.go_to_settings = go_to_settings

        H1 = ctk.CTkFont(family="Noto Sans", size=116, weight="normal", slant="italic")
        H1notitalic = ctk.CTkFont(
            family="Noto Sans", size=116, weight="normal", slant="roman"
        )
        H2 = ctk.CTkFont(family="Noto Sans", size=54, weight="normal", slant="roman")
        H3 = ctk.CTkFont(family="Noto Sans", size=28, weight="normal", slant="roman")
        INFO = ctk.CTkFont(family="Noto Sans", size=18, weight="normal", slant="roman")

        MATERIAL_FONT = ctk.CTkFont(
            family="Material Symbols Sharp", size=24, weight="normal", slant="roman"
        )

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)
        self.grid_rowconfigure(4, weight=1)
        self.grid_rowconfigure(5, weight=1)
        self.grid_rowconfigure(6, weight=1)
        self.grid_rowconfigure(7, weight=1)
        self.grid_rowconfigure(8, weight=1)
        self.grid_rowconfigure(9, weight=1)
        self.grid_rowconfigure(10, weight=1)

        top_frame = ctk.CTkFrame(self, fg_color="transparent", height=130)
        top_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=0)

        dates_frame = ctk.CTkFrame(self, fg_color="transparent")
        dates_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=5)

        progress_frame = ctk.CTkFrame(self, fg_color="transparent")
        progress_frame.grid(
            row=2, column=0, columnspan=2, sticky="nsew", padx=10, pady=5
        )

        semester_frame = ctk.CTkFrame(self, fg_color="transparent")
        semester_frame.grid(
            row=3, column=0, columnspan=2, sticky="nsew", padx=10, pady=5
        )

        kurse_frame = ctk.CTkFrame(self, fg_color="transparent")
        kurse_frame.grid(row=4, column=0, columnspan=2, sticky="nsew", padx=10, pady=5)

        text_kurse_frame = ctk.CTkFrame(self, fg_color="transparent")
        text_kurse_frame.grid(row=5, column=0, sticky="nsew", padx=10, pady=5)

        ects_frame = ctk.CTkFrame(self, fg_color="transparent")
        ects_frame.grid(row=5, column=1, sticky="nsew", padx=10, pady=5)

        noten_frame = ctk.CTkFrame(self, fg_color="gray20")
        noten_frame.grid(row=6, column=0, columnspan=2, sticky="nsew", padx=10, pady=5)

        # --- TOP FRAME ---
        top_frame.grid_columnconfigure(0, weight=1)
        top_frame.grid_rowconfigure(0, weight=0)
        top_frame.grid_propagate(False)

        # DASHBOARD-Label
        dash_label = ctk.CTkLabel(
            top_frame, text="DASHBOARD", font=H1, justify="left", fg_color="transparent"
        )
        dash_label.grid(row=0, column=0, sticky="nw", padx=0, pady=0)

        # rechter Frame
        right_frame = ctk.CTkFrame(top_frame, fg_color="transparent")
        right_frame.grid(row=0, column=1, sticky="e", padx=0, pady=0)

        # Menu-Button
        # TODO: Menu ist im moment leer, evtl. OptionMenu? oder Toplevel-Window?
        menu_button = ctk.CTkButton(
            right_frame,
            text="menu",
            width=10,
            fg_color="transparent",
            text_color="black",
            hover_color="gray95",
            border_color="black",
            font=MATERIAL_FONT,
            anchor="e",
        )
        menu_button.pack(anchor="e", pady=(0, 2))

        # Name-Label
        # TODO: text an tatsächliche student-Daten anpassen.
        name_label = ctk.CTkLabel(
            right_frame,
            text="Max Mustermann\n Angewandte Künstliche Intelligenz\n IU Internationale Hochschule",
            font=INFO,
            justify="right",
        )
        name_label.pack(anchor="e", padx=10, pady=0)

        # --- DATES-FRAME ---
        dates_frame.grid_columnconfigure(0, weight=1)
        dates_frame.grid_columnconfigure(1, weight=0)
        dates_frame.grid_columnconfigure(2, weight=1)
        # TODO: Daten an tatsächliche student-Daten anpassen
        # Start-Label
        start_label = ctk.CTkLabel(
            dates_frame, text="Start: \n01.04.2024", font=H3, justify="left"
        )
        start_label.grid(row=0, column=0, sticky="w", padx=5)

        # Heute-Label
        heute_label = ctk.CTkLabel(
            dates_frame, text="Heute: \n10.11.2025", font=H3, justify="center"
        )
        heute_label.grid(row=0, column=1, sticky="nsew", padx=5)

        # Ziel-Label
        ziel_label = ctk.CTkLabel(
            dates_frame, text="Ziel: \n30.03.2028", font=H3, justify="right"
        )
        ziel_label.grid(row=0, column=2, sticky="e", padx=5)

        # ---PROGRESS-FRAME---
        # Progress-Bar
        progressbar = ctk.CTkProgressBar(
            progress_frame,
            orientation="horizontal",
            progress_color="#0A64FF",
            fg_color="#B5D0FF",
        )
        # TODO: Set-Value an Studienfortschritt anpassen
        progressbar.set(0.3)
        progressbar.pack(fill="both")

        # ---SEMESTER-FRAME---
        # Semester-Label
        semester_label = ctk.CTkLabel(
            semester_frame,
            text="Semester",
            font=INFO,
            justify="left",
            bg_color="transparent",
        )
        semester_label.grid(row=0, column=0, sticky="w", padx=5)

        # Semester-Icons
        # TODO: TEST-Funktion!!! muss mit logik befüllt werden, evtl. ToolTips(siehe Klasse oben)
        test = 6
        color = "orange"

        balken_frame = ctk.CTkFrame(semester_frame, fg_color="transparent")
        balken_frame.grid(row=1, column=0, columnspan=1, sticky="ew", padx=0, pady=4)

        semester_frame.grid_columnconfigure(0, weight=1)

        for i in range(test):
            balken_frame.grid_columnconfigure(i, weight=1, uniform="semester_balken")
            balken = ctk.CTkLabel(
                balken_frame, fg_color=color, corner_radius=8, height=26, text=""
            )
            balken.grid(row=1, column=i, sticky="ew", padx=0)

        # ---KURSE-FRAME---
        # Kurse-Label
        kurse_label = ctk.CTkLabel(
            kurse_frame, text="Kurse", font=INFO, justify="left", bg_color="transparent"
        )
        kurse_label.grid(row=0, column=0, sticky="w", padx=5)

        # Enrollment-Icons
        kurse_test = 36

        one_frame = ctk.CTkFrame(kurse_frame, fg_color="transparent")
        one_frame.grid(row=1, column=0, sticky="ew", padx=0, pady=4)

        kurse_frame.grid_columnconfigure(0, weight=1)

        for i in range(kurse_test):
            one_frame.grid_columnconfigure(i, weight=1, uniform="kurse_icons")
            # icon = EnrollmentIcon(
            #     one_frame,
            #     self.controller,
            #     i
            # )
            icon = ctk.CTkLabel(one_frame, font=MATERIAL_FONT, text="add_circle")
            icon.grid(row=1, column=i, sticky="nsew", padx=2)

        # ---TEXT-KURSE-FRAME---
        # Kurse-vertikal-Label
        canvas = ctk.CTkCanvas(
            text_kurse_frame,
            width=90,
            height=150,
            bg=BACKGROUND,
            highlightthickness=0,
            bd=0,
        )
        canvas.grid(row=0, column=0, rowspan=3, padx=10)
        canvas.create_text(50, 100, text="Kurse", angle=90, font=H2, fill="black")

        # STATS-Label
        testanzahl1 = 4
        testanzahl2 = 6
        testanzahl3 = 22

        abgeschlossen_label = ctk.CTkLabel(
            text_kurse_frame,
            font=H2,
            text_color="#29C731",
            text=f"Abgeschlossen: {testanzahl1}",
            justify="right",
        )
        in_bearbeitung_label = ctk.CTkLabel(
            text_kurse_frame,
            font=H2,
            text_color="#FEC109",
            text=f"In Bearbeitung: {testanzahl2}",
            justify="right",
        )
        ausstehend_label = ctk.CTkLabel(
            text_kurse_frame,
            font=H2,
            text_color="black",
            text=f"Ausstehend: {testanzahl3}",
            justify="right",
        )
        abgeschlossen_label.grid(row=0, column=1, sticky="e", pady=0, padx=10)
        in_bearbeitung_label.grid(row=1, column=1, sticky="e", pady=0, padx=10)
        ausstehend_label.grid(row=2, column=1, sticky="e", pady=0, padx=10)

        # ---ECTS-FRAME---
        erreichte_punkte = 20
        maximale_punkte = 180
        ects_color = "#29C731"
        ects_label = ctk.CTkLabel(
            ects_frame,
            font=H2,
            text_color="black",
            text="Erarbeitete ECTS-Punkte:",
            justify="right",
        )
        ects_erreicht_label = ctk.CTkLabel(
            ects_frame,
            font=H1notitalic,
            text_color=ects_color,
            text=f"{erreichte_punkte}",
        )
        ects_max_label = ctk.CTkLabel(
            ects_frame,
            font=H1notitalic,
            text_color="#D9D9D9",
            text=f"/{maximale_punkte}",
        )

        ects_label.pack()
        ects_max_label.pack(side="right", anchor="e")
        ects_erreicht_label.pack(side="right", anchor="e")

        # ---NOTEN-FRAME---
        # TODO


class EnrollmentFrame(ctk.CTkFrame):
    def __init__(self, master, controller: Controller, go_to_dashboard):
        super().__init__(master, fg_color="transparent")
        # TODO


class SettingsFrame(ctk.CTkFrame):
    def __init__(self, master, controller: Controller, go_to_dashboard):
        super().__init__(master, fg_color="transparent")
        # TODO


class App(ctk.CTk):
    def __init__(self):
        super().__init__(fg_color=BACKGROUND)

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

    def show_studiengang_auswahl(self, cache):
        self.cache = cache
        self.hochschule_id = self.cache["hochschulid"]
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
