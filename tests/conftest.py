"""Fixtures compartidas para los tests."""
import os
import tempfile
from typing import AsyncIterator

import pytest_asyncio

from database.db import init_db


@pytest_asyncio.fixture
async def db_path() -> AsyncIterator[str]:
    """Crea una BD SQLite temporal con el schema aplicado, para cada test."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    await init_db(path)
    yield path
    os.remove(path)
