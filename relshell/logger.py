# -*- coding: utf-8 -*-
"""
    relshell.logger
    ~~~~~~~~~~~~~~~

    :synopsis: Provides pretty colorful logger.
"""
import sys
import logging
from rainbow_logging_handler import RainbowLoggingHandler


def get_logger(loglevel=logging.DEBUG, stream=sys.stderr):
    """Returns logger"""
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    handler   = RainbowLoggingHandler(stream)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)
    logger = logging.getLogger('logger')
    logger.setLevel(loglevel)
    return logger
