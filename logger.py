import os
import logging


logger = logging.getLogger("varta_logger")
logger.setLevel('DEBUG')

logger_handler = logging.FileHandler(os.path.join(os.getcwd(), 'log_varta.log'))  # level=NONSET=0

logger_formatter = logging.Formatter('{asctime} - {levelname} - {message}', datefmt='%Y-%m-%d %H:%M:%S', style="{")
logger_handler.setFormatter(logger_formatter)

logger.addHandler(logger_handler)

