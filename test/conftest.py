import os
from pathlib import Path

import pytest

@pytest.fixture(scope="session")
def root_dir():
    return Path(__file__).parents[1]

