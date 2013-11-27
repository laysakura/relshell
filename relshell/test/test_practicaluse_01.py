# -*- coding: utf-8 -*-
from nose.tools import *
from relshell.recorddef import RecordDef
from relshell.record import Record
from relshell.batch import Batch
from relshell.shelloperator import ShellOperator


def _create_batch():
    rdef = RecordDef([{'name': 'text', 'type': 'STRING'}])
    return Batch((
        Record(rdef, 'test1'),
        Record(rdef, 'test2'),
        Record(rdef, 'test3'),
        Record(rdef, 'test4'),
    ))


def test_output_batch_as_is():
    op = ShellOperator(
        'cat < IN_BATCH0 > OUT_BATCH',
        out_record_def = RecordDef([{'name': 'text', 'type': 'STRING'}]),
    )
    in_batch  = _create_batch()
    out_batch = op.run(in_batches=(in_batch, ))
    eq_(out_batch, in_batch)


def test_output_batch_cascade():
    op = ShellOperator(
        'cat < IN_BATCH0 > OUT_BATCH',
        out_record_def = RecordDef([{'name': 'text', 'type': 'STRING'}]),
    )
    batch_a = _create_batch()
    batch_b = op.run(in_batches=(batch_a, ))
    batch_c = op.run(in_batches=(batch_b, ))
    eq_(batch_c, batch_a)


def test_output_batch_as_is_file():
    op = ShellOperator(
        'cat IN_BATCH0 > OUT_BATCH',
        out_record_def = RecordDef([{'name': 'text', 'type': 'STRING'}]),
    )
    in_batch  = _create_batch()
    out_batch = op.run(in_batches=(in_batch, ))
    eq_(out_batch, in_batch)
