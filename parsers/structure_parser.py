import re
import logging
logger = logging.getLogger(__name__)


def parse_structure(doc_elements):
    """Метод восстановления структуры документа."""
    logger.info("Начало процесса восстановления структуры документа.")

    doc_structure = {
        "intro": [],
        "title": None,
        "elements": [],
        "sections": []
    }

    current_level = {
        "1": {},
        "2": {},
        "3": {},
        "4": {},
        "5": {},
        "6": {}
    }

    for element in doc_elements:
        # Поиск названия документа и элементов перед ним
        if doc_structure["title"] is None:
            if element["type"] != "title":
                doc_structure["intro"].append(element)
            else:
                doc_structure["title"] = element

        # Определение иерархии заголовков и распределение элементов по разделам
        else:
            if element["type"] == "heading":

                level_search = re.search(r"heading ([1-6])", element["style"])
                if not level_search:
                    continue
                level = int(level_search.group(1))
                new_section = create_section(element, level)

                parent_level = level - 1

                while parent_level >= 1:
                    if current_level[str(parent_level)]:
                        current_level[str(parent_level)]["children"].append(new_section)
                        break
                    parent_level -= 1

                else:
                    doc_structure["sections"].append(new_section)

                current_level[str(level)] = new_section

                for key in current_level:
                    if int(key) > level:
                        current_level[key] = {}

            elif element["type"] in ["paragraph", "table", "list_item"]:

                active_level = 6
                while active_level >= 1:
                    if current_level[str(active_level)]:
                        current_level[str(active_level)]["elements"].append(element)
                        break
                    active_level -= 1
                else:
                    doc_structure["elements"].append(element)

    if doc_structure["title"] is None:
        logger.error(f"В документе не найдено название. Проверьте оформление заголовка документа.")
        raise ValueError("В документе не найдено название.")

    logger.info("Структура документа успешно построена.")
    return doc_structure


def create_section(element, level):
    """Создание новой секции в иерархии заголовков."""
    new_section = {
        "position": element["position"],
        "type": element["type"],
        "text": element["text"],
        "hyperlinks": element["hyperlinks"],
        "level": level,
        "elements": [],
        "children": []
    }
    return new_section
