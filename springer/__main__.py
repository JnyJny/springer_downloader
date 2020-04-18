"""Springer Textbook Bulk Downloader
"""

import typer

from loguru import logger
from pathlib import Path

from .constants import FileFormat, Language, Topic, Component
from .catalog import Catalog


cli = typer.Typer()

DOWNLOAD_REPORT = "DOWNLOAD_ERRORS.txt"


@cli.callback()
def main(
    ctx: typer.Context,
    language: Language = typer.Option(
        None,
        "--lang",
        "-L",
        show_choices=True,
        show_default=True,
        help="Choose catalog language",
    ),
    topic: Topic = typer.Option(
        None,
        "--topic",
        "-T",
        show_default=True,
        show_choices=True,
        help="Choose a catalog topic.",
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

    Catalogs are lists of books in specific _language_, spanning a _topic_. Catalogs
    are further subdivided into _packages_ which are books grouped by subtopics.

    The available languages are:
    \b
    - English 
    - German

    The available topics are:

    \b
    - `All Disciplies`, all, 
    - `Emergency Nursing`, med.

    Note: The Emergency Nursing topic is not currently available in English.
    """

    # EJO The callback function is called before any of the command functions
    #     are invoked. Since all the subcommands work with an instantiation of
    #     springer.catalog.Catalog, we create one in the callback and attach it
    #     to the typer.Context object using the attribute 'obj'. I don't
    #     particularly care for accessing the catalog as 'ctx.obj' in the
    #     subcommands, but I haven't found a better solution to this "problem"
    #     yet.

    try:
        ctx.obj = Catalog(language, topic)

    except KeyError as error:
        typer.secho(
            f"Failed to locate a catalog for: '{error.args[0].value!s}'", fg="red"
        )
        raise typer.Exit(-1)


@cli.command(name="get-default-catalog")
def get_default_catalog_subcommand():
    """Print the default catalog identifier.

    This is the default catalog that will be used when listing books and packages.
    """
    print(Catalog())


@cli.command(name="set-default-catalog")
def set_default_catalog_subcommand(ctx: typer.Context):
    """Set default catalog language and topic.

    Examples
    
    Set the default catalog to German language:

    `$ springer -L de set-default-catalog`

    Set the default catalog to German and emergency nursing:

    `$ springer -L de -T med set-default-catalog`

    Set the default catalog to English and all disciplines topic:

    `$ springer -L en -T all set-default-catalog`

    Note: The only English language catalog is en-all.
    """
    ctx.obj.save_defaults()
    get_default_catalog_subcommand()


@cli.command(name="list")
def list_subcommand(
    ctx: typer.Context,
    component: Component,
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
    """List books, package, packages, catalog or catalogs.

    Display information about books, packages, and catalogs. Packages are
    sets of books grouped by subject. There are currently three catalogs
    available: en-all, de-all and de-med.

    Examples
    
    List titles available in the default catalog:

    `$ springer list books`

    List packages available in the default catalog:

    `$ springer list packages`

    List titles available in the German language, all disciplines catalog:

    `$ springer --language de --topic all list books`

    List all eBook packages in the default catalog:

    `$ springer list packages`

    List all eBook packages in the default catalog whose name match:

    `$ springer list package -m science`

    List information about the current catalog:

    `$ springer list catalog`

    List information about the Germal language, Emergency Nursing catalog:

    `$ springer --language de --topic med list catalog`

    """

    if component == Component.Books:

        ctx.obj.list_textbooks(long_format, match)
        return

    if component is Component.Package:
        if match:
            for name, package in ctx.obj.packages.items():
                if match.casefold() in name.casefold():
                    ctx.obj.list_package(name, package, long_format)
            return
        else:
            component = Component.Packages

    if component is Component.Packages:
        ctx.obj.list_packages(long_format)
        return

    if component is Component.Catalog:
        catalogs = [ctx.obj]

    if component is Component.Catalogs:
        catalogs = Catalog.all_catalogs()

    for catalog in catalogs:
        catalog.list_catalog(long_format)


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

    Update German language catalog whose topic is 'all':

    `$ springer --language de --topic all refresh`

    Update German language catalog whose topic is 'med' with a new URL:

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

    Remove the cached default catalog:

    `$ springer clean --force`

    Remove the cached German language emergency nursing catalog:

    `$ springer --language de --topic med clean --force`

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
    
    dest_path/language/topic/book_file_name.fmt

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
    
    `$ springer --language de --topic all download --dest-path german/all/pdfs`

    Download all books from all catelogs in epub format:

    `$ springer download --all --format epub`

    Download all books in the 'Computer Science' package in pdf format:

    `$ springer download --package-name Computer`
    """

    logger.configure(
        **{
            "handlers": [
                {
                    "sink": dest_path / DOWNLOAD_REPORT,
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
        dest = dest_path / catalog.language.name / catalog.topic.value
        if package:
            catalog.download_package(package, dest_path, file_format, overwrite)
            continue
        catalog.download(dest, file_format, overwrite=overwrite)
