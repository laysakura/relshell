# -*- coding: utf-8 -*-
from nose.tools import *
from relshell.recorddef import RecordDef
from relshell.record import Record
from relshell.batch import Batch
# from relshell.daemon_shelloperator import DaemonShellOperator


# def _create_batch():
#     rdef = RecordDef([{'name': 'text', 'type': 'STRING'}])
#     return Batch((
#         Record(rdef, 'test1'),
#         Record(rdef, 'test2'),
#         Record(rdef, 'test3'),
#         Record(rdef, 'test4'),
#     ))


# def test_daemonized_process():
#     op = DaemonShellOperator(
#         'cat < IN_BATCH0 > OUT_BATCH',
#         out_record_def = RecordDef([{'name': 'text', 'type': 'STRING'}]),
#         daemonize      = True,  # op.kill() を明示的に呼び出すまでterminatorの実行がなされない
#     )
#     prev_pid = None
#     for i in xrange(10):
#         in_batch  = _create_batch()
#         out_batch = op.run(in_batches=(in_batch, ))   # [fix] - daemonize=Trueなので，シェルプロセスが走り続けていても，
#                                                       # [fix] - 1個のin_batchについての処理が終わればrun呼び出しは終わる
#                                                       # [fix] - (1個のin_batchについて同期呼び出し)
#                                                       # [fix] - ただし，「どこまでが1つのoutput_batchか」を判定する必要はある．
#                                                       # [fix] - 「空行が1つ出たら」とか，「何ms新しい出力がなかったら」とか?
#         eq_(out_batch, in_batch)

#         cur_pid = op.getpid()
#         if prev_pid:
#             eq_(cur_pid, prev_pid)  # instanciated process does not die during for loop
#         prev_pid = op.getpid()

#     op.kill()  # [todo] - Calling kill() can be easily forgot.
#                # [todo] - Possible ways are
#                # [todo] - 1. `killall -9` in ShellOperator.__del__() w/ some warnings to user
#                # [todo] - 2. `with` syntax
