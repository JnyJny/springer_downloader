"""Springer Textbook Bulk Downloader
"""

import typer

from pathlib import Path

from .file_format import FileFormat
from .catalog import Catalog

cli = typer.Typer()


@cli.callback()
def main(
    ctx: typer.Context,
    verbose: bool = typer.Option(False, "--verbose/--quiet", "-v/-q"),
):
    """Springer Textbook Bulk Download Tool
    """
    ctx.obj = verbose


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
    catalog_url: str = typer.Option(
        None, "--url", "-u", help="URL for Excel formatted catalog"
    ),
    refresh: bool = typer.Option(
        False,
        "--refresh",
        "-R",
        is_flag=True,
        help="Refresh the cached Springer catalog",
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
    dryrun: bool = typer.Option(
        False,
        "--dry-run",
        "-n",
        is_flag=True,
        show_default=True,
        help="Display URLs and files that would be downloaded.",
    ),
):
    """
    """

    catalog = Catalog(catalog_url, refresh=refresh)

    catalog.download(dest_path, file_format, overwrite=overwrite, dryrun=dryrun)
