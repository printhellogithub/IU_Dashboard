from __future__ import annotations
import customtkinter as ctk
import datetime
from pathlib import Path
import tkinter as tk
import tkinter.ttk as ttk
from tkcalendar import Calendar
from email_validator import EmailNotValidError
import textwrap
import webbrowser

from src.main import Controller
from utils.logging_config import setup_logging

# GLOBAL
BACKGROUND = "#FFFFFF"

GRUEN = "#29C731"
HELLGRUEN = "#BFF9C2"
GELB = "#FEC109"
ROT = "#F20D0D"
HELLROT = "#FF8585"
GRAU = "#D9D9D9"
DUNKELBLAU = "#0749BB"
BLAU = "#0A64FF"
HELLBLAU = "#B5D0FF"

FONT_PATH_NOTO = Path("assets/fonts/NotoSans_Condensed-Light.ttf")
FONT_PATH_MATERIAL = Path("assets/fonts/MaterialSymbolsSharp-Light.ttf")


def from_iso_to_ddmmyyyy(date) -> str:
    if isinstance(date, datetime.date):
        return date.strftime("%d.%m.%Y")

    elif isinstance(date, str):
        try:
            new_date = datetime.date.fromisoformat(date)
            return new_date.strftime("%d.%m.%Y")
        except ValueError:
            return date
    elif date is None:
        return ""
    else:
        return "irgendwas ist schiefgelaufen"


class Fonts:
    def __init__(self):
        # self.LOGIN = ctk.CTkFont(family="Segoe UI", size=140, weight="normal", slant="italic")
        # self.H1_italic = ctk.CTkFont(family="Segoe UI", size=84, weight="normal", slant="italic")
        # self.H1 = ctk.CTkFont(
        #     family="Segoe UI", size=84, weight="normal", slant="roman"
        # )
        # self.H1_5_italic = ctk.CTkFont(
        #     family="Segoe UI", size=48, weight="normal", slant="italic"
        # )
        # self.H2_italic = ctk.CTkFont(
        #     family="Segoe UI", size=32, weight="normal", slant="italic"
        # )
        # self.H2 = ctk.CTkFont(family="Segoe UI", size=32, weight="normal", slant="roman")
        # self.H3 = ctk.CTkFont(family="Segoe UI", size=22, weight="normal", slant="roman")
        # self.TEXT = ctk.CTkFont(family="Segoe UI", size=16, weight="normal", slant="roman")

        self.ICONS = ctk.CTkFont(
            family="Material Symbols Sharp", size=26, weight="normal", slant="roman"
        )
        self.ICONS_BIG = ctk.CTkFont(
            family="Material Symbols Sharp", size=42, weight="normal", slant="roman"
        )
        # self.CAL = ctk.CTkFont(family="Segoe UI", size=12, weight="normal", slant="roman")
        self.LOGIN = ctk.CTkFont(
            family="Noto Sans Condensed", size=140, weight="normal", slant="italic"
        )
        self.H1_italic = ctk.CTkFont(
            family="Noto Sans Condensed", size=84, weight="normal", slant="italic"
        )
        self.H1 = ctk.CTkFont(
            family="Noto Sans Condensed", size=84, weight="normal", slant="roman"
        )
        self.H1_5_italic = ctk.CTkFont(
            family="Noto Sans Condensed", size=48, weight="normal", slant="italic"
        )
        self.H2_italic = ctk.CTkFont(
            family="Noto Sans Condensed", size=32, weight="normal", slant="italic"
        )
        self.H2 = ctk.CTkFont(
            family="Noto Sans Condensed", size=32, weight="normal", slant="roman"
        )
        self.H3 = ctk.CTkFont(
            family="Noto Sans Condensed", size=22, weight="normal", slant="roman"
        )
        self.TEXT = ctk.CTkFont(
            family="Noto Sans Condensed", size=16, weight="normal", slant="roman"
        )


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


# EXTRA-Klasse: MultiLineLabel
class MultiLineLabel(ctk.CTkLabel):
    def __init__(self, master, text, width, **kwargs):
        wrapped_text = textwrap.fill(text, width=width)
        super().__init__(master, text=wrapped_text, **kwargs)


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


# EXTRA-KLASSE Enrollment-Icon mit Hover.
class HoverButton(ctk.CTkButton):
    def __init__(
        self, master, hovertext, hovercolor, defaulttext, defaultcolor, **kwargs
    ):
        super().__init__(master=master, **kwargs)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.hovertext = hovertext
        self.hovercolor = hovercolor
        self.defaulttext = defaulttext
        self.defaultcolor = defaultcolor

    def _on_enter(self, event=None):
        self.configure(text=self.hovertext, text_color=self.hovercolor)

    def _on_leave(self, event=None):
        self.configure(text=self.defaulttext, text_color=self.defaultcolor)


# EXTRA-KLASSE Dynamische Kurs-Entries
class DynamicEntries(ctk.CTkFrame):
    def __init__(
        self,
        master,
        *,
        label_name="Kursname",
        label_nummer="Kursnummer",
        # placeholder_name="Kurs",
        # placeholder_nummer="Kursnummer",
        initial_rows=1,
        max_rows=10,
    ):
        super().__init__(
            master, fg_color="transparent", border_color="black", border_width=2
        )
        # self.placeholder_name = placeholder_name
        # self.placeholder_nummer = placeholder_nummer
        self.max_rows = max_rows
        self.rows: list[dict[str, object]] = []

        # Layout
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        # self.grid_columnconfigure(1, weight=1)

        self.header = ctk.CTkFrame(self, fg_color="transparent")
        self.header.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 0))
        self.header.grid_columnconfigure(0, weight=1)
        self.header.grid_columnconfigure(1, weight=1)

        self.title = ctk.CTkLabel(self.header, text=label_name)
        self.title.grid(row=0, column=0, sticky="w", padx=5)

        self.title_nummer = ctk.CTkLabel(self.header, text=label_nummer)
        self.title_nummer.grid(row=0, column=1, sticky="e", padx=5)

        icons = ctk.CTkFont(
            family="Material Symbols Sharp", size=26, weight="normal", slant="roman"
        )

        self.add_button = ctk.CTkButton(
            self.header,
            text="add_circle",
            font=icons,
            width=36,
            text_color="black",
            fg_color="transparent",
            border_color="black",
            border_spacing=2,
            border_width=2,
            hover_color="gray95",
            command=self.add_row,
        )
        self.add_button.grid(row=0, column=2, sticky="e", padx=(8, 0))

        self.list_frame = ctk.CTkScrollableFrame(
            self, label_text="", fg_color="transparent"
        )
        self.list_frame.grid(row=1, column=0, sticky="nsew", padx=8, pady=8)
        self.list_frame.grid_columnconfigure(0, weight=1)
        self.list_frame.grid_columnconfigure(1, weight=1)

        # Startzustand
        for _ in range(max(1, initial_rows)):
            self.add_row(
                # kursname=self.placeholder_name, kursnummer=self.placeholder_nummer
            )

    # FIX: Placeholder Text funktioniert nicht in Kombi mit textvariable. -> PLACEHOLDER DEAKTIVIERT
    def add_row(self, kursname: str = "", kursnummer: str = "") -> None:
        if len(self.rows) >= self.max_rows:
            return
        var_kursname = ctk.StringVar(value=kursname)
        entry_kursname = ctk.CTkEntry(
            self.list_frame,
            textvariable=var_kursname,
            # placeholder_text=f"{self.placeholder_name} {len(self.rows) + 1}",
        )

        var_kursnummer = ctk.StringVar(value=kursnummer)
        entry_kursnummer = ctk.CTkEntry(
            self.list_frame,
            textvariable=var_kursnummer,
            # placeholder_text=f"{self.placeholder_nummer} {len(self.rows) + 1}",
        )

        self.rows.append(
            {
                "var_kursname": var_kursname,
                "entry_kursname": entry_kursname,
                "var_kursnummer": var_kursnummer,
                "entry_kursnummer": entry_kursnummer,
            }
        )
        self._regrid()

    def _regrid(self) -> None:
        for i, r in enumerate(self.rows):
            r["entry_kursname"].grid(row=i, column=0, sticky="w", padx=(8, 4), pady=4)  # type: ignore
            r["entry_kursnummer"].grid(row=i, column=1, sticky="e", padx=(8, 4), pady=4)  # type: ignore

            # if isinstance(r["entry_kursname"], ctk.CTkEntry):
            #     r["entry_kursname"].configure(
            #         placeholder_text=f"{self.placeholder_name} {i + 1}"
            #     )
            # if isinstance(r["entry_kursnummer"], ctk.CTkEntry):
            #     r["entry_kursnummer"].configure(
            #         placeholder_text=f"{self.placeholder_nummer} {i + 1}"
            #     )

    def get_values(self) -> list[dict[str, str]]:
        values: list[dict[str, str]] = []
        for r in self.rows:
            value_kurs_name = r["var_kursname"].get().strip()  # type: ignore
            value_kurs_nummer = r["var_kursnummer"].get().strip()  # type: ignore
            if value_kurs_name and value_kurs_nummer:
                value_dict = {value_kurs_nummer: value_kurs_name}
                values.append(value_dict)
        return values


