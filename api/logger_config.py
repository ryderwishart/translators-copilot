from loguru import logger
import sys

class CustomColors:
    CRITICAL = "red"
    ERROR = "red"
    WARNING = "yellow"
    SUCCESS = "green"
    INFO = "blue"
    DEBUG = "magenta"

log_format = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
    "<level>{message}</level>"
)

logger.remove()
logger.add(sys.stderr, format=log_format, level="DEBUG", colorize=True, diagnose=False,
    enqueue=True, backtrace=True,
    filter=lambda record: record["level"].name == "DEBUG")

logger.level("CRITICAL", color="<red>")
logger.level("ERROR", color="<red>")
logger.level("WARNING", color="<yellow>")
logger.level("SUCCESS", color="<green>")
logger.level("INFO", color="<blue>")
logger.level("DEBUG", color="<magenta>")

