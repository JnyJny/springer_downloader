"""
"""

from .file_format import FileFormat

_SPRINGER_PDF_URL = "https://link.springer.com/content"
_SPRINGER_EPUB_URL = "https://link.springer.com/download"
_SPRINGER_CATALOG_URL = "https://resource-cms.springernature.com/springer-cms/rest/v1/content/17858272/data/v4"


_content_urls = {
    FileFormat.pdf: _SPRINGER_PDF_URL,
    FileFormat.epub: _SPRINGER_EPUB_URL,
}

_urls = {"catalog": _SPRINGER_CATALOG_URL}
_urls.update(_content_urls)
