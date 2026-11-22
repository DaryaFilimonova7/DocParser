from contextlib import nullcontext

from document_processor import process_document
import logging
import logs.logger
logger = logging.getLogger(__name__)



print("-" * 80)
print(f"{' ' * 25}Specification Doc Parser")
print(f"{' ' * 10}Помогает преобразовать DOCX спецификации в Markdown файлы")
print("-" * 80)
print("")

print("Выберите источник документа:")
print("1 - Google Docs")
print("2 - Локальный DOCX")

source_choice = input(">> ")
print("")

doc_url = None
file_path = None

if source_choice == "1":
    print("Введите ссылку на Google Doc")
    doc_url = input(">> ")
elif source_choice == "2":
    print("Укажите путь к DOCX-файлу")
    file_path = input(">> ")
else:
    print("Такой опции нет.")

print("")

try:
    process_document(file_path, doc_url, source_choice)
except Exception:
    logger.error("Обработка файла прервана.")
    print("Не удалось обработать документ. Проверьте файл и журнал ошибок. ")