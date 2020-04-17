"""
"""

import pytest

from pathlib import Path

from springer.textbook import Textbook
from springer.constants import FileFormat

textbook_init_properties = [
    "title",
    "author",
    "edition",
    "copyright_year",
    "copyright_holder",
    "isbn",
    "eisbn",
    "doi_url",
    "openurl",
    "subject_classification",
    "publisher",
    "imprint",
    "section",
    "book_id",
]


@pytest.fixture(scope="module")
def TEXTBOOK():
    return Textbook(*textbook_init_properties, FileFormat.pdf)


def test_creating_textbook_no_args():

    with pytest.raises(TypeError):
        textbook = Textbook()


@pytest.mark.parametrize("file_format", list(FileFormat))
def test_create_textbook_with_args(file_format):

    textbook = Textbook(*textbook_init_properties, file_format)
    assert textbook
    assert isinstance(textbook, Textbook)
    assert textbook.suffix == file_format


all_textbook_properties = [
    ("suffix", str),
    ("ttable", dict),
    ("path", Path),
    ("uid", str),
    ("content_url", str),
]

all_textbook_properties.extend(tuple(zip(textbook_init_properties, [str] * 15)))


@pytest.mark.parametrize(
    "prop_name,prop_type", all_textbook_properties,
)
def test_textbook_property_existence_and_type(prop_name, prop_type, TEXTBOOK):

    value = getattr(TEXTBOOK, prop_name)
    assert isinstance(value, prop_type)


@pytest.mark.parametrize("method_name", ["__repr__", "__str__", "save"])
def test_TEXTBOOK_method_existence(method_name, TEXTBOOK):

    assert getattr(TEXTBOOK, method_name)
