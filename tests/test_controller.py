import datetime
import pytest


def test_create_account_and_semesters(controller):
    cache = {
        "name": "User",
        "matrikelnummer": "111",
        "email": "u@gmail.com",
        "password": "pw",
        "semesteranzahl": 6,
        "modulanzahl": 36,
        "startdatum": "2024-01-01",
        "zieldatum": "2028-01-01",
        "zielnote": 2.0,
        "hochschulname": "HS",
        "hochschulid": None,
        "studiengang_name": "SG",
        "studiengang_id": None,
        "studiengang_ects": 180,
    }
    hs = controller.db.add_hochschule(cache["hochschulname"])
    sg = controller.db.add_studiengang(
        cache["studiengang_name"], cache["studiengang_ects"]
    )
    sg.hochschule = hs
    controller.db.session.commit()
    cache["hochschulid"] = hs.id
    cache["studiengang_id"] = sg.id

    controller.erstelle_account(cache)
    s = controller.student
    assert s is not None
    assert len(s.semester) == cache["semesteranzahl"]
    assert s.hochschule_id == hs.id
    assert s.studiengang_id == sg.id


def test_login(controller):
    hs = controller.db.add_hochschule("HS2")
    sg = controller.db.add_studiengang("SG2", 180)
    sg.hochschule = hs
    controller.db.session.commit()
    s = controller.db.add_student(
        "U",
        "222",
        "u2@gmail.com",
        "pw",
        6,
        36,
        datetime.date(2024, 1, 1),
        datetime.date(2027, 1, 1),
        2.0,
    )
    s.hochschule = hs
    s.studiengang = sg
    controller.db.session.commit()
    controller.student = s
    assert controller.login("u2@gmail.com", "pw")
    assert not controller.login("not_email", "pw")
    assert not controller.login("u2@gmail.com", "xy")


def test_enrollment_flow(controller):
    hs = controller.db.add_hochschule("HS2")
    sg = controller.db.add_studiengang("SG2", 180)
    sg.hochschule = hs
    controller.db.session.commit()
    s = controller.db.add_student(
        "U",
        "222",
        "u2@gmail.com",
        "pw",
        6,
        36,
        datetime.date(2024, 1, 1),
        datetime.date(2027, 1, 1),
        2.0,
    )
    s.hochschule = hs
    s.studiengang = sg
    controller.db.session.commit()
    controller.student = s

    enrollment_cache = {
        "modul_name": "Mathe I",
        "modul_code": "MATH1",
        "modul_ects": 5,
        "kurse_dict": {"K1": "Algebra"},
        "pl_anzahl": 1,
        "startdatum": "2024-02-01",
    }
    e = controller.erstelle_enrollment(enrollment_cache)
    assert e["modul_code"] == "MATH1"
    assert e["anzahl_pruefungsleistungen"] == 1
    # Change-methode
    pl = e["pruefungsleistungen"][0]
    controller.change_pl(
        enrollment_id=e["id"],
        pl_dict={"id": pl["id"], "datum": "2024-06-10", "note": 1.3},
    )
    # Daten neu laden + Status prüfen
    nd = controller.get_enrollment_data(e["id"])
    assert nd["enrollment_note"] == pytest.approx(1.3, abs=1e-12)
    assert nd["status"] == "ABGESCHLOSSEN"


def test_changes(controller):
    hs = controller.db.add_hochschule("HS2")
    sg = controller.db.add_studiengang("SG2", 180)
    sg.hochschule = hs
    controller.db.session.commit()
    s = controller.db.add_student(
        "U",
        "222",
        "u2@gmail.com",
        "pw",
        6,
        36,
        datetime.date(2024, 1, 1),
        datetime.date(2027, 1, 1),
        2.0,
    )
    s.hochschule = hs
    s.studiengang = sg
    controller.db.session.commit()
    controller.student = s

    controller.change_email("new@gmail.com")
    assert s.email == "new@gmail.com"
    controller.change_password("newpw")
    assert s.verify_password("newpw")
    controller.change_name("Neu")
    assert s.name == "Neu"
    controller.change_matrikelnummer("XYZ1")
    assert s.matrikelnummer == "XYZ1"
    controller.change_semester_anzahl(8)
    assert len(s.semester) == 8
    controller.change_startdatum(datetime.date(2024, 2, 1))
    assert s.semester[0].beginn == datetime.date(2024, 2, 1)
    controller.change_gesamt_ects(200)
    assert s.studiengang.gesamt_ects_punkte == 200
    controller.change_modul_anzahl(35)
    assert s.modul_anzahl == 35


def test_time_progress(controller, db):
    s = db.add_student(
        "U",
        "1",
        "t@gmail.com",
        "pw",
        12,
        48,
        datetime.date(2024, 1, 1),
        datetime.date(2024, 12, 31),
        2.0,
    )
    controller.student = s
    controller.erstelle_semester_fuer_student()
    # ohne Exmatrikulation
    p = controller.get_time_progress()
    assert p == 1.0
    # mit Exmatrikulation
    s.exmatrikulationsdatum = datetime.date(2024, 3, 1)
    db.session.commit()
    p2 = controller.get_time_progress()
    assert 0 <= p2 <= 0.164


def test_counts_and_avg(controller, db):
    hs = db.add_hochschule("HS")
    sg = db.add_studiengang("SG", 180)
    sg.hochschule = hs
    db.session.commit()
    s = db.add_student(
        "U",
        "1",
        "u@gmail.com",
        "pw",
        6,
        36,
        datetime.date(2024, 1, 1),
        datetime.date(2024, 12, 31),
        2.0,
    )
    s.hochschule = hs
    s.studiengang = sg
    db.session.commit()
    controller.student = s
    e1 = controller.erstelle_enrollment(
        {
            "modul_name": "M1",
            "modul_code": "M1",
            "modul_ects": 5,
            "kurse_dict": {},
            "pl_anzahl": 1,
            "startdatum": "2024-01-02",
        }
    )
    e2 = controller.erstelle_enrollment(
        {
            "modul_name": "M2",
            "modul_code": "M2",
            "modul_ects": 5,
            "kurse_dict": {},
            "pl_anzahl": 1,
            "startdatum": "2024-01-03",
        }
    )
    # e1 abschließen
    pl = controller.get_enrollment_data(e1["id"])["pruefungsleistungen"][0]
    controller.change_pl(e1["id"], {"id": pl["id"], "datum": "2024-02-01", "note": 2.0})
    assert controller.get_number_of_enrollments_with_status_ausstehend() >= 0
    assert controller.get_erarbeitete_ects() == 5
    assert controller.get_notendurchschnitt() == 2.0
    pl = controller.get_enrollment_data(e2["id"])["pruefungsleistungen"][0]
    controller.change_pl(e2["id"], {"id": pl["id"], "datum": "2024-02-01", "note": 1.0})
    assert controller.get_erarbeitete_ects() == 10
    assert controller.get_notendurchschnitt() == 1.5


def test_logout_and_delete_student(controller, db):
    s = db.add_student(
        "U",
        "1",
        "z@gmail.com",
        "pw",
        8,
        36,
        datetime.date(2024, 1, 1),
        datetime.date(2024, 12, 31),
        2.0,
    )
    controller.student = s
    controller.logout()
    assert controller.student is None
    # neu setzen und löschen
    # controller.student = s
    # controller.delete_student()
    # assert db.lade_student("z@gmail.com") is None


def test_delete_student(controller, db):
    t = db.add_student(
        "X",
        "2",
        "x@gmail.com",
        "pw",
        8,
        36,
        datetime.date(2024, 1, 1),
        datetime.date(2024, 12, 31),
        2.0,
    )
    controller.student = t
    controller.delete_student()
    assert db.lade_student("x@gmail.com") is None
