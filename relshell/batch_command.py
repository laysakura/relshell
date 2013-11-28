# -*- coding: utf-8 -*-
"""
    relshell.batch_command
    ~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Parses shell command w/ BATCH management
"""
import shlex
import re
from tempfile import mkstemp
from relshell.input_batch_source import InputBatchSource


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
        (self.sh_cmd, self.batch_srcs, self.batch_dest) = BatchCommand._parse(batch_cmd)

    @staticmethod
    def _parse(batch_cmd):
        """
        :rtype:   (sh_cmd, batch_srcs, batch_dest)
        :returns: parsed result like below:

        .. code-block:: python

            # when parsing 'diff IN_BATCH0 IN_BATCH1 > OUT_BATCH'
            (
                'diff /tmp/relshell-AbCDeF /tmp/relshell-uVwXyz',
                ( <instance of InputBatchSource>, <instance of InputBatchSource> )    # (IN_BATCH0, IN_BATCH1)
                'STDOUT',
            )
        """
        cmd_array               = shlex.split(batch_cmd)
        (cmd_array, batch_srcs) = BatchCommand._parse_batch_srcs(cmd_array)
        (cmd_array, batch_dest) = BatchCommand._parse_batch_dest(cmd_array)
        return (' '.join(cmd_array), batch_srcs, batch_dest)

    @staticmethod
    def _parse_batch_srcs(cmd_array):
        """Find patterns that match to `in_batches_pat` and replace them into `STDIN` or `FILE`.

        :param cmd_array: `shlex.split`-ed command
        :rtype:   ([cmd_array], ( batch_src, batch_src, ... ) )
        :returns: Modified `cmd_array` and tuple to show how each IN_BATCH is instanciated (FILE or STDIN).
            Returned `cmd_array` drops IN_BATCH related tokens.
        :raises:  `IndexError` if IN_BATCHes don't have sequential ID starting from 0
        """
        res_cmd_array      = cmd_array[:]
        res_batch_srcs = []

        in_batches_cmdidx  = BatchCommand._in_batches_cmdidx(cmd_array)
        for batch_id, cmdidx in enumerate(in_batches_cmdidx):
            if cmdidx > 0 and cmd_array[cmdidx - 1] == '<':  # e.g. `< IN_BATCH0`
                res_batch_srcs.append(InputBatchSource('STDIN'))
                del res_cmd_array[cmdidx], res_cmd_array[cmdidx - 1]

            else:  # IN_BATCHx is FILE
                batch_src = InputBatchSource('TMPFILE')
                res_batch_srcs.append(batch_src)
                res_cmd_array[cmdidx] = batch_src.tmpfile_path()

        return (res_cmd_array, tuple(res_batch_srcs))

    @staticmethod
    def _parse_batch_dest(cmd_array):
        """Find patterns that match to `out_batch_pat` and replace them into `STDOUT` or `FILE`.

        :param cmd_array: `shlex.split`-ed command
        :rtype:   ([cmd_array], ('FILE', <retval of `mkstemp()`>)) or ([cmd_array], ('STDOUT', ))
        :returns: Modified `cmd_array` and tuple to show how OUT_BATCH is instanciated (FILE or STDOUT).
            Returned `cmd_array` drops OUT_BATCH related tokens.
        :raises:  `IndexError` if multiple OUT_BATCH are found
        """
        res_cmd_array     = cmd_array[:]
        res_out_batch_tup = ()

        out_batch_cmdidx = BatchCommand._out_batch_cmdidx(cmd_array)
        if out_batch_cmdidx is None:
            return (res_cmd_array, res_out_batch_tup)

        if out_batch_cmdidx > 0 and cmd_array[out_batch_cmdidx - 1] == '>':  # e.g. `> OUT_BATCH`
            res_out_batch_tup = ('STDOUT', )
            del res_cmd_array[out_batch_cmdidx], res_cmd_array[out_batch_cmdidx - 1]

        else:  # OUT_BATCH is FILE
            tmpfile = mkstemp(prefix='relshell-', suffix='.batch')
            res_out_batch_tup = ('FILE', tmpfile)
            res_cmd_array[out_batch_cmdidx]  = tmpfile[1]

        return (res_cmd_array, tuple(res_out_batch_tup))

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
                        'IN_BATCH%d is used multiple times in command below, while IN_BATCH0 - IN_BATCH%d must be used:\n$ %s' %
                        (batch_idx, len(in_batches_cmdidx_dict) - 1, ' '.join(cmd_array)))
                in_batches_cmdidx_dict[batch_idx] = cmdidx

        in_batches_cmdidx = []
        for batch_idx in range(len(in_batches_cmdidx_dict)):
            try:
                cmdidx = in_batches_cmdidx_dict[batch_idx]
                in_batches_cmdidx.append(cmdidx)
            except KeyError:
                raise IndexError('IN_BATCH%d is not found in command below, while IN_BATCH0 - IN_BATCH%d must be used:\n$ %s' %
                                 (batch_idx, len(in_batches_cmdidx_dict) - 1, ' '.join(cmd_array)))

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
                        'OUT_BATCH is used multiple times in command below:\n$ %s' %
                        (' '.join(cmd_array)))
                out_batch_cmdidx = cmdidx
        return out_batch_cmdidx
