import re
from datetime import date
import logging
logger = logging.getLogger(__name__)


def build_md_structure(doc_structure, doc_sections, config):
    """Метод преобразования данных в строку Markdown структуры. """
    logger.info("Начало преобразования данных в Markdown формат.")

    title = f"# {doc_structure['title']['text']}"
    header = build_header(doc_structure, config)
    related_documents = build_related_documents(config)
    table_of_contents = build_table_of_contents(doc_structure["sections"])
    doc_content = build_doc_content(doc_structure, doc_sections)

    md_lines = [
        title,
        header,
        related_documents,
        table_of_contents,
        doc_content
    ]

    md_text = "\n\n".join(section for section in md_lines if section)

    logger.info("Данные преобразованы в Markdown формат.")

    return md_text


def build_header(doc_structure, config):
    """Метод сборки шапки документа. """
    md_lines = []

    md_title = f"**Название:**  {doc_structure['title']['text']}"
    md_title = re.sub("\n", " ", md_title)
    md_lines.append(md_title)

    md_status = "**Статус:**  `Draft`"
    md_lines.append(md_status)

    md_version = "**Версия:**  1.0"
    md_lines.append(md_version)

    md_owner = f"**Owner:**  {config['owner']}"
    md_lines.append(md_owner)

    md_type = f"**Тип документа:**  {config['document_type']}"
    md_lines.append(md_type)

    md_lines.append("")

    headers = ["История изменений", "Версия", "Что изменилось"]
    creation_date = date.today().strftime("%Y-%m-%d")
    rows = [[f"{creation_date}", "1.0", "Первая версия"]]

    md_history = build_table(headers, rows)
    md_lines.append(md_history)

    return "\n".join(md_lines)


def build_related_documents(config):
    """Метод сборки таблицы связанных документов. """
    headers = ["Связанный документ", "Версия", "Ссылка"]
    rows = []

    for document in config["related_documents"]:
        rows.append([document["name"], document["version"], f"[link]({document['url']})"])

    related_documents = build_table(headers, rows)

    return related_documents


def build_table_of_contents(sections):
    """Метод сборки оглавления документа. """
    toc_lines = ["## Содержание", ""]
    for section in sections:
        toc_lines.extend(build_toc_section(section))

    return "\n".join(toc_lines)


def build_toc_section(section):
    """Метод создания оглавления по заголовкам. """
    md_lines = []
    level = section["level"]
    header = section["text"]

    indent = "  " * (level - 1)

    md_lines.append(f"{indent}- [[#{header}|{header}]]")

    for child in section["children"]:
        md_lines.extend(
            build_toc_section(child)
        )

    return md_lines



def build_doc_content(doc_structure, doc_sections):
    """Метод сборки содержимого документа. """
    md_lines = []

    replacements = prepare_replacements(doc_sections)

    # Обработка текста перед заголовком
    doc_intro = doc_structure["intro"]
    for intro in doc_intro:
        md_lines.append(intro["text"])

    # Обработка текста после заголовка
    doc_elements = doc_structure["elements"]
    for element in doc_elements:
        md_lines.append(element["text"])
        md_lines.append("")

    # Обработка содержимого разделов
    md_lines.extend(
        build_sections(doc_structure["sections"], replacements)
    )

    return "\n".join(md_lines)


def prepare_replacements(doc_sections):
    """Метод подготовки контролов, колонок и значений локальных справочников к замене."""
    replacements = []

    for section in doc_sections["table_columns"]:
        positions = []
        for column in section["Columns"]:
            positions.append(int(column["Position"]))
        replacements.append({
            "type": "table_columns",
            "positions": positions,
            "name": section["Name"],
            "data": section["Columns"]
        })

    for section in doc_sections["panels"]:
        positions = []
        for control in section["Controls"]:
            positions.append(int(control["Position"]))
        replacements.append({
            "type": "panels",
            "positions": positions,
            "name": section["Name"],
            "data": section["Controls"]
        })

    for section in doc_sections["dictionaries"]:
        positions = []
        for value in section["Values"]:
            positions.append(int(value["Position"]))
        replacements.append({
            "type": "dictionaries",
            "positions": positions,
            "name": section["Name"],
            "data": section["Values"]
        })

    return replacements


