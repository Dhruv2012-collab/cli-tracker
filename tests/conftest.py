import pytest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from src.database.core import Base
from unittest.mock import patch

import os

# We use an in-memory SQLite database for fast, isolated tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="session", autouse=True)
def override_db_url():
    os.environ["DATABASE_URL"] = SQLALCHEMY_DATABASE_URL

@pytest.fixture(scope="function")
def engine():
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, 
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    Base.metadata.create_all(bind=engine)
    
    # Override app's engine globally
    import src.config.database
    src.config.database.engine = engine
    src.config.database.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session(engine):
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()

@pytest.fixture(autouse=True)
def mock_config_file(tmp_path):
    """Automatically mock the CONFIG_FILE for all tests so it doesn't touch host system."""
    test_config = tmp_path / f"tracker_config_{os.urandom(4).hex()}.json"
    with patch("src.cli.utils.CONFIG_FILE", test_config):
        yield test_config
