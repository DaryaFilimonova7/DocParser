import logging
import sys
from pathlib import Path


log_dir = Path(__file__).resolve().parent
log_file = log_dir / "doc_parser.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding="utf-8"),
        logging.StreamHandler(sys.stdout)
    ]
)