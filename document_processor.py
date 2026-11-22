from integrations.google_docs_downloader import download_google_doc
from parsers.docx_parser import parse_docx
from parsers.structure_parser import parse_structure
from parsers.semantic_parser import parse_sections
from exporters.md_structure_builder import build_md_structure
from exporters.md_exporter import export_markdown
from config.document_config import DOCUMENT_CONFIG


def process_document(file_path, doc_url, source_choice):
    """Метод преобразования DOCX спецификации в Markdown файл."""

    if source_choice == "1":
        file_path = download_google_doc(doc_url)

    # Чтение исходного DOCX
    doc_elements = parse_docx(file_path)

    # Построение структуры документа
    doc_structure = parse_structure(doc_elements)

    # Извлечение семантических разделов
    doc_sections = parse_sections(doc_structure)

    # Подготовка md структуры
    config = DOCUMENT_CONFIG
    md_structure = build_md_structure(doc_structure, doc_sections, config)

    # Экспорт результата в Markdown файл
    export_markdown(md_structure)