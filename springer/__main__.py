"""Springer Textbook Bulk Downloader
"""

import typer

from loguru import logger
from pathlib import Path

from .constants import FileFormat, Language, Description, Heirarchy
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
    description: Description = typer.Option(
        Description.All_Disciplines,
        "--description",
        "-D",
        show_default=True,
        show_choices=True,
        help="Choose a catalog description.",
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
        ctx.obj = Catalog(language, description)
    except KeyError as error:
        value = error.args[0]
        typer.secho(f"Failed to locate a catalog for '{value}'", fg="red")
        raise typer.Exit(-1)


@cli.command(name="list")
def list_subcommand(
    ctx: typer.Context,
    heirarchy: Heirarchy,
    match: str = typer.Option(None, "--match", "-m", help="String used for matching."),
    long_format: bool = typer.Option(
        False,
        "--long-format",
        "-l",
        is_flag=True,
        show_default=True,
        help="Display selected information in a longer format.",
    ),
):
    """List books, package, packages, catalog or catalogs,

    Examples
    
    List titles available in the default catalog:

    `$ springer list books`

    List packages available in the default catalog:

    `$ springer list packages`

    List titles available in the German language, all disciplines catalog:

    `$ springer --language de --description all list books`

    List all eBook packages in the default catalog:

    `$ springer list packages`

    List all eBook packages in the default catalog whose name match:

    `$ springer list package -m science`

    List information about the current catalog:

    `$ springer list catalog`

    List information about the Germal language, Emergency Nursing catalog:

    `$ springer --language de --description med list catalog`

    

    """

    if heirarchy == Heirarchy.Books:
        ctx.obj.list_books(long_format)
        return

    if heirarchy is Heirarchy.Package:
        if match:
            for name, package in ctx.obj.packages.items():
                if match.casefold() in name.casefold():
                    ctx.obj.list_package(name, package, long_format)
                    return
        else:
            heirarchy = Heirarchy.Packages

    if heirarchy is Heirarchy.Packages:
        ctx.obj.list_packages(long_format)
        return

    if heirarchy is Heirarchy.Catalog:
        catalogs = [ctx.obj]

    if heirarchy is Heirarchy.Catalogs:
        catalogs = Catalog.all_catalogs()

    for catalog in catalogs:
        print(catalog)
        if long_format:
            list_subcommand(ctx, Heirarchy.Packages, long_format)
        print("\N{OCTAGONAL SIGN}")


@cli.command(name="refresh")
def refresh_subcommand(
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

    Update German language catalog whose description is 'all':

    `$ springer --language de --description all refresh`

    Update German language catalog whose description is 'med' with a new URL:

    `$ springer -L de -D med refresh --url https://example.com/api/endpoint/something/v11`

    Update all catalogs:

    `$ springer refresh --all`

    """

    if not all_catalogs:
        ctx.obj.fetch_catalog(catalog_url)
        print(ctx.obj)
        return

    for catalog in Catalog.all_catalogs():
        catalog.fetch_catalog()
        print(catalog)


@cli.command(name="clean")
def clean_subcommand(
    ctx: typer.Context,
    force: bool = typer.Option(False, "--force", "-F", is_flag=True),
    all_catalogs: bool = typer.Option(False, "--all", is_flag=True),
):
    """Removes the cached catalog.

    Examples

    Remove the English language, all disciplines cached catalog:

    `$ springer clean --force`

    Remove the German language emergency nursing cached catalog:

    `$ springer -L de -D med clean --force`

    Remove all catalogs:
    
    `$ springer clean --force --all`
    """

    if not force:
        typer.secho("The --force switch is required!", fg="red")
        raise typer.Exit(-1)

    if not all_catalogs:
        ctx.obj.cache_file.unlink()
        return

    for catalog in Catalog.all_catalogs():
        catalog.cache_file.unlink()


@cli.command(name="download")
def download_subcommand(
    ctx: typer.Context,
    package: str = typer.Option(
        None, "--package-name", "-p", help="Package name to match (partial name OK)."
    ),
    file_format: FileFormat = typer.Option(
        FileFormat.pdf, "--format", "-f", show_default=True, show_choices=True
    ),
    dest_path: Path = typer.Option(
        Path.cwd(),
        "--dest-path",
        "-d",
        show_default=True,
        help="Destination directory for downloaded files.",
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
    
    dest_path/language/description/book_file_name.fmt

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

    Download all books in PDF from the German/All_Disciplines catalog:
    
    `$ springer -L de -D all download --dest-path german/all/pdfs`

    Download all books from all catelogs in epub format:

    `$ springer download --all --format epub`

    Download all books in the 'Computer Science' package in pdf format:

    `$ springer download -p Computer`
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

    dest_path = dest_path.resolve()

    if not all_catalogs:
        if package:
            ctx.obj.download_package(package, dest_path, file_format, overwrite)
            return
        ctx.obj.download(dest_path, file_format, overwrite)
        return

    for catalog in Catalog.all_catalogs():
        dest = dest_path / catalog.language.name / catalog.description.value
        catalog.download(dest, file_format, overwrite=overwrite)
