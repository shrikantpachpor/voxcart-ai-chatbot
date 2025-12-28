import logging
import os
from fastapi import FastAPI

logger = logging.getLogger("myapp")
log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
logger.setLevel(getattr(logging, log_level, logging.INFO))

log_file = os.getenv('LOG_FILE', 'app.log')
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(getattr(logging, log_level, logging.INFO))

console_handler = logging.StreamHandler()
console_handler.setLevel(getattr(logging, log_level, logging.INFO))

formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
)

file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)


