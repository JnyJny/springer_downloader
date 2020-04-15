#!/usr/bin/env python3

import pandas as pd
import requests
import tqdm

from io import BytesIO
from pathlib import Path

## requirements.txt
# pandas
# xlrd
# requests
# tqdm


def get_catalog_dataframe(url: str = None, filename: str = None) -> pd.DataFrame:
    """Downloads the Springer Excel catalog file, caches it,
    and returns a Pandas.DataFrame with empty rows dropped.
    """
    url = (
        url
        or "https://resource-cms.springernature.com/springer-cms/rest/v1/content/17858272/data/v4"
    )
    filename = filename or "catalog.xls"

    if Path(filename).is_file():
        catalog_data = filename
    else:
        result = requests.get(url, stream=True)
        if not result:
            raise ValueError(f"problem opening {url}", result) from None
        catalog_data = BytesIO()
        for chunk in result.iter_content(chunk_size=None):
            catalog_data.write(chunk)
        Path("catalog.xls").write_bytes(catalog_data.getvalue())

    return pd.read_excel(catalog_data).dropna(axis=1, how="all")


if __name__ == "__main__":

    df = get_catalog_dataframe()

    URL_PDF_FMT = "https://link.springer.com/content/pdf/10.1007/{}.pdf"

    df["PDF URL"] = df["DOI URL"].apply(
        lambda v: URL_PDF_FMT.format(v.strip().replace("http://doi.org/10.1007/", ""))
    )

    destination = Path("books")
    destination.mkdir(mode=0o755, exist_ok=True)

    cols = ["Book Title", "PDF URL"]

    failed = {}

    for title, url in tqdm.tqdm(df[cols].values):

        book = (destination / title.replace("/", "_")).with_suffix(".pdf")
        if book.exists():
            continue

        result = requests.get(url, stream=True)
        if not result:
            failed.setdefault(url, result)
            continue

        try:
            with book.open("wb") as fp:
                for chunk in result.iter_content(chunk_size=None):
                    fp.write(chunk)
        except Exception:
            failed.setdefault(str(book), result)

    for title, r in failed.items():
        print(f"Failed: {title} {r.ok}")
