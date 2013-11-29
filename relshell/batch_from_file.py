# -*- coding: utf-8 -*-
"""
    relshell.batch_from_file
    ~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides {file for process output => batch} translations
"""
from os import fdopen
from relshell.batch_to_from_file import BatchToFromFile


class BatchFromFile(BatchToFromFile):
    """Process output file => batch translator"""

    def __init__(self, file_type):
        """Constructor

        :param file_type: 'TMPFILE' or 'STDOUT'
        """
        if file_type not in ('TMPFILE', 'STDOUT'):  # pragma: no cover
            raise NotImplementedError("Only 'TMPFILE' or 'STDOUT' are supported")
        BatchToFromFile.__init__(self, file_type)

    def is_stdout(self):
        return self._type == 'STDOUT'

    def read_stdout(self, stdout):
        self._stdout = stdout
        stdout.flush()
        return stdout.read()  # [fix] - arg is needed not for waiting EOF

    def read_tmpfile(self):
        (fd, path) = self._tmpfile
        with fdopen(fd, 'r') as f:
            return f.read()

    def finish(self):
        if self._type == 'STDOUT':
            self._stdout.close()
        elif self._type == 'TMPFILE':
            self._rm_tmpfile()
        else:  # pragma: no cover
            assert False
