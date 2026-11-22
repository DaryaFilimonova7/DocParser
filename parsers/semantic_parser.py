import re
from config.control_types import CONTROL_TYPE_REFERENCE
import logging
logger = logging.getLogger(__name__)


def parse_sections(doc_structure):
    """Метод поиска содержимого разделов Контролы, Локальные справочники, Колонки."""
    logger.info("Запуск семантического анализа.")

    doc_sections = {
        "panels": [],
        "table_columns": [],
        "dictionaries": []
    }

    for section in doc_structure["sections"]:
        find_section_name(section, "Контролы", doc_sections["panels"])
        find_section_name(section, "Колонки", doc_sections["table_columns"])
        find_section_name(section, "Локальные справочники", doc_sections["dictionaries"])

    doc_sections = {
        "panels": parse_controls(doc_sections["panels"]),
        "table_columns": parse_columns(doc_sections["table_columns"]),
        "dictionaries": parse_dictionaries(doc_sections["dictionaries"])
    }

    logger.info(f"Cемантический анализ завершен. Найдено {len(doc_sections["panels"])} панелей контролов, {len(doc_sections["table_columns"])} таблиц, {len(doc_sections["dictionaries"])} локальных справочников.")
    return doc_sections


def find_section_name(section, section_name, results):
    """Метод рекурсивного поиска элементов раздела по названию."""
    if section["text"].strip() == section_name:
        results.append({
                "parent_section": section["text"],
                "elements": section["children"]
            })

    elements = section["elements"]

    for index, element in enumerate(elements):
        if element["type"] == "paragraph" and element["text"].strip() == section_name:
            results.append({
                "parent_section": section["text"],
                "elements": elements[index + 1:]
            })

    for child in section["children"]:
        find_section_name(child, section_name, results)



def parse_controls(doc_controls):
    """Метод распознавания контролов и их свойств."""
    panels = []

    for doc_section in doc_controls:
        controls = []

        for control_data in doc_section["elements"]:
            if control_data["type"] != "list_item":
                continue

            control_name, name_start, name_end = extract_control_name(control_data)
            control_type = extract_control_type(control_data)
            control_required, required_start, required_end = extract_control_required(control_data)
            control_default_value, default_start, default_end = extract_control_default(control_data)

            excluded_ranges = []
            if name_start is not None and name_end is not None:
                excluded_ranges.append((name_start, name_end))
            if required_start is not None and required_end is not None:
                excluded_ranges.append((required_start, required_end))
            if default_start is not None and default_end is not None:
                excluded_ranges.append((default_start, default_end))
            control_description = extract_control_description(control_data, control_type, excluded_ranges)

            control = {
                "Name": control_name,
                "Type": control_type,
                "Description": control_description,
                "Required": control_required,
                "Default": control_default_value,
                "Position": control_data["position"]
            }
            controls.append(control)

        panels.append({
            "Name": doc_section["parent_section"],
            "Controls": controls
        })

    return panels




def extract_control_name(control_data):
    """Метод извлечения имени контрола."""
    text = control_data["text"]

    sentence_end_pattern = r"[.]\s+[А-ЯЁA-Z]"
    sentence_end = re.search(sentence_end_pattern, text)

    if sentence_end:
        first_sentence = text[:sentence_end.start() + 1]
    else:
        first_sentence = text

    name_pattern = r"^(.+?)\s*[-–—:]\s"
    name = re.search(name_pattern, first_sentence)
    if name:
        return name.group(1).strip(), name.start(), name.end()
    return None, None, None


def extract_control_type(control_data):
    """Метод извлечения типа контрола."""
    control_types = CONTROL_TYPE_REFERENCE

    text = control_data["text"]
    first_match = None
    first_match_position = len(text)
    first_match_len = 0

    for control_type, patterns in control_types.items():
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)

            if match and (
                    match.start() < first_match_position
                    or (match.start() == first_match_position and len(match.group()) > first_match_len)
            ):
                first_match_position = match.start()
                first_match_len = len(match.group())
                first_match = control_type

    if first_match is None:
        return None

    additional_type = extract_additional_type(text, first_match_position)
    if additional_type:
        return f"{first_match} {additional_type}"

    return first_match


