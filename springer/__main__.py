"""Springer Textbook Bulk Download Tool
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
    """__Springer Textbook Bulk Download Tool__
    
    **NOTICE**:

    The author of this software is not affiliated with Springer and this
    tool is not authorized or supported by Springer. Thank you to
    Springer for making these high quality textbooks available at no
    cost.

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
    
    This tool automates the tasks of downloading the Springer provided
    Excel-formatted catalogs and downloading the files described in the
    catalog.

    This utility can be installed using `pip`:

    `$ python3 -m pip install springer`

    Or from the latest source on GitHub:

    `$ python3 -m pip install git+https://github.com/JnyJny/springer_downloader`

    The source is available on [GitHub](https://github.com/JnyJny/springer_downloader).

    Catalogs are lists of books in a specific _language_, spanning a _topic_. Catalogs
    are further subdivided into _packages_ which are books grouped by sub-topics. The
    smallest unit of download is an eBook package.

    The available languages are: English & German.

    The available topics are: _All Disciplines_ and _Emergency Nursing_.

    **Note: The _Emergency Nursing_ topic is not available in English.**

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

    This is the default catalog that will be used when listing books and packages
    and the user has not specified a --language or --topic on the command line.
    """

    typer.secho(f"Default: {Catalog(fetch=False)}", fg="green")


@cli.command(name="set-default-catalog")
def set_default_catalog_subcommand(ctx: typer.Context,):
    """Set default catalog language and topic.

    __Examples__
    
    Set the default catalog to German language:

    `$ springer --language de set-default-catalog`

    Set the default catalog to German and emergency nursing:

    `$ springer --language de --topic med set-default-catalog`

    Set the default catalog to English and all disciplines topic:

    `$ springer --language en --topic all set-default-catalog`

    Note: The only English language catalog is `en-all`.
    """
    prev = Catalog(fetch=False)
    ctx.obj.save_defaults()
    typer.secho(f"Old Default: {prev!s}", fg="red" if prev.is_default else "blue")
    typer.secho(f"New Default: {Catalog(fetch=False)!s}", fg="green")


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

    Display information about books, packages, and catalogs. Packages
    are sets of books grouped by subject.

    __Examples__
    
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


@cli.command(name="refresh-catalog")
def refresh_subcommand(
    ctx: typer.Context,
    catalog_url: str = typer.Option(
        None, "--url", "-u", help="URL for Excel-formatted catalog."
    ),
    all_catalogs: bool = typer.Option(False, "--all", is_flag=True),
):
    """Refresh the cached catalog of springer textbooks.

    If `--all` is specified, the `--url` option is ignored.

    __Examples__

    Update English language catalog:

    `$ springer --language en refresh`

    Update German language catalog whose topic is 'all':

    `$ springer --language de --topic all refresh`

    Update German language catalog whose topic is 'med' with a new url:

    `$ springer -l de -d med refresh --url https://example.com/api/endpoint/something/v11`

    __NOTE: THIS URL DOES NOT REPLACE THE DEFAULT URL FOR THE TARGET CATALOG__

    Update all catalogs:

    `$ springer refresh-catalog --all`

    """

    if not all_catalogs:
        ctx.obj.fetch_catalog(catalog_url)
        print(ctx.obj)
        return

    for catalog in Catalog.all_catalogs():
        catalog.fetch_catalog()
        print(catalog)


@cli.command(name="clean-catalog")
def clean_subcommand(
    ctx: typer.Context,
    force: bool = typer.Option(False, "--force", "-F", is_flag=True),
    all_catalogs: bool = typer.Option(False, "--all", is_flag=True),
):
    """Remove cached catalogs.

    __Examples__

    Remove the cached default catalog:

    `$ springer clean-catalog --force`

    Remove the cached German language _Emergency Nursing_ catalog:

    `$ springer --language de --topic med clean-catalog --force`

    Remove all catalogs:
    
    `$ springer clean-catalog --force --all`
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
    
    `dest_path/language/topic/book_file_name.fmt`

    Files that fail to download will be logged to a file named:

    `dest_path/DOWNLOAD_ERRORS.txt`
    
    The log entries will have the date and time of the attempt,
    the HTTP status code and the URL that was attempted.


    __Examples__

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

    `$ springer download --package-name computer`
    """

    dest_path = dest_path.resolve()

    try:
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
        if not all_catalogs:
            if package:
                dest_path.mkdir(mode=0o755, exist_ok=True, parents=True)
                ctx.obj.download_package(package, dest_path, file_format, overwrite)
                return
            ctx.obj.download(dest_path, file_format, overwrite)
            return

        for catalog in Catalog.all_catalogs():
            dest = dest_path / catalog.language.name / catalog.topic.value
            dest.mkdir(mode=0o755, exist_ok=True, parents=True)
            if package:
                try:
                    catalog.download_package(package, dest_path, file_format, overwrite)
                except KeyError as error:
                    typer.secho(f"{catalog}: ", nl=False)
                    typer.secho(str(error).replace('"', ""), fg="red")
                    continue
            catalog.download(dest, file_format, overwrite=overwrite)

    except KeyError as error:
        typer.secho(str(error), fg="red")
        raise typer.Exit(-1) from None

    except PermissionError as error:
        typer.secho("Permission error for: ", nl=False)
        typer.secho(str(error.filename), fg="red")
        raise typer.Exit(-1) from None
