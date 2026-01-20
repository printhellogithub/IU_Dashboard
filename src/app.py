from __future__ import annotations
import customtkinter as ctk
import datetime
from pathlib import Path
import tkinter as tk
import tkinter.ttk as ttk
from tkcalendar import Calendar
from email_validator import EmailNotValidError
from typing import Callable
import textwrap
import webbrowser
import argparse
import logging

from src.main import Controller
from utils.logging_config import setup_logging

logger = logging.getLogger(__name__)

# GLOBAL - Farben
BACKGROUND = "#FFFFFF"
BACKGROUND_DARK = "#696969"
GRUEN = "#29C731"
DUNKELGRUEN = "#05920C"
HELLGRUEN = "#BFF9C2"
GELB = "#FEC109"
DUNKELGELB = "#C59609"
ROT = "#F20D0D"
DUNKELROT = "#9B0202"
HELLROT = "#FF8585"
GRAU = "#D9D9D9"
DUNKELBLAU = "#0749BB"
BLAU = "#0A64FF"
HELLBLAU = "#B5D0FF"

# GLOBAL - Pfade
BASE_DIR = Path(__file__).resolve().parent.parent


def from_iso_to_ddmmyyyy(date: str | datetime.date | None) -> str:
    """Wandelt ein ISO-Datum in das deutsches Datumsformat ``dd.mm.yyyy``.

    Die Funktion akzeptiert ISO-Daten als ``datetime.date``-Objekt oder als
    String im Format ``yyyy-mm-dd``. Ist die Eingabe ``None``, wird ein leerer
    String zurückgegeben. Ungültige Datumsstrings werden unverändert
    zurückgegeben.

    Args:
        date (str | datetime.date | None): Datum in ISO-Format oder None.

    Returns:
        str:
        Datum im Format ``dd.mm.yyyy``. Bein ``None`` ein leerer String.
        Bei ungültigen Eingabe-Strings wird der Originalwert zurückgegeben.
    """
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


