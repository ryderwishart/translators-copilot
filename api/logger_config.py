import logging

class CustomColors:
    CRITICAL = "\033[1;31m"  # Bright Red
    ERROR = "\033[0;31m"    # Red
    WARNING = "\033[1;33m"  # Bright Yellow
    INFO = "\033[0;34m"     # Blue
    DEBUG = "\033[0;35m"    # Magenta
    RESET = "\033[0m"       # Reset

LOG_COLORS = {
    'CRITICAL': CustomColors.CRITICAL,
    'ERROR': CustomColors.ERROR,
    'WARNING': CustomColors.WARNING,
    'INFO': CustomColors.INFO,
    'DEBUG': CustomColors.DEBUG,
}

class ColoredFormatter(logging.Formatter):
    def format(self, record):
        log_msg = logging.Formatter.format(self, record)
        return LOG_COLORS.get(record.levelname, CustomColors.RESET) + log_msg + CustomColors.RESET

# Create a console handler with a custom format
console_handler = logging.StreamHandler()
console_handler.setFormatter(ColoredFormatter())

# Get the "uvicorn.access" logger and configure it
access_logger = logging.getLogger('uvicorn.access')
access_logger.handlers = [console_handler]

# Get the "uvicorn" logger and configure it
uvicorn_logger = logging.getLogger('uvicorn')
uvicorn_logger.handlers = [console_handler]

def setup_logger(name, level=logging.DEBUG):
    handler = logging.StreamHandler()
    handler.setFormatter(ColoredFormatter())

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.handlers = [handler]

    return logger

access_logger = setup_logger('uvicorn.access')
uvicorn_logger = setup_logger('uvicorn')