class LoginFrame(ctk.CTkFrame):
    def __init__(self, master, controller: Controller, go_to_dashboard, go_to_new_user):
        super().__init__(master, fg_color="transparent")

        self.controller = controller
        self.go_to_dashboard = go_to_dashboard
        self.go_to_new_user = go_to_new_user

        # H1 = ctk.CTkFont(family="Segoe UI", size=140, weight="normal", slant="italic")

        ctk.CTkLabel(self, text="DASHBOARD", font=master.fonts.LOGIN).pack(pady=20)

        self.entry_email = ctk.CTkEntry(self, placeholder_text="Email-Adresse")
        self.entry_email.focus()
        self.entry_email.pack(pady=5)

        self.entry_pw = ctk.CTkEntry(
            self,
            placeholder_text="Passwort",
            show="●",
        )
        self.entry_pw.pack(pady=5)
        self.entry_pw.bind("<Return>", lambda event: self.check_login())

        self.label_info = ctk.CTkLabel(self, text="", text_color=ROT)
        self.label_info.pack(pady=5)

        self.button_login = ctk.CTkButton(
            self,
            text="Login",
            text_color="black",
            fg_color="transparent",
            border_color="black",
            border_spacing=2,
            border_width=2,
            hover_color="gray95",
            command=self.check_login,
        )
        self.button_login.pack(pady=10)

        self.button_to_new_user = ctk.CTkButton(
            self,
            text="Neuer Account",
            text_color="black",
            fg_color="transparent",
            border_color="black",
            border_spacing=2,
            border_width=2,
            hover_color="gray95",
            command=lambda: self.after(0, self.go_to_new_user),
        )
        self.button_to_new_user.pack(pady=20)

    def check_login(self):
        email = self.entry_email.get()
        password = self.entry_pw.get()
        if self.controller.login(email, password):
            self.after(0, self.go_to_dashboard)
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

        H15italic = ctk.CTkFont(
            family="Segoe UI", size=48, weight="normal", slant="italic"
        )

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        # self.grid_rowconfigure(2, weight=1)
        # self.grid_rowconfigure(3, weight=1)

        header_frame = ctk.CTkFrame(
            self, fg_color=BACKGROUND, border_color="black", border_width=2
        )
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        # SETTINGS FRAME ÜBERSCHRIFT
        header_frame.grid_columnconfigure(0, weight=1)
        header_frame.grid_columnconfigure(1, weight=0)

        header_ueber_label = ctk.CTkLabel(
            header_frame, text="Dein Account", font=H15italic, justify="left"
        )
        header_ueber_label.grid(row=0, sticky="nw", padx=10, pady=10)

        header_close_button = ctk.CTkButton(
            header_frame,
            text="Close",
            font=master.fonts.ICONS,
            width=10,
            fg_color="transparent",
            text_color="black",
            hover_color="gray95",
            # border_color="black",
            command=lambda: self.after(0, self.go_to_login),
        )
        header_close_button.grid(row=0, column=1, padx=(0, 2), pady=(2, 0), sticky="ne")

        nu_frame = ctk.CTkFrame(
            self, fg_color=BACKGROUND, border_color="black", border_width=2
        )
        nu_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        nu_frame.grid_columnconfigure(0, weight=1)
        nu_frame.grid_columnconfigure(1, weight=1)
        nu_frame.grid_columnconfigure(2, weight=1)
        nu_frame.grid_columnconfigure(3, weight=1)
        nu_frame.grid_rowconfigure(0, weight=1)
        nu_frame.grid_rowconfigure(1, weight=1)
        nu_frame.grid_rowconfigure(2, weight=1)
        nu_frame.grid_rowconfigure(3, weight=1)
        nu_frame.grid_rowconfigure(4, weight=1)
        nu_frame.grid_rowconfigure(5, weight=1)
        nu_frame.grid_rowconfigure(6, weight=1)
        nu_frame.grid_rowconfigure(7, weight=1)
        nu_frame.grid_rowconfigure(8, weight=1)
        nu_frame.grid_rowconfigure(9, weight=1)
        nu_frame.grid_rowconfigure(10, weight=1)

        # User-Email
        self.entry_email_label = ctk.CTkLabel(nu_frame, text="Deine Email-Adresse")
        self.entry_email_label.grid(row=1, column=0, padx=10, pady=10)
        self.entry_email = ctk.CTkEntry(
            nu_frame, placeholder_text="username@example.com"
        )
        self.entry_email.grid(row=1, column=1, sticky="ew", padx=10, pady=10)
        self.label_email_not_valid = ctk.CTkLabel(nu_frame, text="", text_color=ROT)
        self.label_email_not_valid.grid(
            row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=2
        )

        # PW
        self.entry_pw_label = ctk.CTkLabel(nu_frame, text="Dein Passwort")
        self.entry_pw_label.grid(row=1, column=2, sticky="ew", padx=10, pady=10)
        self.entry_pw = ctk.CTkEntry(nu_frame, placeholder_text="Passwort", show="●")
        self.entry_pw.grid(row=1, column=3, sticky="ew", padx=10, pady=10)

        # Name
        self.entry_name_label = ctk.CTkLabel(nu_frame, text="Dein Name")
        self.entry_name_label.grid(row=2, column=0, padx=10, pady=10)
        self.entry_name = ctk.CTkEntry(nu_frame, placeholder_text="Max Mustermann")
        self.entry_name.grid(row=2, column=1, sticky="ew", padx=10, pady=10)

        # Matrikelnummer
        self.entry_name_label = ctk.CTkLabel(nu_frame, text="Deine Matrikelnummer")
        self.entry_name_label.grid(row=2, column=2, sticky="ew", padx=10, pady=10)
        self.entry_matrikelnummer = ctk.CTkEntry(nu_frame, placeholder_text="1234567")
        self.entry_matrikelnummer.grid(row=2, column=3, sticky="ew", padx=10, pady=10)

        # Hochschule
        self.hochschulen_dict = self.controller.get_hochschulen_dict()
        self.label_hochschule = ctk.CTkLabel(
            nu_frame, text="Wie heißt deine Hochschule?"
        )
        self.label_hochschule.grid(row=3, column=0, sticky="ew", padx=10, pady=10)
        self.search_combo = SearchableComboBox(nu_frame, options=self.hochschulen_dict)
        self.search_combo.grid(
            row=3, column=2, columnspan=2, sticky="ew", padx=10, pady=10
        )

        # Semesteranzahl
        self.label_semesteranzahl = ctk.CTkLabel(
            nu_frame, text="Wie viele Semester hast Du?"
        )
        self.label_semesteranzahl.grid(row=4, column=0, sticky="ew", padx=10, pady=10)
        self.entry_semesteranzahl = ctk.CTkOptionMenu(
            nu_frame,
            values=["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"],
            text_color="black",
            fg_color="gray95",
            button_color="gray95",
            button_hover_color="gray85",
        )
        self.entry_semesteranzahl.grid(
            row=4, column=2, columnspan=2, sticky="ew", padx=10, pady=10
        )

        # Ziel-Note
        self.entry_zielnote: float = 0.0
        self.slider_zielnote = ctk.CTkSlider(
            nu_frame,
            from_=1,
            to=4,
            number_of_steps=30,
            fg_color=HELLBLAU,
            progress_color=BLAU,
            button_color=BLAU,
            button_hover_color=DUNKELBLAU,
            command=self.slider_zielnote_event,
        )
        self.slider_zielnote.grid(
            row=5, column=2, columnspan=2, sticky="ew", padx=10, pady=10
        )
        self.label_zielnote = ctk.CTkLabel(
            nu_frame,
            text="Deine Wunsch-Abschlussnote:",
        )
        self.label_zielnote.grid(row=5, column=0, sticky="nsew", padx=10, pady=10)
        self.label_note = ctk.CTkLabel(
            nu_frame, text=f"{round(self.slider_zielnote.get(), 1)}"
        )
        self.label_note.grid(row=5, column=1, sticky="nsew", padx=10, pady=10)

        # Start-Datum
        self.selected_startdatum = tk.StringVar(value="Kein Datum ausgewählt")

        self.label_startdatum = ctk.CTkLabel(
            nu_frame, text="Wann war Dein Studienstart?"
        )
        self.label_startdatum.grid(row=6, column=0, sticky="ew", padx=10, pady=10)

        self.button_startdatum = ctk.CTkButton(
            nu_frame,
            text="Startdatum auswählen",
            text_color="black",
            fg_color="transparent",
            border_color="black",
            border_spacing=2,
            border_width=2,
            hover_color="gray95",
            command=self.start_datum_calendar_at_button,
        )
        self.button_startdatum.grid(
            row=6, column=2, columnspan=2, sticky="ew", padx=10, pady=10
        )

        self.label_startdatum_variable = ctk.CTkLabel(
            nu_frame, textvariable=self.selected_startdatum
        )
        self.label_startdatum_variable.grid(
            row=6, column=1, sticky="ew", padx=10, pady=10
        )

        self.selected_startdatum_real: str

        # Ziel-Datum
        self.selected_zieldatum = tk.StringVar(value="Kein Datum ausgewählt")

        self.label_zieldatum = ctk.CTkLabel(
            nu_frame, text="Bis wann willst Du fertig sein?"
        )
        self.label_zieldatum.grid(row=7, column=0, sticky="ew", padx=10, pady=10)

        self.button_zieldatum = ctk.CTkButton(
            nu_frame,
            text="Zieldatum auswählen",
            text_color="black",
            fg_color="transparent",
            border_color="black",
            border_spacing=2,
            border_width=2,
            hover_color="gray95",
            command=self.ziel_datum_calendar_at_button,
        )
        self.button_zieldatum.grid(
            row=7, column=2, columnspan=2, sticky="ew", padx=10, pady=10
        )

        self.label_zieldatum_variable = ctk.CTkLabel(
            nu_frame, textvariable=self.selected_zieldatum
        )
        self.label_zieldatum_variable.grid(
            row=7, column=1, sticky="ew", padx=10, pady=10
        )

        self.selected_zieldatum_real: str

        # Submit-Button
        self.button_submit = ctk.CTkButton(
            nu_frame,
            text="Weiter",
            text_color="black",
            fg_color="transparent",
            border_color="black",
            border_spacing=2,
            border_width=2,
            hover_color="gray95",
            command=self.on_submit,
        )
        self.button_submit.grid(
            row=11, column=0, columnspan=4, sticky="ew", padx=10, pady=10
        )
        self.label_leere_felder = ctk.CTkLabel(nu_frame, text="", text_color=ROT)
        self.label_leere_felder.grid(
            row=10, column=0, columnspan=4, sticky="ew", padx=10, pady=10
        )

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

        if self.controller.check_if_email_exists(self.selected_email):
            self.label_email_not_valid.configure(
                text="Diese Email hat schon einen Account"
            )
            return

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

        try:
            self.selected_startdatum_str = self.selected_startdatum_real
            self.selected_zieldatum_str = self.selected_zieldatum_real
        except AttributeError:
            self.label_leere_felder.configure(
                text="Start oder Zieldatum nicht ausgewählt."
            )
            return

        # user-input validiert, speicher eingaben
        self.selected_password = self.entry_pw.get()
        self.selected_name = self.entry_name.get()
        self.selected_matrikelnummer = self.entry_matrikelnummer.get()
        self.selected_semesteranzahl = int(self.entry_semesteranzahl.get())
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
            "startdatum": self.selected_startdatum_str,
            "zieldatum": self.selected_zieldatum_str,
            "zielnote": self.selected_zielnote,
            "hochschulname": self.selected_hochschule_name,
            "hochschulid": self.selected_hochschule_id,
        }

        # Zur Studiengangauswahl
        self.after(0, lambda: self.go_to_StudiengangAuswahl(cache=cache))

    def start_datum_calendar_at_button(self):
        self.start_datum_calendar(anchor=self.button_startdatum)

    def start_datum_calendar(self, anchor):
        top = ctk.CTkToplevel(self)
        top.overrideredirect(True)
        top.transient(self.winfo_toplevel())
        top.attributes("-topmost", True)
        top.grab_set()
        top.bind("<FocusOut>", lambda e: top.destroy())

        bx = anchor.winfo_rootx()
        by = anchor.winfo_rooty()
        bw = anchor.winfo_width()
        bh = anchor.winfo_height()

        x = bx
        y = by + bh

        popup_w, popup_h = 250, 250
        sw = top.winfo_screenwidth()
        sh = top.winfo_screenheight()

        if x + popup_w > sw:
            x = max(0, bx + bw - popup_w)
        if y + popup_h > sh:
            y = max(0, by - popup_h)

        top.geometry(f"{popup_w}x{popup_h}+{x}+{y}")

        mindate_start = datetime.date(year=2010, month=1, day=1)
        maxdate_start = datetime.date.today()

        cal_start = Calendar(
            top,
            font="SegoeUI 12",
            selectmode="day",
            locale="de_DE",
            date_pattern="yyyy-mm-dd",
            mindate=mindate_start,
            maxdate=maxdate_start,
            showweeknumbers=False,
            selectforeground=GELB,
            normalforeground=BLAU,
            weekendforeground=BLAU,
            weekendbackground="gray90",
            background="gray95",
            foreground="black",
            selectbackground=DUNKELBLAU,
            headersbackground="gray95",
            headersforeground="black",
            disabledforeground="gray50",
            disabledbackground="gray80",
        )

        cal_start.pack(fill="both", expand=True)

        def save():
            self.selected_startdatum.set(from_iso_to_ddmmyyyy(cal_start.get_date()))
            self.selected_startdatum_real = cal_start.get_date()
            top.destroy()

        self.save_button_start = ctk.CTkButton(
            top,
            text="ok",
            text_color="black",
            fg_color="transparent",
            border_color="black",
            border_spacing=2,
            border_width=2,
            hover_color="gray95",
            command=save,
        )
        self.save_button_start.pack(pady=5)

    def ziel_datum_calendar_at_button(self):
        self.ziel_datum_calendar(anchor=self.button_zieldatum)

    def ziel_datum_calendar(self, anchor):
        top = ctk.CTkToplevel(self)
        top.overrideredirect(True)
        top.transient(self.winfo_toplevel())
        top.attributes("-topmost", True)
        top.grab_set()
        top.bind("<FocusOut>", lambda e: top.destroy())

        bx = anchor.winfo_rootx()
        by = anchor.winfo_rooty()
        bw = anchor.winfo_width()
        bh = anchor.winfo_height()

        x = bx
        y = by + bh

        popup_w, popup_h = 250, 250
        sw = top.winfo_screenwidth()
        sh = top.winfo_screenheight()

        if x + popup_w > sw:
            x = max(0, bx + bw - popup_w)
        if y + popup_h > sh:
            y = max(0, by - popup_h)

        top.geometry(f"{popup_w}x{popup_h}+{x}+{y}")

        mindate_ziel = datetime.date.today()
        maxdate_ziel = datetime.date(year=2200, month=12, day=31)
        top.title("Zieldatum auswählen")

        cal_ziel = Calendar(
            top,
            font="SegoeUI 12",
            selectmode="day",
            locale="de_DE",
            date_pattern="yyyy-mm-dd",
            mindate=mindate_ziel,
            maxdate=maxdate_ziel,
            showweeknumbers=False,
            selectforeground=GELB,
            normalforeground=BLAU,
            weekendforeground=BLAU,
            weekendbackground="gray90",
            background="gray95",
            foreground="black",
            selectbackground=DUNKELBLAU,
            headersbackground="gray95",
            headersforeground="black",
            disabledforeground="gray50",
            disabledbackground="gray80",
        )

        cal_ziel.pack(fill="both", expand=True)

        def save():
            self.selected_zieldatum.set(from_iso_to_ddmmyyyy(cal_ziel.get_date()))
            self.selected_zieldatum_real = cal_ziel.get_date()
            top.destroy()

        self.save_button_ziel = ctk.CTkButton(
            top,
            text="ok",
            text_color="black",
            fg_color="transparent",
            border_color="black",
            border_spacing=2,
            border_width=2,
            hover_color="gray95",
            command=save,
        )
        self.save_button_ziel.pack(pady=10)

    def slider_zielnote_event(self, value: float):
        self.entry_zielnote = round(float(value), 1)
        self.label_note.configure(text=f"{round(float(value), 1)}")

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

        # FONTS
        H2italic = ctk.CTkFont(
            family="Segoe UI", size=32, weight="normal", slant="italic"
        )

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        # self.grid_rowconfigure(2, weight=1)
        # self.grid_rowconfigure(3, weight=1)

        header_frame = ctk.CTkFrame(
            self, fg_color=BACKGROUND, border_color="black", border_width=2
        )
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        # SETTINGS FRAME ÜBERSCHRIFT
        header_frame.grid_columnconfigure(0, weight=1)
        header_frame.grid_columnconfigure(1, weight=0)

        header_ueber_label = ctk.CTkLabel(
            header_frame, text="Dein Account", font=H2italic, justify="left"
        )
        header_ueber_label.grid(row=0, sticky="nw", padx=10, pady=10)

        header_close_button = ctk.CTkButton(
            header_frame,
            text="Close",
            font=master.fonts.ICONS,
            width=10,
            fg_color="transparent",
            text_color="black",
            hover_color="gray95",
            # border_color="black",
            command=lambda: self.after(0, self.go_to_login),
        )
        header_close_button.grid(row=0, column=1, padx=(0, 2), pady=(2, 0), sticky="ne")

        sa_frame = ctk.CTkFrame(
            self, fg_color=BACKGROUND, border_color="black", border_width=2
        )
        sa_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        # Studiengang
        self.label_studiengang = ctk.CTkLabel(
            sa_frame, text="Wie heißt Dein Studiengang?"
        )
        self.label_studiengang.pack(pady=5)

        self.entry_studiengang = ctk.CTkEntry(
            sa_frame, placeholder_text="z.B. Medizin", width=440
        )
        self.entry_studiengang.focus()
        self.entry_studiengang.pack(pady=20)

        # Gesamt-ECTS-Punkte
        self.label_ects = ctk.CTkLabel(
            sa_frame, text="Wie viele ECTS-Punkte hat dein Studium?"
        )
        self.label_ects.pack(pady=5)
        self.entry_ects = ctk.CTkEntry(sa_frame, placeholder_text="ECTS-Punkte")
        self.entry_ects.pack(pady=10)
        self.label_no_int = ctk.CTkLabel(sa_frame, text="", text_color=ROT)
        self.label_no_int.pack(pady=5)

        # Modul-Anzahl
        self.label_modulanzahl = ctk.CTkLabel(
            sa_frame, text="Wie viele Module hat Dein Studiengang?"
        )

        self.label_modulanzahl.pack(pady=10)
        modulvalues = [str(i) for i in range(1, 71)]
        self.entry_modulanzahl = ctk.CTkOptionMenu(
            sa_frame,
            values=modulvalues,
            text_color="black",
            fg_color="gray95",
            button_color="gray95",
            button_hover_color="gray85",
        )
        self.entry_modulanzahl.pack(pady=10)

        # Submit-Button
        self.button_submit = ctk.CTkButton(
            sa_frame,
            text="Weiter",
            text_color="black",
            fg_color="transparent",
            border_color="black",
            border_spacing=2,
            border_width=2,
            hover_color="gray95",
            command=self.on_submit,
        )
        self.button_submit.pack(pady=20)
        self.label_leere_felder = ctk.CTkLabel(sa_frame, text="", text_color=ROT)
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

        if self.entry_studiengang.get() == "":
            self.label_leere_felder.configure(text="Etwas ist nicht ausgefüllt.")
            return

        if len(self.entry_studiengang.get()) > 50:
            self.label_leere_felder.configure(text="Name des Studiengangs zu lang")
            return
        self.selected_studiengang_name = self.entry_studiengang.get()

        # checke ob Feld leer oder fange ab,
        # falls keine id aus searchableComboBox
        if self.selected_studiengang_name.strip() == "":
            self.label_leere_felder.configure(text="Etwas ist nicht ausgefüllt.")
            return

        if (
            self.selected_studiengang_name
            not in self.controller.get_studiengaenge_von_hs_dict(
                self.cache["hochschulid"]
            )
        ):
            studiengang = self.controller.erstelle_studiengang(
                studiengang_name=self.selected_studiengang_name,
                gesamt_ects_punkte=self.selected_ects,
            )
        else:
            studiengang = self.controller.get_studiengang_id(
                self.selected_studiengang_name, self.cache["hochschulid"]
            )
        for k, v in studiengang.items():
            if v == self.selected_studiengang_name:
                self.selected_studiengang_id = k
            else:
                raise ValueError(
                    "Datenbankrückgabe entspricht nicht Eingabewert: Studiengang"
                )

        self.selected_modulanzahl = int(self.entry_modulanzahl.get())

        # Fuege values zum Cache hinzu
        self.cache["studiengang_ects"] = self.selected_ects
        self.cache["modulanzahl"] = self.selected_modulanzahl
        self.cache["studiengang_name"] = self.selected_studiengang_name
        self.cache["studiengang_id"] = self.selected_studiengang_id

        # erstelle Account
        self.controller.erstelle_account(self.cache)

        # wechsle Fenster
        self.after(0, self.go_to_dashboard)


