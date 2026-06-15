import logging
import os
from logging.handlers import RotatingFileHandler

def get_logger(nombre: str, log_file: str = "logs/pipeline.log") -> logging.Logger:
    """
    Crea/obtiene un logger con:
    - Consola (INFO)
    - Archivo rotativo (DEBUG) con rotación por tamaño
    """
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    logger = logging.getLogger(nombre)

    # Evita duplicar handlers si se llama más de una vez
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Consola
    sh = logging.StreamHandler()
    sh.setLevel(logging.INFO)
    sh.setFormatter(fmt)

    # Archivo (rotativo)
    fh = RotatingFileHandler(
        log_file,
        maxBytes=2_000_000,   # ~2MB
        backupCount=5,
        encoding="utf-8"
    )
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)

    logger.addHandler(sh)
    logger.addHandler(fh)

    return logger