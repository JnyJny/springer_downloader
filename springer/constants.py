"""
"""

from enum import Enum


class FileFormat(str, Enum):
    """Supported file formats"""

    pdf = "pdf"
    epub = "epub"


class Language(str, Enum):
    """Supported languages"""

    English: str = "en"
    German: str = "de"


class Category(str, Enum):
    """Catalog categories"""

    AllDisciplines: str = "all"
    EmergencyNursing: str = "med"