def extract_additional_type(text, start_position):
    """Метод извлечения подтипа и свойства контрола."""
    text = text[start_position:]
    additional_info_patterns = [
        r"с типом\s+([a-zA-Z_.]+)",
        r"типа\s+([a-zA-Z_.]+)",
        r"со свойством\s+([a-zA-Z_.]+)"
    ]

    additional_info = []
    for pattern in additional_info_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            additional_info.append(match.group())

    return " ".join(additional_info)


def extract_control_required(control_data):
    """Метод излвечения обязательности контрола."""
    text = control_data["text"].lower()
    required_patterns = [
        r"контрол\s+обязател[а-яё]{1,5}\s+для\s+заполнен[а-яё]{1,3}",
        r"обязател[а-яё]{1,5}\s+для\s+заполнен[а-яё]{1,3}",
        r"является\s+обязател[а-яё]{1,5}",
        r"обязател[а-яё]{1,5}\s+поле",
        r"обязател[а-яё]{1,5}\s+контрол",
        r"обязател[а-яё]{1,5}"
    ]
    optional_patterns = [
        r"контрол\s+не(?:\s+)?обязател[а-яё]{1,5}\s+для\s+заполнен[а-яё]{1,3}",
        r"не(?:\s+)?обязател[а-яё]{1,5}\s+для\s+заполнен[а-яё]{1,3}",
        r"является\s+не(?:\s+)?обязател[а-яё]{1,5}",
        r"не(?:\s+)?обязател[а-яё]{1,5}\s+поле",
        r"не(?:\s+)?обязател[а-яё]{1,5}\s+контрол",
        r"не(?:\s+)?обязател[а-яё]{1,5}"
    ]

    for pattern in optional_patterns:
        match = re.search(pattern, text)
        if match:
            end = match.end()
            while end < len(text) and text[end] in ".,":
                end += 1
            return False, match.start(), end

    for pattern in required_patterns:
        match = re.search(pattern, text)
        if match:
            end = match.end()
            while end < len(text) and text[end] in ".,":
                end += 1
            return True, match.start(), end

    return None, None, None


def extract_control_default(control_data):
    """Метод поиска значения по умолчанию для контрола."""
    text = control_data["text"]

    default_value_patterns = (
        r"(?:значение\s+)?по\s+умолчанию"
        r"(?!\s+(?:не\s+)?(?:отобража[а-яё]*|обязательн[а-яё]*))"
        r"\s*[:\-]?\s*[^.!?\n]+")

    match = re.search(default_value_patterns, text, re.IGNORECASE)

    if not match:
        return None, None, None

    end = match.end()
    while end < len(text) and text[end] in ".,":
        end += 1

    return match.group(), match.start(), end


def extract_control_description(control_data, control_type, excluded_ranges):
    """Метод извлечения описания контрола."""
    text = control_data["text"]

    for start, end in sorted(excluded_ranges, reverse=True):
        text = text[:start] + text [end:]

    if text:
        if control_type:
            text = re.sub(re.escape(control_type), "", text, flags=re.IGNORECASE)
        extra_spaces_pattern = r"\s{2,}"
        text = re.sub(extra_spaces_pattern, " ", text).strip()
        dash_and_colon_pattern = r"^\s*[-–—:]+\s*"
        text = re.sub(dash_and_colon_pattern, "", text)
        extra_words_pattern = r"(?i)\bконтрол\s*[.]"
        text = re.sub(extra_words_pattern, "", text)
        text = text.strip()
        if text:
            if text[0] == "[":
                description = text[0] + text[1].upper() + text[2:]
            else:
                description = text[0].upper() + text[1:]
            return description

    return None



def parse_columns(doc_columns):
    """Метод распознавания колонок и их свойств."""
    tables = []

    for doc_section in doc_columns:
        columns = []

        for column_data in doc_section["elements"]:
            if column_data["text"] == "Возможности таблицы":
                break
            if column_data["type"] != "list_item":
                continue

            column_name, name_start, name_end = extract_column_name(column_data)
            column_type, type_start, type_end = extract_column_type(column_data)

            excluded_ranges = []
            if name_start is not None and name_end is not None:
                excluded_ranges.append((name_start, name_end))
            if type_start is not None and type_end is not None:
                excluded_ranges.append((type_start, type_end))
            column_description = extract_column_description(column_data, excluded_ranges)

            column = {
                "Name": column_name,
                "Data_type": column_type,
                "Description": column_description,
                "Position": column_data["position"]
            }
            columns.append(column)

        tables.append({
            "Name": doc_section["parent_section"],
            "Columns": columns
        })

    return tables


