"""
"""

from .constants import FileFormat, Language, Category

_SPRINGER_PDF_URL = "https://link.springer.com/content/pdf"
_SPRINGER_EPUB_URL = "https://link.springer.com/download/epub"

_SPRINGER_REST_URL = "https://resource-cms.springernature.com/springer-cms/rest"

_SPRINGER_CATALOG_EN_URL = f"{_SPRINGER_REST_URL}/v1/content/17858272/data/v4"
_SPRINGER_CATALOG_DE_URL = f"{_SPRINGER_REST_URL}/v1/content/17863240/data/v2"
_SPRINGER_NURSING_CATALOG_DE_URL = f"{_SPRINGER_REST_URL}/v1/content/17856246/data/v3"


_SPRINGER_ANNOUNCEMENT_URL = "https://www.springernature.com/gp/librarians/news-events/all-news-articles/industry-news-initiatives/free-access-to-textbooks-for-institutions-affected-by-coronaviru/17855960"


_urls = {
    "announcement": _SPRINGER_ANNOUNCEMENT_URL,
    "catalogs": {
        Language.English: {Category.AllDisciplines: _SPRINGER_CATALOG_EN_URL},
        Language.German: {
            Category.AllDisciplines: _SPRINGER_CATALOG_DE_URL,
            Category.EmergencyNursing: _SPRINGER_NURSING_CATALOG_DE_URL,
        },
    },
    "content": {
        FileFormat.pdf: _SPRINGER_PDF_URL,
        FileFormat.epub: _SPRINGER_EPUB_URL,
    },
}
