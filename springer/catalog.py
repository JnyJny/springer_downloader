"""the Springer Free Textbook Catalog
"""


import pandas
import typer
import requests

from itertools import product
from loguru import logger
from time import sleep
from pathlib import Path

from .constants import FileFormat, Language, Topic, Token

from . import _urls


_ttable = str.maketrans(
    {
        "/": "_",
        "\\": "_",
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
        "`": "",
        "~": "",
    }
)


class Catalog:
    """A wrapper around an Excel file provided by Springer, listing information
    about the textbooks offered free of charge.
    """

    @classmethod
    def all_catalogs(cls):
        """Generator classmethod that returns a configured Catalog
        for all valid combinations of Language and Topic.
        """
        for language, topic in product(Language, Topic):
            try:
                yield cls(language, topic)
            except KeyError:
                pass

    def __init__(self, language: Language = None, topic: Topic = None):
        """
        :param url: str
        """
        self.language = language or Language.English
        self.topic = topic or Topic.AllDisciplines

        if not self.cache_file.exists():
            self.fetch_catalog()

    def __repr__(self):

        return (
            f"{self.__class__.__name__}(language={self.language}, topic={self.topic})"
        )

    def __str__(self):
        desc = self.topic.name.replace("_", " ")
        s = []
        s.append(f"{Token.Catalog.value}         URL: {self.url}")
        s.append(
            f"{Token.Catalog.value}    Language: {self.language}/{self.language.name}"
        )
        s.append(f"{Token.Catalog} Topic: {self.topic}/{desc!r}")
        s.append(f"{Token.Catalog}  Cache File: {self.cache_file}")
        s.append(f"{Token.Catalog}       Books: {self.dataframe.count().max()}")
        s.append(f"{Token.Catalog}    Packages: {len(self.packages)}")

        return "\n".join(s)

    def __iter__(self):
        return self.books()

    @property
    def name(self):
        try:
            return self._name
        except AttributeError:
            pass
        self._name = f"{self.topic}-{self.language}"
        return self._name

    @property
    def url(self) -> str:
        try:
            return self._url
        except AttributeError:
            pass

        self._url = _urls["catalogs"][self.language][self.topic]

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

        self._cache_file = self.app_dir / f"catalog-{self.language}-{self.topic}.csv"

        return self._cache_file

    @property
    def dataframe(self) -> pandas.DataFrame:
        """A pandas.DataFrame populated with the contents of the Springer free textbook catalog.

        Column names are lower-cased and embedded spaces replaced with underscores.
        Columns added: uid, package_name
        Columns removed: english_package_name, german_package_name, "Unnamed: 0"

        The dataframe is sorted by book_title in ascending order.
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

        try:
            df.drop(columns="Unnamed: 0", inplace=True)
        except KeyError:
            pass

        # normalize column names to make them easier to use. in this case,
        # it means replacing embedded spaces with underscores and lower
        # casing the resultant string. The column names should then be
        # valid python identifiers which makes the dataframe easier to use.

        df.columns = [c.lower().replace(" ", "_") for c in df.columns]

        # German language catalogs have 'German Package Name' and 'English
        # Package Name' columns where the English column is empty. To make
        # things easier later on, I remove the english_package_name column
        # (normalized form) from the German catalogs and rename all the
        # remaining "<language>_package_name" columns to "package_name".

        if "german_package_name" in df.columns:
            df["package_name"] = df["german_package_name"]
        else:
            df["package_name"] = df["english_package_name"]

        # For each book in the catalog, construct a filename stem whis is:
        # - descriptive of the book.
        # - unique
        # - a valid file name for most modern filesystems.
        #
        # Settled on {book_title}-{springer_section}-{eisbn} and then
        # applying a translationg table, `_ttable` to the resulting string
        # to clean up punctuation and embedded spaces, periods and slashes.

        df["path"] = (
            df["book_title"]
            .str.cat(df["uid"], sep="-")
            .apply(lambda v: v.translate(_ttable))
        )

        self._dataframe = df

        return self._dataframe

    @property
    def packages(self) -> dict:
        """Dictionary of pandas.DataFrames whose keys are eBook package names.
        """
        try:
            return self._packages
        except AttributeError:
            pass

        pkg_dfs = [pkg for _, pkg in self.dataframe.groupby("package_name")]

        pkg_names = [x.package_name.unique()[0] for x in pkg_dfs]

        self._packages = dict(zip(pkg_names, pkg_dfs))

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
            self.textbooks(dataframe),
            length=len(dataframe),
            label=f"{self.name}:{file_format}",
            show_percent=False,
            show_pos=True,
            width=10,
            empty_char=Token.Empty,
            fill_char=Token.Book,
            item_show_func=show_title,
        ) as workitems:
            for textbook in workitems:
                self.download_book(textbook, dest, file_format, overwrite=overwrite)
        return

    def textbooks(self, dataframe: pandas.DataFrame = None) -> tuple:
        """This generator function returns a namedtuple for each row in `dataframe`.

        If `dataframe` is got supplied, `self.dataframe` is used. 

        :param dataframe: pandas.DataFrame
        :return: namedtuple called 'TextBook'
        """

        if dataframe is None:
            dataframe is self.dataframe

        for textbook in dataframe.itertuples(index=None, name="Textbook"):
            yield textbook

    def download(self, dest: Path, file_format: FileFormat, overwrite: bool) -> int:
        """Download all the textbooks in this catalog to `dest` with format `file_format`.

        :param dest: pathlib.path
        :param file_format: springer.constants.FileFormat
        :param overwrite: bool
        :return: int <bytes written>
        """
        return self.download_dataframe(dest, file_format, overwrite)

    def list_dataframe(self, dataframe: pandas.DataFrame, long_format: bool) -> None:
        """Displays one line per book described in the source `dataframe`. 

        :param dataframe: pandas.DataFrame
        :param long_format: bool
        """

        if long_format:
            print(f"{Token.Book}|NDX|PkgID|Electronic ISBN  |Title|Author")

        for index, textbook in enumerate(self.textbooks(dataframe), start=1):
            if long_format:
                fields = [
                    Token.Book,
                    f"{index:3d}",
                    f"{textbook.ebook_package}",
                    f"{textbook.electronic_isbn:17}",
                    f"{textbook.book_title}",
                    f"{textbook.author}",
                ]
                print("|".join(fields))
            else:
                print(f"{Token.Book}|{textbook.book_title}")

    def list_textbooks(self, long_format: bool) -> None:
        """Displays all books in a catalog, one line per book.
        """

        self.list_dataframe(self.dataframe, long_format)

    def list_package(
        self, name: str, package: pandas.DataFrame, long_format: bool,
    ):
        """
        """

        pid = package.ebook_package.unique()[0]
        cnt = len(package)

        if long_format:
            print(f"{Token.Package}|#Bk|PkgID|Name")

        print(f"{Token.Package}|{cnt:3d}|{pid}|{name}")
        if long_format:
            self.list_dataframe(package, True)

    def list_packages(self, long_format: bool) -> None:
        """
        """

        if not long_format:
            print(f"{Token.Package}|#Bk|PkgID|Name")

        for name, package in self.packages.items():
            self.list_package(name, package, long_format)
