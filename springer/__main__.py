"""Springer Textbook Bulk Downloader
"""

import typer

from pathlib import Path

from .file_format import FileFormat
from .catalog import Catalog

cli = typer.Typer()


@cli.callback()
def main(ctx: typer.Context):
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

    ctx.obj = Catalog()


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
):
    """Download textbooks from Springer.

    This command will download all the textbooks found in the catalog
    of free textbooks provided by Springer. The default file format 
    is PDF and the files are saved by default to the current working
    directory.

    If a download is interrupted, you can re-start the download and it
    will skip over files that have been previously downloaded and pick up
    where it left off. 

    EXAMPLES

    Download all books in PDF format to the current directory.
    
    $ springer download
    
    Download all books in EPUB format to the current directory.

    $ springer download --format epub

    Download all books in PDF format to a directory `pdfs`.

    $ springer download --dest-path pdfs

    Download books in PDF format to `pdfs` with overwriting.

    $ springer download --dest-path pdfs --over-write
    
    
    """

    ctx.obj.download(dest_path, file_format, overwrite=overwrite)


@cli.command()
def refresh(
    ctx: typer.Context,
    catalog_url: str = typer.Option(
        None, "--url", "-u", help="URL for Excel-formatted catalog"
    ),
):
    """Refresh the cached catalog of Springer textbooks.
    """

    ctx.obj.fetch_catalog(catalog_url)


@cli.command()
def clean(
    ctx: typer.Context, force: bool = typer.Option(False, "--force", "-F"),
):
    """Removes the cached catalog.
    """

    if not force:
        typer.secho("The --force switch is required!", fg="red")
        raise typer.Exit(-1)

    ctx.obj.cache_file.unlink()


@cli.command()
def urls():
    """List catalog and content URLS.
    """

    from . import _urls as URLS

    for key, value in URLS.items():
        print(f"{key.upper()}={value}")