def parse_args() -> argparse.Namespace:
    """Parsed Command Line Argumente und fügt mögliche Argumente hinzu.

    Konfiguriert folgende Command Line Argumente:
        * ``--offline``: Aktiviert Offline-Modus.
        * ``--debug``: Aktivert Logging-DEBUG-Level.
        * ``--log_to_console``: Aktiviert Log-Anzeige in der Console
        * ``--follow_system_mode``: Light-/Dark-Mode wird von System übernommen
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--offline", action="store_true", help="Startet das Programm im Offline-Modus"
    )
    parser.add_argument(
        "--debug", action="store_true", help="Aktiviert Logging-DEBUG-Level"
    )
    parser.add_argument(
        "--log_to_console",
        action="store_true",
        help="Aktiviert Log-Anzeige in der Console",
    )
    parser.add_argument(
        "--follow_system_mode",
        action="store_true",
        help="Light-/Dark-Mode wird von System übernommen",
    )
    return parser.parse_args()


class Icons:
    """Zentrale Sammlung vordefinierter Icons für das Dashboard.

    Die Klasse speichert Unicode-Punkte der Schriftart ``Segoe Fluent Icons`` von Microsoft in Variablen.
    Die Namen der Variablen stammen von der vorher verwendeten Schriftart ``Material Symbols Sharp`` von Google,
    die durch Segoe ersetzt wurde.
    """

    # Frame schließen
    CLOSE = "\uf78a"  # e711

    # Menu
    MENU = "\ue700"

    # Enrollment ausstehend (leerer Kreis)
    RADIO_BUTTON_UNCHECKED = "\uecca"  # ea3a

    # Enrollment hinzufügen (hover)
    ADD_CIRCLE = "\uecc8"  # E710

    # Enrollment in Bearbeitung
    PENDING = "\ue895"  # f143 f16a

    # Enrollment: Bestanden
    CHECK_CIRCLE = "\ue930"  # ec61

    # Enrollment nicht bestanden
    CANCEL = "\uea39"  # eb90

    # Prüfungsleistung (leere Checkbox)
    CHECK_BOX_OUTLINE_BLANK = "\uf16b"

    # Prüfungsleistung hinzufügen (hover)
    ADD_BOX = "\uf164"

    # nicht auswählbare Prüfungsleistung ()
    SELECT = "\ue72e"  # nutze CHECK_BOX_OUTLINE_BLANK und mache Button disabled.

    # Prüfungsleistung bestanden
    SELECT_CHECK_BOX = "\uf16c"

    # Prüfungsleistung nicht bestanden
    DISABLED_BY_DEFAULT = "\uf16d"

    # Account löschen
    WARNING = "\ue7ba"  # e730 oder e783


class Fonts:
    """Zentrale Sammlung vordefinierter Fonts für das Dashboard.

    Die Klasse erzeugt verschiedene ``CTkFont``-Objekte auf Basis von
    ``Segoe UI`` für Text und Überschriften, sowie
    ``Segoe Fluent Icons`` für Icons. Dadurch stehen konsistente
    Schriftgrößen und -stile im gesamten User Interface zur Verfügung.

    Diese Schriftarten sind auf Windows 11 Systemen vorinstalliert und
    somit für das Dashboard verfügbar.
    Auf anderen Systemen muss ``Segoe Fluent Icons`` installiert werden.
    Auf Mac-Systemen wird statt ``Segoe UI`` der automatische System-Fallback verwendet.

    Attribute:
        LOGIN (ctk.CTkFont): Sehr groß und italic für DASHBOARD-Banner auf Login-Screen (140px).
        H1_italic (ctk.CTkFont): H1-Überschriften italic (84px).
        H1 (ctk.CTkFont): H1 Überschriften roman (84px).
        H1_5_italic (ctk.CTkFont): Mittelgroße Überschriften italic (48px).
        H2_italic (ctk.CTkFont): Mittlere Überschriften italic (32px).
        H2 (ctk.CTkFont): Mittlere Überschriften roman (32px).
        H3 (ctk.CTkFont): Kleine Überschriften roman (22px).
        TEXT (ctk.CTkFont): Standard Text Font (16px).
        ICONS (ctk.CTkFont): Standard Icon Font (26px).
        ICONS_BIG (ctk.CTkFont): großer Icon Font (42px).
    """

    def __init__(self) -> None:
        """Erzeugt und konfiguriert ``CTkFont``-Objekte."""
        self.ICONS = ctk.CTkFont(
            family="Segoe Fluent Icons", size=26, weight="normal", slant="roman"
        )
        self.ICONS_BIG = ctk.CTkFont(
            family="Segoe Fluent Icons", size=42, weight="normal", slant="roman"
        )
        self.LOGIN = ctk.CTkFont(
            family="Segoe UI", size=140, weight="normal", slant="italic"
        )
        self.H1_italic = ctk.CTkFont(
            family="Segoe UI", size=84, weight="normal", slant="italic"
        )
        self.H1 = ctk.CTkFont(
            family="Segoe UI", size=84, weight="normal", slant="roman"
        )
        self.H1_5_italic = ctk.CTkFont(
            family="Segoe UI", size=48, weight="normal", slant="italic"
        )
        self.H2_italic = ctk.CTkFont(
            family="Segoe UI", size=32, weight="normal", slant="italic"
        )
        self.H2 = ctk.CTkFont(
            family="Segoe UI", size=32, weight="normal", slant="roman"
        )
        self.H3 = ctk.CTkFont(
            family="Segoe UI", size=22, weight="normal", slant="roman"
        )
        self.TEXT = ctk.CTkFont(
            family="Segoe UI", size=16, weight="normal", slant="roman"
        )


class SearchableComboBox(ctk.CTkComboBox):
    """Eine ComboBox, die ihre Optionen dynamisch nach Nutzereingabe filtert.

    Statt einer Liste erwartet das Widget ein Dictionary, dessen Keys IDs
    (ints) und dessen Values die anzuzeigenden Texte sind. Bei jeder
    Tastatureingabe wird die Dropdown-Liste gefiltert (ohne
    Groß-/Kleinschreibung). Ist kein Treffer vorhanden, wird der aktuelle
    Text angezeigt, sodass auch benutzerdefinierte Werte möglich sind.

    Attribute:
        options_dict (dict[int, str]): Original-Dictionary mit ID-Werte-Paaren.
        all_values (list[str]): Liste aller Werte des options-dictionary.

    Beispiel:
        >>> options = {1: "Option A", 2: "Option B", 3: "Option C"}
        >>> combo = SearchableComboBox(root, options=options)
        >>> combo.get_value()   # Eingabetext
        >>> combo.get_id()      # zugehörige ID oder None
    """

    def __init__(self, master, options: dict[int, str], **kwargs) -> None:
        """Initialisiert die SearchableComboBox.

        Args:
        master:
            Das Eltern-Widget.
        options (dict[int, str]):
            Dictionary, dessen Keys IDs (int) und dessen Values
            die anzuzeigenden Texte sind.
        **kwargs:
            Weitere Keyword-Argumente für ``CTkComboBox``
        """
        self.options_dict = options
        self.all_values = list(options.values())

        super().__init__(master, values=self.all_values, **kwargs)

        self.bind("<KeyRelease>", self.on_key_release)

    def on_key_release(self, event) -> None:
        """Filtert die Dropdown-Werte basierend auf aktueller Eingabe.

        Der eingegebene Text wird mit allen verfügbaren Werten
        (ohne Groß-/Kleinschreibung) verglichen.
        Ist das Textfeld leer, werden alle Optionen angezeigt.
        Wenn keine Übereinstimmungen gefunden werden, wird der
        eingegebene Text angezeigt.

        Args:
            event:
                KeyRelease-Event, welches durch den User ausgelöst wird.
        """
        text = self.get()
        if not text:
            self.configure(values=self.all_values)
            return
        filtered = [value for value in self.all_values if text.lower() in value.lower()]
        self.configure(values=filtered or [text])

    def get_value(self) -> str:
        """Gibt den aktuellen Eingabetext zurück"""
        return self.get()

    def get_id(self) -> int | None:
        """Gibt die ID (key) des aktuellen Wertes zurück.

        Wenn der eingegebene Wert einem Value im ``options_dict`` entspricht,
        wird dessen Key zurückgegeben. Existiert kein solcher Eintrag,
        wird ``None`` zurückgegeben.
        """
        value = self.get()
        for k, v in self.options_dict.items():
            if v == value:
                return k
        return None


class MultiLineLabel(ctk.CTkLabel):
    """Ein Label, das Text automatisch auf eine angegebene Breite (Anzahl an Zeichen) umbrechen kann."""

    def __init__(self, master, text, width, **kwargs) -> None:
        """
        Initialisiert das Label mit automatisch umgebrochenen Text.

        Args:
            master: Das Eltern-Widget.
            text (str): Text, der automatisch umgebrochen werden soll.
            width (int): Maximale Anzahl an Zeichen in einer Zeile.
            **kwargs:
                Weitere Parameter für ``CTkLabel``.
        """
        wrapped_text = textwrap.fill(text, width=width)
        super().__init__(master, text=wrapped_text, **kwargs)


class ToolTip:
    """ToolTip-Widget für CustomTkinter-Elemente.

    Beim Überfahren eines Widgets mit der Maus wird ein kleines Overlay mit erklärendem Text angezeigt.
    """

    def __init__(self, widget, text) -> None:
        """Inititalisiert ToolTip-Objekt und bindet Maus-Events.

        Args:
            widget:
                Das Widget, dem der ToolTip zugeordnet wird.
            text:
                Im ToolTip angezeigter Text.
        """
        self.widget = widget
        self.text = text
        self.tip = None
        widget.bind("<Enter>", self.show, add="+")
        widget.bind("<Leave>", self.hide, add="+")
        widget.bind("<ButtonPress>", self.hide, add="+")
        widget.bind("<Button-1>", self.hide, add="+")
        widget.bind("<ButtonRelease-1>", self.hide, add="+")

    def show(self, event) -> None:
        """Zeigt den ToolTip nahe der aktuellen Mausposition an.

        Ein rahmenloses ``CTkToplevel``-Fenster wird erzeugt, sofern
        noch keines existiert. Der Text wird mithilfe eines ``CTkLabel``
        innerhalb des Overlays dargestellt.

        Args:
            event:
                Tkinter-Event, das die Mausposition enthält.
        """
        if self.tip:
            return
        # Position 10px rechts/unten vom Mauszeiger
        x = event.x_root + 10
        y = event.y_root + 10
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

    def hide(self, event) -> None:
        """Blendet den ToolTip aus, sobald die Maus das Widget verlässt

        Falls ein ToolTip-Fenster existiert, wird es zerstört und der
        interne Referenzwert zurückgesetzt.

        Args:
            event:
                Tkinter-Event, ausgelöst bei Verlassen des Widgets.
        """
        if self.tip:
            self.tip.destroy()
            self.tip = None


class HoverButton(ctk.CTkButton):
    """Ein Button, der beim Überfahren der Maus Text/Icon und Textfarbe ändert."""

    def __init__(
        self, master, hovertext, hovercolor, defaulttext, defaultcolor, **kwargs
    ) -> None:
        """Initialisiert HoverButton und bindet Maus-Events.

        Args:
            master: Das Eltern-Widget.
            hovertext (str): Text/Icon, das während des Hover-Zustands angezeigt werden soll.
            hovercolor (str): Text-/Icon-Farbe während des Hover-Zustands.
            defaulttext (str): Standard-Text/Icon, wenn nicht gehovert wird.
            defaultcolor (str): Standard-Farbe, wenn nicht gehovert wird.
            **kwargs: Zusätzliche Keyword-Argumente die an die Eltern-Klasse CTkButton weitergegeben werden.
        """
        super().__init__(master=master, **kwargs)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.hovertext = hovertext
        self.hovercolor = hovercolor
        self.defaulttext = defaulttext
        self.defaultcolor = defaultcolor

    def on_enter(self, event=None) -> None:
        """Wird aufgerufen, wenn der Mauszeiger den Button betritt.

        Ändert Text/Icon und Text-/Icon-Farbe in konfigurierte Hover-Werte."""
        self.configure(text=self.hovertext, text_color=self.hovercolor)

    def on_leave(self, event=None) -> None:
        """Wird aufgerufen, wenn der Mauszeiger den Button verlässt.

        Setzt Text/Icon sowie Text-/Icon-Farbe auf die Standardwerte zurück."""
        self.configure(text=self.defaulttext, text_color=self.defaultcolor)


class DynamicEntries(ctk.CTkFrame):
    """Frame, der dynamisch mehrere Eingabezeilen (z.B. Kursname/Kursnummer) erzeugen und verwalten kann.

    Das Widget stellt einen Header mit Spaltentiteln und einen scrollbaren Bereich bereit.
    Über einen Add-Button können neue Eingabezeilen bis zu einer Maximalanzahl hinzugefügt werden.
    Ausgefüllte Zeilen können über ``get_values`` strukturiert ausgelesen werden;
    Zeilen mit leeren Feldern werden ignoriert.
    """

    def __init__(
        self,
        master,
        *,
        label_links: str,
        label_rechts: str,
        placeholder_links: str,
        placeholder_rechts: str,
        initial_rows: int = 1,
        max_rows: int = 10,
    ) -> None:
        """Initialisiert ein DynamicEntries-Objekt.

        Args:
            master:
                Eltern-Widget.
            label_links (str):
                Bezeichnung der linken Spalte.
            label_rechts (str):
                Bezeichnung der rechten Spalte.
            placeholder_links (str):
                Platzhaltertext des Eingabefeldes links.
            placeholder_rechts (str):
                Platzhaltertext des Eingabefeldes rechts.
            initial_rows (int):
                Anzahl der Eingabezeilen beim Start.
            max_rows (int):
                Maximale Anzahl der vom User erzeugbaren Eingabezeilen.
        """
        super().__init__(
            master, fg_color="transparent", border_color="black", border_width=2
        )
        self.max_rows = max_rows
        self.rows: list[dict[str, object]] = []

        # Layout
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        # Header Frame
        self.header = ctk.CTkFrame(self, fg_color="transparent")
        self.header.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 0))
        self.header.grid_columnconfigure(0, weight=1)
        self.header.grid_columnconfigure(1, weight=1)
        # Label für label_links
        self.title_links = ctk.CTkLabel(self.header, text=label_links)
        self.title_links.grid(row=0, column=0, sticky="w", padx=5)
        # Label für label_rechts
        self.title_rechts = ctk.CTkLabel(self.header, text=label_rechts)
        self.title_rechts.grid(row=0, column=1, sticky="e", padx=5)

        # Font für Icon
        icons = ctk.CTkFont(
            family="Segoe Fluent Icons", size=26, weight="normal", slant="roman"
        )
        # Add-Button
        self.add_button = ctk.CTkButton(
            self.header,
            # text="add_circle",
            text="\ue710",
            font=icons,
            width=36,
            text_color="black",
            fg_color="transparent",
            border_color="black",
            border_spacing=2,
            border_width=2,
            hover_color="gray95",
            command=lambda: self.add_row(
                placeholder_links=placeholder_links,
                placeholder_rechts=placeholder_rechts,
            ),
        )
        self.add_button.grid(row=0, column=2, sticky="e", padx=(8, 0))

        # ScrollableFrame für dynamische Eingabezeilen
        self.list_frame = ctk.CTkScrollableFrame(
            self, label_text="", fg_color="transparent"
        )
        self.list_frame.grid(row=1, column=0, sticky="nsew", padx=8, pady=8)
        self.list_frame.grid_columnconfigure(0, weight=1)
        self.list_frame.grid_columnconfigure(1, weight=1)

        # Startzustand
        for _ in range(max(1, initial_rows)):
            self.add_row(
                placeholder_links=placeholder_links,
                placeholder_rechts=placeholder_rechts,
            )

    def add_row(self, placeholder_links: str, placeholder_rechts: str) -> None:
        """Fügt eine neue Eingabezeile hinzu.

        Die Platzhaltertexte der Eingabefelder können mit ``placeholder_links``
        und ``placeholder_rechts`` konfiguriert werden. Falls die maximale Anzahl
        an Eingabezeilen erreicht ist, wird keine neue erstellt.

        Args:
            placeholder_links (str):
                Platzhaltertext des Eingabefeldes links.
            placeholder_rechts (str):
                Platzhaltertext des Eingabefeldes rechts.
        """
        if len(self.rows) >= self.max_rows:
            return

        entry_links = ctk.CTkEntry(self.list_frame, placeholder_text=placeholder_links)

        entry_rechts = ctk.CTkEntry(
            self.list_frame, placeholder_text=placeholder_rechts
        )

        self.rows.append(
            {
                "entry_links": entry_links,
                "entry_rechts": entry_rechts,
            }
        )
        self.regrid()

    def regrid(self) -> None:
        """Platziert alle Eingabezeilen neu.

        Sorgt dafür, dass alle Entry-Widgets passend angeordnet werden.
        Wird automatisch beim Hinzufügen neuer Zeilen aufgerufen.
        """
        for i, row in enumerate(self.rows):
            row["entry_links"].grid(row=i, column=0, sticky="w", padx=(8, 4), pady=4)  # type: ignore
            row["entry_rechts"].grid(row=i, column=1, sticky="e", padx=(8, 4), pady=4)  # type: ignore

    def get_values(self) -> dict[str, str]:
        """Gibt die ausgefüllten Eingaben als Dictionary zurück.

        Es werden nur Zeilen berücksichtigt, in denen beide Felder ausgefüllt sind.
        Der linke Eintrag wird als Schlüssel und der rechte Eintrag als Wert verwendet.

        Returns:
            dict[str, str]:
                Ein Dictionary in der Form ``{entry_links: entry_rechts}``.
        """
        values = {}
        for row in self.rows:
            entry_links = row["entry_links"].get().strip()  # type: ignore
            entry_rechts = row["entry_rechts"].get().strip()  # type: ignore
            if entry_links and entry_rechts:
                values.update({entry_links: entry_rechts})
        return values


class CalendarMixin:
    """Mixin für CTk-Widgets, das ein Kalender-Popup bereitstellt.

    Die aufnehmende Klasse muss ein CTk-Widget sein (z.B. CTkFrame), da das
    Popup relativ zu diesem Widget positioniert wird. Das Mixin stellt die
    Methode `_open_calendar_popup` bereit, welche einen unter dem Anchor-Widget
    ausgerichteten Kalender erzeugt.
    """

    def _open_calendar_popup(
        self,
        anchor: ctk.CTkBaseClass,
        mindate: datetime.date,
        maxdate: datetime.date,
        on_date_selected: Callable[[datetime.date], None],
    ) -> None:
        """Öffnet einen Kalender als Popup unterhalb des angegebenen Widgets.

        Args:
            anchor:
                Widget, an dem das Popup positioniert werden soll.
            mindate:
                Frühestes auswählbares Datum.
            maxdate:
                Spätestes auswählbares Datum.
            on_date_selected:
                Callback, der mit dem ausgewählten ``datetime.date``-Objekt
                aufgerufen wird.
        """
        top = ctk.CTkToplevel(self)
        top.overrideredirect(True)
        top.transient(anchor.winfo_toplevel())
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

        cal = Calendar(
            top,
            font="SegoeUI 12",
            selectmode="day",
            locale="de_DE",
            date_pattern="yyyy-mm-dd",
            mindate=mindate,
            maxdate=maxdate,
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
        cal.pack(fill="both", expand=True)

        def save() -> None:
            """Übergibt ausgewähltes Datums-Objekt und zerstört Popup."""
            iso_str = cal.get_date()
            date_obj = datetime.date.fromisoformat(iso_str)
            on_date_selected(date_obj)
            top.destroy()

        save_button = ctk.CTkButton(
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
        save_button.pack(pady=5)


class MenuMixin:
    """Mixin für CTk-Widgets, das ein Menü-Popup bereitstellt.

    Die aufnehmende Klasse muss ein CTk-Widget sein (z.B. CTkFrame), da das
    Popup relativ zu diesem Widget positioniert wird. Das Mixin stellt die
    Methode `_open_menu_popup` bereit, welche ein unter dem Anchor-Widget
    ausgerichtetes Menü erzeugt und interne Verwaltung über `menu_popup`
    übernimmt.
    """

    def _open_menu_popup(
        self,
        anchor: ctk.CTkBaseClass,
        values: dict[str, Callable],
    ) -> None:
        """Öffnet ein Menü als Popup unterhalb des angegebenen Widgets.

        Für jedes Element in ``values`` wird ein Button im Popup angezeigt.
        Dabei sind die Keys die Buttontexte, die Values die aufzurufenden Callbacks.
        Das Popup schließt sich bei Focus-Verlust.

        Args:
            anchor:
                Widget, an dem das Popup positioniert werden soll.
            values:
                Ein Dictionary, dessen Keys die angezeigten Button-Texte sind,
                und dessen Values die aufzurufenden Funktionen darstellen.
        """
        top = ctk.CTkToplevel(self)
        self.menu_popup = top
        top.overrideredirect(True)
        top.transient(anchor.winfo_toplevel())
        top.attributes("-topmost", True)
        top.bind("<FocusOut>", lambda e: self.close_menu())

        bx = anchor.winfo_rootx()
        by = anchor.winfo_rooty()
        bw = anchor.winfo_width()
        bh = anchor.winfo_height()

        popup_w = 180
        item_height = 32
        popup_h = item_height * len(values)

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

        for key, value in values.items():
            button = ctk.CTkButton(
                top,
                fg_color=(BACKGROUND, BACKGROUND_DARK),
                hover_color="gray95",
                border_color="black",
                border_width=1,
                text_color="black",
                text=key,
                command=lambda v=value: (self.close_menu(), v()),
            )
            button.pack(fill="both", expand=True, pady=1, padx=1)

    def close_menu(self) -> None:
        """Zerstört Popup, falls es existiert und setzt internen Verweis ``menu_popup`` auf ``None``."""
        if self.menu_popup and self.menu_popup.winfo_exists():
            self.menu_popup.destroy()
        self.menu_popup = None


class LoginFrame(ctk.CTkFrame):
    """Frame, der zum Programmstart sichtbar ist und einen Login-Bereich anzeigt.

    Dieser Frame bietet Eingabefelder für Email und Passwort sowie
    Buttons zum Anmelden und zum Wechsel in den User-Registrierungs-Frame.

    Attribute:
        controller (Controller):
            Zuständig für Authentifizierung und weitere Geschäftslogik.
        go_to_dashboard (callable):
            Callback-Funktion, um zum Dashboard zu navigieren.
        go_to_new_user (callable):
            Callback-Funktion, um zum User-Registrierungs-Frame zu navigieren.
        label_info (ctk.CTkLabel):
            Label zum Anzeigen von Fehlermeldungen.
    """

    def __init__(
        self, master, controller: Controller, go_to_dashboard, go_to_new_user
    ) -> None:
        """
        Initialisiert den Login-Frame und baut UI-Elemente auf.

        Args:
            master:
                Eltern-Widget, das u. a. die verwendeten Fonts bereitstellt.
            controller:
                Instanz, die den Login fachlich auswertet.
            go_to_dashboard:
                Callback-Funktion, wird bei erfolgreichem Login aufgerufen, um zum Dashboard zu wechseln.
            go_to_new_user:
                Callback-Funktion, um zum User-Registrierungs-Frame zu navigieren.
        """
        super().__init__(master, fg_color="transparent")

        self.controller = controller
        self.go_to_dashboard = go_to_dashboard
        self.go_to_new_user = go_to_new_user

        self.fonts = master.fonts
        self.icons = master.icons

        ctk.CTkLabel(self, text="DASHBOARD", font=self.fonts.LOGIN).pack(pady=20)

        entry_email = ctk.CTkEntry(self, placeholder_text="Email-Adresse")
        entry_email.focus()
        entry_email.pack(pady=5)

        entry_password = ctk.CTkEntry(
            self,
            placeholder_text="Passwort",
            show="●",
        )
        entry_password.pack(pady=5)
        entry_password.bind(
            "<Return>",
            lambda event: self.check_login(entry_email.get(), entry_password.get()),
        )

        self.label_info = ctk.CTkLabel(self, text="", text_color=ROT)
        self.label_info.pack(pady=5)

        button_login = ctk.CTkButton(
            self,
            text="Login",
            text_color="black",
            fg_color="transparent",
            border_color="black",
            border_spacing=2,
            border_width=2,
            hover_color="gray95",
            command=lambda: self.check_login(entry_email.get(), entry_password.get()),
        )
        button_login.pack(pady=10)

        button_to_new_user = ctk.CTkButton(
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
        button_to_new_user.pack(pady=20)

    def check_login(self, email: str, password: str) -> None:
        """Prüft die eingegebenen Zugangsdaten und reagiert entsprechend.

        Die Methode delegiert die Prüfung an ``controller.login``.
        Bei Erfolg wird über ``go_to_dashboard`` zum Dashboard gewechselt.
        Bei negativer Prüfung wird eine Fehlermeldung im Info-Label angezeigt.

        Args:
            email (str):
                Eingegebene Email-Adresse.
            password (str):
                Eingegebenes Passwort.
        """
        if self.controller.login(email, password):
            self.after(0, self.go_to_dashboard)
        else:
            self.label_info.configure(text="Login fehlgeschlagen")


class NewUserFrame(ctk.CTkFrame, CalendarMixin):
    """Frame für die Erstellung eines neuen Accounts.

    Der Frame bildet den ersten Teil des Registrierungs-Flow ab und erfasst E-Mail,
    Passwort, Name, Matrikelnummer, Hochschule, Semesteranzahl,
    Wunsch-Abschlussnote sowie Start- und Zieldatum des Studiums.
    Nach erfolgreicher Validierung werden die Daten gesammelt und
    an Teil Zwei der Registrierung, dem Studiengang-Auswahl-Frame, weitergegeben.
    """

    def __init__(
        self,
        master,
        controller: Controller,
        go_to_login,
        go_to_studiengang_auswahl,
    ) -> None:
        """Initialisiert den Registrierungs-Frame und baut Header und Formular auf.

        Args:
            master:
                Eltern-Widget, das u. a. die Fonts bereitstellt.
            controller (Controller):
                Instanz, die Validierung und Datenzugriffe und generell die Geschäftslogik übernimmt.
            go_to_login:
                Callback ohne Parameter, um zum Login-Frame zurückzukehren.
            go_to_studiengang_auswahl:
                Callback, der mit einem ``cache``-Dictionary aufgerufen wird und
                zur Studiengang-Auswahl navigiert.
        """
        super().__init__(master, fg_color="transparent")

        self.controller = controller
        self.go_to_login = go_to_login
        self.go_to_studiengang_auswahl = go_to_studiengang_auswahl

        self.fonts = master.fonts
        self.icons = master.icons

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)

        self._init_header()
        self._init_form()

    def _init_header(self) -> None:
        """Erzeugt den Header-Bereich mit Titel und Close-Button."""
        header_frame = ctk.CTkFrame(
            self,
            fg_color=(BACKGROUND, BACKGROUND_DARK),
            border_color="black",
            border_width=2,
        )
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        header_frame.grid_columnconfigure(0, weight=1)
        header_frame.grid_columnconfigure(1, weight=0)

        header_ueber_label = ctk.CTkLabel(
            header_frame,
            text="Dein Account",
            font=self.fonts.H1_5_italic,
            justify="left",
        )
        header_ueber_label.grid(row=0, sticky="nw", padx=10, pady=10)

        header_close_button = ctk.CTkButton(
            header_frame,
            text=self.icons.CLOSE,
            font=self.fonts.ICONS,
            width=10,
            fg_color="transparent",
            text_color="black",
            hover_color="gray95",
            command=lambda: self.after(0, self.go_to_login),
        )
        header_close_button.grid(row=0, column=1, padx=(0, 2), pady=(2, 0), sticky="ne")

    def _init_form(self) -> None:
        """Erzeugt das Formular zur Abfrage von Benutzer- und Studiendaten."""
        nu_frame = ctk.CTkFrame(
            self,
            fg_color=(BACKGROUND, BACKGROUND_DARK),
            border_color="black",
            border_width=2,
        )
        nu_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        for column in range(4):
            nu_frame.grid_columnconfigure(column, weight=1)
        for row in range(11):
            nu_frame.grid_rowconfigure(row, weight=1)

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

        # Passwort
        self.entry_password_label = ctk.CTkLabel(nu_frame, text="Dein Passwort")
        self.entry_password_label.grid(row=1, column=2, sticky="ew", padx=10, pady=10)
        self.entry_password = ctk.CTkEntry(
            nu_frame, placeholder_text="Passwort", show="●"
        )
        self.entry_password.grid(row=1, column=3, sticky="ew", padx=10, pady=10)

        # Name
        self.entry_name_label = ctk.CTkLabel(nu_frame, text="Dein Name")
        self.entry_name_label.grid(row=2, column=0, padx=10, pady=10)
        self.entry_name = ctk.CTkEntry(nu_frame, placeholder_text="Max Mustermann")
        self.entry_name.grid(row=2, column=1, sticky="ew", padx=10, pady=10)

        # Matrikelnummer
        self.entry_matrikelnummer_label = ctk.CTkLabel(
            nu_frame, text="Deine Matrikelnummer"
        )
        self.entry_matrikelnummer_label.grid(
            row=2, column=2, sticky="ew", padx=10, pady=10
        )
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

        self.selected_startdatum_real: str | None = None

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

        self.selected_zieldatum_real: str | None = None

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

    def on_submit(self) -> None:
        """Validiert die Formulareingaben und leitet bei Erfolg weiter.

        Ablauf:
            * E-Mail prüfen und ausschließen, dass es schon einen Account gibt.
            * Pflichtfelder (Passwort, Name, Matrikelnummer, Semesteranzahl,
            Hochschule, Start- und Zieldatum) auf leere Eingaben prüfen.
            * Hochschule neu anlegen, falls sie noch nicht
            in der Datenbank existiert.
            * Alle validierten Eingaben in einem ``cache``-Dictionary sammeln
            und an ``go_to_studiengang_auswahl`` übergeben.

        Bei Validierungsfehlern werden entsprechende Fehlermeldungen in den
        dafür vorgesehenen Labels angezeigt und die Methode bricht ab.
        """
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

        # validiere User-input
        self.list_for_validation = [
            self.entry_password.get(),
            self.entry_name.get(),
            self.entry_matrikelnummer.get(),
            self.entry_semesteranzahl.get(),
            self.search_combo.get_value(),
        ]

        if not self.validate_entries(entries=self.list_for_validation):
            return

        # Prüfe, ob Datumsangaben vorhanden sind
        try:
            self.selected_startdatum_str = self.selected_startdatum_real
            self.selected_zieldatum_str = self.selected_zieldatum_real
        except AttributeError:
            self.label_leere_felder.configure(
                text="Start oder Zieldatum nicht ausgewählt."
            )
            return

        # User-input validiert, speicher Eingaben
        self.selected_password = self.entry_password.get()
        self.selected_name = self.entry_name.get()
        self.selected_matrikelnummer = self.entry_matrikelnummer.get()
        self.selected_semesteranzahl = int(self.entry_semesteranzahl.get())
        self.selected_zielnote = self.entry_zielnote
        self.selected_hochschule_name = self.search_combo.get_value()
        self.selected_hochschule_id = self.search_combo.get_id()

        # Lege Hochschule an, falls noch nicht in db
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

        # Lege cache an, um über Daten in anderem Frame zu verfügen
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
        self.after(0, lambda: self.go_to_studiengang_auswahl(cache=cache))

    def start_datum_calendar_at_button(self) -> None:
        """Öffnet den Kalender zur Auswahl des Studienstartdatums."""
        self._open_calendar_popup(
            anchor=self.button_startdatum,
            mindate=datetime.date(2010, 1, 1),
            maxdate=datetime.date.today(),
            on_date_selected=self._set_startdatum,
        )

    def _set_startdatum(self, date: datetime.date) -> None:
        """Verarbeitet das im Kalender gewählte Studienstartdatum.

        Aktualisiert sowohl die sichtbare Textvariable als auch den
        intern genutzten ISO-String für das Startdatum.
        """
        self.selected_startdatum.set(from_iso_to_ddmmyyyy(date=date))
        self.selected_startdatum_real = date.isoformat()

    def ziel_datum_calendar_at_button(self) -> None:
        """Öffnet den Kalender zur Auswahl des Studienzieldatums."""
        self._open_calendar_popup(
            anchor=self.button_zieldatum,
            mindate=datetime.date.today(),
            maxdate=datetime.date(year=2200, month=12, day=31),
            on_date_selected=self._set_zieldatum,
        )

    def _set_zieldatum(self, date: datetime.date) -> None:
        """Verarbeitet das im Kalender gewählte Studienzieldatum.

        Aktualisiert sowohl die sichtbare Textvariable als auch den
        intern genutzten ISO-String für das Zieldatum.
        """
        self.selected_zieldatum.set(from_iso_to_ddmmyyyy(date=date))
        self.selected_zieldatum_real = date.isoformat()

    def slider_zielnote_event(self, value: float) -> None:
        """Aktualisiert die Wunsch-Abschlussnote basierend auf dem Slider-Wert.

        Der übergebene Wert wird auf eine Nachkommastelle gerundet,
        intern gespeichert und im Label angezeigt.

        Args:
            value (float): Aktueller Slider-Wert zwischen 1.0 und 4.0.
        """
        self.entry_zielnote = round(float(value), 1)
        self.label_note.configure(text=f"{self.entry_zielnote}")

    def validate_entries(self, entries: list[str]) -> bool:
        """Prüft, ob alle Werte der übergebenen Liste nicht leer sind.

        Leere oder nur aus Leerzeichen bestehende Einträge führen zu einer
        Fehlermeldung im Label ``label_leere_felder`` und die Methode gibt
        ``False`` zurück. Sind alle Werte gültig, wird ``True`` zurückgegeben.

        Args:
            entries (list[str]):
                Liste der zu prüfenden Eingaben.

        Returns:
            bool:
                ``True``, wenn alle Felder gefüllt sind, sonst ``False``.
        """
        for value in entries:
            if str(value).strip() == "":
                self.label_leere_felder.configure(text="Etwas ist nicht ausgefüllt.")
                return False
        return True


class StudiengangAuswahlFrame(ctk.CTkFrame):
    """Frame für die Auswahl und Anlage eines Studiengangs.

    Dieser Frame bildet den zweiten Teil des Registrierungs-Flows ab.
    Er erfasst Name, Gesamt-ECTS und Modulanzahl des Studiengangs.
    Die Eingaben werden validiert, bei Bedarf wird der Studiengang
    über den Controller erzeugt. Die gesammelten Daten werden in den Cache
    übernommen und an den Controller zur Accounterstellung weitergegeben,
    bevor der Benutzer zum Dashboard weitergeleitet wird.
    """

    def __init__(
        self,
        master,
        controller: Controller,
        cache,
        go_to_dashboard,
        go_to_login,
    ) -> None:
        """Initialisiert den Studiengang-Auswahl-Frame und baut Header und Formular auf.

        Args:
            master:
                Eltern-Widget, das u. a. die Fonts bereitstellt.
            controller (Controller):
                Instanz, die Datenzugriffe und Geschäftslogik übernimmt.
            cache (dict):
                Dictionary mit bereits erfassten Registrierungsdaten,
                das um Studiengang-Informationen ergänzt wird.
            go_to_dashboard:
                Callback ohne Parameter, um nach erfolgreicher Registrierung
                zum Dashboard zu wechseln.
            go_to_login:
                Callback ohne Parameter, um zurück zum Login-Frame zu wechseln.
        """
        super().__init__(master, fg_color="transparent")

        self.controller = controller
        self.cache = cache
        self.go_to_dashboard = go_to_dashboard
        self.go_to_login = go_to_login

        self.fonts = master.fonts
        self.icons = master.icons

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)

        self._init_header()
        self._init_form()

    def _init_header(self) -> None:
        """Erzeugt den Header-Bereich mit Titel und Close-Button."""
        header_frame = ctk.CTkFrame(
            self,
            fg_color=(BACKGROUND, BACKGROUND_DARK),
            border_color="black",
            border_width=2,
        )
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        header_frame.grid_columnconfigure(0, weight=1)
        header_frame.grid_columnconfigure(1, weight=0)

        header_ueber_label = ctk.CTkLabel(
            header_frame, text="Dein Account", font=self.fonts.H2_italic, justify="left"
        )
        header_ueber_label.grid(row=0, sticky="nw", padx=10, pady=10)

        header_close_button = ctk.CTkButton(
            header_frame,
            text=self.icons.CLOSE,
            font=self.fonts.ICONS,
            width=10,
            fg_color="transparent",
            text_color="black",
            hover_color="gray95",
            command=lambda: self.after(0, self.go_to_login),
        )
        header_close_button.grid(row=0, column=1, padx=(0, 2), pady=(2, 0), sticky="ne")

    def _init_form(self) -> None:
        """Erzeugt das Formular zur Abfrage von Studiengangsdaten."""
        sa_frame = ctk.CTkFrame(
            self,
            fg_color=(BACKGROUND, BACKGROUND_DARK),
            border_color="black",
            border_width=2,
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
        # self.entry_ects = ctk.CTkEntry(sa_frame, placeholder_text="ECTS-Punkte")
        # self.entry_ects.pack(pady=10)
        self.entry_ects = ctk.CTkComboBox(
            sa_frame,
            # placeholder_text="ECTS-Punkte",
            values=[str(p) for p in range(30, 390, 30)],
        )
        self.entry_ects.pack(pady=10)
        self.label_no_int = ctk.CTkLabel(sa_frame, text="", text_color=ROT)
        self.label_no_int.pack(pady=5)
        ToolTip(
            self.entry_ects,
            text="Wenn der Studiengang in der Datenbank vorhanden ist, \n"
            "wird der vorhandene Wert an ECTS-Punkten \n"
            "für diesen Studiengang verwendet.",
        )

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

    def validate_ects(self, ects: str) -> bool:
        """Prüft, ob der eingegebene ECTS-Wert gültig ist.

        Wird nicht mehr benötigt, da CTk.Entry zu CTk.Combobox geändert wurde.

        Eine Eingabe ist gültig, wenn sie sich in eine Ganzzahl zwischen
        1 und 500 umwandeln lässt. Im Fehlerfall wird eine passende
        Fehlermeldung im Label ``label_no_int`` angezeigt.

        Args:
            ects (str): ECTS-Wert als String.

        Returns:
            bool: ``True``, wenn der Wert gültig ist, sonst ``False``.
        """
        try:
            number = int(ects)
        except ValueError:
            self.label_no_int.configure(text="Muss eine (Ganz-) Zahl sein")
            return False

        if number > 0 and number <= 500:
            return True

        self.label_no_int.configure(text="Zahl muss zwischen 1 und 500 liegen")
        return False

    def on_submit(self) -> None:
        """Validiert die Eingaben und erstellt bei Erfolg den Account.

        Ablauf:
            * ECTS-Punkte-Eingabe validieren (Ganzzahl zwischen 1 und 500).
            * Studiengangsname prüfen (nicht leer, maximale Länge 50 Zeichen).
            * Prüfen, ob der Studiengang für die gewählte Hochschule bereits
            existiert; falls nicht, wird er neu angelegt.
            * Studiengang-ID und weitere Angaben (ECTS, Modulanzahl) in den
            Cache übernehmen.
            * Über den Controller den Account erstellen und zum Dashboard wechseln.

        Bei Validierungsfehlern werden entsprechende Fehlermeldungen in den
        dafür vorgesehenen Labels angezeigt und die Methode bricht ab.
        """
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
        self.selected_studiengang_name = self.entry_studiengang.get().strip()

        if self.selected_studiengang_name.strip() == "":
            self.label_leere_felder.configure(text="Etwas ist nicht ausgefüllt.")
            return

        if (
            self.selected_studiengang_name.lower()
            not in self.controller.get_studiengaenge_von_hs(
                self.cache["hochschulid"]
            ).values()
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
            if v.lower() == self.selected_studiengang_name.lower():
                self.selected_studiengang_id = k
            else:
                raise ValueError(
                    "Datenbankrückgabe entspricht nicht Eingabewert: Studiengang"
                )

        self.selected_modulanzahl = int(self.entry_modulanzahl.get())

        self.cache["studiengang_ects"] = self.selected_ects
        self.cache["modulanzahl"] = self.selected_modulanzahl
        self.cache["studiengang_name"] = self.selected_studiengang_name
        self.cache["studiengang_id"] = self.selected_studiengang_id

        self.controller.erstelle_account(self.cache)

        self.after(0, self.go_to_dashboard)


class DashboardFrame(ctk.CTkFrame, MenuMixin):
    """Hauptansicht des Programms: Das Dashboard.

    Der Frame zeigt eine Übersicht über Studienverlauf und Fortschritt,
    sodass Studienziele eingehalten werden können:
    Start- und Zieldatum, Zeitfortschritt, Semesterübersicht, Modulstatus,
    erarbeitete ECTS-Punkte und Notenschnitt. Über die Modulicons können
    neue Module gebucht werden und über das Menü können weitere
    Aktionen wie Einstellungen, Exmatrikulation, Zielanpassung und Logout
    aufgerufen werden.
    """

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
    ) -> None:
        """Initialisiert das Dashboard und baut alle Bereiche auf.

        Args:
            master:
                Eltern-Widget, das u. a. die Fonts bereitstellt.
            controller (Controller):
                Instanz, die die Dashboard-Daten lädt und Geschäftslogik bereitstellt.
            go_to_login:
                Callback ohne Parameter, um zum Login-Frame zu wechseln.
            go_to_add_enrollment:
                Callback ohne Parameter zu Frame, um ein Enrollment, eine Einschreibung in ein Modul, hinzuzufügen.
            go_to_enrollment:
                Callback, der Details zu einer bestehenden Einschreibung in ein Modul anzeigt.
                Erwartet eine Enrollment-ID als Parameter.
            go_to_settings:
                Callback, um den Einstellungen-Frame aufzurufen.
            go_to_ex:
                Callback, um den Exmatrikulations-Frame aufzurufen.
            go_to_ziele:
                Callback zur Ansicht, in der Ziele angepasst werden können.
            go_to_ueber:
                Callback zur „Über Dashboard“-Ansicht.
        """
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

        self.fonts = master.fonts
        self.icons = master.icons

        self.data = self.controller.load_dashboard_data()

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        for row in range(11):
            self.grid_rowconfigure(row, weight=1)

        self._init_header()
        self._init_dates()
        self._init_progress()
        self._init_semester()
        self._init_module()
        self._init_text_module()
        self._init_ects()
        self._init_noten()

    def _init_header(self) -> None:
        """Erzeugt den Header-Bereich mit Titel, Menü-Button und Benutzerinfos."""
        header_frame = ctk.CTkFrame(self, fg_color="transparent", height=130)
        header_frame.grid(
            row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=(2, 0)
        )

        header_frame.grid_columnconfigure(0, weight=1)
        header_frame.grid_rowconfigure(0, weight=0)
        header_frame.grid_propagate(False)

        # DASHBOARD-Label
        dash_label = ctk.CTkLabel(
            header_frame,
            text="DASHBOARD",
            font=self.fonts.H1_italic,
            justify="left",
            fg_color="transparent",
        )
        dash_label.grid(row=0, column=0, sticky="nw", padx=0, pady=(2, 0))

        # rechter Frame
        right_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        right_frame.grid(row=0, column=1, sticky="e", padx=0, pady=(2, 0))

        # Menu-Button
        self.menu_button = ctk.CTkButton(
            right_frame,
            text=self.icons.MENU,
            width=10,
            fg_color="transparent",
            text_color="black",
            hover_color="gray95",
            border_color="black",
            font=self.fonts.ICONS,
            anchor="e",
            command=self.menu_on_button,
        )
        self.menu_button.pack(anchor="e", pady=(0, 2))

        # Name-Studiengang-Hochschule-Label
        name_label_text = f"{self.data['name']}\n{self.data['studiengang']}\n{self.controller.get_hs_kurzname_if_notwendig(self.data['hochschule'], max_length=50)}"
        name_label = ctk.CTkLabel(
            right_frame,
            text=name_label_text,
            font=self.fonts.TEXT,
            justify="right",
        )
        name_label.pack(anchor="e", padx=10, pady=0)

    def _init_dates(self) -> None:
        """Erzeugt den Bereich mit Start-, Heute-/Exmatrikulations- und Zieldatum.

        Das aktuelle Datum bzw. Exmatrikulationsdatum wird relativ zur
        Zeitachse zwischen Start- und Zieldatum positioniert. Ist das
        Zieldatum überschritten, wird es rot dargestellt.
        """
        dates_frame = ctk.CTkFrame(self, fg_color="transparent")
        dates_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=10, pady=5)

        dates_frame.grid_columnconfigure(0, weight=0)
        dates_frame.grid_columnconfigure(1, weight=1)
        dates_frame.grid_columnconfigure(2, weight=0)
        dates_frame.grid_rowconfigure(0, weight=0)

        # Start-Label
        start_label = ctk.CTkLabel(
            dates_frame,
            text=f"Start: \n{from_iso_to_ddmmyyyy(self.data['startdatum'])}",
            font=self.fonts.H3,
            justify="left",
        )
        start_label.grid(row=0, column=0, sticky="w", padx=5)

        # Heute-Label (auch Exmatrikulation)
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
            font=self.fonts.H3,
            justify="center",
        )
        heute_label.place(relx=position, rely=0.5, anchor=anchor)

        # Ziel-Label
        if datetime.date.today() > self.data["zieldatum"]:
            ziel_color = ROT
        else:
            ziel_color = ("black", "#FFFFFF")

        ziel_label = ctk.CTkLabel(
            dates_frame,
            text=f"Ziel: \n{from_iso_to_ddmmyyyy(self.data['zieldatum'])}",
            font=self.fonts.H3,
            text_color=ziel_color,
            justify="right",
        )
        ziel_label.grid(row=0, column=2, sticky="e", padx=5)

    def _init_progress(self) -> None:
        """Erzeugt die Fortschrittsanzeige für den zeitlichen Studienverlauf.

        Die Farbe der Progressbar richtet sich nach dem Status:
            * rot, wenn exmatrikuliert und noch nicht alle ECTS erreicht sind
            * grün, wenn alle ECTS erreicht sind
            * blau, normales laufendes Studium (nicht alle ECTS erreicht, nicht exmatrikuliert)
        """

        progress_frame = ctk.CTkFrame(
            self,
            height=10,
            fg_color="transparent",
        )
        progress_frame.grid(
            row=2, column=0, columnspan=2, sticky="nsew", padx=10, pady=5
        )

        if (
            self.data["exmatrikulationsdatum"]
            and self.data["erarbeitete_ects"] < self.data["gesamt_ects"]
        ):
            progress_color = ROT
            background_color = HELLROT
        elif (
            self.data["exmatrikulationsdatum"]
            and self.data["erarbeitete_ects"] >= self.data["gesamt_ects"]
        ):
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

    def _init_semester(self) -> None:
        """Erzeugt die Semesterübersicht als Balken mit Farbcodierung.

        Jedes Semester wird als Segment dargestellt und abhängig vom Status
        (zurückliegend, aktuell, zukünftig, exmatrikuliert) farblich markiert.
        Tooltips zeigen Beginn und Ende der jeweiligen Semester an.
        """
        semester_frame = ctk.CTkFrame(self, fg_color="transparent")
        semester_frame.grid(
            row=3, column=0, columnspan=2, sticky="nsew", padx=10, pady=5
        )
        # Semester-Label
        semester_label = ctk.CTkLabel(
            semester_frame,
            text="Semester:",
            font=self.fonts.TEXT,
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
                # zurückliegende Semester immer grün
                color = GRUEN
            elif (
                # aktuelles Semester bei laufendem Studium -> gelb
                semester["status"] == "SemesterStatus.AKTUELL"
                and self.data["exmatrikulationsdatum"] is None
            ):
                color = GELB
            elif (
                # abgebrochenes Studium -> letztes begonnenes Semester -> rot
                semester["status"] == "SemesterStatus.AKTUELL"
                and self.data["exmatrikulationsdatum"] is not None
                and self.data["erarbeitete_ects"] < self.data["gesamt_ects"]
            ):
                color = ROT
            elif (
                # alle ECTS-Punkte erreicht -> aktuelles/letztes begonnenes Semester (erfolgreich exmatrikuliert) -> grün
                semester["status"] == "SemesterStatus.AKTUELL"
                and self.data["erarbeitete_ects"] >= self.data["gesamt_ects"]
            ):
                color = GRUEN
            elif semester["status"] == "SemesterStatus.ZUKUENFTIG":
                # zukünftige Semester immer grau
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

    def _init_module(self) -> None:
        """Erzeugt die Modul-/Enrollment-Übersicht als Icon-Leiste.

        Für jedes Modul wird je nach Enrollment-Status ein anderes Icon
        angezeigt (abgeschlossen, in Bearbeitung, nicht bestanden, noch offen).
        Offene Plätze werden als klickbare „add“-Buttons dargestellt, über die
        neue Enrollments angelegt werden können.
        """
        module_frame = ctk.CTkFrame(self, fg_color="transparent")
        module_frame.grid(row=4, column=0, columnspan=2, sticky="nsew", padx=10, pady=5)

        # Module-Label
        module_label = ctk.CTkLabel(
            module_frame,
            text="Module:",
            font=self.fonts.TEXT,
            justify="left",
            bg_color="transparent",
        )
        module_label.grid(row=0, column=0, sticky="w", padx=5)

        # Enrollment-Icons-Größe
        if self.data["modulanzahl"] < 39:
            size = 22
        elif self.data["modulanzahl"] < 49:
            size = 16
        elif self.data["modulanzahl"] < 56:
            size = 12
        else:
            size = 10

        ENROLLMENTICONS = ctk.CTkFont(
            family="Segoe Fluent Icons", size=size, weight="normal", slant="roman"
        )

        one_frame = ctk.CTkFrame(module_frame, fg_color="transparent")
        one_frame.grid(row=1, column=0, sticky="ew", padx=0, pady=4)

        module_frame.grid_columnconfigure(0, weight=1)
        # Enrollment-Icons platzieren
        for i in range(self.data["modulanzahl"]):
            if self.data["enrollments"] != [] and i < len(self.data["enrollments"]):
                enrollment = self.data["enrollments"][i]
                status = str(enrollment["status"])
                if status == "ABGESCHLOSSEN":
                    one_frame.grid_columnconfigure(i, weight=1, uniform="modul_icons")
                    icon = HoverButton(
                        one_frame,
                        font=ENROLLMENTICONS,
                        text=self.icons.CHECK_CIRCLE,
                        text_color=GRUEN,
                        defaulttext=self.icons.CHECK_CIRCLE,
                        defaultcolor=GRUEN,
                        hovertext=self.icons.CHECK_CIRCLE,
                        hovercolor=DUNKELGRUEN,
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
                    icon = HoverButton(
                        one_frame,
                        font=ENROLLMENTICONS,
                        text=self.icons.PENDING,
                        text_color=GELB,
                        defaulttext=self.icons.PENDING,
                        defaultcolor=GELB,
                        hovertext=self.icons.PENDING,
                        hovercolor=DUNKELGELB,
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
                    icon = HoverButton(
                        one_frame,
                        font=ENROLLMENTICONS,
                        text=self.icons.CANCEL,
                        text_color=ROT,
                        defaulttext=self.icons.CANCEL,
                        defaultcolor=ROT,
                        hovertext=self.icons.CANCEL,
                        hovercolor=DUNKELROT,
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
                    text=self.icons.RADIO_BUTTON_UNCHECKED,
                    text_color=GRAU,
                    defaulttext=self.icons.RADIO_BUTTON_UNCHECKED,
                    defaultcolor=GRAU,
                    hovertext=self.icons.ADD_CIRCLE,
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

    def _init_text_module(self) -> None:
        """Zeigt statistische Kennzahlen zu den Modulen an.

        Darstellt werden die Anzahl von jeweils abgeschlossenen, in Bearbeitung,
        ausstehenden und ggf. nicht bestandener Module. Links steht eine
        vertikale „Module“-Überschrift.
        """
        text_module_frame = ctk.CTkFrame(self, fg_color="transparent")
        text_module_frame.grid(row=5, column=0, sticky="nsew", padx=10, pady=5)
        # Module-vertikal-Label
        if self._get_appearance_mode() == "light":
            bg = BACKGROUND
        else:
            bg = BACKGROUND_DARK

        canvas = ctk.CTkCanvas(
            text_module_frame,
            width=100,
            height=120,
            bg=bg,
            highlightthickness=0,
            bd=0,
        )
        canvas.grid(row=0, column=0, rowspan=3, padx=10)
        canvas.create_text(
            30, 60, text="Module", angle=90, font=self.fonts.H2_italic, fill="black"
        )

        # STATS-Label
        abgeschlossen_label = ctk.CTkLabel(
            text_module_frame,
            font=self.fonts.H2,
            text_color=GRUEN,
            text=f"Abgeschlossen: {self.data['abgeschlossen']}",
            justify="right",
        )
        in_bearbeitung_label = ctk.CTkLabel(
            text_module_frame,
            font=self.fonts.H2,
            text_color=GELB,
            text=f"In Bearbeitung: {self.data['in_bearbeitung']}",
            justify="right",
        )
        ausstehend_label = ctk.CTkLabel(
            text_module_frame,
            font=self.fonts.H2,
            text_color="black",
            text=f"Ausstehend: {self.data['ausstehend']}",
            justify="right",
        )
        nicht_bestanden_label = ctk.CTkLabel(
            text_module_frame,
            font=self.fonts.H2,
            text_color=ROT,
            text=f"Nicht bestanden: {self.data['nicht_bestanden']}",
            justify="right",
        )

        abgeschlossen_label.grid(row=0, column=1, sticky="e", pady=0, padx=10)
        in_bearbeitung_label.grid(row=1, column=1, sticky="e", pady=0, padx=10)
        ausstehend_label.grid(row=2, column=1, sticky="e", pady=0, padx=10)
        if self.data["nicht_bestanden"] > 0:
            nicht_bestanden_label.grid(row=3, column=1, sticky="e", pady=0, padx=10)

    def _init_ects(self) -> None:
        """Zeigt die erarbeiteten und gesamten ECTS-Punkte an.

        Die Farbe der erreichten ECTS ist grün, wurde das
        Studium nicht erfolgreich beendet ist sie rot.
        """
        ects_frame = ctk.CTkFrame(self, fg_color="transparent")
        ects_frame.grid(row=5, column=1, sticky="nsew", padx=10, pady=5)

        ects_color = GRUEN
        if (
            self.data["exmatrikulationsdatum"] is not None
            and self.data["erarbeitete_ects"] < self.data["gesamt_ects"]
        ):
            ects_color = ROT

        ects_label = ctk.CTkLabel(
            ects_frame,
            font=self.fonts.H2,
            text_color="black",
            text="Erarbeitete ECTS-Punkte:",
            justify="right",
        )
        ects_erreicht_label = ctk.CTkLabel(
            ects_frame,
            font=self.fonts.H1,
            text_color=ects_color,
            text=f"{self.data['erarbeitete_ects']}",
        )
        ects_max_label = ctk.CTkLabel(
            ects_frame,
            font=self.fonts.H1,
            text_color=GRAU,
            text=f"/{self.data['gesamt_ects']}",
        )

        ects_label.pack()
        ects_max_label.pack(side="right", anchor="e")
        ects_erreicht_label.pack(side="right", anchor="e")

    def _init_noten(self) -> None:
        """Zeigt aktuellen Notendurchschnitt und Wunschnote an.

        Ist ein Notendurchschnitt vorhanden und schlechter als die Wunschnote,
        wird er rot dargestellt, sonst grün.
        """
        noten_frame = ctk.CTkFrame(self, fg_color=("gray95", "gray75"))
        noten_frame.grid(row=6, column=0, columnspan=2, padx=10, pady=5)

        if self.data["notendurchschnitt"] is not None:
            if self.data["notendurchschnitt"] > self.data["zielnote"]:
                noten_color = ROT
            else:
                noten_color = GRUEN
        else:
            noten_color = "black"

        if self.data["notendurchschnitt"] is None:
            notendurchschnitt_txt = "--"
        else:
            notendurchschnitt_txt = self.data["notendurchschnitt"]

        ds_text_label = ctk.CTkLabel(
            noten_frame,
            font=self.fonts.H2,
            text_color="black",
            text="Dein \nNotendurchschnitt:",
            justify="left",
        )
        ds_note_label = ctk.CTkLabel(
            noten_frame,
            font=self.fonts.H1,
            text_color=noten_color,
            text=f"{notendurchschnitt_txt}",
        )
        ziel_text_label = ctk.CTkLabel(
            noten_frame,
            font=self.fonts.H2,
            text_color="black",
            text="Dein \nZiel:",
            justify="left",
        )
        ziel_note_label = ctk.CTkLabel(
            noten_frame,
            font=self.fonts.H1,
            text_color="black",
            text=f"{self.data['zielnote']}",
        )
        ds_text_label.pack(side="left", padx=10)
        ds_note_label.pack(side="left", padx=20)
        ziel_text_label.pack(side="left", padx=10)
        ziel_note_label.pack(side="left", padx=20)

    def get_position(self, progress, old_min=0.2, old_max=0.8) -> float:
        """Normiert einen Fortschrittswert auf den Bereich [0, 1] für die Platzierung.

        Der angegebene Fortschritt wird vom ursprünglichen Intervall
        ``[old_min, old_max]`` linear in den Bereich [0, 1] abgebildet und
        anschließend auf diesen Bereich begrenzt. Wird für die Positionierung
        des Heute-/Exmatrikulationslabels auf der Zeitachse verwendet.

        Args:
            progress (float):
                Ursprünglicher Fortschrittswert (z.B. Zeitfortschritt).
            old_min (float):
                Untere Grenze des ursprünglichen Intervalls.
            old_max (float):
                Obere Grenze des ursprünglichen Intervalls.

        Returns:
            float:
                Normierter Wert zwischen 0.0 und 1.0.
        """
        value = (progress - old_min) / (old_max - old_min)
        return max(0, min(1, value))

    def menu_on_button(self) -> None:
        """Öffnet das Menü am Menü-Button.

        Das Menü navigiert zu Frames zum Profil bearbeiten, Exmatrikulation angeben,
        Studienziele anpassen, Über-Ansicht und bietet eine Logout-Funktion.
        """
        self._open_menu_popup(
            anchor=self.menu_button,
            values={
                "Profil bearbeiten": self.go_to_settings,
                "Du wurdest exmatrikuliert?": self.go_to_ex,
                "Ziele anpassen": self.go_to_ziele,
                "Über Dashboard": self.go_to_ueber,
                "Abmelden": self.logout,
            },
        )

    def logout(self) -> None:
        """Meldet den Benutzer ab und wechselt zurück zum Login.

        Schließt ein geöffnetes Menü-Popup, führt den Logout über den
        Controller aus und navigiert anschließend zum Login-Frame.
        """
        self.close_menu()
        self.controller.logout()
        self.after(0, self.go_to_login)


class AddEnrollmentFrame(ctk.CTkScrollableFrame, CalendarMixin):
    """Frame zum Anlegen einer neuen Modul-Einschreibung (Enrollment).

    Der Frame erfasst die Daten eines Moduls (Name, Code, ECTS),
    die Anzahl der Prüfungsleistungen, das Startdatum sowie die zugehörigen
    Kurse. Nach erfolgreicher Validierung wird ein neues Enrollment über
    den Controller angelegt und zur Detailansicht des Enrollments
    weitergeleitet.
    """

    def __init__(
        self, master, controller: Controller, go_to_dashboard, go_to_enrollment
    ) -> None:
        """Initialisiert den Frame und baut Header und Formular auf.

        Args:
            master:
                Eltern-Widget, das u. a. die Fonts bereitstellt.
            controller (Controller):
                Instanz, die Enrollments anlegt und benötigte Daten bereitstellt.
            go_to_dashboard:
                Callback ohne Parameter, um zum Dashboard zurückzukehren.
            go_to_enrollment:
                Callback, der mit einer Enrollment-ID aufgerufen wird, um
                zur Detailansicht des neu angelegten Enrollments zu wechseln.
        """
        super().__init__(master, fg_color="transparent")

        self.controller = controller
        self.go_to_dashboard = go_to_dashboard
        self.go_to_enrollment = go_to_enrollment

        self.fonts = master.fonts
        self.icons = master.icons

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)

        self._init_header()
        self._init_form()

    def _init_header(self) -> None:
        """Erzeugt den Header-Bereich mit Titel und Close-Button."""
        header_frame = ctk.CTkFrame(
            self,
            fg_color=(BACKGROUND, BACKGROUND_DARK),
            border_color="black",
            border_width=2,
        )
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        header_frame.grid_columnconfigure(0, weight=1)
        header_frame.grid_columnconfigure(1, weight=0)

        header_ueber_label = ctk.CTkLabel(
            header_frame,
            text="Zu neuem Modul anmelden",
            font=self.fonts.H2_italic,
            justify="left",
        )
        header_ueber_label.grid(row=0, sticky="nw", padx=10, pady=10)

        header_close_button = ctk.CTkButton(
            header_frame,
            text=self.icons.CLOSE,
            font=self.fonts.ICONS,
            width=10,
            fg_color="transparent",
            text_color="black",
            hover_color="gray95",
            command=lambda: self.after(0, self.go_to_dashboard),
        )
        header_close_button.grid(row=0, column=1, padx=(0, 2), pady=(2, 0), sticky="ne")

    def _init_form(self) -> None:
        """Erzeugt das Formular zur Eingabe der Modul- und Kursdaten.

        Das Formular umfasst:
            * Modulname, Modul-Code und ECTS-Punkte
            * Anzahl der Prüfungsleistungen
            * Startdatum des Moduls
            * Liste der zugehörigen Kurse (Nummer und Name)
        """
        form_frame = ctk.CTkFrame(
            self,
            fg_color=(BACKGROUND, BACKGROUND_DARK),
            border_color="black",
            border_width=2,
        )
        form_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        form_frame.grid_columnconfigure(0, weight=1)
        form_frame.grid_columnconfigure(1, weight=1)

        left_frame = ctk.CTkFrame(form_frame, fg_color=(BACKGROUND, BACKGROUND_DARK))
        left_frame.grid(row=0, column=0, padx=5, pady=5)
        right_frame = ctk.CTkFrame(form_frame, fg_color=(BACKGROUND, BACKGROUND_DARK))
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

        self.selected_startdatum_real: str | None = None

        # RIGHT FRAME
        # Welcher Kurs oder welche Kurse müssen absolviert werden?
        kurs_name_label = ctk.CTkLabel(
            right_frame, text="Welcher Kurs oder welche Kurse müssen absolviert werden?"
        )
        kurs_name_label.pack(pady=10)

        self.kurse_eingabe_feld = DynamicEntries(
            right_frame,
            label_links="Kursnummer",
            label_rechts="Kursname",
            placeholder_links="Kursnummer",
            placeholder_rechts="Kursname",
            initial_rows=1,
            max_rows=10,
        )
        self.kurse_eingabe_feld.pack(pady=10)

        # Submit-Button
        submit_button = ctk.CTkButton(
            form_frame,
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
        self.leere_felder_label = ctk.CTkLabel(form_frame, text="", text_color=ROT)
        self.leere_felder_label.grid(
            row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=5
        )

    def on_submit(self) -> None:
        """Validiert die Eingaben und legt bei Erfolg ein neues Enrollment an.

        Ablauf:
            * Pflichtfelder (Modulname, Modul-Code, ECTS-Wert, Startdatum) prüfen.
            * Kursliste auslesen und prüfen, ob mindestens ein Kurs angegeben ist.
            * Enrollment-Daten in einem Cache-Dictionary sammeln und prüfen,
            ob bereits eine Einschreibung für dieses Modul existiert.
            * Bei Erfolg Enrollment über den Controller anlegen und zur
            entsprechenden Detailansicht navigieren.

        Bei Validierungsfehlern werden entsprechende Fehlermeldungen in den
        dafür vorgesehenen Labels angezeigt und die Methode bricht ab.
        """
        if self.validate_ects(self.modul_ects_entry.get().strip()):
            self.selected_modul_ects = int(self.modul_ects_entry.get().strip())
        else:
            return

        self.list_for_validation = [
            self.modul_name_entry.get(),
            self.modul_code_entry.get(),
        ]
        if not self.validate_entries(liste=self.list_for_validation):
            return

        self.entry_kurse_dict = self.kurse_eingabe_feld.get_values()
        if not self.entry_kurse_dict:
            self.leere_felder_label.configure(text="Keine Kurse angegeben.")
            return

        if self.selected_startdatum_real is None:
            self.leere_felder_label.configure(text="Startdatum nicht ausgewählt.")
            return

        # Validierung abgeschlossen
        self.selected_modul_name = self.modul_name_entry.get()
        self.selected_modul_code = self.modul_code_entry.get()
        self.selected_kurse_dict = self.entry_kurse_dict
        self.selected_pl_anzahl = int(self.pl_anzahl_entry.get())
        self.selected_startdatum_str = self.selected_startdatum_real

        enrollment_cache = {
            "modul_name": self.selected_modul_name,
            "modul_code": self.selected_modul_code,
            "modul_ects": self.selected_modul_ects,
            "kurse_dict": self.selected_kurse_dict,
            "pl_anzahl": self.selected_pl_anzahl,
            "startdatum": self.selected_startdatum_str,
        }

        if self.controller.check_if_already_enrolled(enrollment_cache=enrollment_cache):
            self.leere_felder_label.configure(
                text="Du bist schon in dieses Modul eingeschrieben"
            )
            return

        enrollment_dict = self.controller.erstelle_enrollment(
            enrollment_cache=enrollment_cache
        )

        self.after(0, lambda: self.go_to_enrollment(enrollment_dict["id"]))

    def validate_ects(self, ects: str) -> bool:
        """Prüft, ob der ECTS-Wert eine Ganzzahl zwischen 1 und 50 ist.

        Im Fehlerfall wird eine passende Fehlermeldung im
        Label ``label_no_int`` angezeigt.

        Args:
            ects (str):
                Eingegebener ECTS-Wert als String.

        Returns:
            bool:
                ``True``, wenn der Wert gültig ist, sonst ``False``.
        """
        try:
            number = int(ects)
        except ValueError:
            self.label_no_int.configure(text="Muss eine (Ganz-) Zahl sein")
            return False

        if 1 <= number <= 50:
            self.label_no_int.configure(text="")
            return True
        else:
            self.label_no_int.configure(text="Zahl muss zwischen 1 und 50 liegen")
            return False

    def validate_entries(self, liste: list) -> bool:
        """Prüft, ob alle Werte der übergebenen Liste nicht leer sind.

        Leere oder nur aus Leerzeichen bestehende Einträge führen zu einer
        Fehlermeldung im Label ``leere_felder_label`` und die Methode gibt
        ``False`` zurück. Sind alle Werte gefüllt, wird ``True`` zurückgegeben.

        Args:
            liste (list[str]):
                Liste der zu prüfenden Eingaben.

        Returns:
            bool:
                ``True``, wenn alle Felder gefüllt sind, sonst ``False``.
        """
        for value in liste:
            if str(value).strip() == "":
                self.leere_felder_label.configure(text="Etwas ist nicht ausgefüllt.")
                return False
        return True

    def start_datum_calendar_at_button(self) -> None:
        """Öffnet den Kalender zur Auswahl des Modulstartdatums."""
        self._open_calendar_popup(
            anchor=self.button_startdatum,
            mindate=self.controller.get_startdatum(),
            maxdate=datetime.date.today(),
            on_date_selected=self._set_startdatum,
        )

    def _set_startdatum(self, date: datetime.date) -> None:
        """Verarbeitet das im Kalender gewählte Modulstartdatum.

        Aktualisiert sowohl die sichtbare Textvariable als auch den
        intern genutzten ISO-String für das Startdatum.
        """
        self.selected_startdatum.set(from_iso_to_ddmmyyyy(date=date))
        self.selected_startdatum_real = date.isoformat()


class EnrollmentFrame(ctk.CTkScrollableFrame):
    """Detailansicht für ein einzelnes Enrollment (Modul-Einschreibung).

    Der Frame zeigt Modulinformationen, zugehörige Kurse, Prüfungsleistungen,
    Status, Note sowie Einschreibe- und Abschlussdatum. Außerdem können
    über die Prüfungsleistungs-Tabelle einzelne Versuche ausgewählt werden,
    um Prüfungsdaten einzutragen oder anzuzeigen.
    """

    def __init__(
        self,
        master,
        controller: Controller,
        go_to_dashboard,
        go_to_pl,
        enrollment_id,
    ) -> None:
        """Initialisiert die Enrollment-Detailansicht und baut alle UI-Bereiche auf.

        Args:
            master:
                Eltern-Widget, liefert u. a. ``master.fonts``.
            controller (Controller):
                Liefert die Enrollment-Daten und übernimmt Geschäftslogik.
            go_to_dashboard:
                Callback ohne Parameter, um zurück zum Dashboard zu navigieren.
            go_to_pl:
                Callback für die Detailansicht einer Prüfungsleistung.
                Erwartet typischerweise ``(pl_id, enrollment_id)``.
            enrollment_id:
                ID des anzuzeigenden Enrollments.
        """
        super().__init__(master, fg_color="transparent")

        self.controller = controller
        self.go_to_dashboard = go_to_dashboard
        self.go_to_pl = go_to_pl
        self.enrollment_id = enrollment_id

        self.fonts = master.fonts
        self.icons = master.icons

        self.enrollment_data = self.controller.get_enrollment_data(self.enrollment_id)

        self.grid_columnconfigure(0, weight=1, uniform="half")
        self.grid_columnconfigure(1, weight=1, uniform="half")

        self.grid_rowconfigure(0, weight=0)
        for row in range(
            1,
            4,
        ):
            self.grid_rowconfigure(row, weight=1)

        self._init_modul()
        self._init_kurse()
        self._init_pls()
        self._init_status()
        self._init_noten()
        self._init_eingeschrieben()
        self._init_abgeschlossen()

    def _init_modul(self) -> None:
        """Erzeugt den Modul-Headerbereich.

        Enthält Titel, Modulname und -code, Anzahl der ECTS-Punkte sowie den Close-Button.
        """
        modul_frame = ctk.CTkFrame(
            self,
            fg_color=(BACKGROUND, BACKGROUND_DARK),
            border_color="black",
            border_width=2,
        )
        modul_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        modul_frame.grid_columnconfigure(0, weight=1)
        modul_frame.grid_columnconfigure(1, weight=0)

        modul_ueber_label = ctk.CTkLabel(
            modul_frame, text="MODUL:", font=self.fonts.H2_italic, justify="left"
        )
        modul_ueber_label.grid(row=0, sticky="nw", padx=10, pady=10)
        modul_name_label = MultiLineLabel(
            modul_frame,
            width=85,
            text=f"{self.enrollment_data['modul_name']}",
            font=self.fonts.H3,
            justify="left",
        )
        modul_name_label.grid(row=1, sticky="nw", padx=10, pady=10)
        modul_code_label = ctk.CTkLabel(
            modul_frame,
            text=f"{self.enrollment_data['modul_code']}",
            font=self.fonts.TEXT,
            justify="left",
        )
        modul_code_label.grid(row=2, column=0, sticky="nw", padx=10, pady=10)

        modul_close_button = ctk.CTkButton(
            modul_frame,
            text=self.icons.CLOSE,
            font=self.fonts.ICONS,
            width=10,
            fg_color="transparent",
            text_color="black",
            hover_color="gray95",
            command=lambda: self.after(0, self.go_to_dashboard),
        )
        modul_close_button.grid(row=0, column=1, padx=(0, 2), pady=(2, 0), sticky="ne")

        modul_ects_label = ctk.CTkLabel(
            modul_frame,
            text=f"{self.enrollment_data['modul_ects']} ECTS-Punkte",
            font=self.fonts.TEXT,
            justify="right",
        )
        modul_ects_label.grid(row=2, column=1, sticky="e", padx=10, pady=10)

    def _init_kurse(self) -> None:
        """Erzeugt den Kursbereich.

        Listet alle zugehörigen Kurse des Enrollments untereinander auf.
        """
        kurse_frame = ctk.CTkFrame(
            self,
            fg_color=(BACKGROUND, BACKGROUND_DARK),
            border_color="black",
            border_width=2,
        )
        kurse_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        kurse_ueber_label = ctk.CTkLabel(
            kurse_frame, text="KURSE:", font=self.fonts.H2_italic, justify="left"
        )
        kurse_ueber_label.grid(row=0, sticky="nw", padx=10, pady=10)

        row_counter = 1
        for kurs in self.enrollment_data["kurse"]:
            kurs_label = MultiLineLabel(
                master=kurse_frame,
                width=50,
                text=f"{kurs['name']}",
                font=self.fonts.TEXT,
                justify="left",
            )
            kurs_label.grid(row=row_counter, padx=10, pady=5, sticky="w")
            row_counter += 1

    def _init_pls(self) -> None:
        """Erzeugt die Tabelle der Prüfungsleistungen mit einem Button pro Versuch.

        Logik:
            * Der Button zeigt an, ob ein Versuch einer Prüfungsleistung erfolgreich,
              unerfolgreich oder noch unbearbeitet ist.
            * Versuch 2/3 wird nur dann freigeschaltet, wenn der vorherige Versuch
              vorhanden und *nicht bestanden* ist.
            * Wird der Button einer unbearbeiteten Prüfungsleistung geklickt,
              können Prüfungsdaten hinzugefügt werden.
            * Wird ein Button eines bearbeiteten Versuchs geklickt, erhält man eine Detailansicht.
        """
        pl_frame = ctk.CTkFrame(
            self,
            fg_color=(BACKGROUND, BACKGROUND_DARK),
            border_color="black",
            border_width=2,
        )
        pl_frame.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)
        pl_frame.grid_columnconfigure(0, weight=1)

        # Überschrift
        pl_ueber_label = ctk.CTkLabel(
            pl_frame,
            text="PRÜFUNGSLEISTUNGEN:",
            font=self.fonts.H2_italic,
            justify="left",
        )
        pl_ueber_label.grid(row=0, sticky="nw", padx=10, pady=10)

        # Titelzeile
        pl_tabelle_title_frame = ctk.CTkFrame(
            pl_frame,
            fg_color=(BACKGROUND, BACKGROUND_DARK),
            border_color="gray95",
            border_width=2,
        )
        pl_tabelle_title_frame.grid(row=1, sticky="ew", padx=4, pady=4)
        for column, txt in enumerate(
            ["Nr.", "1. Versuch", "2. Versuch", "3. Versuch", "Gewichtung:"]
        ):
            label = ctk.CTkLabel(
                pl_tabelle_title_frame, text=txt, font=self.fonts.TEXT, justify="left"
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

        # Tabelle
        pls = self.enrollment_data["pruefungsleistungen"]
        anzahl = self.enrollment_data["anzahl_pruefungsleistungen"]

        pls_dict: dict[int, list[dict]] = {}
        for pl in pls:
            pls_dict.setdefault(pl["teilpruefung"], []).append(pl)

        zustand = ["offen", "bestanden", "nicht_bestanden", "deaktiviert"]

        for i in range(anzahl):
            versuche = pls_dict.get(i, [])
            zustand_letzte_pl = zustand[0]
            # zustand_letzte_pl steuert die Freischaltung der nächsten Versuche pro Teilprüfung:
            # Versuch 2/3 nur klickbar, wenn der vorherige Versuch "nicht_bestanden" ist.

            row_frame = ctk.CTkFrame(
                pl_frame,
                fg_color=(BACKGROUND, BACKGROUND_DARK),
                border_color="gray95",
                border_width=2,
            )
            row_frame.grid(row=i + 2, sticky="ew", padx=4, pady=4)
            for column in range(5):
                row_frame.grid_columnconfigure(column, weight=1 if column > 0 else 0)

            index_label = ctk.CTkLabel(
                row_frame,
                text=f"{i + 1}.",
                font=self.fonts.TEXT,
                justify="left",
            )
            index_label.grid(row=0, column=0, padx=5, pady=2, sticky="w")

            gewicht = versuche[0]["teilpruefung_gewicht"] if versuche else "--"
            gewicht_label = ctk.CTkLabel(
                row_frame,
                text=f"{gewicht}",
                font=self.fonts.TEXT,
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
                            hovertext=self.icons.ADD_BOX,
                            defaultcolor="black",
                            defaulttext=self.icons.CHECK_BOX_OUTLINE_BLANK,
                            text=self.icons.CHECK_BOX_OUTLINE_BLANK,
                            text_color="black",
                            font=self.fonts.ICONS,
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
                            text=self.icons.CHECK_BOX_OUTLINE_BLANK,
                            font=self.fonts.ICONS,
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
                            text=self.icons.SELECT_CHECK_BOX,
                            font=self.fonts.ICONS,
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
                            text=self.icons.DISABLED_BY_DEFAULT,
                            font=self.fonts.ICONS,
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

    def _init_status(self) -> None:
        """Erzeugt den Statusbereich.

        Zeigt den Enrollment-Status (z.B. in Bearbeitung / abgeschlossen / nicht bestanden)
        mit passender Farbkennzeichnung.
        """
        status_frame = ctk.CTkFrame(
            self,
            fg_color=(BACKGROUND, BACKGROUND_DARK),
            border_color="black",
            border_width=2,
        )
        status_frame.grid(row=2, column=0, sticky="nsew", padx=5, pady=5)

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
            font=self.fonts.TEXT,
            text_color=status_color,
        )
        status_label.pack(
            pady=4,
        )

    def _init_noten(self) -> None:
        """Erzeugt den Notenbereich.

        Zeigt die berechnete Enrollment-Note oder ``--`` falls noch nicht vorhanden.
        """
        noten_frame = ctk.CTkFrame(
            self,
            fg_color=(BACKGROUND, BACKGROUND_DARK),
            border_color="black",
            border_width=2,
        )
        noten_frame.grid(row=2, column=1, sticky="nsew", padx=5, pady=5)

        if self.enrollment_data["enrollment_note"] is None:
            note = "--"
        else:
            note = self.enrollment_data["enrollment_note"]

        noten_label = ctk.CTkLabel(
            noten_frame,
            text=f"Deine Note: {note}",
            font=self.fonts.TEXT,
        )
        noten_label.pack(
            pady=4,
        )

    def _init_eingeschrieben(self) -> None:
        """Erzeugt den Bereich, in dem das Einschreibedatum angezeigt wird."""
        eingeschrieben_frame = ctk.CTkFrame(
            self,
            fg_color=(BACKGROUND, BACKGROUND_DARK),
            border_color="black",
            border_width=2,
        )
        eingeschrieben_frame.grid(row=3, column=0, sticky="nsew", padx=5, pady=5)

        eingeschrieben_label = ctk.CTkLabel(
            eingeschrieben_frame,
            text=f"Eingeschrieben am: {from_iso_to_ddmmyyyy(self.enrollment_data['einschreibe_datum'])}",
            font=self.fonts.TEXT,
        )
        eingeschrieben_label.pack(
            pady=4,
        )

    def _init_abgeschlossen(self) -> None:
        """Erzeugt den Bereich, in dem das Datum des Modulabschlusses angezeigt wird.

        Ist das Modul noch nicht abgeschlossen, wird ``--`` angezeigt."""
        abgeschlossen_frame = ctk.CTkFrame(
            self,
            fg_color=(BACKGROUND, BACKGROUND_DARK),
            border_color="black",
            border_width=2,
        )
        abgeschlossen_frame.grid(row=3, column=1, sticky="nsew", padx=5, pady=5)

        if self.enrollment_data["end_datum"] is None:
            abgeschlossen_datum = "--"
        else:
            abgeschlossen_datum = self.enrollment_data["end_datum"]

        abgeschlossen_label = ctk.CTkLabel(
            abgeschlossen_frame,
            text=f"Abgeschlossen am: {from_iso_to_ddmmyyyy(abgeschlossen_datum)}",
            font=self.fonts.TEXT,
        )
        abgeschlossen_label.pack(
            pady=4,
        )


class PLAddFrame(ctk.CTkFrame, CalendarMixin):
    """Frame zum Eintragen oder Anzeigen einer Prüfungsleistung (PL).

    Wenn für die PL noch keine Note existiert, wird ein Eingabeformular angezeigt.
    Andernfalls wird die gespeicherte Note inkl. Datum und Bestanden-Status angezeigt.
    """

    def __init__(
        self,
        master,
        controller: Controller,
        go_to_enrollment: Callable[[int], None],
        pl_id: int,
        e_id: int,
    ) -> None:
        """Lädt PL- und Enrollment-Daten und initialisiert die passende Ansicht.

        Args:
            master:
                Eltern-Widget, liefert u. a. ``master.fonts``.
            controller (Controller):
                Liefert Daten und speichert Änderungen an der Prüfungsleistung.
            go_to_enrollment:
                Callback, um zurück zur Enrollment-Detailansicht zu navigieren.
                Erwartet Enrollment-ID.
            pl_id:
                ID der Prüfungsleistung (konkreter Versuch).
            e_id:
                Enrollment-ID, zu der die Prüfungsleistung gehört.
        """
        super().__init__(master, fg_color="transparent")

        self.controller = controller
        self.go_to_enrollment = go_to_enrollment
        self.pl_id = pl_id
        self.enrollment_id = e_id

        self.fonts = master.fonts
        self.icons = master.icons

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)

        self.pl_data = self.controller.get_pl_with_id(self.enrollment_id, self.pl_id)
        if self.pl_data == {}:
            raise ValueError("Prüfungsleistung nicht gefunden")

        self.enrollment_data = self.controller.get_enrollment_data(self.enrollment_id)

        self._init_header()

        if self.pl_data["note"] is None:
            # wenn keine Note vorhanden, zeige Eingabeformular für Prüfungsleistungsdaten.
            self._init_form()
        else:
            # wenn Note vorhanden, zeige Detailanzeige.
            self._init_content()

    def _init_header(self) -> None:
        """Erzeugt den Header mit Modul-/Prüfungsinformationen und Close-Button."""
        pl_frame = ctk.CTkFrame(
            self,
            fg_color=(BACKGROUND, BACKGROUND_DARK),
            border_color="black",
            border_width=2,
        )
        pl_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        pl_frame.grid_columnconfigure(0, weight=1)
        pl_frame.grid_columnconfigure(1, weight=0)

        pl_ueber_label = ctk.CTkLabel(
            pl_frame,
            text="PRÜFUNGSLEISTUNG:",
            font=self.fonts.H2_italic,
            justify="left",
        )
        pl_ueber_label.grid(row=0, sticky="nw", padx=10, pady=10)
        pl_modul_label = ctk.CTkLabel(
            pl_frame,
            text=f"Modul: {self.enrollment_data['modul_name']}",
            font=self.fonts.H3,
            justify="left",
        )
        pl_modul_label.grid(row=1, sticky="nw", padx=10, pady=10)
        pl_name_label = MultiLineLabel(
            pl_frame,
            width=85,
            text=f"Prüfung: {int(self.pl_data['teilpruefung']) + 1}, Versuch: {self.pl_data['versuch']}",
            font=self.fonts.H3,
            justify="left",
        )
        pl_name_label.grid(row=2, sticky="nw", padx=10, pady=10)

        pl_close_button = ctk.CTkButton(
            pl_frame,
            text=self.icons.CLOSE,
            font=self.fonts.ICONS,
            width=10,
            fg_color="transparent",
            text_color="black",
            hover_color="gray95",
            command=lambda: self.after(0, self.go_to_enrollment, self.enrollment_id),
        )
        pl_close_button.grid(row=0, column=1, padx=(0, 2), pady=(2, 0), sticky="ne")

    def _init_form(self) -> None:
        """Erzeugt das Formular zum Eintragen von Note und Prüfungsdatum."""
        pl_add_frame = ctk.CTkFrame(
            self,
            fg_color=(BACKGROUND, BACKGROUND_DARK),
            border_color="black",
            border_width=2,
        )
        pl_add_frame.grid(row=1, column=0, columnspan=2, sticky="new", padx=5, pady=5)

        pl_add_pl_label = ctk.CTkLabel(
            pl_add_frame,
            text="Prüfungsleistung hinzufügen:",
            font=self.fonts.H2_italic,
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

        self.label_pl_datum_variable = ctk.CTkLabel(
            pl_add_frame, textvariable=self.selected_pl_datum
        )
        self.label_pl_datum_variable.pack(pady=10)

        self.selected_pl_datum_real: str | None = None

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
        self.label_leere_felder = ctk.CTkLabel(pl_add_frame, text="", text_color=ROT)
        self.label_leere_felder.pack(pady=10)

    def _init_content(self) -> None:
        """Zeigt gespeicherte PL-Daten (Bestanden/Nicht bestanden, Note, Datum) an."""
        pl_show_frame = ctk.CTkFrame(
            self,
            fg_color=(BACKGROUND, BACKGROUND_DARK),
            border_color="black",
            border_width=2,
        )
        pl_show_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        pl_status_label_bad = ctk.CTkLabel(
            pl_show_frame,
            text="Nicht bestanden!",
            text_color=ROT,
            font=self.fonts.H1,
        )
        pl_status_label_good = ctk.CTkLabel(
            pl_show_frame,
            text="Bestanden!",
            text_color=GRUEN,
            font=self.fonts.H1,
        )
        if not self.pl_data["ist_bestanden"]:
            pl_status_label_bad.pack(pady=20)
        else:
            pl_status_label_good.pack(pady=20)

        pl_show_note_label = ctk.CTkLabel(
            pl_show_frame,
            text=f"Deine Note: {self.pl_data['note']}",
            text_color="black",
            font=self.fonts.H2,
        )
        pl_show_note_label.pack(pady=15)
        pl_show_datum_label = ctk.CTkLabel(
            pl_show_frame,
            text=f"Am: {from_iso_to_ddmmyyyy(self.pl_data['datum'])}",
            text_color="black",
            font=self.fonts.H2,
        )
        pl_show_datum_label.pack(pady=15)

    def on_submit(self) -> None:
        """Validiert Eingaben, speichert Note und Datum über den Controller und navigiert zurück."""
        if str(self.pl_add_note_entry.get()).strip() == "":
            self.label_leere_felder.configure(text="Keine Note eingegeben.")
            return

        if not self.selected_pl_datum_real:
            self.label_leere_felder.configure(text="Prüfungsdatum nicht ausgewählt.")
            return
        self.selected_pl_datum_str = self.selected_pl_datum_real

        self.pl_data["note"] = float(self.pl_add_note_entry.get())
        self.pl_data["datum"] = self.selected_pl_datum_str

        self.controller.change_pl(self.enrollment_id, self.pl_data)

        self.after(0, self.go_to_enrollment, self.enrollment_id)

    def pl_datum_calendar_at_button(self) -> None:
        """Öffnet den Kalender zur Auswahl des Prüfungsdatums."""
        self._open_calendar_popup(
            anchor=self.pl_button_datum,
            mindate=self.enrollment_data["einschreibe_datum"],
            maxdate=datetime.date.today(),
            on_date_selected=self._set_pl_datum,
        )

    def _set_pl_datum(self, date: datetime.date) -> None:
        """Verarbeitet das im Kalender gewählte Prüfungsdatum.

        Aktualisiert sowohl die sichtbare Textvariable als auch den
        intern genutzten ISO-String für das Startdatum.
        """
        self.selected_pl_datum.set(from_iso_to_ddmmyyyy(date=date))
        self.selected_pl_datum_real = date.isoformat()


class SettingsFrame(ctk.CTkScrollableFrame, CalendarMixin):
    """Einstellungsframe zur Bearbeitung von Profil- und Studiendaten.

    Ermöglicht das Ändern einzelner Felder (E-Mail, Passwort, Name, Matrikelnummer,
    Semesteranzahl, Startdatum, Gesamt-ECTS, Modulanzahl) mit jeweils separatem Speichern.
    Enthält zusätzlich eine „Danger Zone“ für kritische Änderungen (Hochschule,
    Studiengang) sowie das Löschen des Accounts.
    """

    def __init__(
        self,
        master,
        controller: Controller,
        go_to_dashboard,
        go_to_settings,
        go_to_login,
    ) -> None:
        """Initialisiert den Settings-Frame und lädt aktuelle Profildaten.

        Args:
            master:
                Eltern-Widget ,liefert u. a. ``master.fonts``.
            controller (Controller):
                Stellt Daten bereit und übernimmt Persistenz von Änderungen.
            go_to_dashboard:
                Callback zur Rückkehr zum Dashboard.
            go_to_settings:
                Callback zum erneuten Öffnen/Refresh der Settings-Ansicht (z. B. nach Popups).
            go_to_login:
                Callback zum Login (z. B. nach Account-Löschung).
        """
        super().__init__(master, fg_color="transparent")

        self.controller = controller
        self.go_to_dashboard = go_to_dashboard
        self.go_to_settings = go_to_settings
        self.go_to_login = go_to_login

        self.fonts = master.fonts
        self.icons = master.icons

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)

        self.data = self.controller.load_dashboard_data()

        self._init_header()
        self._init_settings()
        self._init_danger()

    def _init_header(self) -> None:
        """Erzeugt den Header mit Titel und Close-Button."""
        settings_frame = ctk.CTkFrame(
            self,
            fg_color=(BACKGROUND, BACKGROUND_DARK),
            border_color="black",
            border_width=2,
        )
        settings_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        settings_frame.grid_columnconfigure(0, weight=1)
        settings_frame.grid_columnconfigure(1, weight=0)

        settings_ueber_label = ctk.CTkLabel(
            settings_frame,
            text="EINSTELLUNGEN:",
            font=self.fonts.H2_italic,
            justify="left",
        )
        settings_ueber_label.grid(row=0, sticky="nw", padx=10, pady=10)

        settings_close_button = ctk.CTkButton(
            settings_frame,
            text=self.icons.CLOSE,
            font=self.fonts.ICONS,
            width=10,
            fg_color="transparent",
            text_color="black",
            hover_color="gray95",
            command=lambda: self.after(0, self.go_to_dashboard),
        )
        settings_close_button.grid(
            row=0, column=1, padx=(0, 2), pady=(2, 0), sticky="ne"
        )

    def _init_settings(self) -> None:
        """Erzeugt den Bereich mit den 'sicheren' Einstlungen."""
        st_change_frame = ctk.CTkFrame(
            self,
            fg_color=(BACKGROUND, BACKGROUND_DARK),
            border_color="black",
            border_width=2,
        )
        st_change_frame.grid(
            row=1, column=0, columnspan=2, sticky="new", padx=5, pady=5
        )

        for column in range(5):
            st_change_frame.grid_columnconfigure(column, weight=1)
        for row in range(11):
            st_change_frame.grid_rowconfigure(row, weight=1)

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

        # Passwort
        self.password_label = ctk.CTkLabel(
            st_change_frame,
            text="Dein Passwort",
        )
        self.password_label.grid(row=1, column=0, padx=10, pady=10)
        self.entry_password = ctk.CTkEntry(
            st_change_frame, placeholder_text="Passwort", show="●"
        )
        self.entry_password.grid(row=1, column=1, sticky="ew", padx=10, pady=10)
        self.password_button = ctk.CTkButton(
            st_change_frame,
            text="speichern",
            text_color="black",
            fg_color="transparent",
            border_color="black",
            border_spacing=2,
            border_width=2,
            hover_color="gray95",
            command=self.save_password,
        )
        self.password_button.grid(row=1, column=4, padx=10, pady=10)
        self.password_not_valid = ctk.CTkLabel(st_change_frame, text="", text_color=ROT)
        self.password_not_valid.grid(
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
        self.name_button = ctk.CTkButton(
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
        self.name_button.grid(row=2, column=4, padx=10, pady=10)
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
        self.matrikel_button = ctk.CTkButton(
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
        self.matrikel_button.grid(row=3, column=4, padx=10, pady=10)
        self.matrikel_not_valid = ctk.CTkLabel(st_change_frame, text="", text_color=ROT)
        self.matrikel_not_valid.grid(
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
        self.semester_button = ctk.CTkButton(
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
        self.semester_button.grid(row=4, column=4, padx=10, pady=10)
        self.semester_anzahl_not_valid = ctk.CTkLabel(
            st_change_frame, text="", text_color=ROT
        )
        self.semester_anzahl_not_valid.grid(
            row=4, column=2, columnspan=2, sticky="ew", padx=5, pady=10
        )

        # Start-Datum
        # Darf nicht jünger sein als Daten in Enrollments
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
        self.start_button = ctk.CTkButton(
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
        self.start_button.grid(row=5, column=4, padx=10, pady=10)
        self.startdatum_not_valid = ctk.CTkLabel(
            st_change_frame, text="", text_color=ROT
        )
        self.startdatum_not_valid.grid(row=5, column=3, sticky="ew", padx=5, pady=0)

        # Deaktiviert, da sonst Studenten die ECTS-Punkte eines Studiengangs ändern können,
        # das sollte nur durch Admins oder Hochschulen möglich sein.

        # Gesamt-ECTS-Punkte
        # self.label_ects = ctk.CTkLabel(
        #     st_change_frame,
        #     text="ECTS-Punkte deines Studiums?",
        # )
        # self.label_ects.grid(row=6, column=0, padx=5, pady=10)
        # self.entry_ects = ctk.CTkEntry(
        #     st_change_frame, placeholder_text=f"{self.data['gesamt_ects']} ECTS-Punkte"
        # )
        # self.entry_ects.grid(row=6, column=1, sticky="ew", padx=5, pady=10)
        # self.label_no_int = ctk.CTkLabel(st_change_frame, text="", text_color=ROT)
        # self.label_no_int.grid(row=6, column=2, columnspan=2, padx=5, pady=10)
        # self.ects_button = ctk.CTkButton(
        #     st_change_frame,
        #     text="speichern",
        #     text_color="black",
        #     fg_color="transparent",
        #     border_color="black",
        #     border_spacing=2,
        #     border_width=2,
        #     hover_color="gray95",
        #     command=self.save_ects,
        # )
        # self.ects_button.grid(row=6, column=4, padx=10, pady=10)

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
        self.modulanzahl_button = ctk.CTkButton(
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
        self.modulanzahl_button.grid(row=7, column=4, padx=10, pady=10)
        self.modulanzahl_not_valid = ctk.CTkLabel(
            st_change_frame, text="", text_color=ROT
        )
        self.modulanzahl_not_valid.grid(
            row=7, column=2, columnspan=2, sticky="ew", padx=5, pady=10
        )

    def _init_danger(self) -> None:
        """Erzeugt die 'Danger Zone' für kritische Änderungen der Einstellungen und Account-Löschung."""
        danger_frame = ctk.CTkFrame(
            self,
            corner_radius=10,
            fg_color=(BACKGROUND, BACKGROUND_DARK),
            border_color=ROT,
            border_width=10,
        )
        danger_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        danger_label = MultiLineLabel(
            danger_frame,
            width=120,
            text="ACHTUNG: Änderungen an folgenden Einstellungen können dazu führen, dass Deine Daten verloren gehen. Dies kann nicht rückgängig gemacht werden.",
            text_color=ROT,
            font=self.fonts.TEXT,
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
        self.hochschule_button = ctk.CTkButton(
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
        self.hochschule_button.grid(row=1, column=3, padx=10, pady=10)
        self.hochschule_not_valid = ctk.CTkLabel(danger_frame, text="", text_color=ROT)
        self.hochschule_not_valid.grid(row=1, column=2, sticky="ew", padx=5, pady=0)

        # Studiengang
        self.label_studiengang = ctk.CTkLabel(
            danger_frame, text="Wie heißt Dein Studiengang?", justify="left"
        )
        self.label_studiengang.grid(row=2, column=0, padx=10, pady=10)

        self.entry_studiengang = ctk.CTkEntry(
            danger_frame, width=240, placeholder_text=f"{self.data['studiengang']}"
        )
        self.entry_studiengang.grid(row=2, column=1, padx=10, pady=10)
        self.studiengang_button = ctk.CTkButton(
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
        self.studiengang_button.grid(row=2, column=3, padx=10, pady=10)
        self.studiengang_not_valid = ctk.CTkLabel(danger_frame, text="", text_color=ROT)
        self.studiengang_not_valid.grid(row=2, column=2, sticky="nsew", padx=5, pady=0)

        # Account löschen
        self.label_delete_account = ctk.CTkLabel(
            danger_frame, text="Du möchtest Deinen Account löschen?", justify="left"
        )
        self.label_delete_account.grid(row=3, column=0, padx=10, pady=(10, 15))
        self.button_delete_account = ctk.CTkButton(
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
        self.button_delete_account.grid(row=3, column=3, padx=10, pady=10)

    def save_email(self) -> None:
        """Validiert und speichert die neue E-Mail-Adresse"""
        if self.verify_email():
            self.controller.change_email(self.selected_email)
            self.label_email_not_valid.configure(text="Neue Email gespeichert")

    def save_password(self) -> None:
        """Validiert und speichert das neue Passwort."""
        if self.verify_input(self.entry_password.get()):
            self.controller.change_password(self.entry_password.get())
            self.password_not_valid.configure(text="Neues Passwort gespeichert")
        else:
            self.password_not_valid.configure(text="Nicht ausgefüllt")

    def save_name(self) -> None:
        """Validiert und speichert den neuen Namen."""
        if self.verify_input(self.entry_name.get()):
            self.controller.change_name(self.entry_name.get())
            self.name_not_valid.configure(text="Neuer Name gespeichert")
        else:
            self.name_not_valid.configure(text="Nicht ausgefüllt")

    def save_matrikelnummer(self) -> None:
        """Validiert und speichert die neue Matrikelnummer."""
        if self.verify_input(self.entry_matrikelnummer.get()):
            self.controller.change_matrikelnummer(self.entry_matrikelnummer.get())
            self.matrikel_not_valid.configure(text="Neue Matrikelnummer gespeichert")
        else:
            self.matrikel_not_valid.configure(text="Nicht ausgefüllt")

    def save_semester_anzahl(self) -> None:
        """Speichert die neue Semesteranzahl, falls sie vom bisherigen Wert abweicht."""
        neu_semester_anzahl = int(self.entry_semesteranzahl.get())
        if neu_semester_anzahl != len(self.data["semester"]):
            self.controller.change_semester_anzahl(neu_semester_anzahl)
            self.semester_anzahl_not_valid.configure(text="Semester Gespeichert")
        else:
            self.semester_anzahl_not_valid.configure(text="Entspricht bisherigen Wert")

    def save_startdatum(self) -> None:
        """Speichert das neue Studienstartdatum, falls es vom bisherigen abweicht."""
        if self.selected_startdatum_real:
            if (
                datetime.date.fromisoformat(self.selected_startdatum_real)
                == self.data["startdatum"]
            ):
                self.startdatum_not_valid.configure(text="Entspricht bisherigen Wert")
            else:
                self.controller.change_startdatum(
                    datetime.date.fromisoformat(self.selected_startdatum_real)
                )
                self.startdatum_not_valid.configure(text="Gespeichert")
        else:
            self.startdatum_not_valid.configure(text="Kein Datum gewählt")

    # Deaktiviert, da sonst Studenten die ECTS-Punkte eines Studiengangs ändern können,
    # das sollte nur durch Admins oder Hochschulen möglich sein.

    # def save_ects(self) -> None:
    #     """Validiert und speichert die neue Gesamt-ECTS-Punktzahl des Studiums."""
    #     neu_ects_str = self.entry_ects.get().strip()
    #     if self.validate_ects(neu_ects_str):
    #         neu_ects = int(neu_ects_str)
    #         if neu_ects != self.data["gesamt_ects"]:
    #             self.controller.change_gesamt_ects(neu_ects)
    #             self.label_no_int.configure(text="Gespeichert")
    #         else:
    #             self.label_no_int.configure(text="Entspricht bisherigen Wert")

    def save_modul_anzahl(self) -> None:
        """Speichert die neue Modulanzahl, falls sie vom bisherigen Wert abweicht."""
        neu_modulanzahl = int(self.entry_modulanzahl.get())
        if neu_modulanzahl != self.data["modulanzahl"]:
            if neu_modulanzahl < len(self.data["enrollments"]):
                self.modulanzahl_not_valid.configure(
                    text="Du hast schon mehr Module begonnen"
                )
            else:
                self.controller.change_modul_anzahl(neu_modulanzahl)
                self.modulanzahl_not_valid.configure(text="Gespeichert")
        else:
            self.modulanzahl_not_valid.configure(text="Entspricht bisherigen Wert")

    def save_hochschule(self) -> None:
        """Validiert und speichert die neue Hochschule, falls sie vom bisherigen Wert abweicht.

        Ablauf:
            * Prüft, ob die Eingabe leer ist oder nur aus Leerzeichen besteht.
            * Prüft, ob die Eingabe mit bisherigem Wert übereinstimmt.
            * Legt die Hochschule an, falls diese nicht in der Datenbank ist.
            * Übergibt ID und Namen dem Controller zur Verknüpfung der Beziehungen.
            * (Dieser erstellt den Studiengang an der neuen Hochschule, falls dieser dort nicht existiert.)

        Da Enrollments eine Beziehung zwischen Student und Modulen eines Studiengangs
        einer Hochschule sind, gehen bei einem Hochschulwechsel die Enrollments verloren.
        """
        if self.verify_input(self.search_combo.get_value()):
            if self.search_combo.get_value() == self.data["hochschule"]:
                self.hochschule_not_valid.configure(text="Entspricht bisherigen Wert")
                return
            hs_id, hs = self.check_or_create_hochschule()
            self.controller.change_hochschule(hochschul_id=hs_id, hochschul_name=hs)
            self.after(0, self.go_to_dashboard)
        else:
            self.hochschule_not_valid.configure(text="Nicht ausgefüllt")

    def save_studiengang(self) -> None:
        """Validiert und speichert den neuen Studiengang, falls dieser vom bisherigen Wert abweicht.

        Ablauf:
            * Prüft, ob die Eingabe leer ist oder nur aus Leerzeichen besteht.
            * Prüft, ob die Eingabe mit bisherigem Wert übereinstimmt.
            * Legt über den Controller den Studiengang an,
              falls dieser nicht in der Datenbank ist.

        Da Enrollments eine Beziehung zwischen Student und Modulen eines Studiengangs,
        gehen bei einem Studiengangwechsel die Enrollments verloren.
        """
        if self.verify_input(self.entry_studiengang.get()):
            if self.entry_studiengang.get() == self.data["studiengang"]:
                self.studiengang_not_valid.configure(text="Entspricht bisherigen Wert")
                return
            self.controller.change_studiengang(self.entry_studiengang.get())
            self.after(0, self.go_to_dashboard)
        else:
            self.studiengang_not_valid.configure(text="Nicht ausgefüllt")

    def _center_over_parent(self, top: ctk.CTkToplevel, w: int, h: int) -> None:
        """Zentriert das Toplevel-Fenster über dem aktuellen Frame."""
        self.update_idletasks()
        px = self.winfo_rootx()
        py = self.winfo_rooty()
        pw = self.winfo_width()
        ph = self.winfo_height()
        x = px + (pw - w) // 2
        y = py + (ph - h) // 2
        top.geometry(f"{w}x{h}+{x}+{y}")

    def open_delete_account(self) -> None:
        """Öffnet ein Popupfenster zur Bestätigung der Accountlöschung."""
        top = ctk.CTkToplevel(self, fg_color="gray35")
        top.overrideredirect(True)
        top.attributes("-topmost", True)
        top.grab_set()
        popup_w, popup_h = 400, 300
        self._center_over_parent(top=top, w=popup_w, h=popup_h)

        settings_close_button = ctk.CTkButton(
            top,
            text=self.icons.CLOSE,
            font=self.fonts.ICONS,
            width=10,
            fg_color="transparent",
            text_color="white",
            hover_color="gray50",
            border_color="black",
            command=lambda: (top.destroy(), self.after(0, self.go_to_settings)),
        )
        settings_close_button.pack(pady=5, anchor="ne")

        ctk.CTkLabel(
            top, text=self.icons.WARNING, text_color=ROT, font=self.fonts.ICONS
        ).pack(pady=10)

        ctk.CTkLabel(
            top,
            text="Bist Du sicher, dass Du dein Profil löschen möchtest?",
            text_color=ROT,
            font=self.fonts.TEXT,
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
            font=self.fonts.TEXT,
            command=self.delete_account,
        ).pack(pady=10)

    def delete_account(self) -> None:
        """Löscht den Account über den Controller und navigiert zum Login"""
        self.controller.delete_student()
        self.after(0, self.go_to_login)

    def verify_input(self, value) -> bool:
        """Gibt ``True``zurück, wenn der übergebene String nach ``.strip()``nicht leer ist."""
        return bool(str(value).strip())

    def verify_email(self) -> bool:
        """Validiert die Email, prüft Datenbank auf Existenz und gibt ggf. Fehlertext aus.

        Returns:
            bool: ``True`` bei erfolgreicher Prüfung.
                  ``False``, falls EmailNotValidError auftritt oder Email-Adresse schon vorhanden ist.
        """
        valid = self.controller.validate_email_for_new_account(
            str(self.entry_email.get())
        )
        if isinstance(valid, EmailNotValidError):
            error = str(valid)
            self.label_email_not_valid.configure(text=error)
            return False
        else:
            if self.controller.check_if_email_exists(valid):
                self.label_email_not_valid.configure(
                    text="Diese Email hat schon einen Account"
                )
                return False
            self.selected_email = valid
            return True

    def check_or_create_hochschule(self) -> tuple[int, str]:
        """Ermittelt Hochschule (ID, Name) aus der SearchableComboBox, legt sie ggf. neu an."""
        self.selected_hochschule_name = self.search_combo.get_value()
        self.selected_hochschule_id = self.search_combo.get_id()

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
        if self.selected_hochschule_id:
            return (self.selected_hochschule_id, self.selected_hochschule_name)
        else:
            raise ValueError("Hochschule hat keine ID.")

    def start_datum_calendar_at_button(self) -> None:
        """Öffnet den Kalender zur Auswahl des Studienstartdatums."""
        self._open_calendar_popup(
            anchor=self.button_startdatum,
            mindate=datetime.date(2010, 1, 1),
            maxdate=datetime.date.today(),
            on_date_selected=self._set_startdatum,
        )

    def _set_startdatum(self, date: datetime.date) -> None:
        """Verarbeitet das im Kalender gewählte Studienstartdatum.

        Aktualisiert sowohl die sichtbare Textvariable als auch den
        intern genutzten ISO-String für das Startdatum.
        """
        self.selected_startdatum.set(from_iso_to_ddmmyyyy(date=date))
        self.selected_startdatum_real = date.isoformat()

    # Deaktiviert, da sonst Studenten die ECTS-Punkte eines Studiengangs ändern können,
    # das sollte nur durch Admins oder Hochschulen möglich sein.

    # def validate_ects(self, ects: str) -> bool:
    #     """Prüft, ob ECTS eine gültige Ganzzahl (1-500) ist und größer gleich den erarbeiteten ECTS bleibt.

    #     Returns:
    #         bool: ``True``, wenn Prüfung erfolgreich.
    #     """
    #     try:
    #         number = int(ects)
    #     except ValueError:
    #         self.label_no_int.configure(text="Muss eine (Ganz-) Zahl sein")
    #         return False

    #     if 0 < number <= 500:
    #         if number >= self.data["erarbeitete_ects"]:
    #             self.label_no_int.configure(text="")
    #             return True
    #         else:
    #             self.label_no_int.configure(
    #                 text="Du hast schon mehr ECTS-Punkte erarbeitet"
    #             )
    #             return False
    #     else:
    #         self.label_no_int.configure(text="Zahl muss zwischen 1 und 500 liegen")
    #         return False


