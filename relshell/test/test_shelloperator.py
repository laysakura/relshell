# -*- coding: utf-8 -*-
from nose.tools import *
from nose_parameterized import parameterized
import os
import tempfile
import re
from relshell.recorddef import RecordDef
from relshell.record import Record
from relshell.batch import Batch
from relshell.timestamp import Timestamp
from relshell.shelloperator import ShellOperator


n_tmpfile = 0


def setup():
    global n_tmpfile
    n_tmpfile = _get_num_tmpfile()


def teardown():
    global n_tmpfile
    eq_(_get_num_tmpfile(), n_tmpfile, 'Number of relshell tmpfile is not changed during test')


def _get_num_tmpfile():
    # [fix] - tmpfile name is hardcoded
    return len([tmp for tmp in os.listdir(tempfile.gettempdir()) if tmp.startswith('relshell-') and tmp.endswith('.batch')])


def _simple_recdef():
    return RecordDef([{'name': 'text', 'type': 'STRING'}])


def _create_batch():
    return Batch(
        _simple_recdef(),
        (
            Record('test1'),
            Record('test2'),
            Record('test3'),
            Record('test4'),
        )
    )


def _create_batch_sort_in():
    return Batch(
         _simple_recdef(),
        (
            Record('test2'),
            Record('test3'),
            Record('test1'),
            Record('test4'),
        )
    )


@parameterized([
    # ( <simple command w/ RecordDef([{'name': 'text', 'type': 'STRING'}]) in/out> )
    ('cat < IN_BATCH0 > OUT_BATCH'),
    ('cat   IN_BATCH0 > OUT_BATCH'),
    ('tee < IN_BATCH0 OUT_BATCH'),
])
def test_simple_operator(cmd):
    op = ShellOperator(
        cmd,
        out_record_def   = _simple_recdef(),
        out_col_patterns = {'text': re.compile(r'^.+$', re.MULTILINE)},
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
        out_record_def   = _simple_recdef(),
        out_col_patterns = {'text': re.compile(r'^.+$', re.MULTILINE)},
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
        out_record_def   = _simple_recdef(),
        out_col_patterns = {'text': re.compile(r'^.+$', re.MULTILINE)},
    )
    op.run(in_batches=())


def test_output_batch_cascade():
    op = ShellOperator(
        'cat < IN_BATCH0 > OUT_BATCH',
        out_record_def   = _simple_recdef(),
        out_col_patterns = {'text': re.compile(r'^.+$', re.MULTILINE)},
    )
    batch_a = _create_batch()
    batch_b = op.run(in_batches=(batch_a, ))
    batch_c = op.run(in_batches=(batch_b, ))
    eq_(batch_c, batch_a)


def test_output_batch_sorted():
    op = ShellOperator(
        'sort < IN_BATCH0 > OUT_BATCH',
        out_record_def   = _simple_recdef(),
        out_col_patterns = {'text': re.compile(r'^.+$', re.MULTILINE)},
    )
    in_batch     = _create_batch_sort_in()
    sorted_batch = _create_batch()
    out_batch    = op.run(in_batches=(in_batch, ))
    eq_(out_batch, sorted_batch)


@parameterized([
    # ( <simple command w/ RecordDef([{'name': 'text', 'type': 'STRING'}]) in/out> )
    '2013-04-05',
    '2013-04-05 12:00:30',
])
def test_timestamp_type(timestamp_str):
    rdef = RecordDef([{'name': 'timestamp_str', 'type': 'STRING'}])
    op = ShellOperator(
        'cat < IN_BATCH0 > OUT_BATCH',
        out_record_def=RecordDef([{'name': 'timestamp', 'type': 'TIMESTAMP'}]),
        out_col_patterns={'timestamp': re.compile(r'^\d{4}-\d{2}-\d{2}.*$', re.MULTILINE)},
    )
    in_batch  = Batch(rdef, (Record(timestamp_str), ))
    out_batch = op.run(in_batches=(in_batch, ))
    eq_(out_batch,
        Batch(RecordDef([{'name': 'timestamp', 'type': 'TIMESTAMP'}]),
              (Record(Timestamp(timestamp_str)), )))
