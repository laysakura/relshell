# -*- coding: utf-8 -*-
from nose.tools import *
from nose_parameterized import parameterized
import re
from relshell.recorddef import RecordDef
from relshell.record import Record
from relshell.batch import Batch
from relshell.daemon_shelloperator import DaemonShellOperator


def _simple_recdef():
    return RecordDef([{'name': 'text', 'type': 'STRING'}])


def _create_batch():
    rdef = _simple_recdef()
    return Batch((
        Record(rdef, 'test1'),
        Record(rdef, 'test2'),
        Record(rdef, 'test3'),
        Record(rdef, 'test4'),
    ))


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
            eq_(cur_pid, prev_pid)  # instanciated process does not die during for loop
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
