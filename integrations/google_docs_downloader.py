import re
from pathlib import Path
from googleapiclient.discovery import build
from integrations.google_auth import get_credentials
import logging
logger = logging.getLogger(__name__)


DOCX_MIME_TYPE = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


def extract_document_id(url):
    """Метод извлечения ID Google Docs из URL."""
    id_match = re.search(r"/document/d/([a-zA-Z0-9_-]+)", url)
    if not id_match:
        logger.error("Не удалось извлечь ID google документа из ссылки.")
        raise ValueError("Не удалось извлечь ID google документа из ссылки.")
    return id_match.group(1)


def download_google_doc(doc_url, output_dir = "data/google_docs"):
    """Метод выгрузки Google Doc в DOCX формат"""
    doc_id = extract_document_id(doc_url)
    credentials = get_credentials()

    service = build("drive", "v3", credentials = credentials, cache_discovery = False)

    request = service.files().export(fileId = doc_id, mimeType = DOCX_MIME_TYPE)
    content = request.execute()

    output_path = Path(output_dir)
    output_path.mkdir(parents = True, exist_ok = True)

    docx_path = output_path / f"{doc_id}.docx"
    docx_path.write_bytes(content)

    logger.info("Документ успешно извлечен из Google Drive.")
    return docx_path