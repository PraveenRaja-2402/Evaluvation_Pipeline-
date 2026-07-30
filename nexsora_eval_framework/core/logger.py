import logging
import os
import sys

VERBOSE_LEVEL_NUM = 15

def add_verbose_level():
    logging.VERBOSE = VERBOSE_LEVEL_NUM
    logging.addLevelName(VERBOSE_LEVEL_NUM, "VERBOSE")

    def verbose(self, message, *args, **kws):
        if self.isEnabledFor(VERBOSE_LEVEL_NUM):
            self._log(VERBOSE_LEVEL_NUM, message, args, **kws)

    logging.Logger.verbose = verbose

add_verbose_level()

def setup_logger(name: str = "nexsora_eval", log_level: str = "INFO", log_file: str = None) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)  # Capture all logs at logger level, filter at handlers

    # Prevent duplicate handlers if re-initialized
    if logger.hasHandlers():
        logger.handlers.clear()

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    level = getattr(logging, log_level.upper(), logging.INFO)
    console_handler.setLevel(level)

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File Handler
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)  # Log everything to file for debugging
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger