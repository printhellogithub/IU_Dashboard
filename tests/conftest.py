# tests/conftest.py
"""Pytest-Konfiguration und gemeinsame Fixtures für das Testpaket.

Dieses Modul definiert Test-Fixtures für eine isolierte Datenbankumgebung
(SQLite In-Memory) sowie eine Controller-Instanz, die diese Testdatenbank nutzt.

Hinweis:
    Durch die In-Memory-Datenbank ist jeder Testlauf vollständig isoliert und
    hat keine Auswirkungen auf die Produktivdatenbank.
"""

import sys
from pathlib import Path
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models import Base
from src.database import DatabaseManager
from src.main import Controller

# Projekt-Root auf sys.path legen (eine Ebene über tests/)
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


class TestDatabaseManager(DatabaseManager):
    """Testvariante des DatabaseManager mit SQLite In-Memory-Datenbank.

    Diese Klasse überschreibt die Initialisierung des produktiven
    ``DatabaseManager``, um eine flüchtige Datenbank (`` :memory: ``) zu verwenden.

    Die Session wird pro Instanz erstellt und über ``recreate_session`` bei Bedarf
    neu erzeugt.
    """

    def __init__(self):
        """Initialisiert eine SQLite In-Memory-Engine und erstellt das Schema.

        Erstellt anschließend eine SQLAlchemy-Session (``self.session``) für Tests.
        """
        self.engine = create_engine("sqlite+pysqlite:///:memory:", echo=False)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine, expire_on_commit=False)
        self.session = self.SessionLocal()

    def recreate_session(self):
        """Schließt die aktuelle Session und erstellt eine neue."""
        try:
            self.session.close()
        except Exception:
            pass
        self.session = self.SessionLocal()


@pytest.fixture(scope="function")
def db():
    """Stellt pro Testfunktion einen frischen Test-DatabaseManager bereit.

    Das Fixture erzeugt eine neue In-Memory-Datenbank und schließt die Session
    nach dem Test, um Ressourcen sauber freizugeben.

    Yields:
        TestDatabaseManager: Datenbankmanager mit aktiver Session.
    """
    manager = TestDatabaseManager()
    yield manager
    try:
        manager.session.close()
    except Exception:
        pass


@pytest.fixture
def controller(db):
    """Erzeugt eine Controller-Instanz, die die Testdatenbank verwendet.

    Args:
        db: ``db``-Fixture (TestDatabaseManager) als Datenbank-Backend.

    Returns:
        Controller: Controller mit ``seed=False``.
    """
    c = Controller(db=db, seed=False)
    return c
