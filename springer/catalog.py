"""the Springer Free Textbook Catalog
"""


import pandas
import typer
import requests

from itertools import product
from loguru import logger
from time import sleep
from pathlib import Path

from .constants import FileFormat, Language, Description

from . import _urls


_ttable = str.maketrans(
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


class Catalog:
    """A wrapper around an Excel file provided by Springer, listing information
    about the textbooks offered free of charge.
    """

    @classmethod
    def all_catalogs(cls):
        """Generator classmethod that returns a configured Catalog
        for all valid combinations of Language and Description.
        """
        for language, description in product(Language, Description):
            try:
                yield cls(language, description)
            except KeyError:
                pass

    def __init__(
        self,
        language: Language = None,
        description: Description = None,
        refresh: bool = False,
    ):
        """
        :param url: str
        :param refresh: bool
        """
        self.language = language or Language.English
        self.description = description or Description.AllDisciplines

        if not self.cache_file.exists() or refresh:
            self.fetch_catalog()

    def __repr__(self):

        return f"{self.__class__.__name__}(language={self.language}, description={self.description})"

    def __str__(self):
        desc = self.description.name.replace("_", " ")
        s = []
        s.append(f"\N{BOOKS}         URL: {self.url}")
        s.append(f"\N{BOOKS}    Language: {self.language}/{self.language.name}")
        s.append(f"\N{BOOKS} Description: {self.description}/{desc!r}")
        s.append(f"\N{BOOKS}  Cache File: {self.cache_file}")
        s.append(f"\N{BOOKS}       Books: {self.dataframe.count().max()}")
        s.append(f"\N{BOOKS}    Packages: {len(self.packages)}")

        return "\n".join(s)

    def __iter__(self):
        return self.books()

    @property
    def name(self):
        try:
            return self._name
        except AttributeError:
            pass
        self._name = f"{self.description}-{self.language}"
        return self._name

    @property
    def url(self) -> str:
        try:
            return self._url
        except AttributeError:
            pass

        self._url = _urls["catalogs"][self.language][self.description]

        return self._url

    def content_url(self, file_format: FileFormat) -> str:
        """The URL prefix for downloading content.
        
        :param file_format: springer.constants.FileFormat
        :return: str
        """
        return _urls["content"][file_format]

    @property
    def app_dir(self) -> Path:
        """The pathlib.Path specifying the application specific directory.
        """
        try:
            return self._app_dir
        except AttributeError:
            pass

        self._app_dir = Path(typer.get_app_dir(__package__))
        self._app_dir.mkdir(mode=0o755, exist_ok=True)

        return self._app_dir

    @property
    def cache_file(self) -> Path:
        """pathlib.Path for the locally cached catalog.
        """
        try:
            return self._cache_file
        except AttributeError:
            pass

        self._cache_file = (
            self.app_dir / f"catalog-{self.language}-{self.description}.csv"
        )

        return self._cache_file

    @property
    def dataframe(self) -> pandas.DataFrame:
        """A pandas.DataFrame populated with the contents of the Springer free textbook catalog.
        """
        try:
            return self._dataframe
        except AttributeError:
            pass

        if not self.cache_file.exists():
            self.fetch_catalog()

        df = pandas.read_csv(self.cache_file).dropna(axis=1)

        df["UID"] = df["DOI URL"].apply(lambda v: "/".join(v.split("/")[-2:]))

        df.sort_values(by="Book Title", ascending=True, inplace=True)

        df.drop(columns="Unnamed: 0", inplace=True)

        # normalize column names to make them easier to use
        df.columns = [c.lower().replace(" ", "_") for c in df.columns]

        if "german_package_name" in df.columns:
            df["package_name"] = df["german_package_name"]
        else:
            df["package_name"] = df["english_package_name"]

        df["path"] = (
            df["book_title"]
            .str.cat(df["uid"], sep="-")
            .apply(lambda v: v.translate(_ttable))
        )

        self._dataframe = df

        return self._dataframe

    @property
    def package_names(self) -> list:
        try:
            return self._packages
        except AttributeError:
            pass

        self._packages = self.dataframe.package_name.unique().tolist()
        return self._packages

    @property
    def packages(self) -> dict:
        """Dictionary of pandas.DataFrames whose keys are package names.
        """
        try:
            return self._packages
        except AttributeError:
            pass

        df = self.dataframe.sort_values(by=["package_name", "book_title"])

        dfs = [pkg for _, pkg in df.groupby("package_name")]

        names = [x.package_name.unique()[0] for x in dfs]

        self._packages = dict(zip(names, dfs))

        return self._packages

    def fetch_catalog(self, url: str = None) -> None:
        """Reads the Excel file at `url` and writes it to the local filesystem.

        The Excel file is written to `cache_file` in CSV format. If
        `url` is not given, `self.url` is used.

        :param url: str
        :return: None
        """
        pandas.read_excel(url or self.url).dropna(axis=1).to_csv(self.cache_file)

    def download_book(
        self, textbook: tuple, dest: Path, file_format: FileFormat, overwrite: bool,
    ) -> int:
        """Download the book `textbook` to `dest` with format `file_format`.

        :param textbook: namedtuple
        :param dest: Path
        :param file_format: springer.constants.FileFormat
        :param overwrite: bool
        :return: int <bytes written>
        """

        dest.mkdir(mode=0o755, exist_ok=True, parents=True)

        path = (dest / textbook.path).with_suffix(file_format.suffix)

        if not overwrite and path.exists():
            logger.debug(f"Skipped {path}")
            return 0

        url = f"{self.content_url(file_format)}/{textbook.uid}.{file_format}"

        response = requests.get(url, stream=True)

        if not response:
            logger.debug(f"{response} {url}")
            return 0

        size = 0
        with path.open("wb") as fp:
            for chunk in response.iter_content(chunk_size=8192):
                size += len(chunk)
                fp.write(chunk)
        return size

    def download_package(
        self, package: str, dest: Path, file_format: FileFormat, overwrite: bool
    ) -> int:
        """Download all the textbooks that belong to `package` to `dest` with format `file_format`.

        :param package: str
        :param dest: pathlib.path
        :param file_format: springer.constants.FileFormat
        :param overwrite: bool
        :return: int <bytes written>
        """

        df = self.dataframe[
            self.dataframe.package_name.str.contains(package, case=False)
        ]

        return self.download_dataframe(dest, file_format, overwrite, df)

    def download_dataframe(
        self,
        dest: Path,
        file_format: FileFormat,
        overwrite: bool,
        dataframe: pandas.DataFrame = None,
    ) -> int:
        """Downloads all the textbooks in `dataframe` to `dest` with format `file_format`.

        :param dest: pathlib.path
        :param file_format: springer.constants.FileFormat
        :param overwrite: bool
        :param dataframe: pandas.DataFrame
        :return: int <bytes written>
        """
        if dataframe is None:
            dataframe = self.dataframe

        def show_title(item):
            if not item:
                return f"Downloaded to {dest}"
            return item.book_title[:40]

        with typer.progressbar(
            dataframe.itertuples(index=False, name="Textbook"),
            length=len(dataframe),
            label=f"{self.name}:{file_format}",
            show_percent=False,
            show_pos=True,
            width=10,
            empty_char="\N{CLOSED BOOK}",
            fill_char="\N{GREEN BOOK}",
            item_show_func=show_title,
        ) as workitems:
            for textbook in workitems:
                self.download_book(textbook, dest, file_format, overwrite=overwrite)
        return

    def books(self):
        """
        """

        for book in self.dataframe.itertuples(index=None, name="Book"):
            yield book

    def download(self, dest: Path, file_format: FileFormat, overwrite: bool) -> int:
        """Download all the textbooks in this catalog to `dest` with format `file_format`.

        :param dest: pathlib.path
        :param file_format: springer.constants.FileFormat
        :param overwrite: bool
        :return: int <bytes written>
        """
        return self.download_dataframe(dest, file_format, overwrite)

    def list_dataframe(self, dataframe: pandas.DataFrame, long_format: bool) -> None:
        """
        """

        for index, textbook in enumerate(
            dataframe.itertuples(index=None, name="Textbook"), start=1
        ):
            if long_format:
                print(
                    f"\N{GREEN BOOK} {index:3d} {textbook.book_title!r}, {textbook.electronic_isbn!r}"
                )
            else:
                print(repr(textbook.book_title))

    def list_books(self, long_format: bool) -> None:
        """
        """

        if long_format:
            df = self.dataframe.sort_values(by=["package_name", "book_title"])
        else:
            df = self.dataframe.sort_values(by="book_title")

        self.list_dataframe(df, long_format)

    def list_package(
        self, name: str, package: pandas.DataFrame, long_format: bool,
    ):
        """
        """
        print(f"\N{PACKAGE} #books={len(package):02d} {name!r}  ")
        if long_format:
            self.list_dataframe(package, True)

    def list_packages(self, long_format: bool) -> None:
        """
        """
        for name, package in self.packages.items():
            self.list_package(name, package, long_format)