class ExFrame(ctk.CTkFrame, CalendarMixin):
    """Frame zur Verwaltung des Exmatrikulationsdatums.

    Ermöglicht das Setzen eines Exmatrikulationsdatums.
    Bei bereits gesetztem Datum wird die Auswahl gesperrt und
    optional das Löschen des Datums angeboten.
    """

    def __init__(self, master, controller: Controller, go_to_dashboard) -> None:
        """Initialisiert den Exmatrikulations-Frame und lädt aktuellen Daten.

        Args:
            master: Eltern-Widget, liefert u. a. Fonts.
            controller: Controller für Datenzugriff und Persistenz.
            go_to_dashboard: Callback zurück zum Dashboard.
        """
        super().__init__(master, fg_color="transparent")

        self.controller = controller
        self.go_to_dashboard = go_to_dashboard

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)

        self.data = self.controller.load_dashboard_data()

        self.fonts = master.fonts
        self.icons = master.icons

        self._init_header()
        self._init_form()

    def _init_header(self) -> None:
        """Erzeugt Header-Bereich mit Titel und Close-Button."""
        ex_frame = ctk.CTkFrame(
            self,
            fg_color=(BACKGROUND, BACKGROUND_DARK),
            border_color="black",
            border_width=2,
        )
        ex_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        ex_frame.grid_columnconfigure(0, weight=1)
        ex_frame.grid_columnconfigure(1, weight=0)

        ex_ueber_label = ctk.CTkLabel(
            ex_frame,
            text="Du wurdest exmatrikuliert?",
            font=self.fonts.H2_italic,
            justify="left",
        )
        ex_ueber_label.grid(row=0, sticky="nw", padx=10, pady=10)

        ex_close_button = ctk.CTkButton(
            ex_frame,
            text=self.icons.CLOSE,
            font=self.fonts.ICONS,
            width=10,
            fg_color="transparent",
            text_color="black",
            hover_color="gray95",
            command=lambda: self.after(0, self.go_to_dashboard),
        )
        ex_close_button.grid(row=0, column=1, padx=(0, 2), pady=(2, 0), sticky="ne")

    def _init_form(self) -> None:
        """Erzeugt das Formular zum Speichern/Löschen des Exmatrikulationsdatums."""
        set_ex_frame = ctk.CTkFrame(
            self,
            fg_color=(BACKGROUND, BACKGROUND_DARK),
            border_color="black",
            border_width=2,
        )
        set_ex_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        for column in range(4):
            set_ex_frame.grid_columnconfigure(column, weight=1)

        self.selected_exdatum = tk.StringVar(
            value=from_iso_to_ddmmyyyy(self.data["exmatrikulationsdatum"])
        )

        self.label_exdatum = ctk.CTkLabel(
            set_ex_frame, text="Wann wurdest Du exmatrikuliert?"
        )
        self.label_exdatum.grid(row=1, column=0, sticky="ew", padx=10, pady=10)

        self.button_exdatum = ctk.CTkButton(
            set_ex_frame,
            text="Exmatrikulationsdatum wählen",
            text_color="black",
            fg_color="transparent",
            border_color="black",
            border_spacing=2,
            border_width=2,
            hover_color="gray95",
            command=self.ex_datum_calendar_at_button,
        )
        self.button_exdatum.grid(row=1, column=2, padx=10, pady=10)

        self.label_exdatum_variable = ctk.CTkLabel(
            set_ex_frame, textvariable=self.selected_exdatum
        )
        self.label_exdatum_variable.grid(row=1, column=1, sticky="ew", padx=10, pady=10)

        self.selected_exdatum_real: str | None = None

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
            self.button_exdatum.configure(state="disabled")
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

    def delete_ex_date(self) -> None:
        """Löscht das gespeicherte Exmatrikulationsdatum und navigiert zum Dashboard."""
        if self.data["exmatrikulationsdatum"]:
            self.controller.change_exmatrikulationsdatum(None)
            self.after(0, self.go_to_dashboard)

    def datum_submit(self) -> None:
        """Speichert das Exmatrikulationsdatum und navigiert zum Dashboard.

        Zeigt eine Fehlermeldung, wenn kein Datum gewählt wurde.
        """
        if not self.selected_exdatum_real:
            self.label_leere_felder.configure(
                text="Exmatrikulationsdatum nicht ausgewählt."
            )
            return
        self.selected_exdatum_str = self.selected_exdatum_real

        self.controller.change_exmatrikulationsdatum(
            datetime.date.fromisoformat(self.selected_exdatum_str)
        )
        self.after(0, self.go_to_dashboard)

    def ex_datum_calendar_at_button(self) -> None:
        """Öffnet den Kalender zur Auswahl des Exmatrikulationsdatums."""
        self._open_calendar_popup(
            anchor=self.button_exdatum,
            mindate=self.data["startdatum"],
            maxdate=datetime.date.today(),
            on_date_selected=self._set_exdatum,
        )

    def _set_exdatum(self, date: datetime.date) -> None:
        """Verarbeitet das im Kalender gewählte Exmatrikulationsdatum.

        Aktualisiert sowohl die sichtbare Textvariable als auch den
        intern genutzten ISO-String für das Exmatrikulationsdatum.
        """
        self.selected_exdatum.set(from_iso_to_ddmmyyyy(date=date))
        self.selected_exdatum_real = date.isoformat()


