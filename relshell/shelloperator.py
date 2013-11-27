# -*- coding: utf-8 -*-
"""
    relshell.shelloperator
    ~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides `ShellOperator`
"""
from os import fdopen, remove
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
        cwd=None,
        env=None,
        in_record_sep='\n',
        out_record_sep='\n',  # 何か図解してあげる．in_record_sepの方が入力Recordを文字列にする際のもので，out_record_sepの方が出力文字列をRecordにする際のもの
    ):
        self._orig_cmd   = cmd
        self._cmddict    = parse(cmd)
        self._out_recdef = out_record_def
        self._terminator = terminator
        self._cwd        = cwd
        self._env        = env
        self._in_record_sep  = in_record_sep
        self._out_record_sep = out_record_sep

    def run(self, in_batches):
        """Run shell operator synchronously to eat `in_batches`

        :param in_batches: `tuple` of batches to process
        """
        if len(in_batches) != len(self._cmddict['in_batches_src']):
            raise AttributeError('len(in_batches) == %d, while %d IN_BATCH* are specified in command below:\n$ %s' %
                                 (len(in_batches), len(self._cmddict['in_batches_src']), self._orig_cmd))

        # prepare & start process
        ShellOperator._batches_to_file(self._in_record_sep, in_batches, self._cmddict['in_batches_src'])
        process = ShellOperator._start_process(
            self._cmddict['cmd_array'],
            self._cmddict['in_batches_src'],
            self._cmddict['out_batch_dest'],
            self._cwd, self._env,
        )
        using_stdin = ShellOperator._batch_to_stdin(process, self._in_record_sep, in_batches, self._cmddict['in_batches_src'])

        # wait process & get its output
        if using_stdin:
            ShellOperator._close_stdin(process)  # stdin has to recieve EOF explicitly (unlike file)

        process.wait()  # [todo] - check if process has successfully exited
        if self._cmddict['out_batch_dest'][0] == 'STDOUT':
            out_str   = ShellOperator._output_str_stdout(process)
            out_batch = ShellOperator._out_str_to_batch(out_str, self._out_recdef, self._out_record_sep)
            return out_batch
        else:
            raise NotImplementedError

    @staticmethod
    def _start_process(cmd_array, in_batches_src, out_batch_dest, cwd, env):
        return Popen(
            cmd_array,
            stdin  = PIPE if 'STDIN'  in [src[0] for src in in_batches_src] else None,
            stdout = PIPE if 'STDOUT' == out_batch_dest[0]                  else None,
            stderr = None,
            cwd = cwd,
            env = env,
        )

    @staticmethod
    def _input_str(in_batch, in_record_sep):
        input_str = ''
        for i, record in enumerate(in_batch):
            if i > 0: input_str += in_record_sep
            input_str += record[0]  # 複雑なrecorddefに対応してない
        return input_str

    @staticmethod
    def _batches_to_file(in_record_sep, in_batches, in_batches_src):
        """Create files to store in-batches contents (if necessary)"""
        for i, in_src in enumerate(in_batches_src):
            if in_src[0] == 'FILE':
                (fd, path) = in_src[1]
                with fdopen(fd, 'w') as f:
                    input_str = ShellOperator._input_str(in_batches[i], in_record_sep)
                    f.write(input_str)

    @staticmethod
    def _batch_to_stdin(process, in_record_sep, in_batches, in_batches_src):
        """Write in-batch contents to `process` 's stdin (if necessary)

        :returns: True if stdin is used
        """
        for i, in_src in enumerate(in_batches_src):
            if in_src[0] == 'STDIN':
                input_str = ShellOperator._input_str(in_batches[i], in_record_sep)
                process.stdin.write(input_str)
                process.stdin.flush()
                return True
        return False

    @staticmethod
    def _output_str_stdout(process):
        process.stdout.flush()
        output_str = process.stdout.read()
        process.stdout.close()
        return output_str

    @staticmethod
    def _out_str_to_batch(out_str, out_recdef, out_record_sep):
        out_recs = []
        for rec_str in out_str.split(out_record_sep):
            out_recs.append(Record(out_recdef, rec_str))   # これも複雑なrecdefには対応できてない
            out_batch = Batch(tuple(out_recs))
        return out_batch

    @staticmethod
    def _close_stdin(process):
        process.stdin.close()
