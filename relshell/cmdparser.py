# -*- coding: utf-8 -*-
"""
    relshell.cmdparser
    ~~~~~~~~~~~~~~~~~~

    :synopsis: Parses shell command w/ BATCH management
"""


def parse(cmd):
    """
    :returns: parsed result like below:

    .. code-block:: python

        # when parsing 'diff IN_BATCH0 IN_BATCH1 > OUT_BATCH'
        {
            'cmd_line'   : 'diff /tmp/relshell-AbCDeF /tmp/relshell-uVwXyz',  # Can be used for `Popen(shlex.split(ret['cmd_line']))`
            'in_batches' : [('FILE', '/tmp/relshell-AbCDeF'), ('FILE', '/tmp/relshell-uVwXyz')],  # [IN_BATCH0, IN_BATCH1]
            'out_batch'  : 'STDOUT',
        }
    """
    return {
        'cmd_line'       : 'cat',
        'in_batches_src' : [('STDIN', ), ],
        'out_batch_dest' : 'STDOUT',
    }
