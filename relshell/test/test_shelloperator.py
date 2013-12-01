# -*- coding: utf-8 -*-
from nose.tools import *
from nose_parameterized import parameterized
from relshell.recorddef import RecordDef
from relshell.record import Record
from relshell.batch import Batch
from relshell.shelloperator import ShellOperator


def _simple_recdef():
    return RecordDef([{'name': 'text', 'type': 'STRING'}])


def _create_batch():
    rdef = RecordDef([{'name': 'text', 'type': 'STRING'}])
    return Batch((
        Record(rdef, 'test1'),
        Record(rdef, 'test2'),
        Record(rdef, 'test3'),
        Record(rdef, 'test4'),
    ))


@parameterized([
    # ( <simple command w/ RecordDef([{'name': 'text', 'type': 'STRING'}]) in/out> )
    ('cat < IN_BATCH0 > OUT_BATCH'),
    ('cat   IN_BATCH0 > OUT_BATCH'),
    # ('tee < IN_BATCH0 OUT_BATCH'),
])
def test_simple_operator(cmd):
    op = ShellOperator(
        cmd,
        out_record_def=_simple_recdef(),
    )
    in_batch  = _create_batch()
    out_batch = op.run(in_batches=(in_batch, ))
    eq_(out_batch, in_batch)


@parameterized([
    # ( <simple command w/ RecordDef([{'name': 'text', 'type': 'STRING'}]) in/out> )
    ('cat < IN_BATCH0 > OUT_BATCH'),
    ('cat   IN_BATCH0 > OUT_BATCH'),
])
@raises(AttributeError)
def test_simple_operator_batch_mismatch(cmd):
    op = ShellOperator(
        cmd,
        out_record_def=_simple_recdef(),
    )
    in_batch0  = _create_batch()
    in_batch1  = _create_batch()
    op.run(in_batches=(in_batch0, in_batch1))


@parameterized([
    # ( <simple command w/ RecordDef([{'name': 'text', 'type': 'STRING'}]) in/out> )
    ('cat < IN_BATCH0 > OUT_BATCH'),
    ('cat   IN_BATCH0 > OUT_BATCH'),
])
@raises(AttributeError)
def test_simple_operator_batch_mismatch(cmd):
    op = ShellOperator(
        cmd,
        out_record_def=_simple_recdef(),
    )
    in_batch0  = _create_batch()
    in_batch1  = _create_batch()
    op.run(in_batches=(in_batch0, in_batch1))


@parameterized([
    # ( <simple command w/ RecordDef([{'name': 'text', 'type': 'STRING'}]) in/out> )
    ('cat /no/such/file > OUT_BATCH'),
    ('wiredcmd > OUT_BATCH'),
])
@raises(OSError)
def test_simple_operator_error_cmd(cmd):
    op = ShellOperator(
        cmd,
        out_record_def=_simple_recdef,
    )
    op.run(in_batches=())


def test_output_batch_cascade():
    op = ShellOperator(
        'cat < IN_BATCH0 > OUT_BATCH',
        out_record_def = RecordDef([{'name': 'text', 'type': 'STRING'}]),
    )
    batch_a = _create_batch()
    batch_b = op.run(in_batches=(batch_a, ))
    batch_c = op.run(in_batches=(batch_b, ))
    eq_(batch_c, batch_a)


def test_output_batch_sorted():
    op = ShellOperator(
        'sort < IN_BATCH0 > OUT_BATCH',
        out_record_def = RecordDef([{'name': 'text', 'type': 'STRING'}]),
    )
    rdef = RecordDef([{'name': 'text', 'type': 'STRING'}])
    in_batch = Batch((
        Record(rdef, 'test2'),
        Record(rdef, 'test3'),
        Record(rdef, 'test1'),
        Record(rdef, 'test4'),
    ))
    sorted_batch = Batch((
        Record(rdef, 'test1'),
        Record(rdef, 'test2'),
        Record(rdef, 'test3'),
        Record(rdef, 'test4'),
    ))
    in_batch  = _create_batch()
    out_batch = op.run(in_batches=(in_batch, ))
    eq_(out_batch, sorted_batch)
