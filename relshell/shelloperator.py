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

    def run(self, in_batches):
        def _start_process():
            return Popen(
                shlex.split(self._cmddict['cmd_line']),
                stdin  = PIPE if 'STDIN'  in [in_batch[0] for in_batch in self._cmddict['in_batches_src']] else None,
                stdout = PIPE if 'STDOUT' == self._cmddict['out_batch_dest'] else None,
                stderr = None,
                cwd = self._cwd,
                env = self._env,
            )

        def _input_str(in_batch):
            input_str = ''
            for i, record in enumerate(in_batch):
                if i > 0: input_str += self._in_record_sep
                input_str += record[0]  # 複雑なrecorddefに対応してない
            return input_str

        def _batches_to_file():
            for i, in_src in enumerate(self._cmddict['in_batches_src']):
                if in_src[0] == 'FILE':
                    with open(in_src[1], 'w') as f:
                        input_str = _input_str(in_batches[i])
                        f.write(input_str)

        def _batches_to_stdin(process):
            for i, in_src in enumerate(self._cmddict['in_batches_src']):
                if in_src[0] == 'STDIN':
                    input_str = _input_str(in_batches[i])
                    process.stdin.write(input_str)
                    process.stdin.flush()
                    process.stdin.close()   # daemonize=Trueのときはどうしよう

        def _output_str(process):
            process.stdout.flush()
            output_str = process.stdout.read()
            process.stdout.close()
            return output_str

        def _out_str_to_batch(out_str):
            out_recs = []
            for rec_str in out_str.split(self._out_record_sep):
                out_recs.append(Record(self._out_recdef, rec_str))   # これも複雑なrecdefには対応できてない
                out_batch = Batch(tuple(out_recs))
            return out_batch

        if len(in_batches) != len(self._cmddict['in_batches_src']):
            raise AttributeError('len(in_batches) == %d, while %d IN_BATCH* are specified in ShellOperator.__init__()' %
                                 (len(in_batches), len(self._cmddict['in_batches_src'])))

        if self._daemonize:
            raise NotImplementedError

        _batches_to_file()
        process = _start_process()
        _batches_to_stdin(process)
        process.wait()
        out_str = _output_str(process)
        out_batch = _out_str_to_batch(out_str)
        return out_batch


def _chk_terminator(terminator):
    if terminator != 'EOF':
        raise NotImplementedError('Invalid terminator: %s' % terminator)
