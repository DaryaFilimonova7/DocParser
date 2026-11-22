from pathlib import Path
import logging
logger = logging.getLogger(__name__)


PROJECT_ROOT = Path(__file__).resolve().parent.parent
RESULT_DIR = PROJECT_ROOT / "result"


def export_markdown(md_structure):
    """Метод для экспорта данных в Markdown файл"""
    logger.info("Запуск экспорта данных в файл Markdown формата.")

    RESULT_DIR.mkdir(parents=True, exist_ok=True)

    md_path = RESULT_DIR / "interface_spec.md"
    md_path.write_text(md_structure, encoding="utf-8")

    logger.info(f"Markdown файл успешно сохранен: {md_path}")
