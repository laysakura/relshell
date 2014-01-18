# -*- coding: utf-8 -*-
"""
    relshell.logger
    ~~~~~~~~~~~~~~~

    :synopsis: Provides logger
"""
import sys
import logging
from rainbow_logging_handler import RainbowLoggingHandler


class Logger(object):
    """Provides logger"""

    _instance = None

    def __init__(self):
        """
        .. warn::
            Do not use this function. Use `instance()`.
        """
        self._logger = logging.getLogger('relshell_logger')
        self._logger.setLevel(logging.INFO)
        handler = RainbowLoggingHandler(sys.stderr)
        self._logger.addHandler(handler)

    @staticmethod
    def instance():
        """Returns the logger instance"""
        if Logger._instance is None:
            Logger._instance = Logger()
        return Logger._instance._logger
