from pathlib import Path
import logging
logger = logging.getLogger(__name__)


project_root = Path(__file__).resolve().parent.parent
result_dir = project_root / "result"


def export_markdown(md_structure):
    """Метод для экспорта данных в Markdown файл"""
    logger.info("Запуск экспорта данных в файл Markdown формата.")

    result_dir.mkdir(parents=True, exist_ok=True)

    md_path = result_dir / "interface_spec.md"
    md_path.write_text(md_structure, encoding="utf-8")

    logger.info(f"Markdown файл успешно сохранен: {md_path}")
