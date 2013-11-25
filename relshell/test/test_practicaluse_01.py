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
        # 'cat < #IN_BATCH# > #OUT_BATCH#',  # stdin,stdoutでのバッチの扱いはデフォルト化してもいいと思う
        'cat',
        out_record_def = RecordDef([{'name': 'text', 'type': 'STRING'}]),
    )
    in_batch  = _create_batch()
    out_batch = op.run(in_batches=[in_batch, ])   # daemonize=Falseなので，シェルプロセスの終了まで待つ
    eq_(out_batch, in_batch)


# def test_output_2in_1out():
#     batch0 = _create_batch()
#     rdef   = RecordDef([{'name': 'text', 'type': 'STRING'}])
#     batch1 = Batch((
#         Record(rdef, 'test1'),
#         Record(rdef, 'test2xx'),
#         Record(rdef, 'test3'),
#         Record(rdef, 'test4'),
#     ))

#     op = ShellOperator(
#         'diff #IN_BATCH0# #IN_BATCH1# > #OUT_BATCH#'
#         out_record_def=RecordDef([
#             {'name': 'position',
#              'type': 'STRING',
#             },
#             {'name': 'diff',
#              'type': 'STRING',
#             },
#         ]),
#         # terminatorはいらない．diffは2バッチ比較終わったらそのままexit(0)するから．
#         # daemonize=Falseなので暗黙のうちにop.kill()が呼ばれるが，
#         # これは「もうプロセスが死んでいたら何もしない」という動作にする．

#         col_patterns = {   # defaultでは r'^.*$\n' にするって感じ
#             'position': re.compile(r'''
#                 # diff position
#                 (
#                     \d (,\d)? [acd] \d (,\d)?
#                 )
#             ''', re.VERBOSE | re.MULTILINE),

#             'diff': re.compile(r'''
#                 # diff content
#                 (
#                     (^[<>] .*?$\n)+
#                     (
#                         ^---$\n
#                         (^> .*?$\n)*
#                     )?
#                 )
#             ''', re.VERBOSE | re.MULTILINE)
#         }
#     )
#     out_batch = op.run(in_batches=[batch0, ])
#     batch2 = op.run(in_batches=[batch1, ])
#     eq_(batch2, batch0)


# def test_daemonized_process():
#     op = ShellOperator(
#         'cat < #IN_BATCH# > #OUT_BATCH#',
#         out_record_def = RecordDef([{'name': 'text', 'type': 'STRING'}]),
#         terminator     = Terminator.EOF  # Terminator.SIGKILL, ...
#         daemonize      = True,  # op.kill() を明示的に呼び出すまでterminatorの実行がなされない
#     )
#     for i in xrange(10):
#         in_batch  = _create_batch()
#         out_batch = op.run(in_batches=[in_batch, ])   # daemonize=Trueなので，シェルプロセスが走り続けていても，
#                                                 # 1個のin_batchについての処理が終わればrun呼び出しは終わる
#                                                 # (1個のin_batchについて同期呼び出し)
#                                                 # ただし，「どこまでが1つのoutput_batchか」を判定する必要はある．
#                                                 # 「空行が1つ出たら」とか，「何ms新しい出力がなかったら」とか?
#         eq_(out_batch, in_batch)
#     op.kill()  # daemonize=Trueのときのkillし忘れを何とかしたい．subprocessがゾンビになっちゃうし．
#                # デストラクタで警告出しつつkill -9送る?
#                # というか，kill()みたいに「呼び出さないといけない」インターフェースよりwith構文使うべきな感じがある
