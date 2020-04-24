"""
"""

import pytest

from springer.constants import FileFormat
from springer.constants import Language
from springer.constants import Topic
from springer.constants import Component

from enum import Enum


@pytest.mark.parametrize("constant_class", [FileFormat, Language, Topic, Component])
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


def test_topic_constants():

    assert Topic.All_Disciplines.name == "All_Disciplines"
    assert Topic.All_Disciplines.value == "all"
    assert Topic.Emergency_Nursing.name == "Emergency_Nursing"
    assert Topic.Emergency_Nursing.value == "med"


def test_component_constants():

    assert Component.Books == "books"
    assert Component.Packages == "packages"
    assert Component.Package == "package"
    assert Component.Catalog == "catalog"
    assert Component.Catalogs == "catalogs"
