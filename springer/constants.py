"""
"""

from enum import Enum


class Token(str, Enum):
    """Unicode Tokens"""

    Stop = "\N{OCTAGONAL SIGN}"
    Package = "\N{PACKAGE}"
    Catalog = "\N{BOOKS}"
    Book = "\N{GREEN BOOK}"
    Empty = "\N{CLOSED BOOK}"

    def __str__(self):
        return self.value


class FileFormat(str, Enum):
    """Supported file formats."""

    pdf = "pdf"
    epub = "epub"

    @property
    def suffix(self):
        return f".{self.value}"


class Language(str, Enum):
    """Supported languages."""

    English: str = "en"
    German: str = "de"


class Topic(str, Enum):
    """Catalog topics."""

    All_Disciplines: str = "all"
    Emergency_Nursing: str = "med"


class Component(str, Enum):
    """Catalog components."""

    Catalogs = "catalogs"
    Catalog = "catalog"
    Packages = "packages"
    Package = "package"
    Books = "books"
