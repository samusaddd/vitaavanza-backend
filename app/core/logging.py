from loguru import logger
import sys

logger.remove()
logger.add(sys.stdout, level="INFO", backtrace=True, diagnose=True)

def get_logger(name: str = "vitaavanza"):
    return logger.bind(service=name)
