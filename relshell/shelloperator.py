# -*- coding: utf-8 -*-
"""
    relshell.shelloperator
    ~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides `ShellOperator`
"""
import shlex
from subprocess import Popen, PIPE
from relshell.record import Record
from relshell.batch import Batch
from relshell.cmdparser import parse


class ShellOperator(object):
    """ShellOperator"""

    def __init__(
        self,
        cmd,
        out_record_def,
        terminator='EOF',
        daemonize=False,
        cwd=None,
        env=None,
        in_record_sep ='\n',
        out_record_sep='\n',  # 何か図解してあげる．in_record_sepの方が入力Recordを文字列にする際のもので，out_record_sepの方が出力文字列をRecordにする際のもの
    ):
        # check
        _chk_terminator(terminator)

        #set
        self._cmddict    = parse(cmd)
        self._out_recdef = out_record_def
        self._terminator = terminator
        self._daemonize  = daemonize
        self._cwd        = cwd
        self._env        = env
        self._in_record_sep  = in_record_sep
        self._out_record_sep = out_record_sep

    def run(self, in_batch):
        if self._daemonize:
            raise NotImplementedError

        process = Popen(
            shlex.split(self._cmddict['cmd_line']),
            stdin  = PIPE if 'STDIN'  in self._cmddict['in_batches'] else None,
            stdout = PIPE if 'STDOUT' == self._cmddict['out_batch']  else None,
            stderr=None,  # これじゃあ上がってこない
            cwd=self._cwd,
            env=self._env,
        )

        assert('STDIN'  in self._cmddict['in_batches'] and
               'STDOUT' == self._cmddict['out_batch'])  # ちょっとこれ以外の実装はまだ

        input_str = r''
        for i, record in enumerate(in_batch):
            if i > 0: input_str += self._in_record_sep
            input_str += record[0]  # 複雑なrecorddefに対応してない

        try:
            process.stdin.write(input_str)
        except IOError as e:
            if e.errno == errno.EPIPE or e.errno == errno.EINVAL:
                # Stop loop on "Invalid pipe" or "Invalid argument".
                # No sense in continuing with broken pipe.
                pass
            else:
                # Raise any other error.
                raise

        process.stdin.close()  # flush. EOFも送れてる??
        process.wait()

        process.stdout.flush()
        output_str = process.stdout.read()
        process.stdout.close() # flush

        out_recs = []
        for rec_str in output_str.split(self._out_record_sep):
            out_recs.append(Record(self._out_recdef, rec_str))   # これも複雑なrecdefには対応できてない
        out_batch = Batch(tuple(out_recs))

        print in_batch
        print out_batch

        return out_batch


def _chk_terminator(terminator):
    if terminator != 'EOF':
        raise NotImplementedError('Invalid terminator: %s' % terminator)