class DashboardFrame(ctk.CTkFrame):
    def __init__(
        self,
        master,
        controller: Controller,
        go_to_login,
        go_to_add_enrollment,
        go_to_enrollment,
        go_to_settings,
        go_to_ex,
        go_to_ziele,
        go_to_ueber,
    ):
        super().__init__(master, fg_color="transparent")

        self.controller = controller
        self.go_to_login = go_to_login
        self.go_to_add_enrollment = go_to_add_enrollment
        self.go_to_enrollment = go_to_enrollment
        self.go_to_settings = go_to_settings
        self.go_to_ex = go_to_ex
        self.go_to_ziele = go_to_ziele
        self.go_to_ueber = go_to_ueber

        self.menu_popup: ctk.CTkToplevel | None = None

        # DATEN BEKOMMEN
        self.data = self.controller.load_dashboard_data()

        # FONTS
        H1 = ctk.CTkFont(family="Segoe UI", size=84, weight="normal", slant="italic")
        H1notitalic = ctk.CTkFont(
            family="Segoe UI", size=84, weight="normal", slant="roman"
        )
        H2 = ctk.CTkFont(family="Segoe UI", size=32, weight="normal", slant="roman")
        H2italic = ctk.CTkFont(
            family="Segoe UI", size=32, weight="normal", slant="italic"
        )
        H3 = ctk.CTkFont(family="Segoe UI", size=22, weight="normal", slant="roman")
        INFO = ctk.CTkFont(family="Segoe UI", size=16, weight="normal", slant="roman")

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
        top_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=(2, 0))

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

        module_frame = ctk.CTkFrame(self, fg_color="transparent")
        module_frame.grid(row=4, column=0, columnspan=2, sticky="nsew", padx=10, pady=5)

        text_module_frame = ctk.CTkFrame(self, fg_color="transparent")
        text_module_frame.grid(row=5, column=0, sticky="nsew", padx=10, pady=5)

        ects_frame = ctk.CTkFrame(self, fg_color="transparent")
        ects_frame.grid(row=5, column=1, sticky="nsew", padx=10, pady=5)

        noten_frame = ctk.CTkFrame(self, fg_color="gray95")
        noten_frame.grid(row=6, column=0, columnspan=2, padx=10, pady=5)

        # --- TOP FRAME ---
        top_frame.grid_columnconfigure(0, weight=1)
        top_frame.grid_rowconfigure(0, weight=0)
        top_frame.grid_propagate(False)

        # DASHBOARD-Label
        dash_label = ctk.CTkLabel(
            top_frame, text="DASHBOARD", font=H1, justify="left", fg_color="transparent"
        )
        dash_label.grid(row=0, column=0, sticky="nw", padx=0, pady=(2, 0))

        # rechter Frame
        right_frame = ctk.CTkFrame(top_frame, fg_color="transparent")
        right_frame.grid(row=0, column=1, sticky="e", padx=0, pady=(2, 0))

        # Menu-Button
        self.menu_button = ctk.CTkButton(
            right_frame,
            text="menu",
            width=10,
            fg_color="transparent",
            text_color="black",
            hover_color="gray95",
            border_color="black",
            font=master.fonts.ICONS,
            anchor="e",
            command=self.menu_on_button,
        )
        self.menu_button.pack(anchor="e", pady=(0, 2))

        # Name-Label
        name_label_text = f"{self.data['name']}\n{self.data['studiengang']}\n{self.controller.get_hs_kurzname_if_notwendig(self.data['hochschule'])}"
        name_label = ctk.CTkLabel(
            right_frame,
            text=name_label_text,
            font=INFO,
            justify="right",
        )
        name_label.pack(anchor="e", padx=10, pady=0)

        # --- DATES-FRAME ---
        dates_frame.grid_columnconfigure(0, weight=0)
        dates_frame.grid_columnconfigure(1, weight=1)
        dates_frame.grid_columnconfigure(2, weight=0)
        dates_frame.grid_rowconfigure(0, weight=0)

        # Start-Label
        start_label = ctk.CTkLabel(
            dates_frame,
            text=f"Start: \n{from_iso_to_ddmmyyyy(self.data['startdatum'])}",
            font=H3,
            justify="left",
        )
        start_label.grid(row=0, column=0, sticky="w", padx=5)

        # Heute-Label
        heute_frame = ctk.CTkFrame(dates_frame, fg_color="transparent", height=50)
        heute_frame.grid(row=0, column=1, sticky="ew", padx=5)

        if self.data["exmatrikulationsdatum"] is not None:
            heute_label_text = f"Exmatrikulationsdatum:\n{from_iso_to_ddmmyyyy(self.data['exmatrikulationsdatum'])}"
        else:
            heute_label_text = f"Heute:\n{from_iso_to_ddmmyyyy(self.data['heute'])}"
        position = self.get_position(self.data["time_progress"])
        if position < 0.2:
            anchor = "w"
        elif position > 0.8:
            anchor = "e"
        else:
            anchor = "center"

        heute_label = ctk.CTkLabel(
            heute_frame,
            text=heute_label_text,
            font=H3,
            justify="center",
        )
        heute_label.place(relx=position, rely=0.5, anchor=anchor)

        # Ziel-Label
        if datetime.date.today() > self.data["zieldatum"]:
            ziel_color = ROT
        else:
            ziel_color = "black"

        ziel_label = ctk.CTkLabel(
            dates_frame,
            text=f"Ziel: \n{from_iso_to_ddmmyyyy(self.data['zieldatum'])}",
            font=H3,
            text_color=ziel_color,
            justify="right",
        )
        ziel_label.grid(row=0, column=2, sticky="e", padx=5)

        # ---PROGRESS-FRAME---
        # Progress-Bar
        # Farben:
        if (
            self.data["exmatrikulationsdatum"]
            and self.data["erarbeitete_ects"] != self.data["gesamt_ects"]
        ):
            progress_color = ROT
            background_color = HELLROT
        elif self.data["erarbeitete_ects"] == self.data["gesamt_ects"]:
            progress_color = GRUEN
            background_color = HELLGRUEN
        else:
            progress_color = BLAU
            background_color = HELLBLAU

        progressbar = ctk.CTkProgressBar(
            progress_frame,
            orientation="horizontal",
            progress_color=progress_color,
            fg_color=background_color,
        )
        progressbar.set(self.data["time_progress"])
        progressbar.pack(fill="both")

        # ---SEMESTER-FRAME---
        # Semester-Label
        semester_label = ctk.CTkLabel(
            semester_frame,
            text="Semester:",
            font=INFO,
            justify="left",
            bg_color="transparent",
        )
        semester_label.grid(row=0, column=0, sticky="w", padx=5)

        # Semester-Icons
        relative_balken_frame = ctk.CTkFrame(
            semester_frame, fg_color="transparent", height=30
        )
        relative_balken_frame.grid(
            row=1, column=0, columnspan=1, sticky="ew", padx=0, pady=4
        )

        balken_frame = ctk.CTkFrame(relative_balken_frame, fg_color="transparent")
        balken_frame.place(relwidth=self.controller.get_semester_amount(), relheight=1)

        semester_frame.grid_columnconfigure(0, weight=1)

        for semester in self.data["semester"]:
            if semester["status"] == "SemesterStatus.ZURUECKLIEGEND":
                color = GRUEN
            elif (
                semester["status"] == "SemesterStatus.AKTUELL"
                and self.data["exmatrikulationsdatum"] is None
            ):
                color = GELB
            elif (
                semester["status"] == "SemesterStatus.AKTUELL"
                and self.data["exmatrikulationsdatum"] is not None
                and self.data["erarbeitete_ects"] != self.data["gesamt_ects"]
            ):
                color = ROT
            elif (
                semester["status"] == "SemesterStatus.AKTUELL"
                and self.data["erarbeitete_ects"] == self.data["gesamt_ects"]
            ):
                color = GRUEN
            elif semester["status"] == "SemesterStatus.ZUKUENFTIG":
                color = GRAU
            else:
                raise ValueError(
                    f"semester hat keinen gültigen Status: {semester['status']}"
                )
            index = semester["nummer"] - 1

            balken_frame.grid_columnconfigure(
                index=index, weight=1, uniform="semester_balken"
            )
            balken = ctk.CTkLabel(
                balken_frame, fg_color=color, corner_radius=8, height=26, text=""
            )
            balken.grid(row=1, column=index, sticky="ew", padx=0)
            ToolTip(
                balken,
                text=f"Semester {semester['nummer']}\nBeginn: {from_iso_to_ddmmyyyy(semester['beginn'])}\nEnde: {from_iso_to_ddmmyyyy(semester['ende'])}",
            )

        # ---MODULE-FRAME---
        # Module-Label
        module_label = ctk.CTkLabel(
            module_frame,
            text="Module:",
            font=INFO,
            justify="left",
            bg_color="transparent",
        )
        module_label.grid(row=0, column=0, sticky="w", padx=5)

        # Enrollment-Icons
        size = 16
        if self.data["modulanzahl"] < 39:
            size = 26
        elif self.data["modulanzahl"] < 49:
            size = 20
        elif self.data["modulanzahl"] < 56:
            size = 16
        else:
            size = 12

        ENROLLMENTICONS = ctk.CTkFont(
            family="Material Symbols Sharp", size=size, weight="normal", slant="roman"
        )

        one_frame = ctk.CTkFrame(module_frame, fg_color="transparent")
        one_frame.grid(row=1, column=0, sticky="ew", padx=0, pady=4)

        module_frame.grid_columnconfigure(0, weight=1)

        for i in range(self.data["modulanzahl"]):
            if self.data["enrollments"] != [] and i < len(self.data["enrollments"]):
                enrollment = self.data["enrollments"][i]
                status = str(enrollment["status"])
                if status == "ABGESCHLOSSEN":
                    one_frame.grid_columnconfigure(i, weight=1, uniform="modul_icons")
                    icon = ctk.CTkButton(
                        one_frame,
                        font=ENROLLMENTICONS,
                        text="check_circle",
                        text_color=GRUEN,
                        fg_color="transparent",
                        hover_color=BACKGROUND,
                        border_width=0,
                        border_spacing=0,
                        corner_radius=0,
                        command=lambda e_id=enrollment["id"]: self.after(
                            0, self.go_to_enrollment, e_id
                        ),
                    )
                    icon.grid(row=1, column=i, sticky="nsew", padx=0)
                    ToolTip(
                        icon,
                        text=f"{enrollment['modul_name']}\nBegonnen: {from_iso_to_ddmmyyyy(enrollment['einschreibe_datum'])}\nAbgeschlossen: {from_iso_to_ddmmyyyy(enrollment['end_datum'])}\nNote: {enrollment['enrollment_note']}\nStatus: Abgeschlossen",
                    )
                elif status == "IN_BEARBEITUNG":
                    one_frame.grid_columnconfigure(i, weight=1, uniform="modul_icons")
                    icon = ctk.CTkButton(
                        one_frame,
                        font=ENROLLMENTICONS,
                        text="pending",
                        text_color=GELB,
                        fg_color="transparent",
                        hover_color=BACKGROUND,
                        border_width=0,
                        border_spacing=0,
                        corner_radius=0,
                        command=lambda e_id=enrollment["id"]: self.after(
                            0, self.go_to_enrollment, e_id
                        ),
                    )
                    icon.grid(row=1, column=i, sticky="nsew", padx=0)
                    ToolTip(
                        icon,
                        text=f"{enrollment['modul_name']}\nBegonnen: {from_iso_to_ddmmyyyy(enrollment['einschreibe_datum'])}\nStatus: in Bearbeitung",
                    )
                elif status == "NICHT_BESTANDEN":
                    one_frame.grid_columnconfigure(i, weight=1, uniform="modul_icons")
                    icon = ctk.CTkButton(
                        one_frame,
                        font=ENROLLMENTICONS,
                        text="cancel",
                        text_color=ROT,
                        fg_color="transparent",
                        hover_color=BACKGROUND,
                        border_width=0,
                        border_spacing=0,
                        corner_radius=0,
                        command=lambda e_id=enrollment["id"]: self.after(
                            0, self.go_to_enrollment, e_id
                        ),
                    )
                    icon.grid(row=1, column=i, sticky="nsew", padx=0)
                    ToolTip(
                        icon,
                        text=f"{enrollment['modul_name']}\nBegonnen: {from_iso_to_ddmmyyyy(enrollment['einschreibe_datum'])}\nStatus: Nicht bestanden",
                    )
                else:
                    raise ValueError(f"Enrollment hat keinen gültigen Status: {status}")
            else:
                one_frame.grid_columnconfigure(i, weight=1, uniform="modul_icons")
                icon = HoverButton(
                    one_frame,
                    font=ENROLLMENTICONS,
                    text="radio_button_unchecked",
                    text_color=GRAU,
                    defaulttext="radio_button_unchecked",
                    defaultcolor=GRAU,
                    hovertext="add_circle",
                    hovercolor=BLAU,
                    fg_color="transparent",
                    border_width=0,
                    border_spacing=0,
                    corner_radius=0,
                    command=lambda: self.after(0, self.go_to_add_enrollment),
                )
                icon.grid(row=1, column=i, sticky="nsew", padx=0)
                if self.data["exmatrikulationsdatum"]:
                    icon.configure(state="disabled", hover=False)

        # ---TEXT-MODULE-FRAME---
        # Module-vertikal-Label
        canvas = ctk.CTkCanvas(
            text_module_frame,
            width=100,
            height=120,
            bg=BACKGROUND,
            highlightthickness=0,
            bd=0,
        )
        canvas.grid(row=0, column=0, rowspan=3, padx=10)
        canvas.create_text(30, 60, text="Module", angle=90, font=H2italic, fill="black")

        # STATS-Label
        abgeschlossen_label = ctk.CTkLabel(
            text_module_frame,
            font=H2,
            text_color=GRUEN,
            text=f"Abgeschlossen: {self.data['abgeschlossen']}",
            justify="right",
        )
        in_bearbeitung_label = ctk.CTkLabel(
            text_module_frame,
            font=H2,
            text_color=GELB,
            text=f"In Bearbeitung: {self.data['in_bearbeitung']}",
            justify="right",
        )
        ausstehend_label = ctk.CTkLabel(
            text_module_frame,
            font=H2,
            text_color="black",
            text=f"Ausstehend: {self.data['ausstehend']}",
            justify="right",
        )
        nicht_bestanden_label = ctk.CTkLabel(
            text_module_frame,
            font=H2,
            text_color=ROT,
            text=f"Nicht bestanden: {self.data['nicht_bestanden']}",
            justify="right",
        )

        abgeschlossen_label.grid(row=0, column=1, sticky="e", pady=0, padx=10)
        in_bearbeitung_label.grid(row=1, column=1, sticky="e", pady=0, padx=10)
        ausstehend_label.grid(row=2, column=1, sticky="e", pady=0, padx=10)
        if self.data["nicht_bestanden"] > 0:
            nicht_bestanden_label.grid(row=3, column=1, sticky="e", pady=0, padx=10)

        # ---ECTS-FRAME---
        ects_color = GRUEN
        if (
            self.data["exmatrikulationsdatum"] is not None
            and self.data["erarbeitete_ects"] != self.data["gesamt_ects"]
        ):
            # Exmatrikuliert und nicht alle ECTS-Punkte erreicht
            ects_color = ROT

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
            text=f"{self.data['erarbeitete_ects']}",
        )
        ects_max_label = ctk.CTkLabel(
            ects_frame,
            font=H1notitalic,
            text_color=GRAU,
            text=f"/{self.data['gesamt_ects']}",
        )

        ects_label.pack()
        ects_max_label.pack(side="right", anchor="e")
        ects_erreicht_label.pack(side="right", anchor="e")

        # ---NOTEN-FRAME---
        if self.data["notendurchschnitt"] != "--":
            if self.data["notendurchschnitt"] > self.data["zielnote"]:
                noten_color = ROT
            else:
                noten_color = GRUEN
        else:
            noten_color = "black"

        ds_text_label = ctk.CTkLabel(
            noten_frame,
            font=H2,
            text_color="black",
            text="Dein \nNotendurchschnitt:",
            justify="left",
        )
        ds_note_label = ctk.CTkLabel(
            noten_frame,
            font=H1notitalic,
            text_color=noten_color,
            text=f"{self.data['notendurchschnitt']}",
        )
        ziel_text_label = ctk.CTkLabel(
            noten_frame,
            font=H2,
            text_color="black",
            text="Dein \nZiel:",
            justify="left",
        )
        ziel_note_label = ctk.CTkLabel(
            noten_frame,
            font=H1notitalic,
            text_color="black",
            text=f"{self.data['zielnote']}",
        )
        ds_text_label.pack(side="left", padx=10)
        ds_note_label.pack(side="left", padx=20)
        ziel_text_label.pack(side="left", padx=10)
        ziel_note_label.pack(side="left", padx=20)

    def get_position(self, progress, old_min=0.2, old_max=0.8):
        value = (progress - old_min) / (old_max - old_min)
        return max(0, min(1, value))

    def menu_on_button(self):
        if self.menu_popup and self.menu_popup.winfo_exists():
            self.menu_popup.destroy()
            self.menu_popup = None
        else:
            self.open_menu(anchor=self.menu_button)

    def open_menu(self, anchor):
        top = ctk.CTkToplevel(self)
        self.menu_popup = top
        top.overrideredirect(True)
        top.transient(self.winfo_toplevel())
        top.attributes("-topmost", True)
        top.bind("<FocusOut>", lambda e: self.close_menu())

        bx = anchor.winfo_rootx()
        by = anchor.winfo_rooty()
        bw = anchor.winfo_width()
        bh = anchor.winfo_height()

        popup_w, popup_h = 180, 160

        x = bx + bw - popup_w
        y = by + bh

        sw = top.winfo_screenwidth()
        sh = top.winfo_screenheight()

        if x < 0:
            x = 0
        if x + popup_w > sw:
            x = max(0, sw - popup_w)
        if y + popup_h > sh:
            y = max(0, by - popup_h)

        top.geometry(f"{popup_w}x{popup_h}+{x}+{y}")

        values = {
            "Profil bearbeiten": self.go_to_settings,
            "Du wurdest exmatrikuliert?": self.go_to_ex,
            "Ziele anpassen": self.go_to_ziele,
            "Über Dashboard": self.go_to_ueber,
            "Abmelden": self.logout,
        }

        for key, value in values.items():
            button = ctk.CTkButton(
                top,
                # border_spacing=1,
                fg_color=BACKGROUND,
                hover_color="gray95",
                border_color="black",
                border_width=1,
                text_color="black",
                text=key,
                command=lambda v=value: (self.close_menu(), self.after(0, v())),
            )
            button.pack(fill="both", expand=True, pady=1, padx=1)

    def close_menu(self):
        if self.menu_popup and self.menu_popup.winfo_exists():
            self.menu_popup.destroy()
        self.menu_popup = None

    def logout(self):
        if self.menu_popup and self.menu_popup.winfo_exists():
            self.menu_popup.destroy()
            self.menu_popup = None
        self.controller.logout()
        self.after(0, self.go_to_login)


