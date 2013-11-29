# -*- coding: utf-8 -*-
"""
    relshell.batch_to_from_file
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides abstract BatchToFromFile class
"""
from abc import ABCMeta, abstractmethod
from os import remove
from tempfile import mkstemp


class BatchToFromFile(object):
    """(Abstract) batch <=> process (input|output) translator"""
    __metaclass__ = ABCMeta

    def __init__(self, file_type):
        """Constructor

        :param file_type: one of ('TMPFILE', 'STDIN', 'STDOUT')
        """
        self._type = file_type
        if self._type == 'TMPFILE':
            self._tmpfile = mkstemp(prefix='relshell-', suffix='.batch')  # [todo] - Use memory file system for performance

    def is_tmpfile(self):
        return self._type == 'TMPFILE'

    def tmpfile_path(self):
        assert self._type == 'TMPFILE'
        (fd, path) = self._tmpfile
        return path

    def _rm_tmpfile(self):
        assert(self._type == 'TMPFILE')
        (fd, path) = self._tmpfile
        remove(path)

    @abstractmethod
    def finish(self):  # pragma: no cover
        pass
