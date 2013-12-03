# -*- coding: utf-8 -*-
"""
    relshell.batch_command
    ~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Parses shell command w/ BATCH management
"""
import shlex
import os
import re
from subprocess import list2cmdline
from relshell.batch_to_file import BatchToFile
from relshell.batch_from_file import BatchFromFile


class BatchCommand(object):
    """BatchCommand"""

    in_batches_pat = re.compile('IN_BATCH(\d+)')
    """Input batches"""

    out_batch_pat  = re.compile('OUT_BATCH')
    """Output batch"""

    def __init__(self, batch_cmd):
        """Constructor

        :param batch_cmd: command string w/ (IN|OUT)_BATCH*.
        """
        (self.sh_cmd, self.batch_to_file_s, self.batch_from_file) = BatchCommand._parse(batch_cmd)

    def has_input_from_stdin(self):
        """Return if any IN_BATCH* is input from stdin to process"""
        for b2f in self.batch_to_file_s:
            if b2f.is_stdin():
                return True
        return False

    @staticmethod
    def _parse(batch_cmd):
        """
        :rtype:   (sh_cmd, batch_to_file_s, batch_from_file)
        :returns: parsed result like below:

        .. code-block:: python

            # when parsing 'diff IN_BATCH0 IN_BATCH1 > OUT_BATCH'
            (
                'diff /tmp/relshell-AbCDeF /tmp/relshell-uVwXyz',
                ( <instance of BatchToFile>, <instance of BatchToFile> )    # (IN_BATCH0, IN_BATCH1)
                'STDOUT',
            )
        """
        cmd_array                    = shlex.split(batch_cmd)
        (cmd_array, batch_to_file_s) = BatchCommand._parse_in_batches(cmd_array)
        (cmd_array, batch_from_file) = BatchCommand._parse_out_batch(cmd_array)
        return (list2cmdline(cmd_array), batch_to_file_s, batch_from_file)

    @staticmethod
    def _parse_in_batches(cmd_array):
        """Find patterns that match to `in_batches_pat` and replace them into `STDIN` or `TMPFILE`.

        :param cmd_array: `shlex.split`-ed command
        :rtype:   ([cmd_array], ( batch_to_file, batch_to_file, ... ) )
        :returns: Modified `cmd_array` and tuple to show how each IN_BATCH is instantiated (TMPFILE or STDIN).
            Returned `cmd_array` drops IN_BATCH related tokens.
        :raises:  `IndexError` if IN_BATCHes don't have sequential ID starting from 0
        """
        res_cmd_array      = cmd_array[:]
        res_batch_to_file_s = []

        in_batches_cmdidx  = BatchCommand._in_batches_cmdidx(cmd_array)
        for batch_id, cmdidx in enumerate(in_batches_cmdidx):
            if cmdidx > 0 and cmd_array[cmdidx - 1] == '<':  # e.g. `< IN_BATCH0`
                res_batch_to_file_s.append(BatchToFile('STDIN'))
                del res_cmd_array[cmdidx], res_cmd_array[cmdidx - 1]

            else:  # IN_BATCHx is TMPFILE
                batch_to_file = BatchToFile('TMPFILE')
                res_batch_to_file_s.append(batch_to_file)
                res_cmd_array[cmdidx] = batch_to_file.tmpfile_path()

        return (res_cmd_array, tuple(res_batch_to_file_s))

    @staticmethod
    def _parse_out_batch(cmd_array):
        """Find patterns that match to `out_batch_pat` and replace them into `STDOUT` or `TMPFILE`.

        :param cmd_array: `shlex.split`-ed command
        :rtype:   ([cmd_array], batch_from_file)
        :returns: Modified `cmd_array` and tuple to show how OUT_BATCH is instantiated (TMPFILE or STDOUT).
            Returned `cmd_array` drops OUT_BATCH related tokens.
        :raises:  `IndexError` if multiple OUT_BATCH are found
        """
        res_cmd_array     = cmd_array[:]
        res_batch_from_file = None

        out_batch_cmdidx = BatchCommand._out_batch_cmdidx(cmd_array)
        if out_batch_cmdidx is None:
            return (res_cmd_array, res_batch_from_file)

        if out_batch_cmdidx > 0 and cmd_array[out_batch_cmdidx - 1] == '>':  # e.g. `> OUT_BATCH`
            res_batch_from_file = BatchFromFile('STDOUT')
            del res_cmd_array[out_batch_cmdidx], res_cmd_array[out_batch_cmdidx - 1]

        else:  # OUT_BATCH is TMPFILE
            res_batch_from_file = BatchFromFile('TMPFILE')
            res_cmd_array[out_batch_cmdidx]  = res_batch_from_file.tmpfile_path()

        return (res_cmd_array, res_batch_from_file)

    @staticmethod
    def _in_batches_cmdidx(cmd_array):
        """Raise `IndexError` if IN_BATCH0 - IN_BATCHx is not used sequentially in `cmd_array`

        :returns: (IN_BATCH0's cmdidx, IN_BATCH1's cmdidx, ...)
            $ cat a.txt IN_BATCH1 IN_BATCH0 b.txt c.txt IN_BATCH2 => (3, 2, 5)
        """
        in_batches_cmdidx_dict = {}
        for cmdidx, tok in enumerate(cmd_array):
            mat = BatchCommand.in_batches_pat.match(tok)
            if mat:
                batch_idx = int(mat.group(1))
                if batch_idx in in_batches_cmdidx_dict:
                    raise IndexError(
                        'IN_BATCH%d is used multiple times in command below, while IN_BATCH0 - IN_BATCH%d must be used:%s$ %s' %
                        (batch_idx, len(in_batches_cmdidx_dict) - 1, os.linesep, list2cmdline(cmd_array)))
                in_batches_cmdidx_dict[batch_idx] = cmdidx

        in_batches_cmdidx = []
        for batch_idx in range(len(in_batches_cmdidx_dict)):
            try:
                cmdidx = in_batches_cmdidx_dict[batch_idx]
                in_batches_cmdidx.append(cmdidx)
            except KeyError:
                raise IndexError('IN_BATCH%d is not found in command below, while IN_BATCH0 - IN_BATCH%d must be used:%s$ %s' %
                                 (batch_idx, len(in_batches_cmdidx_dict) - 1, os.linesep, list2cmdline(cmd_array)))

        return tuple(in_batches_cmdidx)

    @staticmethod
    def _out_batch_cmdidx(cmd_array):
        """Raise `IndexError` if OUT_BATCH is used multiple time

        :returns: OUT_BATCH cmdidx (None if OUT_BATCH is not in `cmd_array`)
            $ cat a.txt > OUT_BATCH => 3
        """
        out_batch_cmdidx = None
        for cmdidx, tok in enumerate(cmd_array):
            mat = BatchCommand.out_batch_pat.match(tok)
            if mat:
                if out_batch_cmdidx:
                    raise IndexError(
                        'OUT_BATCH is used multiple times in command below:%s$ %s' %
                        (os.linesep, list2cmdline(cmd_array)))
                out_batch_cmdidx = cmdidx
        return out_batch_cmdidx