class AddEnrollmentFrame(ctk.CTkScrollableFrame):
    def __init__(
        self, master, controller: Controller, go_to_dashboard, go_to_enrollment
    ):
        super().__init__(master, fg_color="transparent")

        self.controller = controller
        self.go_to_dashboard = go_to_dashboard
        self.go_to_enrollment = go_to_enrollment

        # FONTS
        H2italic = ctk.CTkFont(
            family="Segoe UI", size=32, weight="normal", slant="italic"
        )

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        # self.grid_rowconfigure(2, weight=1)
        # self.grid_rowconfigure(3, weight=1)

        header_frame = ctk.CTkFrame(
            self, fg_color=BACKGROUND, border_color="black", border_width=2
        )
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        # SETTINGS FRAME ÜBERSCHRIFT
        header_frame.grid_columnconfigure(0, weight=1)
        header_frame.grid_columnconfigure(1, weight=0)

        header_ueber_label = ctk.CTkLabel(
            header_frame, text="Zu neuem Modul anmelden", font=H2italic, justify="left"
        )
        header_ueber_label.grid(row=0, sticky="nw", padx=10, pady=10)

        header_close_button = ctk.CTkButton(
            header_frame,
            text="Close",
            font=master.fonts.ICONS,
            width=10,
            fg_color="transparent",
            text_color="black",
            hover_color="gray95",
            # border_color="black",
            command=lambda: self.after(0, self.go_to_dashboard),
        )
        header_close_button.grid(row=0, column=1, padx=(0, 2), pady=(2, 0), sticky="ne")

        ae_frame = ctk.CTkFrame(
            self, fg_color=BACKGROUND, border_color="black", border_width=2
        )
        ae_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        ae_frame.grid_columnconfigure(0, weight=1)
        ae_frame.grid_columnconfigure(1, weight=1)

        left_frame = ctk.CTkFrame(ae_frame, fg_color=BACKGROUND)
        left_frame.grid(row=0, column=0, padx=5, pady=5)
        right_frame = ctk.CTkFrame(ae_frame, fg_color=BACKGROUND)
        right_frame.grid(row=0, column=1, padx=5, pady=5)

        # Wie heißt dieses Modul?
        modul_name_label = ctk.CTkLabel(
            left_frame, text="Wie heißt dieses Modul?", justify="left"
        )
        modul_name_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.modul_name_entry = ctk.CTkEntry(
            left_frame,
            placeholder_text="Modulname",
        )
        self.modul_name_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.modul_name_entry.focus()
        # Wie ist der Modul-Code?
        modul_code_label = ctk.CTkLabel(left_frame, text="Wie lautet der Modul-Code?")
        modul_code_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.modul_code_entry = ctk.CTkEntry(left_frame, placeholder_text="Modul-Code")
        self.modul_code_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        ToolTip(
            self.modul_code_entry,
            text="Jedes Modul hat einen eindeutigen Identifikationscode",
        )
        # Wie viele ECTS-Punkte hat dieses Modul?
        modul_ects_label = ctk.CTkLabel(
            left_frame, text="Wie viele ECTS-Punkte hat dieses Modul?"
        )
        modul_ects_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.modul_ects_entry = ctk.CTkEntry(left_frame, placeholder_text="z.B. 5")
        self.modul_ects_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        self.label_no_int = ctk.CTkLabel(left_frame, text="", text_color=ROT)
        self.label_no_int.grid(
            row=3, column=0, columnspan=2, padx=5, pady=2, sticky="ew"
        )

        # Wie viele Prüfungsleistungen hat dieses Modul?
        pl_label = ctk.CTkLabel(
            left_frame, text="Wie viele Prüfungsleistungen hat dieses Modul?"
        )
        pl_label.grid(row=4, column=0, padx=5, pady=5, sticky="w")
        pl_values = [str(i) for i in range(1, 20)]
        self.pl_anzahl_entry = ctk.CTkOptionMenu(
            left_frame,
            values=pl_values,
            text_color="black",
            fg_color="gray95",
            button_color="gray95",
            button_hover_color="gray85",
        )
        self.pl_anzahl_entry.grid(row=4, column=1, padx=5, pady=5, sticky="ew")

        # Wann hast du mit diesem Modul begonnen?
        self.selected_startdatum = tk.StringVar(value="Noch kein Datum ausgewählt")

        self.label_startdatum = ctk.CTkLabel(
            left_frame, text="Wann hast du mit diesem Modul begonnen?"
        )
        self.label_startdatum.grid(row=5, column=0, padx=5, pady=5, sticky="w")
        self.button_startdatum = ctk.CTkButton(
            left_frame,
            text="Startdatum auswählen",
            text_color="black",
            fg_color="transparent",
            border_color="black",
            border_spacing=2,
            border_width=2,
            hover_color="gray95",
            command=self.start_datum_calendar_at_button,
        )
        self.button_startdatum.grid(
            row=6, column=0, columnspan=2, padx=5, pady=5, sticky="ew"
        )

        self.label_startdatum_variable = ctk.CTkLabel(
            left_frame, textvariable=self.selected_startdatum
        )
        self.label_startdatum_variable.grid(row=5, column=1, padx=5, pady=5, sticky="e")

        self.selected_startdatum_real: str

        # RIGHT FRAME
        # Welcher Kurs oder welche Kurse müssen absolviert werden?
        kurs_name_label = ctk.CTkLabel(
            right_frame, text="Welcher Kurs oder welche Kurse müssen absolviert werden?"
        )
        kurs_name_label.pack(pady=10)

        self.kurse_eingabe_feld = DynamicEntries(
            right_frame, initial_rows=1, max_rows=10
        )
        self.kurse_eingabe_feld.pack(pady=10)

        # Submit-Button
        submit_button = ctk.CTkButton(
            ae_frame,
            text="Weiter",
            text_color="black",
            fg_color="transparent",
            border_color="black",
            border_spacing=2,
            border_width=2,
            hover_color="gray95",
            command=self.on_submit,
        )
        submit_button.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
        self.leere_felder_label = ctk.CTkLabel(ae_frame, text="", text_color=ROT)
        self.leere_felder_label.grid(
            row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=5
        )

    def on_submit(self):
        # validiere ECTS-Feld
        if self.validate_ects(self.modul_ects_entry.get().strip()):
            self.selected_modul_ects = int(self.modul_ects_entry.get().strip())
        else:
            return

        # validiere user-input
        self.list_for_validation = [
            self.modul_name_entry.get(),
            self.modul_code_entry.get(),
        ]
        if not self.validate_entries(liste=self.list_for_validation):
            return

        self.entry_kurse_list_of_dicts = self.kurse_eingabe_feld.get_values()
        if self.entry_kurse_list_of_dicts == []:
            return

        try:
            self.selected_startdatum_str = self.selected_startdatum_real
        except AttributeError:
            self.leere_felder_label.configure(text="Startdatum nicht ausgewählt.")
            return

        # user-input validiert, speicher eingaben
        self.selected_modul_name = self.modul_name_entry.get()
        self.selected_modul_code = self.modul_code_entry.get()
        self.selected_kurse_list_of_dicts = self.entry_kurse_list_of_dicts
        self.selected_pl_anzahl = int(self.pl_anzahl_entry.get())

        enrollment_cache = {
            "modul_name": self.selected_modul_name,
            "modul_code": self.selected_modul_code,
            "modul_ects": self.selected_modul_ects,
            "kurse_list": self.selected_kurse_list_of_dicts,
            "pl_anzahl": self.selected_pl_anzahl,
            "startdatum": self.selected_startdatum_str,
        }

        if self.controller.check_if_already_enrolled(enrollment_cache=enrollment_cache):
            self.leere_felder_label.configure(
                text="Du bist schon in dieses Modul eingeschrieben"
            )

        enrollment_dict = self.controller.erstelle_enrollment(
            enrollment_cache=enrollment_cache
        )

        self.after(0, lambda: self.go_to_enrollment(enrollment_dict["id"]))

    def validate_ects(self, ects):
        try:
            number = int(ects)
        except ValueError:
            self.label_no_int.configure(text="Muss eine (Ganz-) Zahl sein")
            return False

        if number:
            if number > 0 and number <= 50:
                return True
        else:
            self.label_no_int.configure(text="Zahl muss zwischen 1 und 50 liegen")
            return False

    def validate_entries(self, liste):
        for value in liste:
            if str(value).strip() == "":
                self.leere_felder_label.configure(text="Etwas ist nicht ausgefüllt.")
                return False
            else:
                pass
        return True

    def start_datum_calendar_at_button(self):
        self.start_datum_calendar(anchor=self.button_startdatum)

    def start_datum_calendar(self, anchor):
        top = ctk.CTkToplevel(self)
        top.overrideredirect(True)
        top.transient(self.winfo_toplevel())
        top.attributes("-topmost", True)
        top.grab_set()
        top.bind("<FocusOut>", lambda e: top.destroy())

        bx = anchor.winfo_rootx()
        by = anchor.winfo_rooty()
        bw = anchor.winfo_width()
        bh = anchor.winfo_height()

        x = bx
        y = by + bh

        popup_w, popup_h = 250, 250
        sw = top.winfo_screenwidth()
        sh = top.winfo_screenheight()

        if x + popup_w > sw:
            x = max(0, bx + bw - popup_w)
        if y + popup_h > sh:
            y = max(0, by - popup_h)

        top.geometry(f"{popup_w}x{popup_h}+{x}+{y}")

        mindate_start = self.controller.get_startdatum()
        maxdate_start = datetime.date.today()

        cal_start = Calendar(
            top,
            font="SegoeUI 12",
            selectmode="day",
            locale="de_DE",
            date_pattern="yyyy-mm-dd",
            mindate=mindate_start,
            maxdate=maxdate_start,
            showweeknumbers=False,
            selectforeground=GELB,
            normalforeground=BLAU,
            weekendforeground=BLAU,
            weekendbackground="gray90",
            background="gray95",
            foreground="black",
            selectbackground=DUNKELBLAU,
            headersbackground="gray95",
            headersforeground="black",
            disabledforeground="gray50",
            disabledbackground="gray80",
        )

        cal_start.pack(fill="both", expand=True)

        def save():
            self.selected_startdatum.set(from_iso_to_ddmmyyyy(cal_start.get_date()))
            self.selected_startdatum_real = cal_start.get_date()
            top.destroy()

        self.save_button_start = ctk.CTkButton(
            top,
            text="ok",
            text_color="black",
            fg_color="transparent",
            border_color="black",
            border_spacing=2,
            border_width=2,
            hover_color="gray95",
            command=save,
        )
        self.save_button_start.pack(pady=5)


