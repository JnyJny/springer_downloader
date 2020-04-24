"""Springer Textbook Bulk Download Tool
"""

import typer

from loguru import logger
from pathlib import Path

from .constants import FileFormat, Language, Topic, Component
from .catalog import Catalog


cli = typer.Typer()

DOWNLOAD_REPORT = "DOWNLOAD_REPORT.txt"


@cli.callback()
def main(
    ctx: typer.Context,
    language: Language = typer.Option(
        None,
        "--language",
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
    """![Downloading](https://github.com/JnyJny/springer_downloader/raw/master/demo/animations/download-catalog.gif)
    __Springer Textbook Bulk Download Tool__
    
    ## NOTICE

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

    ## Overview

    This tool automates the process of downloading the Springer-provided
    Excel catalogs, locating URLs and downloading the files in PDF or epub
    format.

    Catalogs are lists of books in a specific _language_, spanning a
    _topic_. Catalogs are further subdivided into _packages_ which are
    books grouped by sub-topics.
    
    Textbooks can be downloaded by; title, package name or the entire
    catalog. Title and package names can be incompletely specified and
    are case-insensitive. 

    The available languages are: English & German.

    The available topics are: _All Disciplines_ and _Emergency Nursing_.

    **Note: The _Emergency Nursing_ topic is not available in English.**

    ## Source and License

    Full source is available on
    [GitHub](https://github.com/JnyJny/springer_downloader) and it is
    licensed under the
    [Apache-2.0](https://www.apache.org/licenses/LICENSE-2.0)
    license.

    ## Installation

    This utility can be installed using `pip`:

    `$ python3 -m pip install springer`

    Or from the latest source on GitHub:

    `$ python3 -m pip install git+https://github.com/JnyJny/springer_downloader`
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
    name: str = typer.Option(
        None, "--name", "-n", help="Name to match against title or pacakge."
    ),
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
        ctx.obj.list_textbooks(long_format, name)
        return

    if component is Component.Package:
        if name:
            for pkgname, pkginfo in ctx.obj.packages.items():
                if name.casefold() in pkgname.casefold():
                    ctx.obj.list_package(pkgname, pkginfo, long_format)
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


def _configure_logger(path: Path, logfile: str = None) -> None:
    """Adds `path` / `logfile` to the logger configuration.

    Makes sure that the path exists (including parents)
    and enables logging to the specified file located in that
    directory.

    :param path: pathlib.Path
    :param logfile: str 

    """

    logfile = logfile or DOWNLOAD_REPORT

    logfmt = "{time:YYYY-MM-DD HH:mm} | <red>{message}</>"
    logger.configure(
        **{"handlers": [{"sink": path / logfile, "format": logfmt, "colorize": True,},]}
    )


@cli.command("download")
def download_subcommand(
    ctx: typer.Context,
    component: Component,
    name: str = typer.Option(
        None, "--name", "-n", help="Name to match against title or package."
    ),
    dest_path: Path = typer.Option(
        Path.cwd(),
        "--dest-path",
        "-d",
        show_default=True,
        help="Destination directory for downloaded files.",
    ),
    file_format: FileFormat = typer.Option(
        FileFormat.pdf, "--format", "-f", show_default=True, show_choices=True,
    ),
    overwrite: bool = typer.Option(
        False,
        "--over-write",
        "-W",
        is_flag=True,
        show_default=True,
        help="Over write downloaded files.",
    ),
):
    """Download textbooks from Springer

    This command downloads textbooks from Springer to the local host. Files
    are saved by default in PDF format to the current working directory.

    If a download is interrupted by the user, it can be later restarted where
    the interruption occurred without downloading previous files. 

    Problems encountered while downloading files are logged to:

    `dest-path/DOWNLOAD_REPORT.txt`

    __Examples__

    Download all books in the default catalog in PDF format to the
    current directory:

    `$ springer download books`

    Download all books in EPUB format whose title includes 'python':

    `$ springer download books --name python --file-format epub`

    Download all books into directories grouped by package:

    `$ springer download packages --dest-path by_pkgs

    Download all books in a specific package in EPUB format:

    `$ springer download package --name 'Computer Science' --file-format epub`

    Download all books in packages whose name includes `Science`:

    `$ springer download package --name science --dest sciences`

    Download all books in all catalogs [en-all, de-all, de-med] in EPUB format:

    `$ springer download catalogs --file-format epub`

    The `catalogs` download subcommand will create a set of directories by language
    and topic for each catalog and save downloaded files into the appropriate
    directory, eg:

    \b
    - dest-path/English/All_Disciplines/package_name/title.fmt
    - dest-path/German/All_Disciplines/package_name/title.fmt
    - dest-path/German/Emergency_Nursing/package_name/title.fmt

    The `package` and `packages` subcommands will also save downloaded
    files into directories with package names rooted in the destination
    path:

    \b
    dest-path/package_name/title.fmt
    ...



    See Also: `set-default-catalog`, `get-default-catalog`, `list`
    """

    dest_path = dest_path.resolve()

    dest_path.mkdir(mode=0o755, exist_ok=True, parents=True)

    _configure_logger(dest_path)

    try:
        if component in [Component.Books, Component.Catalog]:
            if not name:
                ctx.obj.download(dest_path, file_format, overwrite)
            else:
                ctx.obj.download_title(name, dest_path, file_format, overwrite)
            return

        if component in [Component.Package, Component.Packages]:

            if component is Component.Package:
                if not name:
                    typer.secho(f"Please supply a `name` for package", fg="red")
                    raise typer.Exit(-1)
                package_names = [name]
            else:
                package_names = ctx.obj.packages.keys()

            for pkgname in package_names:
                path = dest_path / pkgname.replace(" ", "_")
                path.mkdir(mode=0o755, exist_ok=True, parents=True)
                ctx.obj.download_package(pkgname, path, file_format, overwrite)
            return

        if component is Component.Catalogs:

            for catalog in Catalog.all_catalogs():
                path = dest_path / catalog.language.name / catalog.topic.name
                path.mkdir(mode=0o755, exist_ok=True, parents=True)
                for pkgname in catalog.packages:
                    path = dest_path / pkgname.replace(" ", "_")
                    path.mkdir(mode=0o755, exist_ok=True, parents=True)
                    catalog.download_package(pkgname, path, file_format, overwrite)

    except KeyError as error:
        typer.secho(str(error), fg="red")
        raise typer.Exit(-1) from None

    except PermissionError as error:
        typer.secho("Permission error for: ", nl=False)
        typer.secho(str(error.filename), fg="red")
        raise typer.Exit(-1) from None