class ZieleFrame(ctk.CTkFrame, CalendarMixin):
    """Frame zur Anpassung der persönlichen Studienziele (Note/Datum)."""

    def __init__(self, master, controller: Controller, go_to_dashboard) -> None:
        """Initialisiert den Ziele-Frame und lädt aktuelle Dashboard-Daten.

        Args:
            master: Eltern-Widget ,liefert u. a. ``master.fonts``.
            controller: Controller für Datenzugriff und Persistenz.
            go_to_dashboard: Callback zur Rückkehr zum Dashboard.
        """
        super().__init__(master, fg_color="transparent")

        self.controller = controller
        self.go_to_dashboard = go_to_dashboard

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)

        self.data = self.controller.load_dashboard_data()

        self.fonts = master.fonts
        self.icons = master.icons

        self._init_header()
        self._init_form()

    def _init_header(self) -> None:
        """Erzeugt den Header mit Titel und Close-Button."""
        ziele_frame = ctk.CTkFrame(
            self,
            fg_color=(BACKGROUND, BACKGROUND_DARK),
            border_color="black",
            border_width=2,
        )
        ziele_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        ziele_frame.grid_columnconfigure(0, weight=1)
        ziele_frame.grid_columnconfigure(1, weight=0)

        ziele_ueber_label = ctk.CTkLabel(
            ziele_frame,
            text="Änder Deine Ziele:",
            font=self.fonts.H2_italic,
            justify="left",
        )
        ziele_ueber_label.grid(row=0, sticky="nw", padx=10, pady=10)

        ziele_close_button = ctk.CTkButton(
            ziele_frame,
            text=self.icons.CLOSE,
            font=self.fonts.ICONS,
            width=10,
            fg_color="transparent",
            text_color="black",
            hover_color="gray95",
            command=lambda: self.after(0, self.go_to_dashboard),
        )
        ziele_close_button.grid(row=0, column=1, padx=(0, 2), pady=(2, 0), sticky="ne")

    def _init_form(self) -> None:
        """Erzeugt den Bereich zur Anpassung von Zielnote und Zieldatum."""
        zs_frame = ctk.CTkFrame(
            self,
            fg_color=(BACKGROUND, BACKGROUND_DARK),
            border_color="black",
            border_width=2,
        )
        zs_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

        zs_frame.grid_columnconfigure(0, weight=1)
        zs_frame.grid_columnconfigure(1, weight=1)
        zs_frame.grid_columnconfigure(2, weight=1)
        zs_frame.grid_columnconfigure(3, weight=1)

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
        self.selected_zieldatum_real: str | None = None

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

    def datum_submit(self) -> None:
        """Validiert und speichert das Zieldatum.

        Zeigt eine Fehlermeldung, falls kein Datum gewählt wurde.
        """
        if not self.selected_zieldatum_real:
            self.label_leere_felder.configure(text="Zieldatum nicht ausgewählt.")
            return
        self.selected_zieldatum_str = self.selected_zieldatum_real

        self.controller.change_zieldatum(
            datetime.date.fromisoformat(self.selected_zieldatum_str)
        )
        self.label_leere_felder.configure(
            text="Zieldatum gespeichert", text_color=GRUEN
        )

    def noten_submit(self) -> None:
        """Speichert die aktuell ausgewählte Zielnote."""
        self.selected_zielnote = self.entry_zielnote
        self.controller.change_zielnote(self.selected_zielnote)
        self.label_leere_felder.configure(
            text="Wunschnote gespeichert", text_color=GRUEN
        )

    def ziel_datum_calendar_at_button(self) -> None:
        """Öffnet den Kalender zur Auswahl des Zieldatums."""
        self._open_calendar_popup(
            anchor=self.button_zieldatum,
            mindate=self.data["startdatum"],
            maxdate=datetime.date(year=2200, month=12, day=31),
            on_date_selected=self._set_zieldatum,
        )

    def _set_zieldatum(self, date: datetime.date) -> None:
        """Verarbeitet das im Kalender gewählte Zieldatum.

        Aktualisiert sowohl die sichtbare Textvariable als auch den
        intern genutzten ISO-String für das Zieldatum.
        """
        self.selected_zieldatum.set(from_iso_to_ddmmyyyy(date=date))
        self.selected_zieldatum_real = date.isoformat()

    def slider_zielnote_event(self, value: float) -> None:
        """Fragt Slider-Wert ab und aktualisiert Label mit gerundetem Wert.

        Args:
            value: Aktueller Slider-Wert."""
        self.entry_zielnote = round(float(value), 1)
        self.label_zielnote.configure(text=f"{round(float(value), 1)}")