class EnrollmentFrame(ctk.CTkScrollableFrame):
    def __init__(
        self,
        master,
        controller: Controller,
        go_to_dashboard,
        go_to_pl,
        enrollment_id,
    ):
        super().__init__(master, fg_color="transparent")

        self.controller = controller
        self.go_to_dashboard = go_to_dashboard
        self.go_to_pl = go_to_pl
        self.enrollment_id = enrollment_id

        self.enrollment_data = self.controller.get_enrollment_data(self.enrollment_id)

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)

        modul_frame = ctk.CTkFrame(
            self, fg_color=BACKGROUND, border_color="black", border_width=2
        )
        modul_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        kurse_frame = ctk.CTkFrame(
            self, fg_color=BACKGROUND, border_color="black", border_width=2
        )
        kurse_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        pl_frame = ctk.CTkFrame(
            self, fg_color=BACKGROUND, border_color="black", border_width=2
        )
        pl_frame.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)
        pl_frame.grid_columnconfigure(0, weight=1)

        status_frame = ctk.CTkFrame(
            self, fg_color=BACKGROUND, border_color="black", border_width=2
        )
        status_frame.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)

        noten_frame = ctk.CTkFrame(
            self, fg_color=BACKGROUND, border_color="black", border_width=2
        )
        noten_frame.grid(row=2, column=1, sticky="nsew", padx=5, pady=5)

        eingeschrieben_frame = ctk.CTkFrame(
            self, fg_color=BACKGROUND, border_color="black", border_width=2
        )
        eingeschrieben_frame.grid(row=3, column=0, sticky="nsew", padx=5, pady=5)

        abgeschlossen_frame = ctk.CTkFrame(
            self, fg_color=BACKGROUND, border_color="black", border_width=2
        )
        abgeschlossen_frame.grid(row=3, column=1, sticky="nsew", padx=5, pady=5)

        # FONTS
        H2italic = ctk.CTkFont(
            family="Segoe UI", size=32, weight="normal", slant="italic"
        )
        H3 = ctk.CTkFont(family="Segoe UI", size=22, weight="normal", slant="roman")
        INFO = ctk.CTkFont(family="Segoe UI", size=16, weight="normal", slant="roman")

        self.grid_columnconfigure(0, weight=1, uniform="half")
        self.grid_columnconfigure(1, weight=1, uniform="half")

        # MODUL FRAME ÜBERSCHRIFT
        modul_frame.grid_columnconfigure(0, weight=1)
        modul_frame.grid_columnconfigure(1, weight=0)

        modul_ueber_label = ctk.CTkLabel(
            modul_frame, text="MODUL:", font=H2italic, justify="left"
        )
        modul_ueber_label.grid(row=0, sticky="nw", padx=10, pady=10)
        modul_name_label = MultiLineLabel(
            modul_frame,
            width=85,
            text=f"{self.enrollment_data['modul_name']}",
            font=H3,
            justify="left",
        )
        modul_name_label.grid(row=1, sticky="nw", padx=10, pady=10)
        modul_code_label = ctk.CTkLabel(
            modul_frame,
            text=f"{self.enrollment_data['modul_code']}",
            font=INFO,
            justify="left",
        )
        modul_code_label.grid(row=2, column=0, sticky="nw", padx=10, pady=10)

        modul_close_button = ctk.CTkButton(
            modul_frame,
            text="Close",
            font=master.fonts.ICONS,
            width=10,
            fg_color="transparent",
            text_color="black",
            hover_color="gray95",
            # border_color="black",
            # border_width=2,
            command=lambda: self.after(0, self.go_to_dashboard),
        )
        modul_close_button.grid(row=0, column=1, padx=(0, 2), pady=(2, 0), sticky="ne")

        modul_ects_label = ctk.CTkLabel(
            modul_frame,
            text=f"{self.enrollment_data['modul_ects']} ECTS-Punkte",
            font=INFO,
            justify="right",
        )
        modul_ects_label.grid(row=2, column=1, sticky="e", padx=10, pady=10)

        # KURSE FRAME
        kurse_ueber_label = ctk.CTkLabel(
            kurse_frame, text="KURSE:", font=H2italic, justify="left"
        )
        kurse_ueber_label.grid(row=0, sticky="nw", padx=10, pady=10)

        row_counter = 1
        for kurs in self.enrollment_data["kurse"]:
            kurs_label = MultiLineLabel(
                master=kurse_frame,
                width=50,
                text=f"{kurs['name']}",
                font=INFO,
                justify="left",
            )
            kurs_label.grid(row=row_counter, padx=10, pady=5, sticky="w")
            row_counter += 1

        # PL FRAME
        # Überschrift
        pl_ueber_label = ctk.CTkLabel(
            pl_frame, text="PRÜFUNGSLEISTUNGEN:", font=H2italic, justify="left"
        )
        pl_ueber_label.grid(row=0, sticky="nw", padx=10, pady=10)
        # Titelzeile
        pl_tabelle_title_frame = ctk.CTkFrame(
            pl_frame, fg_color=BACKGROUND, border_color="gray95", border_width=2
        )
        pl_tabelle_title_frame.grid(row=1, sticky="ew", padx=4, pady=4)
        for column, txt in enumerate(
            ["Nr.", "1. Versuch", "2. Versuch", "3. Versuch", "Gewichtung:"]
        ):
            label = ctk.CTkLabel(
                pl_tabelle_title_frame, text=txt, font=INFO, justify="left"
            )
            label.grid(
                row=0,
                column=column,
                padx=(5 if column == 0 else 2, 5),
                pady=4,
                sticky="w" if column == 0 else "e",
            )
            pl_tabelle_title_frame.grid_columnconfigure(
                column,
                weight=1 if column > 0 else 0,
                uniform="outside_frame" if column > 0 and column < 4 else "",
            )

        pls = self.enrollment_data["pruefungsleistungen"]
        anzahl = self.enrollment_data["anzahl_pruefungsleistungen"]

        pls_dict: dict[int, list[dict]] = {}
        for pl in pls:
            pls_dict.setdefault(pl["teilpruefung"], []).append(pl)

        zustand = ["offen", "bestanden", "nicht_bestanden", "deaktiviert"]
        zustand_letzte_pl = zustand[0]

        for i in range(anzahl):
            versuche = pls_dict.get(i, [])
            row_frame = ctk.CTkFrame(
                pl_frame, fg_color=BACKGROUND, border_color="gray95", border_width=2
            )
            row_frame.grid(row=i + 2, sticky="ew", padx=4, pady=4)
            for column in range(5):
                row_frame.grid_columnconfigure(column, weight=1 if column > 0 else 0)

            index_label = ctk.CTkLabel(
                row_frame,
                text=f"{i + 1}.",
                font=INFO,
                justify="left",
            )
            index_label.grid(row=0, column=0, padx=5, pady=2, sticky="w")

            gewicht = versuche[0]["teilpruefung_gewicht"] if versuche else "--"
            gewicht_label = ctk.CTkLabel(
                row_frame,
                text=f"{gewicht}",
                font=INFO,
                justify="right",
            )
            gewicht_label.grid(row=0, column=4, padx=10, pady=2, sticky="e")

            for v in range(1, 4):
                versuch = next((pl for pl in versuche if pl["versuch"] == v), None)
                if versuch:
                    if versuch["note"] is None and (
                        v == 1 or zustand_letzte_pl == "nicht_bestanden"
                    ):
                        add_pl_button = HoverButton(
                            row_frame,
                            width=10,
                            fg_color="transparent",
                            hover_color="gray95",
                            hovercolor=BLAU,
                            hovertext="add_box",
                            defaultcolor="black",
                            defaulttext="check_box_outline_blank",
                            text="check_box_outline_blank",
                            text_color="black",
                            font=master.fonts.ICONS,
                            command=lambda pl_id=versuch["id"],
                            e_id=self.enrollment_id: self.after(
                                0, self.go_to_pl, pl_id, e_id
                            ),
                        )
                        add_pl_button.grid(
                            row=0,
                            column=v,
                            pady=2,
                        )
                        zustand_letzte_pl = zustand[0]
                    elif versuch["note"] is None and (
                        zustand_letzte_pl == "offen"
                        or zustand_letzte_pl == "bestanden"
                        or zustand_letzte_pl == "deaktiviert"
                    ):
                        disabled_button = ctk.CTkButton(
                            row_frame,
                            width=10,
                            fg_color="transparent",
                            hover_color="gray95",
                            text_color=GRAU,
                            text="Select",
                            font=master.fonts.ICONS,
                            state="disabled",
                        )
                        disabled_button.grid(
                            row=0,
                            column=v,
                            pady=2,
                        )
                        zustand_letzte_pl = zustand[3]
                    elif versuch["ist_bestanden"]:
                        pl_bestanden_button = ctk.CTkButton(
                            row_frame,
                            width=10,
                            fg_color="transparent",
                            hover_color="gray95",
                            text_color=GRUEN,
                            text="select_check_box",
                            font=master.fonts.ICONS,
                            command=lambda pl_id=versuch["id"],
                            e_id=self.enrollment_id: self.after(
                                0, self.go_to_pl, pl_id, e_id
                            ),
                        )
                        pl_bestanden_button.grid(
                            row=0,
                            column=v,
                            pady=2,
                        )
                        ToolTip(
                            pl_bestanden_button,
                            text=f"Note: {versuch['note']}\nDatum: {from_iso_to_ddmmyyyy(versuch['datum'])}",
                        )
                        zustand_letzte_pl = zustand[1]
                    elif versuch["note"] is not None and not versuch["ist_bestanden"]:
                        pl_nicht_bestanden_button = ctk.CTkButton(
                            row_frame,
                            width=10,
                            fg_color="transparent",
                            hover_color="gray95",
                            text_color=ROT,
                            text="disabled_by_default",
                            font=master.fonts.ICONS,
                            command=lambda pl_id=versuch["id"],
                            e_id=self.enrollment_id: self.after(
                                0, self.go_to_pl, pl_id, e_id
                            ),
                        )
                        pl_nicht_bestanden_button.grid(
                            row=0,
                            column=v,
                            pady=2,
                        )
                        ToolTip(
                            pl_nicht_bestanden_button,
                            text=f"Note: {versuch['note']}\nDatum: {from_iso_to_ddmmyyyy(versuch['datum'])}",
                        )
                        zustand_letzte_pl = zustand[2]

        # STATUS FRAME
        if str(self.enrollment_data["status"]) == "IN_BEARBEITUNG":
            statustxt = "in Bearbeitung"
            status_color = GELB
        elif str(self.enrollment_data["status"]) == "ABGESCHLOSSEN":
            statustxt = "abgeschlossen"
            status_color = GRUEN
        elif str(self.enrollment_data["status"]) == "NICHT_BESTANDEN":
            statustxt = "nicht bestanden"
            status_color = ROT
        else:
            statustxt = "nicht auslesbar"
            status_color = "black"
        status_label = ctk.CTkLabel(
            status_frame,
            text=f"Status: {statustxt}",
            font=INFO,
            text_color=status_color,
        )
        status_label.pack(
            pady=4,
        )

        # NOTEN FRAME
        if self.enrollment_data["enrollment_note"] is None:
            note = "--"
        else:
            note = self.enrollment_data["enrollment_note"]

        noten_label = ctk.CTkLabel(
            noten_frame,
            text=f"Deine Note: {note}",
            font=INFO,
        )
        noten_label.pack(
            pady=4,
        )

        # EINGESCHRIEBEN FRAME
        eingeschrieben_label = ctk.CTkLabel(
            eingeschrieben_frame,
            text=f"Eingeschrieben am: {from_iso_to_ddmmyyyy(self.enrollment_data['einschreibe_datum'])}",
            font=INFO,
        )
        eingeschrieben_label.pack(
            pady=4,
        )

        # ABGESCHLOSSEN FRAME
        if self.enrollment_data["end_datum"] is None:
            abgeschlossen_datum = "--"
        else:
            abgeschlossen_datum = self.enrollment_data["end_datum"]

        abgeschlossen_label = ctk.CTkLabel(
            abgeschlossen_frame,
            text=f"Abgeschlossen am: {from_iso_to_ddmmyyyy(abgeschlossen_datum)}",
            font=INFO,
        )
        abgeschlossen_label.pack(
            pady=4,
        )


class PLAddFrame(ctk.CTkFrame):
    def __init__(self, master, controller: Controller, go_to_enrollment, pl_id, e_id):
        super().__init__(master, fg_color="transparent")

        self.controller = controller
        self.go_to_enrollment = go_to_enrollment
        self.pl_id = pl_id
        self.enrollment_id = e_id

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)

        self.pl_data = self.controller.get_pl_with_id(self.enrollment_id, self.pl_id)
        if self.pl_data == {}:
            raise UnboundLocalError

        self.enrollment_data = self.controller.get_enrollment_data(self.enrollment_id)

        # FONTS
        H1 = ctk.CTkFont(family="Segoe UI", size=84, weight="normal", slant="italic")
        H1notitalic = ctk.CTkFont(
            family="Segoe UI", size=84, weight="normal", slant="roman"
        )
        H2 = ctk.CTkFont(family="Segoe UI", size=32, weight="normal", slant="roman")
        H2italic = ctk.CTkFont(
            family="Segoe UI", size=32, weight="normal", slant="italic"
        )
        H3 = ctk.CTkFont(family="Segoe UI", size=22, weight="normal", slant="roman")

        pl_frame = ctk.CTkFrame(
            self, fg_color=BACKGROUND, border_color="black", border_width=2
        )
        pl_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        # PL FRAME ÜBERSCHRIFT
        pl_frame.grid_columnconfigure(0, weight=1)
        pl_frame.grid_columnconfigure(1, weight=0)

        pl_ueber_label = ctk.CTkLabel(
            pl_frame, text="PRÜFUNGSLEISTUNG:", font=H2italic, justify="left"
        )
        pl_ueber_label.grid(row=0, sticky="nw", padx=10, pady=10)
        pl_modul_label = ctk.CTkLabel(
            pl_frame,
            text=f"Modul: {self.enrollment_data['modul_name']}",
            font=H3,
            justify="left",
        )
        pl_modul_label.grid(row=1, sticky="nw", padx=10, pady=10)
        pl_name_label = MultiLineLabel(
            pl_frame,
            width=85,
            text=f"Prüfung: {int(self.pl_data['teilpruefung']) + 1}, Versuch: {self.pl_data['versuch']}",
            font=H3,
            justify="left",
        )
        pl_name_label.grid(row=2, sticky="nw", padx=10, pady=10)

        pl_close_button = ctk.CTkButton(
            pl_frame,
            text="Close",
            font=master.fonts.ICONS,
            width=10,
            fg_color="transparent",
            text_color="black",
            hover_color="gray95",
            # border_color="black",
            # border_width=2,
            command=lambda: self.after(0, self.go_to_enrollment, self.enrollment_id),
        )
        pl_close_button.grid(row=0, column=1, padx=(0, 2), pady=(2, 0), sticky="ne")

        if self.pl_data["note"] is None:
            pl_add_frame = ctk.CTkFrame(
                self, fg_color=BACKGROUND, border_color="black", border_width=2
            )
            pl_add_frame.grid(
                row=1, column=0, columnspan=2, sticky="new", padx=5, pady=5
            )

            pl_add_pl_label = ctk.CTkLabel(
                pl_add_frame,
                text="Prüfungsleistung hinzufügen:",
                font=H2italic,
            )
            pl_add_pl_label.pack(pady=10)

            pl_add_note_label = ctk.CTkLabel(pl_add_frame, text="Deine Note:")
            pl_add_note_label.pack(pady=10)

            noten = [str(i / 10) for i in range(10, 61)]
            self.pl_add_note_entry = ctk.CTkOptionMenu(
                pl_add_frame,
                values=noten,
                text_color="black",
                fg_color="gray95",
                button_color="gray95",
                button_hover_color="gray85",
            )
            self.pl_add_note_entry.pack(pady=5)

            self.selected_pl_datum = tk.StringVar(value="Noch kein Datum ausgewählt")

            pl_add_datum_label = ctk.CTkLabel(
                pl_add_frame, text="Wann hast Du die Prüfung abgegeben?"
            )
            pl_add_datum_label.pack(pady=10)
            self.pl_button_datum = ctk.CTkButton(
                pl_add_frame,
                text="Prüfungsdatum auswählen",
                text_color="black",
                fg_color="transparent",
                border_color="black",
                border_spacing=2,
                border_width=2,
                hover_color="gray95",
                command=self.pl_datum_calendar_at_button,
            )
            self.pl_button_datum.pack(pady=10)

            self.label_startdatum_variable = ctk.CTkLabel(
                pl_add_frame, textvariable=self.selected_pl_datum
            )
            self.label_startdatum_variable.pack(pady=10)

            self.selected_pl_datum_real: str

            # Submit-Button
            self.button_submit = ctk.CTkButton(
                pl_add_frame,
                text="Speichern",
                text_color="black",
                fg_color="transparent",
                border_color="black",
                border_spacing=2,
                border_width=2,
                hover_color="gray95",
                command=self.on_submit,
            )
            self.button_submit.pack(pady=10)
            self.label_leere_felder = ctk.CTkLabel(
                pl_add_frame, text="", text_color=ROT
            )
            self.label_leere_felder.pack(pady=10)
        else:
            pl_show_frame = ctk.CTkFrame(
                self, fg_color=BACKGROUND, border_color="black", border_width=2
            )
            pl_show_frame.grid(
                row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=5
            )
            pl_status_label_bad = ctk.CTkLabel(
                pl_show_frame,
                text="Nicht bestanden!",
                text_color=ROT,
                font=H1notitalic,
            )
            pl_status_label_good = ctk.CTkLabel(
                pl_show_frame,
                text="Bestanden!",
                text_color=GRUEN,
                font=H1,
            )
            if not self.pl_data["ist_bestanden"]:
                pl_status_label_bad.pack(pady=20)
            else:
                pl_status_label_good.pack(pady=20)

            pl_show_note_label = ctk.CTkLabel(
                pl_show_frame,
                text=f"Deine Note: {self.pl_data['note']}",
                text_color="black",
                font=H2,
            )
            pl_show_note_label.pack(pady=15)
            pl_show_datum_label = ctk.CTkLabel(
                pl_show_frame,
                text=f"Am: {from_iso_to_ddmmyyyy(self.pl_data['datum'])}",
                text_color="black",
                font=H2,
            )
            pl_show_datum_label.pack(pady=15)

    def on_submit(self):
        if str(self.pl_add_note_entry.get()).strip() == "":
            self.label_leere_felder.configure(text="Keine Note eingegeben.")
            return

        try:
            self.selected_pl_datum_str = self.selected_pl_datum_real
        except AttributeError:
            self.label_leere_felder.configure(text="Prüfungsdatum nicht ausgewählt.")
            return

        self.pl_data["note"] = float(self.pl_add_note_entry.get())
        self.pl_data["datum"] = self.selected_pl_datum_str

        self.controller.change_pl(self.enrollment_id, self.pl_data)

        self.after(0, self.go_to_enrollment, self.enrollment_id)

    def pl_datum_calendar_at_button(self):
        self.pl_datum_calendar(anchor=self.pl_button_datum)

    def pl_datum_calendar(self, anchor):
        top = ctk.CTkToplevel(self)
        top.overrideredirect(True)
        top.transient(self.winfo_toplevel())
        top.attributes("-topmost", True)
        top.grab_set()
        top.bind("<FocusOut>", lambda e: top.destroy())

        bx = anchor.winfo_rootx()
        by = anchor.winfo_rooty()
        bw = anchor.winfo_width()
        bh = anchor.winfo_height()

        x = bx
        y = by + bh

        popup_w, popup_h = 250, 250
        sw = top.winfo_screenwidth()
        sh = top.winfo_screenheight()

        if x + popup_w > sw:
            x = max(0, bx + bw - popup_w)
        if y + popup_h > sh:
            y = max(0, by - popup_h)

        top.geometry(f"{popup_w}x{popup_h}+{x}+{y}")

        mindate_start = self.enrollment_data["einschreibe_datum"]
        maxdate_start = datetime.date.today()

        cal_start = Calendar(
            top,
            font="SegoeUI 12",
            selectmode="day",
            locale="de_DE",
            date_pattern="yyyy-mm-dd",
            mindate=mindate_start,
            maxdate=maxdate_start,
            showweeknumbers=False,
            selectforeground=GELB,
            normalforeground=BLAU,
            weekendforeground=BLAU,
            weekendbackground="gray90",
            background="gray95",
            foreground="black",
            selectbackground=DUNKELBLAU,
            headersbackground="gray95",
            headersforeground="black",
            disabledforeground="gray50",
            disabledbackground="gray80",
        )

        cal_start.pack(fill="both", expand=True)

        def save():
            self.selected_pl_datum.set(from_iso_to_ddmmyyyy(cal_start.get_date()))
            self.selected_pl_datum_real = cal_start.get_date()
            top.destroy()

        self.save_button = ctk.CTkButton(
            top,
            text="ok",
            text_color="black",
            fg_color="transparent",
            border_color="black",
            border_spacing=2,
            border_width=2,
            hover_color="gray95",
            command=save,
        )
        self.save_button.pack(pady=5)


