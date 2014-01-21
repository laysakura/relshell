# -*- coding: utf-8 -*-
from nose.tools import *
from nose_parameterized import parameterized
import os
from os.path import join, abspath, dirname
import tempfile
import re
from relshell.recorddef import RecordDef
from relshell.record import Record
from relshell.batch import Batch
from relshell.daemon_shelloperator import DaemonShellOperator


WORD_COUNT = join(abspath(dirname(__file__)), 'shellcmd', 'word_count')
n_tmpfile = 0


def setup():
    global n_tmpfile
    n_tmpfile = _get_num_tmpfile()


def teardown():
    global n_tmpfile
    eq_(_get_num_tmpfile(), n_tmpfile, 'Number of relshell tmpfile is not changed during test')


def _get_num_tmpfile():
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


def test_daemonized_process():
    op = DaemonShellOperator(
        'cat < IN_BATCH0 > OUT_BATCH',
        out_record_def       = RecordDef([{'name': 'text', 'type': 'STRING'}]),
        out_col_patterns     = {'text': re.compile(r'^.+$', re.MULTILINE)},
        batch_done_indicator = 'BATCH_DONE\n',
        batch_done_output    = 'BATCH_DONE\n',
    )
    prev_pid = op.getpid()
    ok_(prev_pid is None)
    for i in xrange(10):
        in_batch  = _create_batch()
        out_batch = op.run(in_batches=(in_batch, ))
        eq_(out_batch, in_batch)

        cur_pid = op.getpid()
        if prev_pid:
            eq_(cur_pid, prev_pid)  # instantiated process does not die during for loop
        prev_pid = op.getpid()

    op.kill()  # [todo] - Calling kill() can be easily forgot.
               # [todo] - Possible ways are
               # [todo] - 1. `killall -9` in ShellOperator.__del__() w/ some warnings to user
               # [todo] - 2. `with` syntax
    ok_(op.getpid() is None)


@parameterized([
    # ( <simple command w/ RecordDef([{'name': 'text', 'type': 'STRING'}]) in/out> )
    ('cat IN_BATCH0 > OUT_BATCH'),    # [todo] - currently input must be from stdin, but `tail` from file will be also supported
])
@raises(AttributeError)
def test_simple_operator_constraints(cmd):
    DaemonShellOperator(
        cmd,
        out_record_def       = _simple_recdef(),
        out_col_patterns     = {'text': re.compile(r'^.+$', re.MULTILINE)},
        batch_done_indicator = 'BATCH_SEPARATOR\n',
        batch_done_output    = 'BATCH_SEPARATOR\n',
    )


@parameterized([
    # ( <simple command w/ RecordDef([{'name': 'text', 'type': 'STRING'}]) in/out> )
    ('cat < IN_BATCH0 > OUT_BATCH'),
])
@raises(AttributeError)
def test_simple_operator_batch_mismatch(cmd):
    op = DaemonShellOperator(
        cmd,
        out_record_def       = _simple_recdef(),
        out_col_patterns     = {'text': re.compile(r'^.+$', re.MULTILINE)},
        batch_done_indicator = 'BATCH_SEPARATOR\n',
        batch_done_output    = 'BATCH_SEPARATOR\n',
    )
    in_batch0  = _create_batch()
    in_batch1  = _create_batch()
    op.run(in_batches=(in_batch0, in_batch1))


@parameterized([
    # ( <simple command w/ RecordDef([{'name': 'text', 'type': 'STRING'}]) in/out> )
    ('wiredcmd < IN_BATCH0 > OUT_BATCH'),
])
@raises(OSError)
def test_simple_operator_error_cmd(cmd):
    op = DaemonShellOperator(
        cmd,
        out_record_def       = _simple_recdef(),
        out_col_patterns     = {'text': re.compile(r'^.+$', re.MULTILINE)},
        batch_done_indicator = 'BATCH_SEPARATOR\n',
        batch_done_output    = 'BATCH_SEPARATOR\n',
    )
    op.run(in_batches=(_create_batch(), ))


def test_long_batch_to_shelloperator():
    words_file = join(abspath(dirname(__file__)), 'test_daemon_shelloperator_words.txt')
    records    = []
    with open(words_file) as f:
        for line in f:
            records.append(Record(line.strip()))
    long_batch = Batch(RecordDef([{'name': 'word'}]), records)

    op = DaemonShellOperator(
        '%s < IN_BATCH0 > OUT_BATCH' % (WORD_COUNT),
        out_record_def=RecordDef([{'name': 'word', 'type': 'STRING'}, {'name': 'count', 'type': 'INT'}]),
        out_col_patterns={
            'word'  : re.compile(r'^.+(?= )', re.MULTILINE),
            'count' : re.compile(r'\d+$', re.MULTILINE),
        },
        batch_done_indicator='not word\n',
        batch_done_output='single word is expected\n')
    out_batch = op.run(in_batches=(long_batch, ))
