"""the Springer Free Textbook Catalog
"""

import pandas
import toml
import typer
import requests
import string
import sys

from itertools import product
from loguru import logger
from time import sleep
from pathlib import Path

from .constants import FileFormat, Language, Topic, Token
from .urls import urls as DEFAULT_URLS


class Catalog:
    """Manage Springer's Excel-formated catalogs of textbooks

    This class simplifies using the Excel catalogs of textbooks Springer
    has made available free of charge. The class can manage the
    various catalogs, list the contents of the catalogs and finally
    use the catalogs to download textbooks to the local filesystem

    Using it is pretty simple:

    > from springer.catalog import Catalog
    > catalog = Catalog()
    > # will download and cache the initial default catalog 'en-all'
    

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

    def __init__(
        self, language: Language = None, topic: Topic = None, fetch: bool = True
    ):
        """
        :param language: springer.constants.Language
        :param topic: springer.constants.Topic
        :param fetch: bool
        """

        self.language = language or Language(self.defaults.get("language", "en"))
        self.topic = topic or Topic(self.defaults.get("topic", "all"))

        if not self.cache_file.exists() and fetch:
            try:
                self.fetch_catalog()
            except Exception as error:
                raise error from None

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(language={self.language}, topic={self.topic})"
        )

    def __str__(self):
        return f"{Token.Catalog}|{self.name}"

    def __iter__(self):
        """An iterator over all textbooks in a catalog."""
        return self.textbooks()

    @property
    def name(self) -> str:
        """An identifier formed from `language`-`topic`."""
        try:
            return self._name
        except AttributeError:
            pass
        self._name = f"{self.language}-{self.topic}"
        return self._name

    @property
    def is_default(self) -> bool:
        """Returns True if this catalog has the default language and topic."""

        # Avoid fetching the Catalog, normally shouldn't be a problem
        # but can slow down this method if the catalog hasn't been cached
        # locally yet.

        return Catalog(fetch=False) == self

    def __eq__(self, other):
        """Catalogs are equivalent if they have the same name."""
        try:
            return self.name == other.name
        except AttributeError:
            pass
        return False

    @property
    def url(self) -> str:
        """The URL location of the Excel-formatted file for this catalog.

        Accessing this URL can raise KeyError for language/topic
        combinations which do not exist.
        """
        try:
            return self._url
        except AttributeError:
            pass

        self._url = DEFAULT_URLS["catalogs"][self.language][self.topic]

        return self._url

    def content_url(self, uid: str, file_format: FileFormat) -> str:
        """The content download URL for textbook `uid` with `file_format`.
        
        :param uid: str
        :param file_format: springer.constants.FileFormat
        :return: str
        """
        return DEFAULT_URLS["content"][file_format] + f"/{uid}.{file_format}"

    @property
    def config_dir(self) -> Path:
        """A pathlib.Path for the application-specific configuration directory.

        Configuration files and cached catalog CSV files are kept here.
        """
        try:
            return self._config_dir
        except AttributeError:
            pass

        self._config_dir = Path(typer.get_app_dir(__package__))
        self._config_dir.mkdir(mode=0o755, exist_ok=True)

        return self._config_dir

    @property
    def defaults_file(self) -> Path:
        """Path to the default Catalog configuration TOML file."""
        try:
            return self._defaults_file
        except AttributeError:
            pass
        self._defaults_file = self.config_dir / "catalog_defaults.toml"
        return self._defaults_file

    @property
    def defaults(self) -> dict:
        """A dictionary loaded from the file `self.defaults_file`.
        """
        try:
            contents = toml.decoder.load(self.defaults_file)
        except FileNotFoundError:
            contents = {}
        return contents

    def save_defaults(self) -> None:
        """Saves this instance's langauage and topic values to `defaults_file`.
        """
        updated = {"language": self.language.value, "topic": self.topic.value}
        try:
            contents = toml.decoder.load(self.defaults_file)
        except FileNotFoundError:
            contents = {}
        contents.update(updated)
        toml.encoder.dump(contents, self.defaults_file.open("w"))

    @property
    def cache_file(self) -> Path:
        """A pathlib.Path for the locally cached catalog in CSV format.
        """
        try:
            return self._cache_file
        except AttributeError:
            pass

        self._cache_file = self.config_dir / f"catalog-{self.name}.csv"

        return self._cache_file

    @property
    def ttable(self) -> dict:
        """Dictionary result of str.maketrans() for use with str.translate().

        This table collapses punctuation to empty strings and whitespace
        to an underscore.
        """
        try:
            return self._ttable
        except AttributeError:
            pass

        table = {p: "" for p in string.punctuation}
        table.update({w: "_" for w in string.whitespace})
        table.update({"/": "_", "\\": "_"})
        table.update({"™": "", "®": ""})

        self._ttable = str.maketrans(table)

        return self._ttable

    @property
    def dataframe(self) -> pandas.DataFrame:
        """A pandas.DataFrame populated with the contents of the Springer free textbook catalog.

        The dataframe's source data is the cached CSV-formatted file
        self.`cache_file` and we transform the cached data everytime we
        construct the dataframe rather than applying it to the cached
        file. This seemed simpler for handling cached catalog updates.

        The source data is modified to make it easier to work with:

        - Empty rows are dropped
        - Column names are casefolded and embedded spaces replaced with underscores.
        - Column names replaced:
          o english_package_name|german_package_name -> package_name
          o book_title -> title
        - Columns added: uid, filename
        - Columns removed: "Unnamed: 0" if present

        Finally, the dataframe is sorted by title and author in
        ascending order.
        """

        try:
            return self._dataframe
        except AttributeError:
            pass

        if not self.cache_file.exists():
            self.fetch_catalog()

        df = pandas.read_csv(self.cache_file).dropna(axis=1)

        try:
            df.drop(columns="Unnamed: 0", inplace=True)
        except KeyError:
            pass

        # Normalize column names to make them easier to use. In this case, it
        # means replacing embedded spaces with underscores and casefolding the
        # resultant string. The column names should then be valid python
        # identifiers which makes the dataframe easier to use.

        columns = {c: c.casefold().translate(self.ttable) for c in df.columns}

        # later on, textbook.book_title looks funny
        columns["Book Title"] = "title"

        df.rename(columns=columns, inplace=True)

        # German language catalogs have 'german_package_name' and 'english
        # package_name' columns where the English column is empty. Again, to
        # make things easier later on, I conditionally rename
        # 'german_package_name' or 'english_package_name' to 'package_name' and
        # drop any unused package name columns.

        if "german_package_name" in df.columns:
            pkg_rename = {"german_package_name": "package_name"}
            df.drop(columns="english_package_name", inplace=True)
        else:
            pkg_rename = {"english_package_name": "package_name"}

        df.rename(columns=pkg_rename, inplace=True)

        # UID = unique identifier in content download URL
        df["uid"] = df.doi_url.apply(lambda v: "/".join(v.split("/")[-2:]))

        # The filename is composed of the title and uid columns with different
        # rules for collapsing punctuation and white space.

        slash_and_dot_to_dash = str.maketrans({"/": "-", ".": "-",})

        df["filename"] = (
            df["title"]
            .apply(lambda v: v.translate(self.ttable))
            .str.cat(
                df.uid.apply(lambda v: v.translate(slash_and_dot_to_dash)), sep="-",
            )
        )

        self._dataframe = df.sort_values(by=["title", "author"], ascending=[True, True])

        return self._dataframe

    @property
    def packages(self) -> dict:
        """Dictionary of pandas.DataFrames values whose keys are eBook package names.
        
        Keys are in sorted order.

        Note: Do not mutate the package dataframes unless you copy them.
        """
        try:
            return self._packages
        except AttributeError:
            pass

        self._packages = {
            name: pkg for name, pkg in self.dataframe.groupby("package_name")
        }
        return self._packages

    def fetch_catalog(self, url: str = None) -> None:
        """Reads the Excel file at `url` and writes it to the local filesystem.

        The Excel file is written to `cache_file` in CSV format. If
        `url` is not given, `self.url` is used.

        :param url: str
        :return: None
        """
        # XXX update defaults with new url if one is given and it succeeds?
        pandas.read_excel(url or self.url).dropna(axis=1).to_csv(self.cache_file)

    def textbooks(self, dataframe: pandas.DataFrame = None) -> tuple:
        """This generator function returns a namedtuple for each row in `dataframe`.

        If `dataframe` is got supplied, `self.dataframe` is used.

        :param dataframe: pandas.DataFrame
        :return: generator returning namedtuples called 'TextBook'
        """

        if dataframe is None:
            dataframe = self.dataframe

        for textbook in dataframe.itertuples(index=None, name="Textbook"):
            yield textbook

    def download_textbook(
        self, textbook: tuple, dest: Path, file_format: FileFormat, overwrite: bool,
    ) -> int:
        """Download `textbook` to `dest` with format `file_format`.

        Textbook is a Pandas.itertuple generated namedtuple based on
        the row in a dataframe.

        If destination path does not currently exist, it will be
        created.

        If the destination path exists and overwrite is False, a skipped
        entry for that textbook will be logged to the download report and
        zero bytes written is returned.

        If the textbook fails to download, an entry is logged to the
        download report with the HTTP status code and URL of the
        attemtped textbook. Again, zero bytes written is returned to
        the caller.

        Finally, the data received via HTTP is written to the local
        filesystem. The path to save the data is constructed using
        `dest`, the textbook.filename field and `file_format`.suffix.

        If the user interrupts saving the file to the local filesystem,
        the partial file is removed and the path is logged to the
        download report. The intention is to avoid leaving a truncated
        file for the user to trip on later. Not a delighter.

        The number of bytes written to the local filesystem is returned.

        :param textbook: namedtuple
        :param dest: Path
        :param file_format: springer.constants.FileFormat
        :param overwrite: bool
        :return: int <bytes written>

        Raises:
        - ValueError for missing Textbook attributes

        """

        path = (dest / textbook.filename).with_suffix(file_format.suffix)

        if not overwrite and path.exists():
            logger.debug(f"Skipped {path}")
            return 0

        url = self.content_url(textbook.uid, file_format)

        response = requests.get(url, stream=True)

        if not response:
            logger.debug(f"{response} {url}")
            return 0

        try:
            size = 0
            with path.open("wb") as fp:
                for chunk in response.iter_content(chunk_size=8192):
                    size += len(chunk)
                    fp.write(chunk)
            return size
        except KeyboardInterrupt:
            # EJO The user has aborted the download and we don't want to leave
            #     a partially downloaded file to upset them later. Remove the
            #     partial file, issue a log entry with the aborted path and
            #     re-raise the exception.
            path.unlink()
            logger.debug(f"User aborted, removed partial file: {path}")
            raise

    def download_dataframe(
        self,
        dest: Path,
        file_format: FileFormat,
        overwrite: bool,
        dataframe: pandas.DataFrame = None,
        animated: bool = False,
    ) -> int:
        """Downloads all the textbooks in `dataframe` to `dest` with format `file_format`.

        :param dest: pathlib.path
        :param file_format: springer.constants.FileFormat
        :param overwrite: bool
        :param dataframe: pandas.DataFrame
        :return: <bytes written>
        """

        if dataframe is None:
            dataframe = self.dataframe

        if len(dataframe) > 1 or animated:
            return self.download_dataframe_animated(
                dest, file_format, overwrite, dataframe
            )

        total = 0
        for textbook in self.textbooks(dataframe):
            total += self.download_textbook(
                textbook, dest, file_format, overwrite=overwrite
            )
        return total

    def download_dataframe_animated(
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
            return item.title[:20]

        with typer.progressbar(
            self.textbooks(dataframe),
            length=len(dataframe),
            label=f"{self.name}:{file_format:4s}",
            show_percent=False,
            show_pos=True,
            width=10,
            empty_char=Token.Empty,
            fill_char=Token.Book,
            item_show_func=show_title,
        ) as workitems:
            total = 0
            for textbook in workitems:
                total += self.download_textbook(
                    textbook, dest, file_format, overwrite=overwrite
                )
            return total

    def download_title(self, title: str, dest: Path, file_format, overwrite: bool):
        """Download all the textbooks matching `title` to `dest` with format `file_format`.

        :param title: str
        :param dest: pathlib.path
        :param file_format: springer.constants.FileFormat
        :param overwrite: bool
        :return: int <bytes written>

        Raises KeyError if the requested title does not match any textbook titles.
        """

        df = self.dataframe[self.dataframe.title.str.contains(title, case=False)]

        if df.empty:
            raise KeyError(f"No matches for requested title '{title}'")

        return self.download_dataframe(dest, file_format, overwrite, df)

    def download_package(
        self, package: str, dest: Path, file_format: FileFormat, overwrite: bool,
    ) -> int:
        """Download all the textbooks in `package` to `dest` with format `file_format`.

        :param package: str
        :param dest: pathlib.path
        :param file_format: springer.constants.FileFormat
        :param overwrite: bool
        :return: int <bytes written>

        Raises KeyError if the requested package does not match any package names.
        """

        df = self.dataframe[
            self.dataframe.package_name.str.contains(package, case=False)
        ]

        if df.empty:
            raise KeyError(f"No matches for requested package '{package}'")

        return self.download_dataframe(dest, file_format, overwrite, df)

    def download(self, dest: Path, file_format: FileFormat, overwrite: bool,) -> int:
        """Download all the textbooks in this catalog to `dest` with format `file_format`.

        :param dest: pathlib.path
        :param file_format: springer.constants.FileFormat
        :param overwrite: bool
        :return: int <bytes written>
        """
        return self.download_dataframe(dest, file_format, overwrite)

    # EJO A formatter object might be a nice way to abstract all the list_* functions.

    def list_dataframe(self, dataframe: pandas.DataFrame, long_format: bool) -> None:
        """Displays one line per book described in the source `dataframe`. 

        :param dataframe: pandas.DataFrame
        :param long_format: bool
        """

        for textbook in self.textbooks(dataframe):

            lines = []

            for key, value in textbook._asdict().items():
                key = key.replace("_", " ").title()
                lines.append(f"{Token.Book}|{textbook.electronic_isbn}|{key}|{value}")
            lines.append(f"{Token.Stop}{lines[0][1:]}")
            if not long_format:
                lines = lines[:1]

            print("\n".join(lines))

    def list_textbooks(self, long_format: bool, match: str = None) -> None:
        """Displays all books in a catalog.

        :param long_format: bool
        :param match: bool
        """

        if match:
            source = self.dataframe[
                self.dataframe.title.str.contains(match, case=False)
            ]
        else:
            source = self.dataframe

        self.list_dataframe(source, long_format)

    def list_package(
        self, name: str, package: pandas.DataFrame, long_format: bool,
    ):
        """Displays information about an eBook package with `name`.

        :param name: str
        :param package: pandas.DataFrame
        :param long_format: bool
        """

        ebook = package.ebook_package.unique()[0]

        lines = [f"{Token.Package}|{ebook}|Name|{name}"]

        if long_format:
            lines.extend(
                [f"{Token.Package}|{ebook}|Books|{len(package)}",]
            )
        print("\n".join(lines))

        if long_format:
            self.list_dataframe(package, False)
            print(f"{Token.Stop}|{ebook}|Name|{name}")

    def list_packages(self, long_format: bool) -> None:
        """Display package information for all pacakges in the catalog.

        :param long_format: bool
        """

        for name, package in self.packages.items():
            self.list_package(name, package, long_format)

    def list_catalog(self, long_format: bool) -> None:
        """Display catalog information.

        :param long_format: bool
        """

        print(f"{self}|URL|{self.url}")
        print(f"{self}|Default|{self.is_default}")
        print(f"{self}|Cache|{self.cache_file}")
        print(f"{self}|Packages|{len(self.packages)}")
        print(f"{self}|Books|{len(self.dataframe)}")

        if long_format:
            for name, package in self.packages.items():
                self.list_package(name, package, False)
                self.list_dataframe(package, False)
        print(f"{Token.Stop}|{self.name}")