class SettingsFrame(ctk.CTkScrollableFrame):
    def __init__(
        self,
        master,
        controller: Controller,
        go_to_dashboard,
        go_to_settings,
        go_to_login,
    ):
        super().__init__(master, fg_color="transparent")

        self.controller = controller
        self.go_to_dashboard = go_to_dashboard
        self.go_to_settings = go_to_settings
        self.go_to_login = go_to_login

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)

        # DATA
        self.data = self.controller.load_dashboard_data()

        # FONTS

        H2italic = ctk.CTkFont(
            family="Segoe UI", size=32, weight="normal", slant="italic"
        )
        INFO = ctk.CTkFont(family="Segoe UI", size=16, weight="normal", slant="roman")

        settings_frame = ctk.CTkFrame(
            self, fg_color=BACKGROUND, border_color="black", border_width=2
        )
        settings_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        # SETTINGS FRAME ÜBERSCHRIFT
        settings_frame.grid_columnconfigure(0, weight=1)
        settings_frame.grid_columnconfigure(1, weight=0)

        settings_ueber_label = ctk.CTkLabel(
            settings_frame, text="EINSTELLUNGEN:", font=H2italic, justify="left"
        )
        settings_ueber_label.grid(row=0, sticky="nw", padx=10, pady=10)

        settings_close_button = ctk.CTkButton(
            settings_frame,
            text="Close",
            font=master.fonts.ICONS,
            width=10,
            fg_color="transparent",
            text_color="black",
            hover_color="gray95",
            # border_color="black",
            command=lambda: self.after(0, self.go_to_dashboard),
        )
        settings_close_button.grid(
            row=0, column=1, padx=(0, 2), pady=(2, 0), sticky="ne"
        )

        st_change_frame = ctk.CTkFrame(
            self, fg_color=BACKGROUND, border_color="black", border_width=2
        )
        st_change_frame.grid(
            row=1, column=0, columnspan=2, sticky="new", padx=5, pady=5
        )

        st_change_frame.grid_columnconfigure(0, weight=1)
        st_change_frame.grid_columnconfigure(1, weight=1)
        st_change_frame.grid_columnconfigure(2, weight=1)
        st_change_frame.grid_columnconfigure(3, weight=1)
        st_change_frame.grid_columnconfigure(4, weight=1)
        st_change_frame.grid_rowconfigure(0, weight=1)
        st_change_frame.grid_rowconfigure(1, weight=1)
        st_change_frame.grid_rowconfigure(2, weight=1)
        st_change_frame.grid_rowconfigure(3, weight=1)
        st_change_frame.grid_rowconfigure(4, weight=1)
        st_change_frame.grid_rowconfigure(5, weight=1)
        st_change_frame.grid_rowconfigure(6, weight=1)
        st_change_frame.grid_rowconfigure(7, weight=1)
        st_change_frame.grid_rowconfigure(8, weight=1)
        st_change_frame.grid_rowconfigure(9, weight=1)
        st_change_frame.grid_rowconfigure(10, weight=1)

        # User-Email
        self.email_label = ctk.CTkLabel(
            st_change_frame,
            text="Deine Email-Adresse",
        )
        self.email_label.grid(row=0, column=0, padx=10, pady=10)
        self.entry_email = ctk.CTkEntry(
            st_change_frame, placeholder_text=f"{self.data['email']}"
        )
        self.entry_email.grid(row=0, column=1, sticky="ew", padx=10, pady=10)
        self.label_email_not_valid = ctk.CTkLabel(
            st_change_frame, text="", text_color=ROT
        )
        self.label_email_not_valid.grid(
            row=0, column=2, columnspan=2, sticky="ew", padx=5, pady=10
        )

        self.email_button = ctk.CTkButton(
            st_change_frame,
            text="speichern",
            text_color="black",
            fg_color="transparent",
            border_color="black",
            border_spacing=2,
            border_width=2,
            hover_color="gray95",
            command=self.save_email,
        )
        self.email_button.grid(row=0, column=4, padx=10, pady=10)

        # PW
        self.pw_label = ctk.CTkLabel(
            st_change_frame,
            text="Dein Passwort",
        )
        self.pw_label.grid(row=1, column=0, padx=10, pady=10)
        self.entry_pw = ctk.CTkEntry(
            st_change_frame, placeholder_text="Passwort", show="●"
        )
        self.entry_pw.grid(row=1, column=1, sticky="ew", padx=10, pady=10)
        self.pw_button = ctk.CTkButton(
            st_change_frame,
            text="speichern",
            text_color="black",
            fg_color="transparent",
            border_color="black",
            border_spacing=2,
            border_width=2,
            hover_color="gray95",
            command=self.save_pw,
        )
        self.pw_button.grid(row=1, column=4, padx=10, pady=10)
        self.pw_not_valid = ctk.CTkLabel(st_change_frame, text="", text_color=ROT)
        self.pw_not_valid.grid(
            row=1, column=2, columnspan=2, sticky="ew", padx=5, pady=10
        )

        # Name
        self.name_label = ctk.CTkLabel(
            st_change_frame,
            text="Dein Name",
        )
        self.name_label.grid(row=2, column=0, padx=10, pady=10)
        self.entry_name = ctk.CTkEntry(
            st_change_frame, placeholder_text=f"{self.data['name']}"
        )
        self.entry_name.grid(row=2, column=1, sticky="ew", padx=10, pady=10)
        self.button = ctk.CTkButton(
            st_change_frame,
            text="speichern",
            text_color="black",
            fg_color="transparent",
            border_color="black",
            border_spacing=2,
            border_width=2,
            hover_color="gray95",
            command=self.save_name,
        )
        self.button.grid(row=2, column=4, padx=10, pady=10)
        self.name_not_valid = ctk.CTkLabel(st_change_frame, text="", text_color=ROT)
        self.name_not_valid.grid(
            row=2, column=2, columnspan=2, sticky="ew", padx=5, pady=0
        )

        # Matrikelnummer
        self.matrikel_label = ctk.CTkLabel(
            st_change_frame,
            text="Deine Matrikelnummer",
        )
        self.matrikel_label.grid(row=3, column=0, padx=10, pady=10)
        self.entry_matrikelnummer = ctk.CTkEntry(
            st_change_frame, placeholder_text=f"{self.data['matrikelnummer']}"
        )
        self.entry_matrikelnummer.grid(row=3, column=1, sticky="ew", padx=10, pady=10)
        self.button = ctk.CTkButton(
            st_change_frame,
            text="speichern",
            text_color="black",
            fg_color="transparent",
            border_color="black",
            border_spacing=2,
            border_width=2,
            hover_color="gray95",
            command=self.save_matrikelnummer,
        )
        self.button.grid(row=3, column=4, padx=10, pady=10)
        self.mk_not_valid = ctk.CTkLabel(st_change_frame, text="", text_color=ROT)
        self.mk_not_valid.grid(
            row=3, column=2, columnspan=2, sticky="ew", padx=5, pady=10
        )

        # Semesteranzahl
        self.label_semesteranzahl = ctk.CTkLabel(
            st_change_frame,
            text="Wie viele Semester hast Du?",
            justify="left",
        )
        self.label_semesteranzahl.grid(row=4, column=0, sticky="ew", padx=10, pady=10)
        self.entry_semesteranzahl = ctk.CTkOptionMenu(
            st_change_frame,
            values=["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"],
            text_color="black",
            fg_color="gray95",
            button_color="gray95",
            button_hover_color="gray85",
        )
        self.entry_semesteranzahl.set(f"{len(self.data['semester'])}")
        self.entry_semesteranzahl.grid(row=4, column=1, sticky="ew", padx=10, pady=10)
        self.button = ctk.CTkButton(
            st_change_frame,
            text="speichern",
            text_color="black",
            fg_color="transparent",
            border_color="black",
            border_spacing=2,
            border_width=2,
            hover_color="gray95",
            command=self.save_semester_anzahl,
        )
        self.button.grid(row=4, column=4, padx=10, pady=10)
        self.sa_not_valid = ctk.CTkLabel(st_change_frame, text="", text_color=ROT)
        self.sa_not_valid.grid(
            row=4, column=2, columnspan=2, sticky="ew", padx=5, pady=10
        )

        # Start-Datum
        # Darf theoretisch nicht jünger sein als Daten in Enrollments
        self.selected_startdatum = tk.StringVar(
            value=f"{from_iso_to_ddmmyyyy(self.data['startdatum'])}"
        )

        self.label_startdatum = ctk.CTkLabel(
            st_change_frame,
            text="Studienstart ändern?",
        )
        self.label_startdatum.grid(row=5, column=0, padx=10, pady=10)
        ToolTip(self.label_startdatum, text="")

        self.button_startdatum = ctk.CTkButton(
            st_change_frame,
            text="Datum wählen",
            text_color="black",
            fg_color="transparent",
            border_color="black",
            border_spacing=2,
            border_width=2,
            hover_color="gray95",
            command=self.start_datum_calendar_at_button,
        )
        self.button_startdatum.grid(row=5, column=1, sticky="ew", padx=10, pady=10)

        self.label_startdatum_variable = ctk.CTkLabel(
            st_change_frame, textvariable=self.selected_startdatum
        )
        self.label_startdatum_variable.grid(
            row=5, column=2, sticky="ew", padx=10, pady=10
        )

        self.selected_startdatum_real: str | None = None
        self.button = ctk.CTkButton(
            st_change_frame,
            text="speichern",
            text_color="black",
            fg_color="transparent",
            border_color="black",
            border_spacing=2,
            border_width=2,
            hover_color="gray95",
            command=self.save_startdatum,
        )
        self.button.grid(row=5, column=4, padx=10, pady=10)
        self.sd_not_valid = ctk.CTkLabel(st_change_frame, text="", text_color=ROT)
        self.sd_not_valid.grid(row=5, column=3, sticky="ew", padx=5, pady=0)

        # Gesamt-ECTS-Punkte
        self.label_ects = ctk.CTkLabel(
            st_change_frame,
            text="ECTS-Punkte deines Studiums?",
        )
        self.label_ects.grid(row=6, column=0, padx=5, pady=10)
        self.entry_ects = ctk.CTkEntry(
            st_change_frame, placeholder_text=f"{self.data['gesamt_ects']} ECTS-Punkte"
        )
        self.entry_ects.grid(row=6, column=1, sticky="ew", padx=5, pady=10)
        self.label_no_int = ctk.CTkLabel(st_change_frame, text="", text_color=ROT)
        self.label_no_int.grid(row=6, column=2, columnspan=2, padx=5, pady=10)
        self.button = ctk.CTkButton(
            st_change_frame,
            text="speichern",
            text_color="black",
            fg_color="transparent",
            border_color="black",
            border_spacing=2,
            border_width=2,
            hover_color="gray95",
            command=self.save_ects,
        )
        self.button.grid(row=6, column=4, padx=10, pady=10)

        # Modul-Anzahl
        # Darf nicht kleiner sein als begonnene + abgeschlossene + nicht_bestandene
        self.label_modulanzahl = ctk.CTkLabel(
            st_change_frame,
            text="Anzahl der Module",
        )
        self.label_modulanzahl.grid(row=7, column=0, padx=10, pady=10)

        modulvalues = [str(i) for i in range(1, 71)]
        self.entry_modulanzahl = ctk.CTkOptionMenu(
            st_change_frame,
            values=modulvalues,
            text_color="black",
            fg_color="gray95",
            button_color="gray95",
            button_hover_color="gray85",
        )
        self.entry_modulanzahl.set(self.data["modulanzahl"])
        self.entry_modulanzahl.grid(row=7, column=1, sticky="ew", padx=10, pady=10)
        self.button = ctk.CTkButton(
            st_change_frame,
            text="speichern",
            text_color="black",
            fg_color="transparent",
            border_color="black",
            border_spacing=2,
            border_width=2,
            hover_color="gray95",
            command=self.save_modul_anzahl,
        )
        self.button.grid(row=7, column=4, padx=10, pady=10)
        self.ma_not_valid = ctk.CTkLabel(st_change_frame, text="", text_color=ROT)
        self.ma_not_valid.grid(
            row=7, column=2, columnspan=2, sticky="ew", padx=5, pady=10
        )

        # Danger-Zone: Profil löschen, Hochschule wechseln, Studiengang wechseln
        danger_frame = ctk.CTkFrame(
            self,
            corner_radius=10,
            fg_color=BACKGROUND,
            border_color=ROT,
            border_width=10,
        )
        danger_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        danger_label = MultiLineLabel(
            danger_frame,
            width=120,
            text="ACHTUNG: Änderungen an folgenden Einstellungen können dazu führen, dass Deine Daten verloren gehen. Dies kann nicht rückgängig gemacht werden.",
            text_color=ROT,
            font=INFO,
            fg_color="transparent",
            justify="center",
        )
        danger_label.grid(
            row=0,
            column=0,
            columnspan=4,
            padx=20,
            pady=10,
            sticky="ew",
        )

        # Hochschule
        self.hochschulen_dict = self.controller.get_hochschulen_dict()
        self.label_hochschule = ctk.CTkLabel(
            danger_frame, text="Wie heißt deine Hochschule?", justify="left"
        )
        self.label_hochschule.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.search_combo = SearchableComboBox(
            danger_frame, width=240, options=self.hochschulen_dict
        )
        self.search_combo.set(f"{self.data['hochschule']}")
        self.search_combo.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
        self.hs_button = ctk.CTkButton(
            danger_frame,
            text="speichern",
            text_color="black",
            fg_color="transparent",
            border_color="black",
            border_spacing=2,
            border_width=2,
            hover_color="gray95",
            command=self.save_hochschule,
        )
        self.hs_button.grid(row=1, column=3, padx=10, pady=10)
        self.hs_not_valid = ctk.CTkLabel(danger_frame, text="", text_color=ROT)
        self.hs_not_valid.grid(row=1, column=2, sticky="ew", padx=5, pady=0)

        # Studiengang
        self.label_studiengang = ctk.CTkLabel(
            danger_frame, text="Wie heißt Dein Studiengang?", justify="left"
        )
        self.label_studiengang.grid(row=2, column=0, padx=10, pady=10)

        self.entry_studiengang = ctk.CTkEntry(
            danger_frame, width=240, placeholder_text=f"{self.data['studiengang']}"
        )
        self.entry_studiengang.grid(row=2, column=1, padx=10, pady=10)
        self.sg_button = ctk.CTkButton(
            danger_frame,
            text="speichern",
            text_color="black",
            fg_color="transparent",
            border_color="black",
            border_spacing=2,
            border_width=2,
            hover_color="gray95",
            command=self.save_studiengang,
        )
        self.sg_button.grid(row=2, column=3, padx=10, pady=10)
        self.sg_not_valid = ctk.CTkLabel(danger_frame, text="", text_color=ROT)
        self.sg_not_valid.grid(row=2, column=2, sticky="nsew", padx=5, pady=0)

        # Account löschen
        self.label_del_acc = ctk.CTkLabel(
            danger_frame, text="Du möchtest Deinen Account löschen?", justify="left"
        )
        self.label_del_acc.grid(row=3, column=0, padx=10, pady=(10, 15))
        self.button_del_acc = ctk.CTkButton(
            danger_frame,
            text="Account löschen",
            text_color="black",
            fg_color="transparent",
            border_color="black",
            border_spacing=2,
            border_width=2,
            hover_color="gray95",
            command=self.open_delete_account,
        )
        self.button_del_acc.grid(row=3, column=3, padx=10, pady=10)

    def save_email(self):
        if self.verify_email():
            self.controller.change_email(self.selected_email)
            self.label_email_not_valid.configure(text="Neue Email gespeichert")

    def save_pw(self):
        if self.verify_input(self.entry_pw.get()):
            self.controller.change_pw(self.entry_pw.get())
            self.pw_not_valid.configure(text="Neues Passwort gespeichert")
        else:
            self.pw_not_valid.configure(text="Nicht ausgefüllt")

    def save_name(self):
        if self.verify_input(self.entry_name.get()):
            self.controller.change_name(self.entry_name.get())
            self.name_not_valid.configure(text="Neuer Name gespeichert")
        else:
            self.name_not_valid.configure(text="Nicht ausgefüllt")

    def save_matrikelnummer(self):
        if self.verify_input(self.entry_matrikelnummer.get()):
            self.controller.change_matrikelnummer(self.entry_matrikelnummer.get())
            self.mk_not_valid.configure(text="Neue Matrikelnummer gespeichert")
        else:
            self.mk_not_valid.configure(text="Nicht ausgefüllt")

    def save_semester_anzahl(self):
        neu_semester_anzahl = int(self.entry_semesteranzahl.get())
        if neu_semester_anzahl != len(self.data["semester"]):
            self.controller.change_semester_anzahl(neu_semester_anzahl)
            self.sa_not_valid.configure(text="Semester Gespeichert")
        else:
            self.sa_not_valid.configure(text="Entspricht bisherigen Wert")

    def save_startdatum(self):
        if self.selected_startdatum_real:
            if (
                datetime.date.fromisoformat(self.selected_startdatum_real)
                == self.data["startdatum"]
            ):
                self.sd_not_valid.configure(text="Entspricht bisherigen Wert")
            else:
                self.controller.change_startdatum(
                    datetime.date.fromisoformat(self.selected_startdatum_real)
                )
                self.sd_not_valid.configure(text="Gespeichert")
        else:
            self.sd_not_valid.configure(text="Kein Datum gewählt")

    def save_ects(self):
        neu_ects = self.entry_ects.get().strip()
        if self.validate_ects(neu_ects):
            if neu_ects != self.data["gesamt_ects"]:
                self.controller.change_gesamt_ects(int(neu_ects))
                self.label_no_int.configure(text="Gespeichert")
            else:
                self.label_no_int.configure(text="Entspricht bisherigen Wert")

    def save_modul_anzahl(self):
        neu_modulanzahl = int(self.entry_modulanzahl.get())
        if neu_modulanzahl != self.data["modulanzahl"]:
            if neu_modulanzahl < len(self.data["enrollments"]):
                self.ma_not_valid.configure(text="Du hast schon mehr Module begonnen")
            else:
                self.controller.change_modul_anzahl(neu_modulanzahl)
                self.ma_not_valid.configure(text="Gespeichert")
        else:
            self.ma_not_valid.configure(text="Entspricht bisherigen Wert")

    def save_hochschule(self):
        if self.verify_input(self.search_combo.get_value()):
            if self.search_combo.get_value() == self.data["hochschule"]:
                self.hs_not_valid.configure(text="Entspricht bisherigen Wert")
                return
            id, hs = self.check_hs()
            self.controller.change_hochschule(id=id, hs=hs)
            self.after(0, self.go_to_dashboard)
        else:
            self.hs_not_valid.configure(text="Nicht ausgefüllt")

    def save_studiengang(self):
        if self.verify_input(self.entry_studiengang.get()):
            if self.entry_studiengang.get() == self.data["studiengang"]:
                self.sg_not_valid.configure(text="Entspricht bisherigen Wert")
                return
            self.controller.change_studiengang(self.entry_studiengang.get())
            self.after(0, self.go_to_dashboard)
        else:
            self.sg_not_valid.configure(text="Nicht ausgefüllt")

    def _center_over_parent(self, top: ctk.CTkToplevel, w: int, h: int):
        self.update_idletasks()
        px = self.winfo_rootx()
        py = self.winfo_rooty()
        pw = self.winfo_width()
        ph = self.winfo_height()
        x = px + (pw - w) // 2
        y = py + (ph - h) // 2
        top.geometry(f"{w}x{h}+{x}+{y}")

    def open_delete_account(self):
        top = ctk.CTkToplevel(self, fg_color="gray35")
        top.overrideredirect(True)
        top.attributes("-topmost", True)
        top.grab_set()
        popup_w, popup_h = 400, 300
        self._center_over_parent(top=top, w=popup_w, h=popup_h)

        INFO = ctk.CTkFont(family="Segoe UI", size=16, weight="normal", slant="roman")
        MATERIAL_FONT = ctk.CTkFont(
            family="Material Symbols Sharp", size=42, weight="normal", slant="roman"
        )
        settings_close_button = ctk.CTkButton(
            top,
            text="Close",
            font=MATERIAL_FONT,
            width=10,
            fg_color="transparent",
            text_color="white",
            hover_color="gray50",
            border_color="black",
            command=lambda: self.after(0, self.go_to_settings),
        )
        settings_close_button.pack(pady=5, anchor="ne")

        ctk.CTkLabel(top, text="warning", text_color=ROT, font=MATERIAL_FONT).pack(
            pady=10
        )

        ctk.CTkLabel(
            top,
            text="Bist Du sicher, dass Du dein Profil löschen möchtest?",
            text_color=ROT,
            font=INFO,
        ).pack(pady=15)

        ctk.CTkButton(
            top,
            fg_color=ROT,
            text="Profil löschen",
            text_color="black",
            border_color="black",
            border_spacing=2,
            border_width=2,
            hover_color="gray95",
            font=INFO,
            command=self.delete_account,
        ).pack(pady=10)

    def delete_account(self):
        self.controller.delete_student()
        self.after(0, self.go_to_login)

    def verify_input(self, input):
        if str(input).strip() == "":
            return False
        else:
            return True

    def verify_email(self):
        # validiere Email
        valid = self.controller.validate_email_for_new_account(
            str(self.entry_email.get())
        )
        if isinstance(valid, EmailNotValidError):
            error = str(valid)
            self.label_email_not_valid.configure(text=error)
            return False
        else:
            self.selected_email = valid
            return True

    def check_hs(self):
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
        return (self.selected_hochschule_id, self.selected_hochschule_name)

    def start_datum_calendar_at_button(self):
        self.start_datum_calendar(anchor=self.button_startdatum)

    def start_datum_calendar(self, anchor):
        top = ctk.CTkToplevel(self)
        top.overrideredirect(True)
        top.transient(self.winfo_toplevel())
        top.attributes("-topmost", True)
        top.grab_set()
        top.bind("<FocusOut>", lambda e: top.destroy())

        bx = anchor.winfo_rootx()
        by = anchor.winfo_rooty()
        bw = anchor.winfo_width()
        bh = anchor.winfo_height()

        x = bx
        y = by + bh

        popup_w, popup_h = 250, 250
        sw = top.winfo_screenwidth()
        sh = top.winfo_screenheight()

        if x + popup_w > sw:
            x = max(0, bx + bw - popup_w)
        if y + popup_h > sh:
            y = max(0, by - popup_h)

        top.geometry(f"{popup_w}x{popup_h}+{x}+{y}")

        einschreibe_dates = [
            enrollment["einschreibe_datum"] for enrollment in self.data["enrollments"]
        ]

        mindate_start = datetime.date(year=2010, month=1, day=1)
        if einschreibe_dates:
            maxdate_start = min(einschreibe_dates)
        else:
            maxdate_start = datetime.date.today()

        cal_start = Calendar(
            top,
            font="SegoeUI 12",
            selectmode="day",
            locale="de_DE",
            date_pattern="yyyy-mm-dd",
            mindate=mindate_start,
            maxdate=maxdate_start,
            showweeknumbers=False,
            selectforeground=GELB,
            normalforeground=BLAU,
            weekendforeground=BLAU,
            weekendbackground="gray90",
            background="gray95",
            foreground="black",
            selectbackground=DUNKELBLAU,
            headersbackground="gray95",
            headersforeground="black",
            disabledforeground="gray50",
            disabledbackground="gray80",
        )

        cal_start.pack(fill="both", expand=True)

        def save():
            self.selected_startdatum.set(from_iso_to_ddmmyyyy(cal_start.get_date()))
            self.selected_startdatum_real = cal_start.get_date()
            top.destroy()

        self.save_button_start = ctk.CTkButton(
            top,
            text="ok",
            text_color="black",
            fg_color="transparent",
            border_color="black",
            border_spacing=2,
            border_width=2,
            hover_color="gray95",
            command=save,
        )
        self.save_button_start.pack(pady=5)

    def validate_ects(self, ects):
        try:
            number = int(ects)
        except ValueError:
            self.label_no_int.configure(text="Muss eine (Ganz-) Zahl sein")
            return False

        if number:
            if number > 0 and number <= 500:
                if number >= self.data["erarbeitete_ects"]:
                    return True
                else:
                    self.label_no_int.configure(
                        text="Du hast schon mehr ECTS-Punkte erarbeitet"
                    )
                    return False
        else:
            self.label_no_int.configure(text="Zahl muss zwischen 1 und 500 liegen")
            return False


