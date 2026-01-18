import datetime
import pytest
from src.models import Student, EnrollmentStatus


def test_student_password_hashing(db):
    """Testet das sichere Setzen und Prüfen von Passwörtern beim Student-Model, sowie das Ablehnen ungültiger Email-Adressen.

    Verifiziert:
        - dass ``verify_password`` korrektes und falsches Passwort unterscheidet,
        - dass ungültige Email-Adressen nicht akzeptiert werden.
    """
    s = Student(
        name="A",
        matrikelnummer="123",
        email="a@gmail.com",
        password="secret",
        semester_anzahl=6,
        modul_anzahl=36,
        start_datum=datetime.date(2024, 1, 1),
        ziel_datum=datetime.date(2027, 1, 1),
        ziel_note=2.0,
    )
    db.session.add(s)
    db.session.commit()
    assert s.verify_password("secret") is True
    assert s.verify_password("wrong") is False
    with pytest.raises(ValueError):
        s.email = "a@example.com"


def test_exmatrikulationsdatum(db):
    """Testet das Setzen des Exmatrikulationsdatums, auch auf ``None``.

    Verifiziert:
        - dass ``exmatrikulationsdatum`` optional ist,
        - dass ``exmatrikulationsdatum`` gesetzt werden kann,
        - dass ``None`` korrekt persistiert wird.
    """
    s = Student(
        name="B",
        matrikelnummer="456",
        email="b@gmail.com",
        password="pw",
        semester_anzahl=8,
        modul_anzahl=42,
        start_datum=datetime.date(2023, 6, 1),
        ziel_datum=datetime.date(2026, 6, 1),
        ziel_note=3.0,
    )
    db.session.add(s)
    db.session.commit()
    s.exmatrikulationsdatum = datetime.date(2025, 6, 1)
    db.session.commit()
    assert s.exmatrikulationsdatum is not None
    assert s.exmatrikulationsdatum == datetime.date(2025, 6, 1)
    s.exmatrikulationsdatum = None
    db.session.commit()
    assert s.exmatrikulationsdatum is None


def test_enrollment_status_abgeschlossen(db):
    """Testet den Enrollment-Status anhand einer erfolgreichen Prüfungsleistung.

    Ablauf:
        - Student, Hochschule, Studiengang und Modul anlegen,
        - Enrollment mit Prüfungsleistungen erzeugen,
        - Prüfungsleistung mit Note und Datum ergänzen,
        - Enrollment-Status aktualisieren.

    Verifiziert:
        - Statuswechsel von IN_BEARBEITUNG zu ABGESCHLOSSEN,
        - korrekte Berechnung der Modulnote.
    """
    hs = db.add_hochschule("HS")
    sg = db.add_studiengang("SG", 180)
    sg.hochschule = hs
    db.session.commit()
    s = db.add_student(
        name="C",
        matrikelnummer="789",
        email="c@gmail.com",
        password="pw",
        semester_anzahl=10,
        modul_anzahl=32,
        start_datum=datetime.date(2024, 1, 1),
        ziel_datum=datetime.date(2025, 1, 1),
        ziel_note=1.6,
    )
    s.hochschule = hs
    s.studiengang = sg
    db.session.commit()

    m = db.add_modul(
        name="Python", modulcode="P01", ects_punkte=5, studiengang_id=sg.id
    )
    e = db.add_enrollment(
        student=s,
        modul=m,
        status=EnrollmentStatus.IN_BEARBEITUNG,
        einschreibe_datum=datetime.date(2024, 2, 1),
        anzahl_pruefungsleistungen=1,
    )
    assert e.status == EnrollmentStatus.IN_BEARBEITUNG
    e.add_pruefungsleistung(
        teilpruefung=0,
        teilpruefung_gewicht=1.0,
        versuch=1,
        note=1.7,
        datum=datetime.date(2024, 3, 1),
    )
    db.session.commit()
    e.aktualisiere_status()
    assert e.status == EnrollmentStatus.ABGESCHLOSSEN
    assert e.berechne_enrollment_note() == 1.7


def test_enrollment_status_nicht_bestanden(db):
    """Testet den Enrollment-Status anhand von drei nicht bestandenen Prüfungsleistungen.

    Ablauf:
        - Student, Hochschule, Studiengang und Modul anlegen,
        - Enrollment mit Prüfungsleistungen erzeugen,
        - Prüfungsleistungen mit Note und Datum ergänzen,
        - Enrollment-Status aktualisieren.

    Verifiziert:
        - kein Statuswechsel vor drittem Versuch,
        - Statuswechsel von IN_BEARBEITUNG zu NICHT_BESTANDEN nach drittem Versuch.
        - keine Modulnote: ``None``.
    """
    hs = db.add_hochschule("HS")
    sg = db.add_studiengang("SG", 180)
    sg.hochschule = hs
    db.session.commit()
    s = db.add_student(
        name="C",
        matrikelnummer="789",
        email="c@gmail.com",
        password="pw",
        semester_anzahl=10,
        modul_anzahl=32,
        start_datum=datetime.date(2024, 1, 1),
        ziel_datum=datetime.date(2025, 1, 1),
        ziel_note=1.6,
    )
    s.hochschule = hs
    s.studiengang = sg
    db.session.commit()

    m = db.add_modul(
        name="Python", modulcode="P01", ects_punkte=5, studiengang_id=sg.id
    )
    e = db.add_enrollment(
        student=s,
        modul=m,
        status=EnrollmentStatus.IN_BEARBEITUNG,
        einschreibe_datum=datetime.date(2024, 2, 1),
        anzahl_pruefungsleistungen=1,
    )
    assert e.status == EnrollmentStatus.IN_BEARBEITUNG
    e.add_pruefungsleistung(
        teilpruefung=0,
        teilpruefung_gewicht=1.0,
        versuch=1,
        note=4.7,
        datum=datetime.date(2024, 3, 1),
    )
    db.session.commit()
    e.aktualisiere_status()
    assert e.status == EnrollmentStatus.IN_BEARBEITUNG
    e.add_pruefungsleistung(
        teilpruefung=0,
        teilpruefung_gewicht=1.0,
        versuch=2,
        note=4.9,
        datum=datetime.date(2024, 3, 1),
    )
    db.session.commit()
    e.aktualisiere_status()
    assert e.status == EnrollmentStatus.IN_BEARBEITUNG
    e.add_pruefungsleistung(
        teilpruefung=0,
        teilpruefung_gewicht=1.0,
        versuch=3,
        note=5.7,
        datum=datetime.date(2024, 3, 1),
    )
    db.session.commit()
    e.aktualisiere_status()
    assert e.status == EnrollmentStatus.NICHT_BESTANDEN
    assert e.berechne_enrollment_note() is None
