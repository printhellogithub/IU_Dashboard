from src.app import from_iso_to_ddmmyyyy
import datetime


def test_from_iso_to_ddmmyyyy():
    """Testet korrekte Datumsausgabe bei verschiedenen Eingabewerten.

    Verifiziert:
        - dass ein datetime.date-Objekt korrekt gewandelt wird.
        - dass ein ISO-String-Datum korrekt gewandelt wird.
        - dass ``None`` zur Ausgabe von ``""`` führt.
    """
    assert from_iso_to_ddmmyyyy(datetime.date(2024, 5, 9)) == "09.05.2024"
    assert from_iso_to_ddmmyyyy("2024-05-09") == "09.05.2024"
    assert from_iso_to_ddmmyyyy(None) == ""
