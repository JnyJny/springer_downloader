"""Springer URLS

"""

from .constants import Language, Topic, FileFormat

SPRINGER_ANNOUNCEMENT_URL = "https://www.springernature.com/gp/librarians/news-events/all-news-articles/industry-news-initiatives/free-access-to-textbooks-for-institutions-affected-by-coronaviru/17855960"

SPRINGER_REST_URL = "https://resource-cms.springernature.com/springer-cms/rest"

SPRINGER_CATALOG_EN_URL = f"{SPRINGER_REST_URL}/v1/content/17858272/data/v5"
SPRINGER_CATALOG_DE_URL = f"{SPRINGER_REST_URL}/v1/content/17863240/data/v2"
SPRINGER_NURSING_CATALOG_DE_URL = f"{SPRINGER_REST_URL}/v1/content/17856246/data/v3"

SPRINGER_PDF_URL = "https://link.springer.com/content/pdf"
SPRINGER_EPUB_URL = "https://link.springer.com/download/epub"


urls = {
    "announcement": SPRINGER_ANNOUNCEMENT_URL,
    "catalogs": {
        Language.English: {Topic.All_Disciplines: SPRINGER_CATALOG_EN_URL},
        Language.German: {
            Topic.All_Disciplines: SPRINGER_CATALOG_DE_URL,
            Topic.Emergency_Nursing: SPRINGER_NURSING_CATALOG_DE_URL,
        },
    },
    "content": {FileFormat.pdf: SPRINGER_PDF_URL, FileFormat.epub: SPRINGER_EPUB_URL,},
}
