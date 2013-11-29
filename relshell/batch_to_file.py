# -*- coding: utf-8 -*-
"""
    relshell.batch_to_file
    ~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides {batch => file for process input} translations
"""
from os import fdopen
from relshell.batch_to_from_file import BatchToFromFile


class BatchToFile(BatchToFromFile):
    """Batch => process input file translator"""

    def __init__(self, file_type):
        """Constructor

        :param file_type: 'TMPFILE' or 'STDIN'
        """
        if file_type not in ('TMPFILE', 'STDIN'):  # pragma: no cover
            raise NotImplementedError("Only 'TMPFILE' or 'STDIN' are supported")
        BatchToFromFile.__init__(self, file_type)

    def is_stdin(self):
        return self._type == 'STDIN'

    def write_stdin(self, stdin, batch_str):
        stdin.write(batch_str)
        stdin.flush()
        self._stdin = stdin

    def write_tmpfile(self, batch_str):
        (fd, path) = self._tmpfile
        with fdopen(fd, 'w') as f:
            f.write(batch_str)

    def finish(self):
        if self._type == 'STDIN':
            self._stdin.close()  # sending 'EOF'
        elif self._type == 'TMPFILE':
            self._rm_tmpfile()
        else:  # pragma: no cover
            assert False
