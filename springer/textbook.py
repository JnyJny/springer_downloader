""" A Textbook representation of a Textbook

"""

import requests


from dataclasses import dataclass
from loguru import logger
from pathlib import Path

from .constants import FileFormat

from . import _urls


@dataclass
class Textbook:
    """The layout of Textbook is dependent on the layout of the
    catalog Excel file. Changes there must be reflected here.
    """

    title: str
    author: str
    edition: str
    copyright_year: str
    copyright_holder: str
    isbn: str
    eisbn: str
    doi_url: str
    openurl: str
    subject_classification: str
    publisher: str
    imprint: str
    section: str
    book_id: str
    suffix: str

    _dataframe_columns = [
        "Book Title",
        "Author",
        "Edition",
        "Copyright Year",
        "Copyright Holder",
        "Print ISBN",
        "Electronic ISBN",
        "DOI URL",
        "OpenURL",
        "Subject Classification",
        "Publisher",
        "Imprint",
        "Section",
        "Book ID",
    ]

    @property
    def ttable(self) -> dict:
        """A translation table used to normalize local filenames.
        """
        try:
            return self._ttable
        except AttributeError:
            pass
        self._ttable = str.maketrans(
            {
                "/": "_",
                " ": "_",
                ":": "",
                ".": "",
                ",": "",
                '"': "",
                "'": "",
                "(": "",
                ")": "",
                "{": "",
                "}": "",
                "*": "",
                "?": "",
                "®": "",
            }
        )
        return self._ttable

    @property
    def path(self) -> Path:
        """A pathlib.Path local filesystem name for this Textbook.
        """
        try:
            return self._path
        except AttributeError:
            pass

        name = f"{self.title}-EISBN-{self.eisbn}"

        self._path = Path(name.translate(self.ttable)).with_suffix("." + self.suffix)

        return self._path

    @property
    def uid(self):
        """A concatenation of the section and book_id properties.

        The uid is used in conjunction with the content_url and suffix
        properties to construct a URL to download this textbook.
        """
        try:
            return self._uid
        except AttributeError:
            pass
        self._uid = f"{self.section}/{self.book_id}"
        return self._uid

    @property
    def content_url(self) -> str:
        """Base URL to download content with the format indicated by suffix.
        """
        try:
            return _urls["content"][self.suffix]
        except KeyError:
            raise ValueError("Unknown Textbook Suffix:", self.suffix) from None

    def save(self, dest: Path, overwrite: bool = False) -> None:
        """Downloads this Textbook using requests and saves it locally.

        The Textbook is downloaded via HTTP GET requestion into a
        directory specified by the user. If `overwrite` is False,
        existing files in the destination directory files will not be
        over written.

        :param dest: pathlib.Path
        :param overwrite: bool
        :return: None
        """

        path = dest / self.path

        if not overwrite and path.exists() and path.is_file():
            return True

        url = f"{self.content_url}/{self.uid}.{self.suffix}"
        result = requests.get(url, stream=True)

        if not result:
            logger.debug(f"{result.status_code} {url}")
            return

        with path.open("wb") as fp:
            for chunk in result.iter_content(chunk_size=8192):
                fp.write(chunk)