class ExFrame(ctk.CTkFrame):
    def __init__(self, master, controller: Controller, go_to_dashboard, go_to_settings):
        super().__init__(master, fg_color="transparent")

        self.controller = controller
        self.go_to_dashboard = go_to_dashboard
        self.go_to_settings = go_to_settings

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)

        # DATA
        self.data = self.controller.load_dashboard_data()

        # FONTS
        H2italic = ctk.CTkFont(
            family="Segoe UI", size=32, weight="normal", slant="italic"
        )

        ex_frame = ctk.CTkFrame(
            self, fg_color=BACKGROUND, border_color="black", border_width=2
        )
        ex_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        # SETTINGS FRAME ÜBERSCHRIFT
        ex_frame.grid_columnconfigure(0, weight=1)
        ex_frame.grid_columnconfigure(1, weight=0)

        ex_ueber_label = ctk.CTkLabel(
            ex_frame, text="Du wurdest exmatrikuliert?", font=H2italic, justify="left"
        )
        ex_ueber_label.grid(row=0, sticky="nw", padx=10, pady=10)

        ex_close_button = ctk.CTkButton(
            ex_frame,
            text="Close",
            font=master.fonts.ICONS,
            width=10,
            fg_color="transparent",
            text_color="black",
            hover_color="gray95",
            # border_color="black",
            command=lambda: self.after(0, self.go_to_dashboard),
        )
        ex_close_button.grid(row=0, column=1, padx=(0, 2), pady=(2, 0), sticky="ne")

        set_ex_frame = ctk.CTkFrame(
            self, fg_color=BACKGROUND, border_color="black", border_width=2
        )
        set_ex_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        set_ex_frame.grid_columnconfigure(0, weight=1)
        set_ex_frame.grid_columnconfigure(1, weight=1)
        set_ex_frame.grid_columnconfigure(2, weight=1)
        set_ex_frame.grid_columnconfigure(3, weight=1)

        # Ziel-Datum
        self.selected_zieldatum = tk.StringVar(
            value=from_iso_to_ddmmyyyy(self.data["exmatrikulationsdatum"])
        )

        self.label_zieldatum = ctk.CTkLabel(
            set_ex_frame, text="Wann wurdest Du exmatrikuliert?"
        )
        self.label_zieldatum.grid(row=1, column=0, sticky="ew", padx=10, pady=10)

        self.button_zieldatum = ctk.CTkButton(
            set_ex_frame,
            text="Exmatrikulationsdatum wählen",
            text_color="black",
            fg_color="transparent",
            border_color="black",
            border_spacing=2,
            border_width=2,
            hover_color="gray95",
            command=self.ziel_datum_calendar_at_button,
        )
        self.button_zieldatum.grid(row=1, column=2, padx=10, pady=10)

        self.label_zieldatum_variable = ctk.CTkLabel(
            set_ex_frame, textvariable=self.selected_zieldatum
        )
        self.label_zieldatum_variable.grid(
            row=1, column=1, sticky="ew", padx=10, pady=10
        )

        self.selected_zieldatum_real: str

        # Submit-Buttons
        self.button_datum_submit = ctk.CTkButton(
            set_ex_frame,
            text="Exmatrikulationsdatum speichern",
            text_color="black",
            fg_color="transparent",
            border_color=ROT,
            border_spacing=2,
            border_width=2,
            hover_color="gray95",
            command=self.datum_submit,
        )
        self.button_datum_submit.grid(row=1, column=3, padx=10, pady=10, sticky="ew")
        self.label_leere_felder = ctk.CTkLabel(set_ex_frame, text="", text_color=ROT)
        self.label_leere_felder.grid(row=2, column=1, padx=10, pady=10, sticky="ew")

        if self.data["exmatrikulationsdatum"]:
            self.button_zieldatum.configure(state="disabled")
            self.button_datum_submit.configure(state="disabled")
            del_button = ctk.CTkButton(
                set_ex_frame,
                text="Exmatrikulationsdatum löschen",
                text_color="black",
                fg_color="transparent",
                border_color=ROT,
                border_spacing=2,
                border_width=2,
                hover_color="gray95",
                command=self.delete_ex_date,
            )
            del_button.grid(row=2, column=3, padx=10, pady=10, sticky="ew")

    def delete_ex_date(self):
        if self.data["exmatrikulationsdatum"]:
            self.controller.change_exmatrikulationsdatum(None)
            self.after(0, self.go_to_dashboard)

    def datum_submit(self):
        try:
            self.selected_zieldatum_str = self.selected_zieldatum_real
        except AttributeError:
            self.label_leere_felder.configure(
                text="Exmatrikulationsdatum nicht ausgewählt."
            )
            return

        self.controller.change_exmatrikulationsdatum(
            datetime.date.fromisoformat(self.selected_zieldatum_str)
        )
        self.after(0, self.go_to_dashboard)

    def ziel_datum_calendar_at_button(self):
        self.ziel_datum_calendar(anchor=self.button_zieldatum)

    def ziel_datum_calendar(self, anchor):
        top = ctk.CTkToplevel(self)
        top.overrideredirect(True)
        top.transient(self.winfo_toplevel())
        top.attributes("-topmost", True)
        top.grab_set()
        top.bind("<FocusOut>", lambda e: top.destroy())

        bx = anchor.winfo_rootx()
        by = anchor.winfo_rooty()
        bw = anchor.winfo_width()
        bh = anchor.winfo_height()

        x = bx
        y = by + bh

        popup_w, popup_h = 250, 250
        sw = top.winfo_screenwidth()
        sh = top.winfo_screenheight()

        if x + popup_w > sw:
            x = max(0, bx + bw - popup_w)
        if y + popup_h > sh:
            y = max(0, by - popup_h)

        top.geometry(f"{popup_w}x{popup_h}+{x}+{y}")

        mindate_ziel = self.data["startdatum"]
        maxdate_ziel = datetime.date.today()
        top.title("Exmatrikulationsdatum auswählen")

        cal_ziel = Calendar(
            top,
            font="SegoeUI 12",
            selectmode="day",
            locale="de_DE",
            date_pattern="yyyy-mm-dd",
            mindate=mindate_ziel,
            maxdate=maxdate_ziel,
            showweeknumbers=False,
            selectforeground=GELB,
            normalforeground=BLAU,
            weekendforeground=BLAU,
            weekendbackground="gray90",
            background="gray95",
            foreground="black",
            selectbackground=DUNKELBLAU,
            headersbackground="gray95",
            headersforeground="black",
            disabledforeground="gray50",
            disabledbackground="gray80",
        )
        cal_ziel.selection_set(self.data["zieldatum"])

        cal_ziel.pack(fill="both", expand=True)

        def save():
            self.selected_zieldatum.set(from_iso_to_ddmmyyyy(cal_ziel.get_date()))
            self.selected_zieldatum_real = cal_ziel.get_date()
            top.destroy()

        self.save_button_ziel = ctk.CTkButton(
            top,
            text="ok",
            text_color="black",
            fg_color="transparent",
            border_color="black",
            border_spacing=2,
            border_width=2,
            hover_color="gray95",
            command=save,
        )
        self.save_button_ziel.pack(pady=10)


