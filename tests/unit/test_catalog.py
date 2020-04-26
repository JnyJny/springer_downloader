"""
"""

import pytest

from pathlib import Path
from pandas import DataFrame

from springer.catalog import Catalog
from springer.constants import Language, Topic


@pytest.fixture(scope="module")
def CATALOG():
    return Catalog()


def test_creating_catalog_no_args():

    catalog = Catalog()
    assert catalog
    assert isinstance(catalog, Catalog)


@pytest.mark.parametrize(
    "lang,cat",
    [
        (Language.English, Topic.All_Disciplines),
        (Language.German, Topic.All_Disciplines),
        (Language.German, Topic.Emergency_Nursing),
    ],
)
def test_creating_catalog_with_args_xpass(lang, cat):

    catalog = Catalog(lang, cat)
    assert catalog
    assert isinstance(catalog, Catalog)
    assert catalog.language == lang
    assert catalog.topic == cat


@pytest.mark.parametrize(
    "lang,cat", [(Language.English, Topic.Emergency_Nursing),],
)
def test_creating_catalog_with_args_xfail(lang, cat):

    with pytest.raises(KeyError):
        catalog = Catalog(lang, cat)


@pytest.mark.parametrize(
    "prop_name,prop_type",
    [
        ("name", str),
        ("is_default", bool),
        ("language", Language),
        ("topic", Topic),
        ("url", str),
        ("config_dir", Path),
        ("defaults_file", Path),
        ("defaults", dict),
        ("cache_file", Path),
        ("ttable", dict),
        ("dataframe", DataFrame),
        ("packages", dict),
    ],
)
def test_catalog_property_existence_and_type(prop_name, prop_type, CATALOG):

    value = getattr(CATALOG, prop_name)
    assert isinstance(value, prop_type)


@pytest.mark.parametrize(
    "method_name",
    [
        "__repr__",
        "__str__",
        "__iter__",
        "__eq__",
        "all_catalogs",
        "content_url",
        "save_defaults",
        "fetch_catalog",
        "textbooks",
        "download_textbook",
        "download_dataframe",
        "download_dataframe_animated",
        "download_title",
        "download_package",
        "download",
        "list_dataframe",
        "list_textbooks",
        "list_package",
        "list_packages",
        "list_catalog",
    ],
)
def test_catalog_method_existence(method_name, CATALOG):

    method = getattr(CATALOG, method_name)
    assert callable(method)


def test_catalog_classmethod_all_catalogs():

    for catalog in Catalog.all_catalogs():
        assert isinstance(catalog, Catalog)