def extract_column_name(column_data):
    """Метод извлечения имени колонки."""
    text = column_data["text"]

    sentence_end_pattern = r"[.]\s+[А-ЯЁA-Z]"
    sentence_end = re.search(sentence_end_pattern, text)

    if sentence_end:
        first_sentence = text[:sentence_end.start() + 1]
    else:
        first_sentence = text

    name_pattern = r"^(.+?)\s*[-–—:]\s"
    name = re.search(name_pattern, first_sentence)
    if name:
        return name.group(1).strip(), name.start(), name.end()
    return None, None, None


def extract_column_type(column_data):
    """Метод извлечения типа данных колонки."""
    text = column_data["text"]

    data_type_patterns = [
        r"тип данных\s*[-–—:]\s*([а-яёa-z_]+)",
        r"([а-яёa-z_]+)\s+тип данных"
    ]

    for pattern in data_type_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            end = match.end()
            while end < len(text) and text[end] in ".,":
                end += 1
            data_type = match.group(1)[0].upper() + match.group(1)[1:]
            return data_type, match.start(), end

    return None, None, None


def extract_column_description(column_data, excluded_ranges):
    """Метод извлечения описания колонки."""
    text = column_data["text"]

    for start, end in sorted(excluded_ranges, reverse=True):
        text = text[:start] + text [end:]

    extra_spaces_pattern = r"\s{2,}"
    text = re.sub(extra_spaces_pattern, " ", text).strip()
    dash_and_colon_pattern = r"^\s*[-–—:]+\s*"
    text = re.sub(dash_and_colon_pattern, "", text)
    text = text.strip()
    if text:
        description = text[0].upper() + text[1:]
        return description

    return None



def parse_dictionaries(doc_dictionaries):
    """Метод распознавания локальных справочников."""
    dictionaries = []

    for doc_section in doc_dictionaries:
        for dictionary_data in doc_section["elements"]:
            if dictionary_data["type"] != "heading":
                continue
            dictionary_values = []

            for doc_value in dictionary_data["elements"]:
                if doc_value["type"] != "list_item":
                    continue

                dict_value_name, dict_value_start, dict_value_end = extract_dict_value_name(doc_value)

                excluded_ranges = []
                if dict_value_start is not None and dict_value_end is not None:
                    excluded_ranges.append((dict_value_start, dict_value_end))
                dict_value_description = extract_dict_value_description(doc_value, excluded_ranges)

                dictionary_value = {
                    "Name": dict_value_name,
                    "Description": dict_value_description,
                    "Position": doc_value["position"],
                }
                dictionary_values.append(dictionary_value)

            dictionary = {
                "Name": dictionary_data["text"],
                "Values": dictionary_values
            }
            dictionaries.append(dictionary)

    return dictionaries


def extract_dict_value_name(dictionary_data):
    """Метод извлечения имени значения справочника."""
    text = dictionary_data["text"]

    sentence_end_pattern = r"[.]\s+[А-ЯЁA-Z]"
    sentence_end = re.search(sentence_end_pattern, text)

    if sentence_end:
        first_sentence = text[:sentence_end.start() + 1]
    else:
        first_sentence = text

    name_pattern = r"^(.+?)\s*[-–—:]\s"
    name = re.search(name_pattern, first_sentence)
    if name:
        return name.group(1).strip(), name.start(), name.end()
    return None, None, None


def extract_dict_value_description(dictionary_data, excluded_ranges):
    """Метод извлечения описания значения справочника."""
    text = dictionary_data["text"]

    for start, end in sorted(excluded_ranges, reverse=True):
        text = text[:start] + text [end:]

    extra_spaces_pattern = r"\s{2,}"
    text = re.sub(extra_spaces_pattern, " ", text).strip()
    dash_and_colon_pattern = r"^\s*[-–—:]+\s*"
    text = re.sub(dash_and_colon_pattern, "", text)
    text = text.strip()
    if text:
        description = text[0].upper() + text[1:]
        return description

    return None