# -*- coding: utf-8 -*-
from nose.tools import *
from relshell.recorddef import RecordDef
from relshell.record import Record
from relshell.batch import Batch
from relshell.daemon_shelloperator import DaemonShellOperator


def _create_batch():
    rdef = RecordDef([{'name': 'text', 'type': 'STRING'}])
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


@raises(AttributeError)
def test_daemon_shelloperator_constraints():
    DaemonShellOperator(
        'cat IN_BATCH0 > OUT_BATCH',    # [todo] - currently input must be from stdin, but `tail` from file will be also supported
        out_record_def       = RecordDef([{'name': 'text', 'type': 'STRING'}]),
        batch_done_indicator = 'BATCH_SEPARATOR\n',
        batch_done_output    = 'BATCH_SEPARATOR\n',
    )


@raises(OSError)
def test_output_batch_error_cmd():
    op = DaemonShellOperator(
        'wiredcmd < IN_BATCH0',
        out_record_def       = RecordDef([{'name': 'text', 'type': 'STRING'}]),
        batch_done_indicator = 'BATCH_SEPARATOR\n',
        batch_done_output    = 'BATCH_SEPARATOR\n',
    )
    batch = _create_batch()
    op.run(in_batches=(batch, ))
