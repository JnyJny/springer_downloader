"""
"""

import pandas as pd
import requests
import typer

from dataclasses import dataclass
from time import sleep
from pathlib import Path

from .file_format import FileFormat

_SPRINGER_CONTENT_URL = "https://link.springer.com/content"
_SPRINGER_CATALOG_URL = "https://resource-cms.springernature.com/springer-cms/rest/v1/content/17858272/data/v4"


@dataclass
class Textbook:
    title: str
    section: str
    book_id: str
    isbn: str
    suffix: str

    @property
    def ttable(self) -> dict:
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
        try:
            return self._path
        except AttributeError:
            pass

        name = f"{self.title}-EISBN-{self.isbn}"

        self._path = Path(name.translate(self.ttable)).with_suffix(f".{self.suffix}")

        return self._path

    @property
    def uid(self):
        try:
            return self._uid
        except AttributeError:
            pass
        self._uid = f"{self.section}/{self.book_id}"
        return self._uid

    def save(
        self, dest: Path, overwrite: bool = False, content_url: str = None
    ) -> None:
        """
        """

        content_url = content_url or _SPRINGER_CONTENT_URL

        path = dest / self.path

        if not overwrite and path.exists() and path.is_file():
            return True

        url = f"{content_url}/{self.suffix}/{self.uid}.{self.suffix}"

        result = requests.get(url, stream=True)

        if not result:
            return

        with path.open("wb") as fp:
            for chunk in result.iter_content(chunk_size=8192):
                fp.write(chunk)


class Catalog:

    _URL = _SPRINGER_CATALOG_URL

    def __init__(
        self, url: str = None, application_name: str = "springer", refresh: bool = False
    ):
        """
        :param url: str
        :param application_name: str
        :param refresh: bool
        """
        self.url = url or self._URL
        self.app_name = application_name
        self.refresh = refresh

    @property
    def app_dir(self) -> Path:
        """The pathlib.Path specifying the application specific directory.
        """
        try:
            return self._app_dir
        except AttributeError:
            pass

        self._app_dir = Path(typer.get_app_dir(self.app_name))
        self._app_dir.mkdir(mode=0o755, exist_ok=True)

        return self._app_dir

    @property
    def cache_file(self) -> Path:
        """pathlib.Path identifying where the cached catalog is
        located in the filesystem. If the cached catalog file
        does not exist or catalog.refresh is True, the catalog
        Excel file will be read into a pandas.DataFrame and
        writen to the cache file path in CSV format. 
        """
        if not self.refresh:
            try:
                return self._cache_file
            except AttributeError:
                pass

        self._cache_file = self.app_dir / "catalog.csv"

        if not self._cache_file.exists() or self.refresh:
            self.fetch_catalog()
            self.refresh = False

        return self._cache_file

    def fetch_catalog(self) -> None:
        """Reads the Excel file at `self.url` and writes it to the
        `cache_file` in CSV format.
        """

        df = pd.read_excel(self.url).dropna(axis=1)
        df["Section"] = df["DOI URL"].apply(lambda v: v.split("/")[-2])
        df["Book ID"] = df["DOI URL"].apply(lambda v: v.split("/")[-1])
        df.to_csv(self._cache_file)

    @property
    def dataframe(self):
        """A pandas.DataFrame populated with the contents of the
        Springer catalog.
        """
        try:
            return self._dataframe
        except AttributeError:
            pass

        self._dataframe = pd.read_csv(self.cache_file).dropna(axis=1)

        return self._dataframe

    def textbooks(self, file_format: FileFormat) -> Textbook:
        """A generator function that returns a springer.catalog.Textbook
        for each entry in the catalog configured for the specified
        `file_format`.

        :param file_format: springer.file_format.FileFormat
        :return: list
        """
        columns = ["Book Title", "Section", "Book ID", "Electronic ISBN"]
        for values in self.dataframe[columns].values:
            yield Textbook(*values, file_format)

    def download(
        self,
        dest: Path,
        file_format: FileFormat,
        overwrite: bool,
        dryrun: bool,
        filter: dict = None,
    ) -> None:
        """Downloads all the books found in the Springer textbook catalog.

        :param dest: Path
        :param file_format: springer.file_format.FileFormat
        :param overwrite: bool
        :param dryrun: bool:
        :param filter: dict <NotImplemented>
        :return: None
        """

        dest = dest.resolve()

        if dryrun:
            print("Destination: {dest}")
            for textbook in self.textbooks(file_format):
                print(f"Title: {textbook.title}")
                print(f" Path> {dest / textbook.path}")
            return

        dest.mkdir(mode=0o755, exist_ok=True)

        def item_title(value):
            if not value:
                return f"Downloaded to {dest}"
            return value.title[:40]

        with typer.progressbar(
            self.textbooks(file_format),
            item_show_func=item_title,
            length=self.dataframe.count().max(),
            fill_char="📕",
            label=f"{file_format.upper():4s}",
            show_pos=True,
            show_percent=False,
            show_eta=True,
            width=10,
        ) as workitems:
            for textbook in workitems:
                textbook.save(dest, overwrite=overwrite)
