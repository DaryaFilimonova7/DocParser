from document_processor import process_document
import logging
import logs.logger
logger = logging.getLogger(__name__)



print("-" * 80)
print(f"{' ' * 25}Specification Doc Parser")
print(f"{' ' * 10}Помогает преобразовать DOCX спецификации в Markdown файлы")
print("-" * 80)
print("")

print("Укажите путь к DOCX-файлу")
file_path = input(">> ")
print("")

try:
    process_document(file_path)
except Exception:
    logger.error("Обработка файла прервана.")
    print("Не удалось обработать документ. Проверьте файл и журнал ошибок. ")