class ZieleFrame(ctk.CTkFrame):
    def __init__(self, master, controller: Controller, go_to_dashboard, go_to_settings):
        super().__init__(master, fg_color="transparent")

        self.controller = controller
        self.go_to_dashboard = go_to_dashboard
        self.go_to_settings = go_to_settings

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)

        # DATA
        self.data = self.controller.load_dashboard_data()

        # FONTS
        H2italic = ctk.CTkFont(
            family="Segoe UI", size=32, weight="normal", slant="italic"
        )

        ziele_frame = ctk.CTkFrame(
            self, fg_color=BACKGROUND, border_color="black", border_width=2
        )
        ziele_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        # SETTINGS FRAME ÜBERSCHRIFT
        ziele_frame.grid_columnconfigure(0, weight=1)
        ziele_frame.grid_columnconfigure(1, weight=0)

        ziele_ueber_label = ctk.CTkLabel(
            ziele_frame, text="Änder Deine Ziele:", font=H2italic, justify="left"
        )
        ziele_ueber_label.grid(row=0, sticky="nw", padx=10, pady=10)

        ziele_close_button = ctk.CTkButton(
            ziele_frame,
            text="Close",
            font=master.fonts.ICONS,
            width=10,
            fg_color="transparent",
            text_color="black",
            hover_color="gray95",
            # border_color="black",
            command=lambda: self.after(0, self.go_to_dashboard),
        )
        ziele_close_button.grid(row=0, column=1, padx=(0, 2), pady=(2, 0), sticky="ne")

        zs_frame = ctk.CTkFrame(
            self, fg_color=BACKGROUND, border_color="black", border_width=2
        )
        zs_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        zs_frame.grid_columnconfigure(0, weight=1)
        zs_frame.grid_columnconfigure(1, weight=1)
        zs_frame.grid_columnconfigure(2, weight=1)

        # Ziel-Note
        self.entry_zielnote: float = self.data["zielnote"]
        self.slider_zielnote = ctk.CTkSlider(
            zs_frame,
            from_=1,
            to=4,
            number_of_steps=30,
            fg_color=HELLBLAU,
            progress_color=BLAU,
            button_color=BLAU,
            button_hover_color=DUNKELBLAU,
            command=self.slider_zielnote_event,
        )
        self.slider_zielnote.set(self.entry_zielnote)
        self.slider_zielnote.grid(row=0, column=2, sticky="ew", padx=10, pady=10)
        self.label_zielnote = ctk.CTkLabel(
            zs_frame,
            text="Deine Wunsch-Abschlussnote:",
        )
        self.label_zielnote.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

        self.label_zielnote = ctk.CTkLabel(
            zs_frame,
            text=f"{round(self.slider_zielnote.get(), 1)}",
        )
        self.label_zielnote.grid(row=0, column=1, sticky="ew", padx=10, pady=10)

        # Ziel-Datum
        self.selected_zieldatum = tk.StringVar(
            value=from_iso_to_ddmmyyyy(self.data["zieldatum"])
        )

        self.label_zieldatum = ctk.CTkLabel(
            zs_frame, text="Bis wann möchtest Du Dein Studium beenden?"
        )
        self.label_zieldatum.grid(row=1, column=0, sticky="ew", padx=10, pady=10)

        self.button_zieldatum = ctk.CTkButton(
            zs_frame,
            text="Zieldatum auswählen",
            text_color="black",
            fg_color="transparent",
            border_color="black",
            border_spacing=2,
            border_width=2,
            hover_color="gray95",
            command=self.ziel_datum_calendar_at_button,
        )
        self.button_zieldatum.grid(row=1, column=2, sticky="ew", padx=10, pady=10)

        self.label_zieldatum_variable = ctk.CTkLabel(
            zs_frame, textvariable=self.selected_zieldatum
        )
        self.label_zieldatum_variable.grid(
            row=1, column=1, sticky="ew", padx=10, pady=10
        )

        self.selected_zieldatum_real: str

        # Submit-Buttons
        self.button_datum_submit = ctk.CTkButton(
            zs_frame,
            text="Zieldatum speichern",
            text_color="black",
            fg_color="transparent",
            border_color="black",
            border_spacing=2,
            border_width=2,
            hover_color="gray95",
            command=self.datum_submit,
        )
        self.button_datum_submit.grid(row=1, column=3, padx=10, pady=10, sticky="ew")
        self.label_leere_felder = ctk.CTkLabel(zs_frame, text="", text_color=ROT)
        self.label_leere_felder.grid(row=2, column=2, padx=10, pady=10, sticky="ew")

        self.button_note_submit = ctk.CTkButton(
            zs_frame,
            text="Wunschnote speichern",
            text_color="black",
            fg_color="transparent",
            border_color="black",
            border_spacing=2,
            border_width=2,
            hover_color="gray95",
            command=self.noten_submit,
        )
        self.button_note_submit.grid(row=0, column=3, padx=10, pady=10, sticky="ew")

    def datum_submit(self):
        try:
            self.selected_zieldatum_str = self.selected_zieldatum_real
        except AttributeError:
            self.label_leere_felder.configure(text="Zieldatum nicht ausgewählt.")
            return

        self.controller.change_zieldatum(
            datetime.date.fromisoformat(self.selected_zieldatum_str)
        )

    def noten_submit(self):
        self.selected_zielnote = self.entry_zielnote
        self.controller.change_zielnote(self.selected_zielnote)

    def ziel_datum_calendar_at_button(self):
        self.ziel_datum_calendar(anchor=self.button_zieldatum)

    def ziel_datum_calendar(self, anchor):
        top = ctk.CTkToplevel(self)
        top.overrideredirect(True)
        top.transient(self.winfo_toplevel())
        top.attributes("-topmost", True)
        top.grab_set()
        top.bind("<FocusOut>", lambda e: top.destroy())

        bx = anchor.winfo_rootx()
        by = anchor.winfo_rooty()
        bw = anchor.winfo_width()
        bh = anchor.winfo_height()

        x = bx
        y = by + bh

        popup_w, popup_h = 250, 250
        sw = top.winfo_screenwidth()
        sh = top.winfo_screenheight()

        if x + popup_w > sw:
            x = max(0, bx + bw - popup_w)
        if y + popup_h > sh:
            y = max(0, by - popup_h)

        top.geometry(f"{popup_w}x{popup_h}+{x}+{y}")

        mindate_ziel = self.data["startdatum"]
        maxdate_ziel = datetime.date(year=2200, month=12, day=31)
        top.title("Zieldatum auswählen")

        cal_ziel = Calendar(
            top,
            font="SegoeUI 12",
            selectmode="day",
            locale="de_DE",
            date_pattern="yyyy-mm-dd",
            mindate=mindate_ziel,
            maxdate=maxdate_ziel,
            showweeknumbers=False,
            selectforeground=GELB,
            normalforeground=BLAU,
            weekendforeground=BLAU,
            weekendbackground="gray90",
            background="gray95",
            foreground="black",
            selectbackground=DUNKELBLAU,
            headersbackground="gray95",
            headersforeground="black",
            disabledforeground="gray50",
            disabledbackground="gray80",
        )
        cal_ziel.selection_set(self.data["zieldatum"])

        cal_ziel.pack(fill="both", expand=True)

        def save():
            self.selected_zieldatum.set(from_iso_to_ddmmyyyy(cal_ziel.get_date()))
            self.selected_zieldatum_real = cal_ziel.get_date()
            top.destroy()

        self.save_button_ziel = ctk.CTkButton(
            top,
            text="ok",
            text_color="black",
            fg_color="transparent",
            border_color="black",
            border_spacing=2,
            border_width=2,
            hover_color="gray95",
            command=save,
        )
        self.save_button_ziel.pack(pady=10)

    def slider_zielnote_event(self, value: float):
        self.entry_zielnote = round(float(value), 1)
        self.label_zielnote.configure(text=f"{round(float(value), 1)}")


class UeberFrame(ctk.CTkFrame):
    def __init__(self, master, controller: Controller, go_to_dashboard):
        super().__init__(master, fg_color="transparent")
        self.controller = controller
        self.go_to_dashboard = go_to_dashboard

        # FONTS
        H1 = ctk.CTkFont(family="Segoe UI", size=84, weight="normal", slant="italic")
        H3 = ctk.CTkFont(family="Segoe UI", size=22, weight="normal", slant="roman")
        INFO = ctk.CTkFont(family="Segoe UI", size=16, weight="normal", slant="roman")

        ueber_close_button = ctk.CTkButton(
            self,
            text="Close",
            font=master.fonts.ICONS,
            width=10,
            fg_color="transparent",
            text_color="black",
            hover_color="gray95",
            border_color="black",
            command=lambda: self.after(0, self.go_to_dashboard),
        )
        ueber_close_button.pack(pady=25)

        ueber_ueber_label = ctk.CTkLabel(
            self,
            text="Über DASHBOARD",
            font=H1,
        )
        ueber_ueber_label.pack(pady=20)

        version_label = ctk.CTkLabel(
            self,
            text="Version: 1.0",
            font=H3,
        )
        version_label.pack(pady=20)

        ueber_label = MultiLineLabel(
            self,
            width=110,
            text="Dieses Programm ist im Rahmen des Studiums 'Angewandte Künstliche Intelligenz' an der IU Internationalen Hochschule entstanden. Es wurde im 'Projekt: Objektorientierte und funktionale Programmierung mit Python' von Florian Erik Janssens entworfen und programmiert.",
            font=INFO,
        )
        ueber_label.pack(pady=20)

        cc_label = MultiLineLabel(
            self,
            width=110,
            text="Diese Software nutzt folgende Open-Source-Bibliotheken: "
            "SQLAlchemy (MIT), CustomTkinter (MIT), tkcalendar (MIT), "
            "argon2-cffi (MIT), python-dateutil (Apache 2.0), "
            "email-validator (CC0). Vollständige Lizenzen siehe THIRD_PARTY_LICENSES.txt",
            font=INFO,
        )
        cc_label.pack(pady=20)

        url = "https://github.com/printhellogithub/IU_Dashboard"
        gh_button = ctk.CTkButton(
            self,
            text="Visit on Github",
            font=INFO,
            text_color="black",
            fg_color="transparent",
            border_color="black",
            border_spacing=2,
            border_width=2,
            hover_color="gray95",
            command=lambda: webbrowser.open(url),
        )
        gh_button.pack(pady=20)
        ToolTip(gh_button, text="Öffnet GitHub-Repository im Browser")


class App(ctk.CTk):
    def __init__(self):
        setup_logging(debug=False, log_to_console=True)
        super().__init__(fg_color=BACKGROUND)

        ctk.FontManager.load_font(str(FONT_PATH_NOTO))
        ctk.FontManager.load_font(str(FONT_PATH_MATERIAL))
        self.fonts = Fonts()

        self.controller = Controller(seed=True)
        self.title("Dashboard")
        self.geometry("960x640")  # orig: 960x540
        self.minsize(960, 640)
        self.maxsize(1920, 1080)
        ctk.set_appearance_mode("light")
        style = ttk.Style()
        try:
            style.theme_use("default")
        except Exception:
            pass
        self.center_window()
        self.current_frame = None
        self.show_login()

    def center_window(self):
        """Zentriert das Fenster auf dem Bildschirm."""
        self.update_idletasks()  # Fenster aktualisieren, um korrekte Größe zu bekommen

        # Fenstergröße
        window_width = self.winfo_width()
        window_height = self.winfo_height()

        # Bildschirmgröße
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # Position berechnen (zentriert)
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        # Position setzen
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")

    def show_login(self):
        if self.current_frame:
            self.current_frame.pack_forget()
            self.current_frame.destroy()
            self.update_idletasks()
        self.current_frame = LoginFrame(
            self,
            controller=self.controller,
            go_to_dashboard=self.show_dashboard,
            go_to_new_user=self.show_new_user,
        )
        self.current_frame.pack(fill="both", expand=True)

    def show_new_user(self):
        if self.current_frame:
            self.current_frame.pack_forget()
            self.current_frame.destroy()
            self.update_idletasks()
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
            self.current_frame.pack_forget()
            self.current_frame.destroy()
            self.update_idletasks()
        self.current_frame = StudiengangAuswahlFrame(
            self,
            controller=self.controller,
            cache=self.cache,
            go_to_dashboard=self.show_dashboard,
            go_to_login=self.show_login,
            go_to_new_user=self.show_new_user,
        )
        self.current_frame.pack(fill="both", expand=True)

    def show_dashboard(self):
        if self.current_frame:
            self.current_frame.pack_forget()
            self.current_frame.destroy()
            self.update_idletasks()
        self.current_frame = DashboardFrame(
            self,
            controller=self.controller,
            go_to_login=self.show_login,
            go_to_add_enrollment=self.show_add_enrollment,
            go_to_enrollment=self.show_enrollment,
            go_to_settings=self.show_settings,
            go_to_ex=self.show_exmatrikulation,
            go_to_ziele=self.show_ziele,
            go_to_ueber=self.show_ueber,
        )
        self.current_frame.pack(fill="both", expand=True)

    def show_add_enrollment(self):
        if self.current_frame:
            self.current_frame.pack_forget()
            self.current_frame.destroy()
            self.update_idletasks()
        self.current_frame = AddEnrollmentFrame(
            self,
            controller=self.controller,
            go_to_enrollment=self.show_enrollment,
            go_to_dashboard=self.show_dashboard,
        )
        self.current_frame.pack(fill="both", expand=True)

    def show_enrollment(self, enrollment_id):
        if self.current_frame:
            self.current_frame.pack_forget()
            self.current_frame.destroy()
            self.update_idletasks()
        self.current_frame = EnrollmentFrame(
            self,
            controller=self.controller,
            go_to_dashboard=self.show_dashboard,
            go_to_pl=self.show_pl,
            enrollment_id=enrollment_id,
        )
        self.current_frame.pack(fill="both", expand=True)

    def show_pl(self, pl_id, e_id):
        if self.current_frame:
            self.current_frame.pack_forget()
            self.current_frame.destroy()
            self.update_idletasks()
        self.current_frame = PLAddFrame(
            self,
            controller=self.controller,
            go_to_enrollment=self.show_enrollment,
            pl_id=pl_id,
            e_id=e_id,
        )
        self.current_frame.pack(fill="both", expand=True)

    def show_settings(self):
        if self.current_frame:
            self.current_frame.pack_forget()
            self.current_frame.destroy()
            self.update_idletasks()
        self.current_frame = SettingsFrame(
            self,
            controller=self.controller,
            go_to_dashboard=self.show_dashboard,
            go_to_settings=self.show_settings,
            go_to_login=self.show_login,
        )
        self.current_frame.pack(fill="both", expand=True)

    def show_exmatrikulation(self):
        if self.current_frame:
            self.current_frame.pack_forget()
            self.current_frame.destroy()
            self.update_idletasks()
        self.current_frame = ExFrame(
            self,
            controller=self.controller,
            go_to_dashboard=self.show_dashboard,
            go_to_settings=self.show_settings,
        )
        self.current_frame.pack(fill="both", expand=True)

    def show_ziele(self):
        if self.current_frame:
            self.current_frame.pack_forget()
            self.current_frame.destroy()
            self.update_idletasks()
        self.current_frame = ZieleFrame(
            self,
            controller=self.controller,
            go_to_dashboard=self.show_dashboard,
            go_to_settings=self.show_settings,
        )
        self.current_frame.pack(fill="both", expand=True)

    def show_ueber(self):
        if self.current_frame:
            self.current_frame.pack_forget()
            self.current_frame.destroy()
            self.update_idletasks()
        self.current_frame = UeberFrame(
            self, controller=self.controller, go_to_dashboard=self.show_dashboard
        )
        self.current_frame.pack(fill="both", expand=True)


if __name__ == "__main__":
    app = App()
    app.mainloop()
