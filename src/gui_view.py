from __future__ import annotations
import customtkinter as ctk
import datetime
import tkinter as tk
from tkcalendar import Calendar
from email_validator import EmailNotValidError
import textwrap

from main import Controller

# GLOBAL
BACKGROUND = "#FFFFFF"

GRUEN = "#29C731"
GELB = "#FEC109"
ROT = "#F20D0D"
GRAU = "#D9D9D9"
BLAU = "#0A64FF"
HELLBLAU = "#B5D0FF"


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

        # "radio_button_unchecked", text_color="#D9D9D9")


# EXTRA-KLASSE Dynamische Kurs-Entries
class DynamicEntries(ctk.CTkFrame):
    def __init__(
        self,
        master,
        *,
        label_name="Kursname",
        label_nummer="Kursnummer",
        placeholder_name="Kurs",
        placeholder_nummer="Kursnummer",
        initial_rows=1,
        max_rows=20,
    ):
        super().__init__(master, fg_color="transparent")
        self.placeholder_name = placeholder_name
        self.placeholder_nummer = placeholder_nummer
        self.max_rows = max_rows
        self.rows: list[dict[str, object]] = []

        MATERIAL_FONT = ctk.CTkFont(
            family="Material Symbols Sharp", size=26, weight="normal", slant="roman"
        )

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

        self.add_button = ctk.CTkButton(
            self.header,
            text="add_circle",
            font=MATERIAL_FONT,
            width=36,
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
                kursname=self.placeholder_name, kursnummer=self.placeholder_nummer
            )

    def add_row(self, kursname: str = "", kursnummer: str = "") -> None:
        if len(self.rows) >= self.max_rows:
            return
        var_kursname = ctk.StringVar(value=kursname)
        entry_kursname = ctk.CTkEntry(
            self.list_frame,
            textvariable=var_kursname,
            placeholder_text=f"{self.placeholder_name} {len(self.rows) + 1}",
        )

        var_kursnummer = ctk.StringVar(value=kursnummer)
        entry_kursnummer = ctk.CTkEntry(
            self.list_frame,
            textvariable=var_kursnummer,
            placeholder_text=f"{self.placeholder_nummer} {len(self.rows) + 1}",
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

            if isinstance(r["entry_kursname"], ctk.CTkEntry):
                r["entry_kursname"].configure(
                    placeholder_text=f"{self.placeholder_name} {i + 1}"
                )
            if isinstance(r["entry_kursnummer"], ctk.CTkEntry):
                r["entry_kursnummer"].configure(
                    placeholder_text=f"{self.placeholder_nummer} {i + 1}"
                )

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

        H1 = ctk.CTkFont(family="Segoe UI", size=140, weight="normal", slant="italic")

        ctk.CTkLabel(self, text="DASHBOARD", font=H1).pack(pady=20)

        self.entry_email = ctk.CTkEntry(self, placeholder_text="Email-Adresse")
        self.entry_email.focus()
        self.entry_email.pack(pady=5)

        self.entry_pw = ctk.CTkEntry(self, placeholder_text="Passwort", show="●")
        self.entry_pw.pack(pady=5)
        self.entry_pw.bind("<Return>", lambda event: self.check_login())

        self.label_info = ctk.CTkLabel(self, text="", text_color="red")
        self.label_info.pack(pady=5)

        ctk.CTkButton(self, text="Login", command=self.check_login).pack(pady=10)

        self.button_to_new_user = ctk.CTkButton(
            self,
            text="Neuer Account",
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

        H2 = ctk.CTkFont(family="Segoe UI", size=48, weight="normal", slant="italic")

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
        self.entry_email.grid(row=1, column=0, padx=10, pady=10)
        self.label_email_not_valid = ctk.CTkLabel(self, text="", text_color="red")
        self.label_email_not_valid.grid(row=2, column=0, sticky="nsew", padx=10, pady=0)

        # PW
        self.entry_pw = ctk.CTkEntry(self, placeholder_text="Passwort", show="●")
        self.entry_pw.grid(row=1, column=1, padx=10, pady=10)

        # Name
        self.entry_name = ctk.CTkEntry(self, placeholder_text="Dein Name")
        self.entry_name.grid(row=3, column=0, padx=10, pady=10)

        # Matrikelnummer
        self.entry_matrikelnummer = ctk.CTkEntry(
            self, placeholder_text="Deine Matrikelnummer"
        )
        self.entry_matrikelnummer.grid(row=3, column=1, padx=10, pady=10)

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
        self.entry_semesteranzahl.grid(row=5, column=1, padx=10, pady=10)

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
            self,
            text="Startdatum auswählen",
            command=self.start_datum_calendar_at_button,
        )
        self.button_startdatum.grid(row=7, column=1, padx=10, pady=10)

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
            self, text="Zieldatum auswählen", command=self.ziel_datum_calendar_at_button
        )
        self.button_zieldatum.grid(row=8, column=1, padx=10, pady=10)

        self.label_zieldatum_variable = ctk.CTkLabel(
            self, textvariable=self.selected_zieldatum
        )
        self.label_zieldatum_variable.grid(
            row=8, column=0, sticky="e", padx=10, pady=10
        )

        self.selected_zieldatum_real: str

        # Submit-Button
        self.button_submit = ctk.CTkButton(self, text="Weiter", command=self.on_submit)
        self.button_submit.grid(row=10, column=1, padx=10, pady=10)
        self.label_leere_felder = ctk.CTkLabel(self, text="", text_color="red")
        self.label_leere_felder.grid(row=9, column=1, sticky="nsew", padx=10, pady=10)

        # Zurück-Button
        self.button_back = ctk.CTkButton(
            self, text="Zurück", command=lambda: self.after(0, self.go_to_login)
        )
        self.button_back.grid(row=10, column=0, padx=10, pady=10)

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

        popup_w, popup_h = 320, 320
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
            font="Arial 14",
            selectmode="day",
            locale="de_DE",
            date_pattern="yyyy-mm-dd",
            mindate=mindate_start,
            maxdate=maxdate_start,
            showweeknumbers=False,
        )

        cal_start.pack(fill="both", expand=True)

        def save():
            self.selected_startdatum.set(cal_start.get_date())
            self.selected_startdatum_real = cal_start.get_date()
            top.destroy()

        self.save_button_start = ctk.CTkButton(top, text="ok", command=save)
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

        popup_w, popup_h = 320, 320
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
        if self.studiengaenge_dict == {}:
            self.studiengaenge_dict = {0: "z.B. Medizin"}
        self.search_combo_studiengang = SearchableComboBox(
            self, options=self.studiengaenge_dict
        )
        self.search_combo_studiengang.focus()
        self.search_combo_studiengang.pack(pady=20)

        # Gesamt-ECTS-Punkte
        self.label_ects = ctk.CTkLabel(
            self, text="Wie viele ECTS-Punkte hat dein Studium?"
        )
        self.label_ects.pack(pady=5)
        self.entry_ects = ctk.CTkEntry(self, placeholder_text="ECTS-Punkte")
        self.entry_ects.pack(pady=10)
        self.label_no_int = ctk.CTkLabel(self, text="", text_color="red")
        self.label_no_int.pack(pady=5)

        # Modul-Anzahl
        self.label_modulanzahl = ctk.CTkLabel(
            self, text="Wie viele Module hat Dein Studiengang?"
        )

        self.label_modulanzahl.pack(pady=10)
        modulvalues = [str(i) for i in range(1, 101)]
        self.entry_modulanzahl = ctk.CTkOptionMenu(
            self,
            values=modulvalues,
        )
        self.entry_modulanzahl.pack(pady=10)

        # Submit-Button
        self.button_submit = ctk.CTkButton(self, text="Weiter", command=self.on_submit)
        self.button_submit.pack(pady=20)
        self.label_leere_felder = ctk.CTkLabel(self, text="", text_color="red")
        self.label_leere_felder.pack(pady=5)

        # Zurück-Button
        self.button_back = ctk.CTkButton(
            self, text="Zurück", command=lambda: self.after(0, self.go_to_login)
        )
        self.button_back.pack(pady=20)

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
        if self.search_combo_studiengang.get_value() == "z.B. Medizin":
            self.label_leere_felder.configure(text="Etwas ist nicht ausgefüllt.")
            return
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

        MATERIAL_FONT = ctk.CTkFont(
            family="Material Symbols Sharp", size=26, weight="normal", slant="roman"
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
        dash_label.grid(row=0, column=0, sticky="nw", padx=0, pady=0)

        # rechter Frame
        right_frame = ctk.CTkFrame(top_frame, fg_color="transparent")
        right_frame.grid(row=0, column=1, sticky="e", padx=0, pady=0)

        # Menu-Button
        # TODO: Menu ist im moment leer, evtl. OptionMenu? oder Toplevel-Window?
        self.menu_button = ctk.CTkButton(
            right_frame,
            text="menu",
            width=10,
            fg_color="transparent",
            text_color="black",
            hover_color="gray95",
            border_color="black",
            font=MATERIAL_FONT,
            anchor="e",
            command=self.menu_on_button,
        )
        self.menu_button.pack(anchor="e", pady=(0, 2))

        # TODO: Was wenn hochschule zu lang?
        # Name-Label
        name_label_text = f"{self.data['name']}\n{self.data['studiengang']}\n{self.data['hochschule']}"
        name_label = ctk.CTkLabel(
            right_frame,
            text=name_label_text,
            font=INFO,
            justify="right",
        )
        name_label.pack(anchor="e", padx=10, pady=0)

        # --- DATES-FRAME ---
        dates_frame.grid_columnconfigure(0, weight=1)
        dates_frame.grid_columnconfigure(1, weight=0)
        dates_frame.grid_columnconfigure(2, weight=1)

        # Start-Label
        start_label = ctk.CTkLabel(
            dates_frame,
            text=f"Start: \n{self.data['startdatum']}",
            font=H3,
            justify="left",
        )
        start_label.grid(row=0, column=0, sticky="w", padx=5)

        # Heute-Label
        if self.data["exmatrikulationsdatum"] is not None:
            heute_label_text = (
                f"Exmatrikulationsdatum:\n{self.data['exmatrikulationsdatum']}"
            )
        else:
            heute_label_text = f"Heute:\n{self.data['heute']}"

        heute_label = ctk.CTkLabel(
            dates_frame, text=heute_label_text, font=H3, justify="center"
        )
        heute_label.grid(row=0, column=1, sticky="nsew", padx=5)

        # Ziel-Label
        ziel_label = ctk.CTkLabel(
            dates_frame,
            text=f"Ziel: \n{self.data['zieldatum']}",
            font=H3,
            justify="right",
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
        balken_frame = ctk.CTkFrame(semester_frame, fg_color="transparent")
        balken_frame.grid(row=1, column=0, columnspan=1, sticky="ew", padx=0, pady=4)

        semester_frame.grid_columnconfigure(0, weight=1)

        for semester in self.data["semester"]:
            if semester["status"] == "SemesterStatus.ZURUECKLIEGEND":
                color = "#29C731"
            elif (
                semester["status"] == "SemesterStatus.AKTUELL"
                and self.data["exmatrikulationsdatum"] is None
            ):
                color = "#FEC109"
            elif (
                semester["status"] == "SemesterStatus.AKTUELL"
                and self.data["exmatrikulationsdatum"] is not None
            ):
                color = "#F20D0D"
            elif semester["status"] == "SemesterStatus.ZUKUENFTIG":
                color = "#D9D9D9"
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
                text=f"Semester {semester['nummer']}\nBeginn: {semester['beginn']}\nEnde: {semester['ende']}",
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
                        font=MATERIAL_FONT,
                        text="check_circle",
                        text_color="#29C731",
                        fg_color="transparent",
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
                        text=f"{enrollment['modul_name']}\nBegonnen: {enrollment['einschreibe_datum']}\nAbgeschlossen: {enrollment['end_datum']}\nNote: {enrollment['enrollment_note']}\nStatus: Abgeschlossen",
                    )
                elif status == "IN_BEARBEITUNG":
                    one_frame.grid_columnconfigure(i, weight=1, uniform="modul_icons")
                    icon = ctk.CTkButton(
                        one_frame,
                        font=MATERIAL_FONT,
                        text="pending",
                        text_color="#FEC109",
                        fg_color="transparent",
                        hover_color="white",
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
                        text=f"{enrollment['modul_name']}\nBegonnen: {enrollment['einschreibe_datum']}\nStatus: In Bearbeitung",
                    )
                elif status == "NICHT_BESTANDEN":
                    one_frame.grid_columnconfigure(i, weight=1, uniform="modul_icons")
                    icon = ctk.CTkButton(
                        one_frame,
                        font=MATERIAL_FONT,
                        text="cancel",
                        text_color="#F20D0D",
                        fg_color="transparent",
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
                        text=f"{enrollment['modul_name']}\nBegonnen: {enrollment['einschreibe_datum']}\nStatus: Nicht bestanden",
                    )
                else:
                    raise ValueError(f"Enrollment hat keinen gültigen Status: {status}")
            else:
                one_frame.grid_columnconfigure(i, weight=1, uniform="modul_icons")
                icon = HoverButton(
                    one_frame,
                    font=MATERIAL_FONT,
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
            text_color="#29C731",
            text=f"Abgeschlossen: {self.data['abgeschlossen']}",
            justify="right",
        )
        in_bearbeitung_label = ctk.CTkLabel(
            text_module_frame,
            font=H2,
            text_color="#FEC109",
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
            text_color="red",
            text=f"Nicht bestanden: {self.data['nicht_bestanden']}",
            justify="right",
        )

        abgeschlossen_label.grid(row=0, column=1, sticky="e", pady=0, padx=10)
        in_bearbeitung_label.grid(row=1, column=1, sticky="e", pady=0, padx=10)
        ausstehend_label.grid(row=2, column=1, sticky="e", pady=0, padx=10)
        if self.data["nicht_bestanden"] > 0:
            nicht_bestanden_label.grid(row=3, column=1, sticky="e", pady=0, padx=10)

        # ---ECTS-FRAME---
        ects_color = "#29C731"
        if (
            self.data["exmatrikulationsdatum"] is not None
            and self.data["erarbeitete_ects"] != self.data["gesamt_ects"]
        ):
            # Exmatrikuliert und nicht alle ECTS-Punkte erreicht
            ects_color = "#F20D0D"

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
            text_color="#D9D9D9",
            text=f"/{self.data['gesamt_ects']}",
        )

        ects_label.pack()
        ects_max_label.pack(side="right", anchor="e")
        ects_erreicht_label.pack(side="right", anchor="e")

        # ---NOTEN-FRAME---
        if self.data["notendurchschnitt"] != "--":
            if self.data["notendurchschnitt"] > self.data["zielnote"]:
                noten_color = "#F20D0D"
            else:
                noten_color = "#29C731"
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

    def menu_on_button(self):
        self.menu(anchor=self.menu_button)

    def menu(self, anchor):
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

        popup_w, popup_h = 320, 320
        sw = top.winfo_screenwidth()
        sh = top.winfo_screenheight()

        if x + popup_w > sw:
            x = max(0, bx + bw - popup_w)
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

        for k, v in values.items():
            ctk.CTkButton(
                top,
                border_spacing=0,
                fg_color="gray95",
                hover_color="gray85",
                border_color="black",
                text_color="black",
                text=k,
                command=v,
            ).pack()

    def logout(self):
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

        titel_label = ctk.CTkLabel(self, text="Zu neuem Modul anmelden", font=H2italic)
        titel_label.pack(pady=20)
        # Wie heißt dieses Modul?
        modul_name_label = ctk.CTkLabel(self, text="Wie heißt dieses Modul?")
        modul_name_label.pack(pady=10)
        self.modul_name_entry = ctk.CTkEntry(self, placeholder_text="Modulname")
        self.modul_name_entry.pack(pady=0)
        self.modul_name_entry.focus()
        # Wie ist der Modul-Code?
        modul_code_label = ctk.CTkLabel(self, text="Wie lautet der Modul-Code?")
        modul_code_label.pack(pady=10)
        self.modul_code_entry = ctk.CTkEntry(self, placeholder_text="Modul-Code")
        self.modul_code_entry.pack(pady=0)
        ToolTip(
            self.modul_code_entry,
            text="Jedes Modul hat einen eindeutigen Identifikationscode",
        )
        # Wie viele ECTS-Punkte hat dieses Modul?
        modul_ects_label = ctk.CTkLabel(
            self, text="Wie viele ECTS-Punkte hat dieses Modul?"
        )
        modul_ects_label.pack(pady=10)
        self.modul_ects_entry = ctk.CTkEntry(self, placeholder_text="z.B. 5")
        self.modul_ects_entry.pack(pady=0)
        self.label_no_int = ctk.CTkLabel(self, text="", text_color="red")
        self.label_no_int.pack(pady=0)

        # Welcher Kurs oder welche Kurse müssen absolviert werden?
        kurs_name_label = ctk.CTkLabel(
            self, text="Welcher Kurs oder welche Kurse müssen absolviert werden?"
        )
        kurs_name_label.pack(pady=10)

        self.kurse_eingabe_feld = DynamicEntries(self, initial_rows=1, max_rows=10)
        self.kurse_eingabe_feld.pack(pady=10)

        # Wie viele Prüfungsleistungen hat dieses Modul?
        pl_label = ctk.CTkLabel(
            self, text="Wie viele Prüfungsleistungen hat dieses Modul?"
        )
        pl_label.pack(pady=10)
        pl_values = [str(i) for i in range(1, 20)]
        self.pl_anzahl_entry = ctk.CTkOptionMenu(self, values=pl_values)
        self.pl_anzahl_entry.pack(pady=10)

        # Wann hast du mit diesem Modul begonnen?
        self.selected_startdatum = tk.StringVar(value="Noch kein Datum ausgewählt")

        self.label_startdatum = ctk.CTkLabel(
            self, text="Wann hast du mit diesem Modul begonnen?"
        )
        self.label_startdatum.pack(pady=10)
        self.button_startdatum = ctk.CTkButton(
            self,
            text="Startdatum auswählen",
            command=self.start_datum_calendar_at_button,
        )
        self.button_startdatum.pack(pady=0)

        self.label_startdatum_variable = ctk.CTkLabel(
            self, textvariable=self.selected_startdatum
        )
        self.label_startdatum_variable.pack(pady=0)

        self.selected_startdatum_real: str

        # Submit-Button
        submit_button = ctk.CTkButton(self, text="Weiter", command=self.on_submit)
        submit_button.pack(pady=10)
        self.leere_felder_label = ctk.CTkLabel(self, text="", text_color="red")
        self.leere_felder_label.pack(pady=0)

        # Zurück-Button
        back_button = ctk.CTkButton(
            self, text="Zurück", command=lambda: self.after(0, self.go_to_dashboard)
        )
        back_button.pack(pady=10)

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

        popup_w, popup_h = 320, 320
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
            font="Arial 14",
            selectmode="day",
            locale="de_DE",
            date_pattern="yyyy-mm-dd",
            mindate=mindate_start,
            maxdate=maxdate_start,
            showweeknumbers=False,
        )

        cal_start.pack(fill="both", expand=True)

        def save():
            self.selected_startdatum.set(cal_start.get_date())
            self.selected_startdatum_real = cal_start.get_date()
            top.destroy()

        self.save_button_start = ctk.CTkButton(top, text="ok", command=save)
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

        modul_frame = ctk.CTkFrame(self, fg_color="gray95")
        modul_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=0)

        kurse_frame = ctk.CTkFrame(self, fg_color="gray95")
        kurse_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        pl_frame = ctk.CTkFrame(self, fg_color="gray95")
        pl_frame.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)
        pl_frame.grid_columnconfigure(0, weight=1)

        status_frame = ctk.CTkFrame(self, fg_color="gray95")
        status_frame.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)

        noten_frame = ctk.CTkFrame(self, fg_color="gray95")
        noten_frame.grid(row=2, column=1, sticky="nsew", padx=5, pady=5)

        eingeschrieben_frame = ctk.CTkFrame(self, fg_color="gray95")
        eingeschrieben_frame.grid(row=3, column=0, sticky="nsew", padx=5, pady=5)

        abgeschlossen_frame = ctk.CTkFrame(self, fg_color="gray95")
        abgeschlossen_frame.grid(row=3, column=1, sticky="nsew", padx=5, pady=5)

        # FONTS
        # H1 = ctk.CTkFont(family="Segoe UI", size=84, weight="normal", slant="italic")
        # H1notitalic = ctk.CTkFont(
        #     family="Segoe UI", size=84, weight="normal", slant="roman"
        # )
        # H2 = ctk.CTkFont(family="Segoe UI", size=32, weight="normal", slant="roman")
        H2italic = ctk.CTkFont(
            family="Segoe UI", size=32, weight="normal", slant="italic"
        )
        H3 = ctk.CTkFont(family="Segoe UI", size=22, weight="normal", slant="roman")
        INFO = ctk.CTkFont(family="Segoe UI", size=16, weight="normal", slant="roman")

        MATERIAL_FONT = ctk.CTkFont(
            family="Material Symbols Sharp", size=26, weight="normal", slant="roman"
        )

        self.grid_columnconfigure(0, weight=1, uniform="half")
        self.grid_columnconfigure(1, weight=1, uniform="half")

        # MODUL FRAME ÜBERSCHRIFT
        modul_frame.grid_columnconfigure(0, weight=1)
        modul_frame.grid_columnconfigure(1, weight=0)

        modul_ueber_label = ctk.CTkLabel(
            modul_frame, text="MODUL:", font=H2italic, justify="left"
        )
        modul_ueber_label.grid(row=0, sticky="nw", padx=10, pady=0)
        modul_name_label = MultiLineLabel(
            modul_frame,
            width=85,
            text=f"{self.enrollment_data['modul_name']}",
            font=H3,
            justify="left",
        )
        modul_name_label.grid(row=1, sticky="nw", padx=10, pady=0)
        modul_code_label = ctk.CTkLabel(
            modul_frame,
            text=f"{self.enrollment_data['modul_code']}",
            font=INFO,
            justify="left",
        )
        modul_code_label.grid(row=2, column=0, sticky="nw", padx=10, pady=0)

        modul_close_button = ctk.CTkButton(
            modul_frame,
            text="Close",
            font=MATERIAL_FONT,
            width=10,
            fg_color="transparent",
            text_color="black",
            hover_color="gray90",
            border_color="black",
            command=lambda: self.after(0, self.go_to_dashboard),
        )
        modul_close_button.grid(row=0, column=1, sticky="ne")

        modul_ects_label = ctk.CTkLabel(
            modul_frame,
            text=f"{self.enrollment_data['modul_ects']} ECTS-Punkte",
            font=INFO,
            justify="right",
        )
        modul_ects_label.grid(row=2, column=1, sticky="e", padx=10, pady=0)

        # KURSE FRAME
        kurse_ueber_label = ctk.CTkLabel(
            kurse_frame, text="KURSE:", font=H2italic, justify="left"
        )
        kurse_ueber_label.grid(row=0, sticky="nw", padx=10, pady=0)

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
        pl_ueber_label.grid(row=0, sticky="nw", padx=10, pady=0)
        # Titelzeile
        pl_tabelle_title_frame = ctk.CTkFrame(pl_frame, fg_color="gray95")
        pl_tabelle_title_frame.grid(row=1, sticky="ew", padx=0, pady=0)
        for column, txt in enumerate(
            ["Nr.", "1. Versuch", "2. Versuch", "3. Versuch", "Gewichtung:"]
        ):
            label = ctk.CTkLabel(
                pl_tabelle_title_frame, text=txt, font=INFO, justify="left"
            )
            label.grid(
                row=0,
                column=column,
                padx=(5 if column == 0 else 0, 5),
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
            row_frame = ctk.CTkFrame(pl_frame, fg_color="gray95")
            row_frame.grid(row=i + 2, sticky="ew", padx=0, pady=2)
            for column in range(5):
                row_frame.grid_columnconfigure(column, weight=1 if column > 0 else 0)

            index_label = ctk.CTkLabel(
                row_frame,
                text=f"{i + 1}.",
                font=INFO,
                justify="left",
            )
            index_label.grid(row=0, column=0, padx=5, sticky="w")

            gewicht = versuche[0]["teilpruefung_gewicht"] if versuche else "--"
            gewicht_label = ctk.CTkLabel(
                row_frame,
                text=f"{gewicht}",
                font=INFO,
                justify="right",
            )
            gewicht_label.grid(row=0, column=4, padx=10, sticky="e")

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
                            hover_color="gray85",
                            hovercolor=BLAU,
                            hovertext="add_box",
                            defaultcolor="black",
                            defaulttext="check_box_outline_blank",
                            text="check_box_outline_blank",
                            text_color="black",
                            font=MATERIAL_FONT,
                            command=lambda pl_id=versuch["id"],
                            e_id=self.enrollment_id: self.after(
                                0, self.go_to_pl, pl_id, e_id
                            ),
                        )
                        add_pl_button.grid(
                            row=0,
                            column=v,
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
                            hover_color="gray85",
                            text_color=GRAU,
                            text="Select",
                            font=MATERIAL_FONT,
                            state="disabled",
                        )
                        disabled_button.grid(
                            row=0,
                            column=v,
                        )
                        zustand_letzte_pl = zustand[3]
                    elif versuch["ist_bestanden"]:
                        pl_bestanden_button = ctk.CTkButton(
                            row_frame,
                            width=10,
                            fg_color="transparent",
                            hover_color="gray85",
                            text_color=GRUEN,
                            text="select_check_box",
                            font=MATERIAL_FONT,
                            command=lambda pl_id=versuch["id"],
                            e_id=self.enrollment_id: self.after(
                                0, self.go_to_pl, pl_id, e_id
                            ),
                        )
                        pl_bestanden_button.grid(
                            row=0,
                            column=v,
                        )
                        ToolTip(
                            pl_bestanden_button,
                            text=f"Note: {versuch['note']}\nDatum: {versuch['datum']}",
                        )
                        zustand_letzte_pl = zustand[1]
                    elif versuch["note"] is not None and not versuch["ist_bestanden"]:
                        pl_nicht_bestanden_button = ctk.CTkButton(
                            row_frame,
                            width=10,
                            fg_color="transparent",
                            hover_color="gray85",
                            text_color=ROT,
                            text="disabled_by_default",
                            font=MATERIAL_FONT,
                            command=lambda pl_id=versuch["id"],
                            e_id=self.enrollment_id: self.after(
                                0, self.go_to_pl, pl_id, e_id
                            ),
                        )
                        pl_nicht_bestanden_button.grid(
                            row=0,
                            column=v,
                        )
                        ToolTip(
                            pl_nicht_bestanden_button,
                            text=f"Note: {versuch['note']}\nDatum: {versuch['datum']}",
                        )
                        zustand_letzte_pl = zustand[2]

        # STATUS FRAME
        status = str(self.enrollment_data["status"]).replace("_", " ").capitalize()
        status_label = ctk.CTkLabel(status_frame, text=f"Status: {status}", font=INFO)
        status_label.pack()

        # NOTEN FRAME
        noten_label = ctk.CTkLabel(
            noten_frame,
            text=f"Deine Note: {self.enrollment_data['enrollment_note']}",
            font=INFO,
        )
        noten_label.pack()

        # EINGESCHRIEBEN FRAME
        eingeschrieben_label = ctk.CTkLabel(
            eingeschrieben_frame,
            text=f"Eingeschrieben am: {self.enrollment_data['einschreibe_datum']}",
            font=INFO,
        )
        eingeschrieben_label.pack()

        # ABGESCHLOSSEN FRAME
        abgeschlossen_label = ctk.CTkLabel(
            abgeschlossen_frame,
            text=f"Abgeschlossen am: {self.enrollment_data['end_datum']}",
            font=INFO,
        )
        abgeschlossen_label.pack()


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

        # FONTS
        # H1 = ctk.CTkFont(family="Segoe UI", size=84, weight="normal", slant="italic")
        # H1notitalic = ctk.CTkFont(
        #     family="Segoe UI", size=84, weight="normal", slant="roman"
        # )
        # H2 = ctk.CTkFont(family="Segoe UI", size=32, weight="normal", slant="roman")
        H2italic = ctk.CTkFont(
            family="Segoe UI", size=32, weight="normal", slant="italic"
        )
        H3 = ctk.CTkFont(family="Segoe UI", size=22, weight="normal", slant="roman")
        # INFO = ctk.CTkFont(family="Segoe UI", size=16, weight="normal", slant="roman")

        MATERIAL_FONT = ctk.CTkFont(
            family="Material Symbols Sharp", size=26, weight="normal", slant="roman"
        )

        pl_frame = ctk.CTkFrame(self, fg_color="gray95")
        pl_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=0)

        # PL FRAME ÜBERSCHRIFT
        pl_frame.grid_columnconfigure(0, weight=1)
        pl_frame.grid_columnconfigure(1, weight=0)

        pl_ueber_label = ctk.CTkLabel(
            pl_frame, text="PRÜFUNGSLEISTUNG:", font=H2italic, justify="left"
        )
        pl_ueber_label.grid(row=0, sticky="nw", padx=10, pady=0)
        pl_name_label = MultiLineLabel(
            pl_frame,
            width=85,
            text=f"Prüfung: {int(self.pl_data['teilpruefung']) + 1}, Versuch: {self.pl_data['versuch']}",
            font=H3,
            justify="left",
        )
        pl_name_label.grid(row=1, sticky="nw", padx=10, pady=0)

        pl_close_button = ctk.CTkButton(
            pl_frame,
            text="Close",
            font=MATERIAL_FONT,
            width=10,
            fg_color="transparent",
            text_color="black",
            hover_color="gray90",
            border_color="black",
            command=lambda: self.after(0, self.go_to_enrollment, self.enrollment_id),
        )
        pl_close_button.grid(row=0, column=1, sticky="ne")

        if self.pl_data["note"] is None:
            pl_add_frame = ctk.CTkFrame(self, fg_color="gray95")
            pl_add_frame.grid(
                row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=10
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
            self.pl_add_note_entry = ctk.CTkOptionMenu(pl_add_frame, values=noten)
            self.pl_add_note_entry.pack(pady=5)

            self.selected_pl_datum = tk.StringVar(value="Noch kein Datum ausgewählt")

            pl_add_datum_label = ctk.CTkLabel(
                pl_add_frame, text="Wann hast Du die Prüfung abgegeben?"
            )
            pl_add_datum_label.pack(pady=10)
            self.pl_button_datum = ctk.CTkButton(
                pl_add_frame,
                text="Prüfungsdatum auswählen",
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
                pl_add_frame, text="Speichern", command=self.on_submit
            )
            self.button_submit.pack(pady=10)
            self.label_leere_felder = ctk.CTkLabel(
                pl_add_frame, text="", text_color="red"
            )
            self.label_leere_felder.pack(pady=10)

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

        popup_w, popup_h = 320, 320
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
            font="Arial 14",
            selectmode="day",
            locale="de_DE",
            date_pattern="yyyy-mm-dd",
            mindate=mindate_start,
            maxdate=maxdate_start,
            showweeknumbers=False,
        )

        cal_start.pack(fill="both", expand=True)

        def save():
            self.selected_pl_datum.set(cal_start.get_date())
            self.selected_pl_datum_real = cal_start.get_date()
            top.destroy()

        self.save_button = ctk.CTkButton(top, text="ok", command=save)
        self.save_button.pack(pady=5)


