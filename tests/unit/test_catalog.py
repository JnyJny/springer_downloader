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
        ("language", Language),
        ("topic", Topic),
        ("url", str),
        ("config_dir", Path),
        ("cache_file", Path),
        ("dataframe", DataFrame),
    ],
)
def test_catalog_property_existence_and_type(prop_name, prop_type, CATALOG):

    value = getattr(CATALOG, prop_name)
    assert isinstance(value, prop_type)


@pytest.mark.parametrize(
    "method_name", ["__repr__", "__str__", "fetch_catalog", "textbooks", "download"]
)
def test_catalog_method_existence(method_name, CATALOG):

    assert getattr(CATALOG, method_name)
