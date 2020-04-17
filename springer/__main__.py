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
    
    **NOTICE**:

    Author not affiliated with Springer and this tool is not authorized
    or supported by Springer. Thank you to Springer for making these
    high quality textbooks available at no cost. 

    \b
    >"With the Coronavirus outbreak having an unprecedented impact on
    >education, Springer Nature is launching a global program to support
    >learning and teaching at higher education institutions
    >worldwide. Remote access to educational resources has become
    >essential. We want to support lecturers, teachers and students
    >during this challenging period and hope that this initiative will go
    >some way to help.
    >
    >Institutions will be able to access more than 500 key textbooks
    >across Springer Nature’s eBook subject collections for free. In
    >addition, we are making a number of German-language Springer medical
    >training books on emergency nursing freely accessible.  These books
    >will be available via SpringerLink until at least the end of July."

    [Source](https://www.springernature.com/gp/librarians/news-events/all-news-articles/industry-news-initiatives/free-access-to-textbooks-for-institutions-affected-by-coronaviru/17855960)
    
    This tool automates the tasks of downloading the Excel-formatted
    catalogs and downloading the files described in the catalog.

    This utility can be installed using `pip`:

    `$ python3 -m pip install springer`

    Or the latest from master:

    `$ python3 -m pip install git+https://github.com/JnyJny/springer_downloader`

    The source is available on [GitHub](https://github.com/JnyJny/springer_downloader).
    """

    # EJO The callback function is called before any of the command functions
    #     are invoked. Since all the subcommands work with an instantiation of
    #     springer.catalog.Catalog, we create one in the callback and attach
    #     it to the typer.Context object using the attribute 'obj'.

    try:
        ctx.obj = Catalog(language, category)
    except KeyError as error:
        value = error.args[0]
        typer.secho(f"Failed to locate a catalog for '{value}'", fg="red")
        raise typer.Exit(-1)


@cli.command()
def list(
    ctx: typer.Context,
    file_format: FileFormat = typer.Option(
        FileFormat.pdf, "--format", "-f", show_default=True, show_choices=True
    ),
    long_format: bool = typer.Option(
        False, "--long-format", "-l", help="Show more information for each book.",
    ),
):
    """List titles of textbooks in the catalog.

    Examples
    
    List titles available in the default catalog (en-all):

    `$ springer list`

    List titles available in the German language, all disciplines catalog:

    `$ springer --language de --category all list`

    """

    for index, textbook in enumerate(ctx.obj.textbooks(file_format), start=1):
        print(f"  Title #{index:03d}: ", textbook.title)
        if long_format:
            print("        Path> ", textbook.path)
            print("      Author> ", textbook.author)
            print("     Edition> ", textbook.edition)
            print("        ISBN> ", textbook.isbn)
            print("       EISBN> ", textbook.eisbn)
            print("     DOI URL> ", textbook.doi_url)


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

    If the --all option is specified, the --dest-path option specifies the
    root directory where files will be stored. Each catalog will save 
    it's textbooks to:
    
    dest_path/language/category/book_file_name.fmt

    Files that fail to download will be logged to a file named:

    dest_path/DOWNLOAD_ERRORS.txt
    
    The log entries will have the date and time of the attempt,
    the HTTP status code and the URL that was attempted.


    EXAMPLES

    Download all books in PDF format to the current directory:
    
    `$ springer download`
    
    Download all books in EPUB format to the current directory:

    `$ springer download --format epub`

    Download all books in PDF format to a directory `pdfs`:

    `$ springer download --dest-path pdfs`

    Download books in PDF format to `pdfs` with overwriting:

    `$ springer download --dest-path pdfs --over-write`

    Download all books in PDF from the German all disciplines catalog:
    
    `$ springer -L de -C all download --dest-path german/all/pdfs`

    Download all books from all catelogs in epub format:

    `$ springer download --all --dest-path books --format epub`
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

    `$ springer --language en refresh`

    Update German language catalog whose category is 'all':

    `$ springer --language de --category all refresh`

    Update German language catalog whose category is 'med' with a new URL:

    `$ springer -L de -C med refresh --url https://example.com/api/endpoint/something/v11`

    Update all catalogs:

    `$ springer refresh --all`

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

    Examples

    Remove the English language, all disciplines cached catalog:

    `$ springer clean -F`

    Remove the German language emergency nursing cached catalog:

    `$ springer -L de -C med clean -F`
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
def catalogs():
    """List available catalogs.

    Prints an entry for each known catalog:
    
    \b
    - Catalog URL
    - Language
    - Category
    - Cache file path
    - Number of books in the catalog.

    """

    for language in Language:
        for category in Category:
            try:
                catalog = Catalog(language, category)
                print(catalog)
            except KeyError:
                pass
