# -*- coding: utf-8 -*-
"""
    relshell.in_batch_source
    ~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides {batch => process input} translations
"""
from os import fdopen, remove
from tempfile import mkstemp


class InBatchSource(object):
    """InBatchSource"""

    def __init__(self, batch_src_type):
        """Constructor

        :param batch_src_type: 'TMPFILE' or 'STDIN'
        """
        if batch_src_type not in ('TMPFILE', 'STDIN'):
            raise NotImplementedError("Only 'TMPFILE' or 'STDIN' are supported")
        self._type = batch_src_type

        if self._type == 'TMPFILE':
            self._tmpfile = mkstemp(prefix='relshell-', suffix='.batch')  # [todo] - Use memory file system for performance

    def from_stdin(self):
        return self._type == 'STDIN'

    def from_tmpfile(self):
        return self._type == 'TMPFILE'

    def tmpfile_path(self):
        (fd, path) = self._tmpfile
        return path

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
            (fd, path) = self._tmpfile
            remove(path)
        else:  # pragma: no cover
            assert False