class SettingsFrame(ctk.CTkFrame):
    def __init__(self, master, controller: Controller, go_to_dashboard):
        super().__init__(master, fg_color="transparent")
        # TODO


class ExFrame(ctk.CTkFrame):
    def __init__(self, master, controller: Controller, go_to_dashboard):
        super().__init__(master, fg_color="transparent")
        # TODO


class ZieleFrame(ctk.CTkFrame):
    def __init__(self, master, controller: Controller, go_to_dashboard):
        super().__init__(master, fg_color="transparent")
        # TODO


class UeberFrame(ctk.CTkFrame):
    def __init__(self, master, controller: Controller, go_to_dashboard):
        super().__init__(master, fg_color="transparent")
        # TODO


class App(ctk.CTk):
    def __init__(self):
        super().__init__(fg_color=BACKGROUND)

        self.controller = Controller()
        self.title("Dashboard")
        self.geometry("960x640")  # orig: 960x540
        ctk.set_appearance_mode("light")
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
            self, controller=self.controller, go_to_dashboard=self.show_dashboard
        )
        self.current_frame.pack(fill="both", expand=True)

    def show_exmatrikulation(self):
        if self.current_frame:
            self.current_frame.pack_forget()
            self.current_frame.destroy()
            self.update_idletasks()
        self.current_frame = ExFrame(
            self, controller=self.controller, go_to_dashboard=self.show_dashboard
        )
        self.current_frame.pack(fill="both", expand=True)

    def show_ziele(self):
        if self.current_frame:
            self.current_frame.pack_forget()
            self.current_frame.destroy()
            self.update_idletasks()
        self.current_frame = ZieleFrame(
            self, controller=self.controller, go_to_dashboard=self.show_dashboard
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
