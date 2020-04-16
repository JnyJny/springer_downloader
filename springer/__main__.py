"""Springer Textbook Bulk Downloader
"""

import typer

from loguru import logger
from pathlib import Path

from .constants import FileFormat, Language, Category
from .catalog import Catalog

cli = typer.Typer()


@cli.callback()
def main(
    ctx: typer.Context,
    language: Language = typer.Option(
        Language.English,
        "--lang",
        "-L",
        show_choices=True,
        show_default=True,
        help="Choose catalog language",
    ),
    category: Category = typer.Option(
        Category.AllDisciplines,
        "--category",
        "-C",
        show_default=True,
        show_choices=True,
        help="Choose a catalog catagory.",
    ),
):
    """Springer Textbook Bulk Download Tool
    
    NOTICE:

    Author not affiliated with Springer and this tool is not authorized
    or supported by Springer. Thank you to Springer for making these
    high quality textbooks available at no cost. 
    """
    # EJO The callback function is called before any of the command functions
    #     are invoked. Since all the subcommands work with an instantiation of
    #     springer.catalog.Catalog, we create one in the callback and attach
    #     it to the typer.Context object using the attribute 'obj'.

    ctx.obj = Catalog(language, category)


@cli.command()
def list(
    ctx: typer.Context,
    file_format: FileFormat = typer.Option(
        FileFormat.pdf, "--format", "-f", show_default=True, show_choices=True
    ),
    show_path: bool = typer.Option(
        False, "--show-path", "-p", help="Show generated filename for each book.",
    ),
):
    """List textbooks in the catalog.
    """

    ctx.obj.list(file_format, show_path=show_path)


@cli.command()
def download(
    ctx: typer.Context,
    dest_path: Path = typer.Option(
        Path.cwd(),
        "--dest-path",
        "-d",
        show_default=True,
        help="Destination directory for downloaded files.",
    ),
    file_format: FileFormat = typer.Option(
        FileFormat.pdf, "--format", "-f", show_default=True, show_choices=True
    ),
    overwrite: bool = typer.Option(
        False,
        "--over-write",
        "-W",
        is_flag=True,
        show_default=True,
        help="Over write downloaded files.",
    ),
    all_catalogs: bool = typer.Option(
        False, "--all", is_flag=True, help="Downloads books from all catalogs."
    ),
):
    """Download textbooks from Springer.

    This command will download all the textbooks found in the catalog
    of free textbooks provided by Springer. The default file format 
    is PDF and the files are saved by default to the current working
    directory.

    If a download is interrupted, you can re-start the download and it
    will skip over files that have been previously downloaded and pick up
    where it left off. 

    If the --all option is specified, the --dest=path option specifies the
    root directory where files will be stored. Each catalog will save 
    it's textbooks to:
    
    dest_path/language/category/book_file_name.fmt


    EXAMPLES

    Download all books in PDF format to the current directory:
    
    $ springer download
    
    Download all books in EPUB format to the current directory:

    $ springer download --format epub

    Download all books in PDF format to a directory `pdfs`:

    $ springer download --dest-path pdfs

    Download books in PDF format to `pdfs` with overwriting:

    $ springer download --dest-path pdfs --over-write

    Download all books in PDF from the German all disciplines catalog:
    
    $ springer -L de -C all download --dest-path german/all/pdfs

    Download all books from all catelogs in epub format:

    $ springer download --all --dest-path books --format epub
    """

    logger.configure(
        **{
            "handlers": [
                {
                    "sink": dest_path / "DOWNLOAD_ERRORS.txt",
                    "format": "{time:YYYY-MM-DD HH:mm} | <red>{message}</>",
                    "colorize": True,
                },
            ]
        }
    )

    if not all_catalogs:
        ctx.obj.download(dest_path, file_format, overwrite=overwrite)
        return

    for language in Language:
        for category in Category:
            try:
                catalog = Catalog(language, category)
            except KeyError:
                continue
            dest = dest_path / language.value / category.value
            catalog.download(dest, file_format, overwrite=overwrite)


@cli.command()
def refresh(
    ctx: typer.Context,
    catalog_url: str = typer.Option(
        None, "--url", "-u", help="URL for Excel-formatted catalog"
    ),
    all_catalogs: bool = typer.Option(False, "--all", is_flag=True),
):
    """Refresh the cached catalog of Springer textbooks.

    If --all is specified, the --url option is ignored.

    Examples

    Update English language catalog:

    $ springer --language en refresh

    Update German language catalog whose category is 'all':

    $ springer --language de --category all refresh

    Update German language catalog whose category is 'med' with a new URL:

    $ springer -L de -C med refresh --url https://example.com/api/endpoint/something/v11

    Update all catalogs:

    $ springer refresh --all

    """

    if not all_catalogs:
        ctx.obj.fetch_catalog(catalog_url)
        return

    for language in Language:
        for category in Category:
            try:
                catalog = Catalog(language, category)
                catalog.fetch_catalog()
                print(catalog)

            except KeyError:
                pass


@cli.command()
def clean(
    ctx: typer.Context,
    force: bool = typer.Option(False, "--force", "-F"),
    all_catalogs: bool = typer.Option(False, "--all", is_flag=True),
):
    """Removes the cached catalog.
    """

    if not force:
        typer.secho("The --force switch is required!", fg="red")
        raise typer.Exit(-1)

    if not all_catalogs:
        ctx.obj.cache_file.unlink()
        return

    for language in Language:
        for category in Category:
            try:
                Catalog(language, category).cache_file.unlink()
            except KeyError:
                pass


@cli.command()
def catalogs(ctx: typer.Context):
    """List available catalogs.
    """

    for language in Language:
        for category in Category:
            try:
                catalog = Catalog(language, category)
                print(catalog)
            except KeyError:
                pass
