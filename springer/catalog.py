"""the Springer Free Textbook Catalog
"""

import pandas as pd
import typer

from time import sleep
from pathlib import Path

from .constants import FileFormat, Language, Category

from .textbook import Textbook

from . import _urls


class Catalog:
    """A wrapper around an Excel file provided by Springer, listing information
    about the textbooks offered free of charge.
    """

    def __init__(
        self,
        language: Language = None,
        category: Category = None,
        refresh: bool = False,
    ):
        """
        :param url: str
        :param refresh: bool
        """
        self.language = language or Language.English
        self.category = category or Category.AllDisciplines

        if not self.cache_file.exists() or refresh:
            self.fetch_catalog()

    def __repr__(self):

        return f"{self.__class__.__name__}(language={self.language}, category={self.category})"

    def __str__(self):

        return (
            "\n".join(
                [
                    f"Catalog: {self.url}",
                    f"    Language: {self.language}",
                    f"    Category: {self.category}",
                    f"  Cache File: {self.cache_file}",
                    f"  # of Books: {self.dataframe.count().max()}",
                ]
            )
            + "\n"
        )

    @property
    def url(self) -> str:
        try:
            return self._url
        except AttributeError:
            pass

        self._url = _urls["catalogs"][self.language][self.category]

        return self._url

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

        self._cache_file = self.app_dir / f"catalog-{self.language}-{self.category}.csv"

        return self._cache_file

    @property
    def dataframe(self):
        """A pandas.DataFrame populated with the contents of the Springer free textbook catalog.
        """
        try:
            return self._dataframe
        except AttributeError:
            pass

        if not self.cache_file.exists():
            self.fetch_catalog()

        df = pd.read_csv(self.cache_file).dropna(axis=1)

        df["Section"] = df["DOI URL"].apply(lambda v: v.split("/")[-2])
        df["Book ID"] = df["DOI URL"].apply(lambda v: v.split("/")[-1])

        df.sort_values(by="Book Title", ascending=True, inplace=True)

        self._dataframe = df

        return self._dataframe

    def fetch_catalog(self, url: str = None) -> None:
        """Reads the Excel file at `url` and writes it to the local filesystem.

        The Excel file is written to `cache_file` in CSV format. If
        `url` is not given, `self.url` is used.

        :param url: str
        :return: None
        """

        url = url or self.url

        pd.read_excel(url).dropna(axis=1).to_csv(self.cache_file)

    def textbooks(self, file_format: FileFormat, filter: dict = None) -> Textbook:
        """A generator function that returns initialized Textbook objects.
        
        For each entry in the catalog configured for the specified
        `file_format`, a Textbook object initialized from values in
        self.dataframe is yield'ed to the caller.

        :param file_format: springer.constants.FileFormat
        :param filter: dict <NotImplemented>
        :return: list
        """

        for values in self.dataframe[Textbook._dataframe_columns].values:
            yield Textbook(*values, file_format)

    def download(
        self,
        dest: Path,
        file_format: FileFormat,
        overwrite: bool,
        log: bool = True,
        filter: dict = None,
    ) -> None:
        """Downloads all the books found in the Springer textbook catalog.

        :param dest: Path
        :param file_format: springer.constants.FileFormat
        :param overwrite: bool
        :param dryrun: bool:
        :param filter: dict <NotImplemented>
        :return: None
        """

        dest = dest.resolve()

        dest.mkdir(mode=0o755, exist_ok=True, parents=True)

        def item_title(value):
            if not value:
                return f"Downloaded to {dest}"
            return value.title[:40]

        with typer.progressbar(
            self.textbooks(file_format),
            item_show_func=item_title,
            length=self.dataframe.count().max(),
            fill_char="📕",
            label=f"{file_format.upper():4s}:{self.language.value.upper()}",
            show_pos=True,
            show_percent=False,
            show_eta=True,
            width=10,
        ) as workitems:
            for textbook in workitems:
                textbook.save(dest, overwrite=overwrite)

    def list(
        self, file_format: FileFormat, show_path: bool = False, filter: dict = None,
    ) -> None:
        """List available textbooks titles.

        :param file_format: springer.constant.FileFormat
        :param show_path: bool
        :param filter: dict <NotImplemented>
        """

        for count, textbook in enumerate(self.textbooks(file_format, filter), start=1):
            print(f"Title #{count:03d}: {textbook.title}")
            if show_path:
                print(f" Path #{count:03d}> {textbook.path}")
