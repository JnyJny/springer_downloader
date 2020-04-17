"""
"""

import pytest

from springer.constants import FileFormat
from springer.constants import Language
from springer.constants import Category

from enum import Enum


@pytest.mark.parametrize("constant_class", [FileFormat, Language, Category])
def test_constant_class_issubclass_enum(constant_class):
    assert issubclass(constant_class, Enum)


def test_file_format_constants():

    assert FileFormat.pdf.name == "pdf"
    assert FileFormat.pdf.value == "pdf"
    assert FileFormat.epub.name == "epub"
    assert FileFormat.epub.value == "epub"


def test_language_constants():

    assert Language.English.name == "English"
    assert Language.English.value == "en"
    assert Language.German.name == "German"
    assert Language.German.value == "de"


def test_category_constants():

    assert Category.AllDisciplines.name == "AllDisciplines"
    assert Category.AllDisciplines.value == "all"
    assert Category.EmergencyNursing.name == "EmergencyNursing"
    assert Category.EmergencyNursing.value == "med"
