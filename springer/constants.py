"""
"""

from enum import Enum


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


class Description(str, Enum):
    """Catalog descriptions."""

    All_Disciplines: str = "all"
    Emergency_Nursing: str = "med"


class Heirarchy(str, Enum):
    """Catalog entity heirarchy."""

    Catalogs = "catalogs"
    Catalog = "catalog"
    Packages = "packages"
    Package = "package"
    Books = "books"
