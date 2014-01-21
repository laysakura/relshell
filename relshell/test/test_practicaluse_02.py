# -*- coding: utf-8 -*-
import nose.tools as ns
import re
from os.path import join, abspath, dirname
from relshell.recorddef import RecordDef
from relshell.record import Record
from relshell.batch import Batch
from relshell.daemon_shelloperator import DaemonShellOperator


SPLIT_SENTENCE = join(abspath(dirname(__file__)), 'shellcmd', 'split_sentence')


def _create_batch():
    return Batch(
        RecordDef([{'name': 'sentence', 'type': 'STRING'}]),
        (
            Record('This is test'),
            Record('That is also test'),
            Record('This is not a test'),
        )
    )


def test_wordcount():
    batch = _create_batch()

    op = DaemonShellOperator(
        '%s < IN_BATCH0 > OUT_BATCH' % (SPLIT_SENTENCE),
        out_record_def=RecordDef([{'name': 'word', 'type': 'STRING'}]),
        out_col_patterns={'word': re.compile(r'^.+$', re.MULTILINE)},
        batch_done_indicator='extraordinarylongword\n',
        batch_done_output='extraordinarylongword\n')
    out_batch = op.run(in_batches=(batch, ))

    ns.eq_(next(out_batch), Record('This'))
    ns.eq_(next(out_batch), Record('is'))
    ns.eq_(next(out_batch), Record('test'))

    ns.eq_(next(out_batch), Record('That'))
    ns.eq_(next(out_batch), Record('is'))
    ns.eq_(next(out_batch), Record('also'))
    ns.eq_(next(out_batch), Record('test'))

    ns.eq_(next(out_batch), Record('This'))
    ns.eq_(next(out_batch), Record('is'))
    ns.eq_(next(out_batch), Record('not'))
    ns.eq_(next(out_batch), Record('a'))
    ns.eq_(next(out_batch), Record('test'))