class UeberFrame(ctk.CTkFrame):
    """Über-Frame der DASHBOARD-Anwendung.

    Zeigt Projektbeschreibung, Version, Hinweise zu verwendeten Bibliotheken/Lizenzen
    sowie einen Button zum Öffnen des GitHub-Repositories im Browser.
    """

    def __init__(self, master, controller: Controller, go_to_dashboard) -> None:
        """Initialisiert den Über-Frame und baut alle UI-Elemente auf.

        Args:
            master: Eltern-Widget, liefert u. a. ``master.fonts``.
            controller: Controller-Referenz (aktuell nicht genutzt).
            go_to_dashboard: Callback zur Rückkehr zum Dashboard.
        """
        super().__init__(master, fg_color="transparent")
        self.controller = controller
        self.go_to_dashboard = go_to_dashboard

        self.fonts = master.fonts
        self.icons = master.icons

        ueber_close_button = ctk.CTkButton(
            self,
            text=self.icons.CLOSE,
            font=self.fonts.ICONS,
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
            font=self.fonts.H1,
        )
        ueber_ueber_label.pack(pady=20)

        version_label = ctk.CTkLabel(
            self,
            text="Version: 1.0",
            font=self.fonts.H3,
        )
        version_label.pack(pady=20)

        ueber_label = MultiLineLabel(
            self,
            width=110,
            text="Dieses Programm ist im Rahmen des Studiums 'Angewandte Künstliche Intelligenz' "
            "an der IU Internationalen Hochschule entstanden. Es wurde im 'Projekt: Objektorientierte "
            "und funktionale Programmierung mit Python' von Florian Erik Janssens entworfen und programmiert.",
            font=self.fonts.TEXT,
        )
        ueber_label.pack(pady=20)

        cc_label = MultiLineLabel(
            self,
            width=110,
            text="Diese Software nutzt folgende Open-Source-Bibliotheken: "
            "SQLAlchemy (MIT), CustomTkinter (MIT), tkcalendar (MIT), "
            "argon2-cffi (MIT), python-dateutil (Apache 2.0), "
            "email-validator (CC0). Vollständige Lizenzen siehe THIRD_PARTY_LICENSES.txt.\n"
            "Die Liste deutscher Hochschulen wird von Hochschulkompass.de als txt-Datei zur Verfügung gestellt.",
            font=self.fonts.TEXT,
        )
        cc_label.pack(pady=20)

        hochschulkompass_url = (
            "https://www.hochschulkompass.de/hochschulen/downloads.html"
        )

        hochschulkompass_url_button = ctk.CTkButton(
            self,
            text="Hochschulkompass.de",
            font=self.fonts.TEXT,
            text_color="black",
            fg_color="transparent",
            border_color="black",
            border_spacing=2,
            border_width=2,
            hover_color="gray95",
            command=lambda: webbrowser.open_new_tab(hochschulkompass_url),
        )
        hochschulkompass_url_button.pack(pady=(10, 5))
        ToolTip(
            hochschulkompass_url_button, text="Öffnet Hochschulkompass.de im Browser"
        )

        url = "https://github.com/printhellogithub/IU_Dashboard"
        gh_button = ctk.CTkButton(
            self,
            text="Visit on Github",
            font=self.fonts.TEXT,
            text_color="black",
            fg_color="transparent",
            border_color="black",
            border_spacing=2,
            border_width=2,
            hover_color="gray95",
            command=lambda: webbrowser.open_new_tab(url),
        )
        gh_button.pack(pady=10)
        ToolTip(gh_button, text="Öffnet GitHub-Repository im Browser")


