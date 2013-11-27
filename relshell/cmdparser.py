# -*- coding: utf-8 -*-
"""
    relshell.cmdparser
    ~~~~~~~~~~~~~~~~~~

    :synopsis: Parses shell command w/ BATCH management
"""
import shlex
import re
from tempfile import mkstemp


in_batches_pat = re.compile('IN_BATCH(\d+)')
"""Input batches"""

out_batch_pat  = re.compile('OUT_BATCH')
"""Output batch"""


def parse(cmd):
    """
    :returns: parsed result like below:

    .. code-block:: python

        # when parsing 'diff IN_BATCH0 IN_BATCH1 > OUT_BATCH'
        {
            'cmd_array'  : ['diff', '/tmp/relshell-AbCDeF', '/tmp/relshell-uVwXyz'],  # Can be used for `Popen(ret['cmd_line'])`
            'in_batches' : ( ('FILE', <retval of `mkstemp()`>), ('FILE', <retval of `mkstemp()`>) ),  # (IN_BATCH0, IN_BATCH1)
            'out_batch'  : 'STDOUT',
        }
    """
    cmd_array = shlex.split(cmd)
    (cmd_array, in_batches_src) = _parse_in_batches_src(cmd_array)
    (cmd_array, out_batch_dest) = _parse_out_batch_dest(cmd_array)
    return {
        'cmd_array'      : cmd_array,
        'in_batches_src' : in_batches_src,
        'out_batch_dest' : out_batch_dest,
    }


def _parse_in_batches_src(cmd_array):
    """Find patterns that match to `in_batches_pat` and replace them into `STDIN` or `FILE`.

    :param cmd_array: `shlex.split`-ed command
    :rtype:   ([cmd_array], ( ('FILE', <retval of `mkstemp()`>), ('STDIN', ), ... ) )
    :returns: Modified `cmd_array` and tuple to show how each IN_BATCH is instanciated (FILE or STDIN).
        Returned `cmd_array` drops IN_BATCH related tokens.
    :raises:  `IndexError` if IN_BATCHes don't have sequential ID starting from 0
    """
    res_cmd_array      = cmd_array[:]
    res_in_batches_tup = []

    in_batches_cmdidx  = _batches_id_cmdidx(cmd_array)
    for batch_id, cmdidx in enumerate(in_batches_cmdidx):
        if cmdidx > 0 and cmd_array[cmdidx - 1] == '<':  # e.g. `< IN_BATCH0`
            res_in_batches_tup.append(('STDIN', ))
            del res_cmd_array[cmdidx], res_cmd_array[cmdidx - 1]

        else:  # IN_BATCHx is FILE
            tmpfile = mkstemp(prefix='relshell-', suffix='.batch')  # [todo] - Use memory file system for performance
            res_in_batches_tup.append(('FILE', tmpfile))
            res_cmd_array[cmdidx] = tmpfile[1]

    return (res_cmd_array, tuple(res_in_batches_tup))


def _parse_out_batch_dest(cmd_array):
    """Find patterns that match to `out_batch_pat` and replace them into `STDOUT` or `FILE`.

    :param cmd_array: `shlex.split`-ed command
    :rtype:   ([cmd_array], ('FILE', <retval of `mkstemp()`>)) or ([cmd_array], ('STDOUT', ))
    :returns: Modified `cmd_array` and tuple to show how OUT_BATCH is instanciated (FILE or STDOUT).
        Returned `cmd_array` drops OUT_BATCH related tokens.
    :raises:  `IndexError` if multiple OUT_BATCH are found
    """
    res_cmd_array     = cmd_array[:]
    res_out_batch_tup = ()
    for i, tok in enumerate(cmd_array):
        mat = out_batch_pat.match(tok)
        if mat:
            if res_out_batch_tup != ():
                raise IndexError(
                    'OUT_BATCH is used multiple times in command below:\n$ %s' %
                    (' '.join(cmd_array)))

            if i > 0 and cmd_array[i - 1] == '>':  # e.g. `> OUT_BATCH`
                res_out_batch_tup = ('STDOUT', )
                del res_cmd_array[i], res_cmd_array[i - 1]

            else:  # OUT_BATCH is FILE
                tmpfile = mkstemp(prefix='relshell-', suffix='.batch')
                res_out_batch_tup = ('FILE', tmpfile)
                res_cmd_array[i]  = tmpfile[1]

    return (res_cmd_array, tuple(res_out_batch_tup))


def _batches_id_cmdidx(cmd_array):
    """Raise `IndexError` if IN_BATCH0 - IN_BATCHx is not used sequentially in `cmd_array`

    :returns: (IN_BATCH0's cmdidx, IN_BATCH1's cmdidx, ...)
        $ cat a.txt IN_BATCH1 IN_BATCH0 b.txt c.txt IN_BATCH2 => (3, 2, 5)
    """
    in_batches_cmdidx_dict = {}
    for cmdidx, tok in enumerate(cmd_array):
        mat = in_batches_pat.match(tok)
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
