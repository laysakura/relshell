# -*- coding: utf-8 -*-
"""
    relshell.shelloperator
    ~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides `ShellOperator`
"""
from relshell.cmdparser import parse


class ShellOperator(object):
    """ShellOperator"""

    def __init__(
        self,
        cmd,
        out_record_def,
        terminator='EOF',
    ):
        # check
        _chk_terminator(terminator)

        #set
        self._cmddict = parse(cmd)
        self._out_recdef = out_record_def
        self._terminator = terminator

    def run(self, in_batch):
        return in_batch


def _chk_terminator(terminator):
    if terminator != 'EOF':
        raise NotImplementedError('Invalid terminator: %s' % terminator)