def build_sections(sections, replacements):
    """Метод обработки разделов."""
    md_lines = []

    for section in sections:
        # Заголовок раздела
        md_lines.append(f"{'#' * (section['level'] + 1)} {section['text']}")

        # Элементы внутри раздела
        md_lines.extend(
            build_elements(section["elements"], replacements)
        )

        # Вложенные разделы
        md_lines.extend(
            build_sections(section["children"], replacements)
        )

    return md_lines


def build_elements(elements, replacements):
    """Метод обработки элементов раздела."""
    md_lines = []

    for element in elements:
        replacement = None

        # Поиск блоков замены
        for item in replacements:
            if element["position"] in item["positions"]:
                replacement = item
                break
        if replacement:
            if element["position"] == replacement["positions"][0]:
                md_replacement_table = build_replacement_table(replacement)
                md_lines.append(md_replacement_table)
            continue

        # Поведение для незаменяемых элементов
        if element["type"] == "paragraph":
            md_lines.append(element["text"])
            md_lines.append("")

        elif element["type"] == "list_item":
            indent = "  " * element["list_level"]
            md_lines.append(f"{indent}- {element['text']}")

        elif element["type"] == "table":
            md_table = build_original_table(element)
            md_lines.append(md_table)
            md_lines.append("")

    return md_lines


def build_table(headers, rows):
    """Метод сборки таблицы."""
    md_lines = [
        "| " + "|".join(headers) + " |",
        "| " + "|".join(["---"] * len(headers)) + " |",
    ]

    for row in rows:
        escaped_row = [character_escaping(cell) for cell in row]
        md_lines.append("| " + "|".join(escaped_row) + " |")

    return "\n".join(md_lines)


def character_escaping(value):
    """Метод экранирования символов."""
    if value is None:
        return "-"

    value = str(value)
    value = value.replace("\\", "\\\\")
    value = value.replace("|", "\\|")
    value = value.replace("\n", "<br>")

    return value


def build_replacement_table(replacement):
    if replacement["type"] == "panels":
        return build_controls_table(replacement["data"])
    elif replacement["type"] == "table_columns":
        return build_columns_table(replacement["data"])
    elif replacement["type"] == "dictionaries":
        return build_dictionaries_tables(replacement["data"])
    else:
        return None


def build_controls_table(controls):
    """Метод преобразования данных о контролах в md таблицу."""

    headers = ["Имя", "Тип", "Описание", "Обяз.", "По умолчанию"]
    rows = []
    for control in controls:

        if control["Required"] is True:
            required = "Да"
        elif control["Required"] is False:
            required = "Нет"
        else:
            required = "-"

        row = [
            control["Name"],
            control["Type"],
            control["Description"],
            required,
            control["Default"]
        ]
        rows.append(row)

    return build_table(headers, rows)


def build_columns_table(columns):
    """Метод преобразования данных о колонках в md таблицу."""

    headers = ["Имя", "Тип данных", "Описание"]
    rows = []

    for column in columns:

        row = [
            column["Name"],
            column["Data_type"],
            column["Description"]
        ]
        rows.append(row)

    return build_table(headers, rows)


def build_dictionaries_tables(values):
    """Метод преобразования данных о локальном справочнике в md таблицу."""

    headers = ["Значение", "Описание"]
    rows = []

    for value in values:

        row = [
            value["Name"],
            value["Description"]
        ]
        rows.append(row)

    return build_table(headers, rows)


def build_original_table(table_data):
    """Метод преобразования исходных таблиц DOCX в Markdown формат."""
    original_rows = table_data["rows"]

    rows = []

    for row in original_rows:
        row_data = []

        for cell in row:
            cell_text = ""

            for element in cell:
                cell_text += element["text"]

            row_data.append(cell_text)
        rows.append(row_data)

    if not rows:
        return ""

    headers = rows[0]
    other_rows = rows[1:]

    return build_table(headers, other_rows)