class App(ctk.CTk):
    """
    Hauptprogrammfenster-Klasse des Dashboards.
    Die Klasse dient als Hauptfenster und regelt die Navigation zwischen
    verschiedenen Frames (Fenster).

    Attribute:
        controller (Controller): Anwendungssteuerung mit Geschäftslogik.
        fonts (Fonts): Font Manager der Anwendung.
        current_frame (ctk.CTkFrame): Der aktuell angezeigte Frame.
    """

    def __init__(
        self,
        *,
        offline: bool = False,
        debug: bool = False,
        log_to_console: bool = False,
        follow_system_mode: bool = False,
    ) -> None:
        """
        Initialisiert das Dashboard Programm.

        * Setzt Logging auf.

        Args:
            offline (bool): Wenn True, wird das Programm im Offline-Modus gestartet.
            debug (bool): Wenn True, aktiviert Logging auf DEBUG Level.
            log_to_console (bool): Wenn True, aktiviert Logging-Anzeige in der Console.
            follow_system_mode (bool): Wenn True, wird Light-/Dark-Mode vom System übernommen.
        """
        setup_logging(debug=debug, log_to_console=log_to_console)
        logger.info(
            "Programmstart: Level=Debug: %s, log_to_console: %s.", debug, log_to_console
        )
        super().__init__(fg_color=(BACKGROUND, BACKGROUND_DARK))

        # Fonts und Icons laden
        self.fonts = Fonts()
        self.icons = Icons()

        self.controller = Controller(seed=True, offline=offline)

        # Konfiguriere Programmfenster
        self.title("Dashboard")
        self.geometry("960x640")
        self.minsize(960, 640)
        self.maxsize(1920, 1080)
        # Erzwinge Tag-Modus bis Darkmode ausreichend getestet
        logger.info("follow_system_mode: %s", follow_system_mode)
        if not follow_system_mode:
            ctk.set_appearance_mode("light")
            style = ttk.Style()
            try:
                style.theme_use("default")
            except Exception:
                pass
        # Zentriere Fenster auf Bildschirm
        self.center_window()
        self.current_frame = None
        # Zeige Login zu Programmstart
        self.show_login()

    def center_window(self) -> None:
        """Zentriert das Fenster auf dem Bildschirm."""

        # Aktualisiere, damit winfo_* korrekte Fenstergröße zurückgibt
        self.update_idletasks()

        window_width = self.winfo_width()
        window_height = self.winfo_height()

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # Berechnet linken oberen Punkt, dass das Fenster zentriert erscheint
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        self.geometry(f"{window_width}x{window_height}+{x}+{y}")

    def show_login(self) -> None:
        """
        Blendet aktuellen Inhalt aus und zeigt den Login-Frame an.

        Falls ein Frame aktiv ist, wird er entfernt und zerstört.
        Anschließend wird ein neuer 'LoginFrame' erzeugt und als aktuelles UI-Element angezeigt.

        Der Login-Frame erhält Callback-Funktionen, mit denen er zum Dashboard
        oder zum 'NewUserFrame'-Frame wechseln kann.
        """

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

    def show_new_user(self) -> None:
        """
        Blendet aktuellen Inhalt aus und zeigt den 'NewUserFrame' an.

        Dieser Frame ist der erste Frame (1/2) im Prozess der User-Registrierung.
        Falls ein Frame aktiv ist, wird er entfernt und zerstört.
        Anschließend wird ein neuer 'NewUserFrame' erzeugt und als aktuelles UI-Element angezeigt.

        Der 'NewUserFrame'-Frame erhält Callback-Funktionen, mit denen er zum Login-Frame zurück
        oder zum 'StudiengangAuswahlFrame'-Frame wechseln kann.
        """
        if self.current_frame:
            self.current_frame.pack_forget()
            self.current_frame.destroy()
            self.update_idletasks()
        self.current_frame = NewUserFrame(
            self,
            controller=self.controller,
            go_to_login=self.show_login,
            go_to_studiengang_auswahl=self.show_studiengang_auswahl,
        )
        self.current_frame.pack(fill="both", expand=True)

    def show_studiengang_auswahl(self, cache) -> None:
        """
        Blendet aktuellen Inhalt aus und zeigt den 'StudiengangAuswahlFrame' an.

        Dieser Frame ist der zweite Frame (2/2) im Prozess der User-Registrierung.
        Falls ein Frame aktiv ist, wird er entfernt und zerstört.
        Anschließend wird ein neuer 'StudiengangAuswahlFrame' erzeugt und als aktuelles UI-Element angezeigt.

        Der 'StudiengangAuswahlFrame'-Frame erhält Callback-Funktionen, mit denen er zum Login-Frame zurück
        oder zum Dashboard wechseln kann.
        """
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
        )
        self.current_frame.pack(fill="both", expand=True)

    def show_dashboard(self) -> None:
        """Blendet aktuellen Inhalt aus und zeigt das Dashboard.

        Dieser Frame ist das zentrale Fenster der Anwendung.
        Falls ein Frame aktiv ist, wird er entfernt und zerstört.
        Anschließend wird ein neuer 'DashboardFrame' erzeugt und als aktuelles UI-Element angezeigt.

        Der 'DashboardFrame'-Frame erhält Callback-Funktionen, mit denen er zu allen Frames, außer denen zur User-Registrierung, wechseln kann.
        """
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

    def show_add_enrollment(self) -> None:
        """
        Blendet aktuellen Inhalt aus und zeigt den 'AddEnrollmentFrame' an.

        Dieser Frame zeigt ein Formular zur Erstellung eines Enrollments.
        Falls ein Frame aktiv ist, wird er entfernt und zerstört.
        Anschließend wird ein neuer 'AddEnrollmentFrame' erzeugt und als aktuelles UI-Element angezeigt.

        Der 'AddEnrollmentFrame'-Frame erhält Callback-Funktionen, mit denen er zum Dashboard zurück
        oder zum 'EnrollmentFrame' wechseln kann.
        """
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

    def show_enrollment(self, enrollment_id) -> None:
        """
        Blendet aktuellen Inhalt aus und zeigt den Enrollment-Frame an.

        Dieser Frame zeigt die Daten eines Enrollments.
        Falls ein Frame aktiv ist, wird er entfernt und zerstört.
        Anschließend wird ein neuer 'EnrollmentFrame' erzeugt und als aktuelles UI-Element angezeigt.

        Der 'EnrollmentFrame'-Frame erhält Callback-Funktionen, mit denen er zum Dashboard zurück
        oder zum 'PLAddFrame' wechseln kann.
        """
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

    def show_pl(self, pl_id, e_id) -> None:
        """
        Blendet aktuellen Inhalt aus und zeigt den Prüfungsleistungs-Frame an.

        Dieser Frame zeigt die Daten einer Prüfungsleistung oder ein Formular, um eine Prüfungsleistung zu erstellen.
        Falls ein Frame aktiv ist, wird er entfernt und zerstört.
        Anschließend wird ein neuer 'PLAddFrame' erzeugt und als aktuelles UI-Element angezeigt.

        Der 'PLAddFrame'-Frame erhält eine Callback-Funktion, mit der er zum Enrollment zurück wechseln kann.
        """
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

    def show_settings(self) -> None:
        """
        Blendet aktuellen Inhalt aus und zeigt den Settings-Frame an.

        Dieser Frame zeigt Einstellungen, um Profildaten zu ändern.
        Falls ein Frame aktiv ist, wird er entfernt und zerstört.
        Anschließend wird ein neuer 'SettingsFrame' erzeugt und als aktuelles UI-Element angezeigt.

        Der 'SettingsFrame'-Frame erhält Callback-Funktionen, mit denen er sich selbst neu laden, zum Dashboard zurück
        oder zum 'LoginFrame' wechseln kann.
        """
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

    def show_exmatrikulation(self) -> None:
        """
        Blendet aktuellen Inhalt aus und zeigt den Exmatrikulations-Frame an.

        Dieser Frame zeigt Einstellungen zum Exmatrikulationsdatum.
        Falls ein Frame aktiv ist, wird er entfernt und zerstört.
        Anschließend wird ein neuer 'ExFrame' erzeugt und als aktuelles UI-Element angezeigt.

        Der 'ExFrame'-Frame erhält eine Callback-Funktion, mit der er zum Dashboard zurück wechseln kann.
        """
        if self.current_frame:
            self.current_frame.pack_forget()
            self.current_frame.destroy()
            self.update_idletasks()
        self.current_frame = ExFrame(
            self,
            controller=self.controller,
            go_to_dashboard=self.show_dashboard,
        )
        self.current_frame.pack(fill="both", expand=True)

    def show_ziele(self) -> None:
        """
        Blendet aktuellen Inhalt aus und zeigt den Ziele-Frame an.

        Dieser Frame zeigt Einstellungen zu den Studienzielen.
        Falls ein Frame aktiv ist, wird er entfernt und zerstört.
        Anschließend wird ein neuer 'ZieleFrame' erzeugt und als aktuelles UI-Element angezeigt.

        Der 'ZieleFrame'-Frame erhält eine Callback-Funktion, mit der er zum Dashboard zurück wechseln kann.
        """
        if self.current_frame:
            self.current_frame.pack_forget()
            self.current_frame.destroy()
            self.update_idletasks()
        self.current_frame = ZieleFrame(
            self,
            controller=self.controller,
            go_to_dashboard=self.show_dashboard,
        )
        self.current_frame.pack(fill="both", expand=True)

    def show_ueber(self) -> None:
        """
        Blendet aktuellen Inhalt aus und zeigt den Über-Frame an.

        Falls ein Frame aktiv ist, wird er entfernt und zerstört.
        Anschließend wird ein neuer 'UeberFrame' erzeugt und als aktuelles UI-Element angezeigt.

        Der 'UeberFrame'-Frame erhält eine Callback-Funktion, mit der er zum Dashboard zurück wechseln kann.
        """
        if self.current_frame:
            self.current_frame.pack_forget()
            self.current_frame.destroy()
            self.update_idletasks()
        self.current_frame = UeberFrame(
            self, controller=self.controller, go_to_dashboard=self.show_dashboard
        )
        self.current_frame.pack(fill="both", expand=True)


if __name__ == "__main__":
    args = parse_args()
    app = App(
        offline=args.offline,
        debug=args.debug,
        log_to_console=args.log_to_console,
        follow_system_mode=args.follow_system_mode,
    )
    app.mainloop()
