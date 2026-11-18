from parsers.docx_parser import parse_docx
from parsers.structure_parser import parse_structure
from parsers.semantic_parser import parse_sections
from exporters.md_structure_builder import build_md_structure
from exporters.md_exporter import export_markdown
from config.document_config import DOCUMENT_CONFIG


def process_document(file_path):
    """Метод преобразования DOCX спецификации в Markdown файл."""

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

