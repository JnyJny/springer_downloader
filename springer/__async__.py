""" Asynchronous Downloader
"""

import asyncio
import requests

from concurrent.futures import ThreadPoolExecutor
from springer import Catalog, FileFormat
from loguru import logger


from pathlib import Path
import typer

cli = typer.Typer()


@cli.callback()
def main(ctx: typer.Context):
    """Test Asynchronous Downloader
    """
    ctx.obj = Catalog()


@cli.command("all")
def download_all_subcommand(
    ctx: typer.Context,
    dest: Path = typer.Option(Path("."), "--dest-dir", "-d"),
    file_format: FileFormat = typer.Option(FileFormat.pdf, "--file-format", "-f"),
):
    """Download all books.
    """

    dest.mkdir(mode=0o744, exist_ok=True, parents=True)

    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(download_textbooks(ctx.obj, dest, file_format))
    loop.run_until_complete(future)


def fetch(taskid, session, url, path):

    with session.get(url, stream=True) as response:
        try:
            with path.open("wb") as fp:
                for chunk in response.iter_content(chunk_size=8192):
                    fp.write(chunk)
        except KeyboardInterrupt:
            path.unlink()
        except Exception as error:
            print(f"{error} -> url")
    return url


async def download_textbooks(catalog: Catalog, dest: Path, file_format: FileFormat):

    with ThreadPoolExecutor(max_workers=10) as executor:

        with requests.Session() as session:

            loop = asyncio.get_event_loop()

            tasks = [
                loop.run_in_executor(
                    executor,
                    fetch,
                    *(
                        session,
                        catalog.content_url(textbook.uid, FileFormat.pdf),
                        (dest / textbook.filename).with_suffix(file_format.suffix),
                    ),
                )
                for textbook in catalog.textbooks()
            ]

            for response in await asyncio.gather(*tasks):
                pass
