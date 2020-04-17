"""
"""

import pytest

from typer.testing import CliRunner


@pytest.fixture(scope="module")
def CliRunner() -> CliRunner:
    return CliRunner()
