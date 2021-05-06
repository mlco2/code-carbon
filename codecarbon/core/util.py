from contextlib import contextmanager
import logging

logger = logging.getLogger("codecarbon")


@contextmanager
def suppress(*exceptions):
    try:
        yield
    except exceptions:
        logger.info(exceptions, exc_info=True)
        pass


def set_log_level(level: str):
    level = level.upper()
    levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
    assert level in levels

    for lev in levels:
        if level == lev:
            logger.setLevel(getattr(logging, level))
            return
    logger.error(f"Unknown log level: {level}")
