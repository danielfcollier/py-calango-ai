from pathlib import Path

import pytest


@pytest.fixture
def temp_db_path(tmp_path):
    """Creates a temporary directory for the database."""
    d = tmp_path / ".calango"
    d.mkdir()
    return d


@pytest.fixture
def mock_db_paths(monkeypatch, temp_db_path):
    """
    Forces the Database Managers to use the temporary path
    instead of the real user home directory.
    """

    def mock_home():
        return temp_db_path.parent

    monkeypatch.setattr(Path, "home", mock_home)
    return temp_db_path
