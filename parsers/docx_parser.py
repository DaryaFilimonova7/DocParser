import re
from pathlib import Path

from docx import Document
from docx.text.paragraph import Paragraph
from docx.text.run import Run
from docx.text.hyperlink import Hyperlink
from docx.table import Table
from docx.oxml.ns import qn
from docx.opc.exceptions import PackageNotFoundError

import logging
logger = logging.getLogger(__name__)


def parse_docx(file_path):
    """Метод получения списка элементов из документа в исходном порядке и их классификация."""
    logger.info("Начало обработки DOCX файла.")

    file_path = Path(file_path)
    if file_path.suffix.lower() != ".docx":
        logger.error("Поддерживаются только DOCX файлы.")
        raise ValueError("Поддерживаются только DOCX файлы.")

    try:
        doc = Document(str(file_path))
    except PackageNotFoundError as error:
        logger.error(f"Файл не найден: {error}.")
        raise
    except Exception as error:
        logger.error(f"Ошибка при чтении DOCX файла: {error}.")
        raise


    doc_elements = []
    next_position = 0

    for elem in doc.element.body:
        if elem.tag.endswith("p"):
            paragraph = Paragraph(elem, doc)
            text = paragraph.text.strip()

            if not text:
                continue

            style_name = paragraph.style.name.lower()

            if "heading" in style_name:
                extracted_heading = extract_heading(paragraph, style_name, next_position)
                doc_elements.append(extracted_heading)

            elif "title" in style_name:
                extracted_title = extract_title(paragraph, next_position)
                doc_elements.append(extracted_title)

            elif paragraph._p.pPr is not None and paragraph._p.pPr.find(qn('w:numPr')) is not None:
                extracted_list_item = extract_list_info(paragraph, next_position)
                doc_elements.append(extracted_list_item)

            else:
                extracted_paragraph = extract_paragraph(paragraph, next_position)
                doc_elements.append(extracted_paragraph)

            next_position += 1

        elif elem.tag.endswith('tbl'):
            table = Table(elem, doc)
            extracted_table = extract_table(table, next_position)
            doc_elements.append(extracted_table)

            next_position += 1

    if len(doc_elements) == 0:
        logger.error(f"Загружен пустой файл.")
        raise LookupError("Загружен пустой файл.")
    logger.info(f"DOCX файл успешно обработан. Найдено элементов: {len(doc_elements)}.")
    return doc_elements


def extract_heading(paragraph, style_name, next_position):
    """Метод извлечения заголовка."""

    element_type = "heading"
    position = next_position

    paragraph_data = extract_text_and_links(paragraph)
    text_parts = paragraph_data["text"]
    hyperlinks = paragraph_data["hyperlinks"]

    if "title" in style_name:
        style = "title"
    else:
        heading_pattern = r"heading ([1-6])"
        heading_match = re.search(heading_pattern, style_name)

        if heading_match:
            style = f"heading {heading_match.group(1)}"
        else:
            logger.error(f"Неподдерживаемый стиль заголовка: {style_name}.")
            raise ValueError(f"Неподдерживаемый стиль заголовка: {style_name}.")

    return {
        "type": element_type,
        "position": position,
        "text": text_parts.strip(),
        "style": style,
        "hyperlinks": hyperlinks,
    }


def extract_title(paragraph, next_position):
    """Метод извлечения названия документа."""

    element_type = "title"
    position = next_position

    paragraph_data = extract_text_and_links(paragraph)
    text_parts = paragraph_data["text"]
    hyperlinks = paragraph_data["hyperlinks"]

    return {
        "type": element_type,
        "position": position,
        "text": text_parts.strip(),
        "hyperlinks": hyperlinks,
    }


def extract_list_info(paragraph, next_position):
    """Метод извлечения элемента списка."""

    num_pr = paragraph._p.pPr.find(qn('w:numPr'))

    element_type = "list_item"
    position = next_position

    paragraph_data = extract_text_and_links(paragraph)
    text_parts  = paragraph_data["text"]
    hyperlinks = paragraph_data["hyperlinks"]

    list_id = int(num_pr.find(qn("w:numId")).val)
    ilvl = num_pr.find(qn("w:ilvl"))
    list_level = int(ilvl.val) if ilvl is not None else 0

    return {
        "type": element_type,
        "position": position,
        "text": text_parts,
        "hyperlinks": hyperlinks,
        "list_id": list_id,
        "list_level": list_level
    }


def extract_paragraph(paragraph, next_position):
    """Метод извлечения абзаца."""

    element_type = "paragraph"
    position = next_position
    paragraph_data = extract_text_and_links(paragraph)
    text_parts = paragraph_data["text"]
    hyperlinks = paragraph_data["hyperlinks"]

    return {
        "type": element_type,
        "position": position,
        "text": text_parts,
        "hyperlinks": hyperlinks
    }


def extract_table(table, next_position):
    """Метод извлечения таблицы."""

    rows = []

    for row in table.rows:
        row_data = []

        for cell in row.cells:
            cell_data = []
            for paragraph in cell.paragraphs:
                paragraph_data = extract_text_and_links(paragraph)
                cell_data.append(paragraph_data)
            row_data.append(cell_data)
        rows.append(row_data)

    return {
        "type": "table",
        "position": next_position,
        "rows": rows
    }


def extract_text_and_links(paragraph):
    """Метод извлечения текста и гиперссылок из абзаца."""

    text_parts = ""
    hyperlinks = []

    for elem in paragraph.iter_inner_content():
        if isinstance(elem, Run):
            text_parts += elem.text

        elif isinstance(elem, Hyperlink):
            link_text = elem.text
            link_url = elem.url

            text_parts += f"[{link_text}]({link_url})"

            hyperlinks.append({
                "text": link_text,
                "url": link_url
            })

    return {
        "text": text_parts,
        "hyperlinks": hyperlinks
    }