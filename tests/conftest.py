# tests/conftest.py
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
    def __init__(self):
        self.engine = create_engine("sqlite+pysqlite:///:memory:", echo=False)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine, expire_on_commit=False)
        self.session = self.SessionLocal()

    def recreate_session(self):
        try:
            self.session.close()
        except Exception:
            pass
        self.session = self.SessionLocal()


@pytest.fixture(scope="function")
def db():
    manager = TestDatabaseManager()
    yield manager
    try:
        manager.session.close()
    except Exception:
        pass


@pytest.fixture
def controller(db):
    c = Controller(db=db, seed=False)
    return c
