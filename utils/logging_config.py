import logging
import logging.config
from pathlib import Path

LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)


def setup_logging(debug: bool = False, log_to_console: bool = False) -> None:
    """
    Initialisiert das Logging für das ganze Projekt.

    Parameter:
        debug (bool):
            - Wenn True -> globales Log-Level == DEBUG.
            - Wenn False -> globales Log-Level == INFO

        log_to_console (bool):
            - Wenn True -> Logs werden zusätzlich im Terminal ausgegeben.
            - Wenn False -> nur Datei-Logging aktiv.

    Verhalten:
        - Erstellt einen Ordner 'logs' (falls nicht vorhanden).
        - Schreibt alle Logs in 'dashboard.log'.
        - Der File-Handler loggt immer ab DEBUG.
        - Die Konsole (falls aktiv) loggt ab INFO oder DEBUG, je nach debug-Flag.
        - SQLAlchemy-Engine-Logs werden auf INFO begrenzt und nur in Datei gespeichert.

    Verwendung:
        - möglichst früh bei Programmstart aufrufen, damit Logger korrekt konfiguriert sind.
    """

    # Globales Logging-Level abhängig von debug-Flag
    level = "DEBUG" if debug else "INFO"

    # Standard: nur Datei loggen, +Terminal mit log_to_console-Flag
    handlers_for_root = ["file"]
    if log_to_console:
        handlers_for_root.append("console")

    # Logging-Konfiguration
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        # vers. Ausgabeformate
        "formatters": {
            # für Datei
            "standard": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"},
            # für Terminal
            "short": {"format": "[%(levelname)s] %(name)s: %(message)s"},
        },
        # Handler definieren, wohin das Log geschrieben wird
        "handlers": {
            "console": {  # Terminal-Ausgabe
                "class": "logging.StreamHandler",
                "formatter": "short",
                "level": level,
            },
            "file": {  # Datei-Ausgabe (rotierend)
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "standard",
                "level": "DEBUG",
                "filename": str(LOG_DIR / "dashboard.log"),
                "maxBytes": 5 * 1024 * 1024,  # 5MB pro Datei
                "backupCount": 5,  # Anzahl Archivdateien
                "encoding": "utf-8",
            },
        },
        # Root-Logger: gilt für alle Logger ohne eigenen Eintrag
        "root": {
            "handlers": handlers_for_root,
            "level": level,
        },
        # Spezielle Einstellungen für bestimmte Logger
        "loggers": {
            "sqlalchemy.engine": {
                "level": "INFO",
                "handlers": ["file"],  # nur Datei-Logging
                "propagate": False,  # nicht an root weitergeben
            },
        },
    }

    # Konfiguration aktivieren
    logging.config.dictConfig(config)
