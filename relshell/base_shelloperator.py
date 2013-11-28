# -*- coding: utf-8 -*-
"""
    relshell.base_shelloperator
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides abstract `BaseShellOperator`
"""
from abc import ABCMeta, abstractmethod
from os import fdopen, remove
from subprocess import Popen, PIPE
from relshell.record import Record
from relshell.batch import Batch
from relshell.cmdparser import parse


class BaseShellOperator(object):
    """BaseShellOperator

    :param ignore_record_pat: ignore string which match w/ `ignore_record_pat` will not be output as record
    """
    __metaclass__ = ABCMeta

    _ignore_record_pat = None

    def __init__(
        self,
        cmd,
        out_record_def,
        cwd,
        env,
        in_record_sep,
        out_record_sep,  # [todo] - explain how this parameter is used (using diagram?)
                         # [todo] - in_record_sepの方が入力Recordを文字列にする際のもので，out_record_sepの方が出力文字列をRecordにする際のもの
        ignore_record_pat,
    ):
        """Constructor

            :param ignore_record_pat: ignore string which match w/ `ignore_record_pat` will not be output as record (can be `None`)
        """
        self._orig_cmd   = cmd
        self._cmddict    = parse(cmd)
        self._out_recdef = out_record_def
        self._cwd        = cwd
        self._env        = env
        self._in_record_sep  = in_record_sep
        self._out_record_sep = out_record_sep
        if ignore_record_pat: BaseShellOperator._ignore_record_pat = ignore_record_pat

    @abstractmethod
    def run(self, in_batches):
        """Run shell operator synchronously to eat `in_batches`

        :param in_batches: `tuple` of batches to process
        """
        pass

    @staticmethod
    def _start_process(cmd_array, in_batches_src, out_batch_dest, cwd, env):
        return Popen(
            cmd_array,
            stdin  = PIPE if 'STDIN'  in [src[0] for src in in_batches_src] else None,  # [fix] - cmdparserと密結合すぎる
            stdout = PIPE if 'STDOUT' == out_batch_dest[0]                  else None,
            stderr = None,
            cwd = cwd,
            env = env,
        )

    @staticmethod
    def _input_str(in_batch, in_record_sep):
        input_str = ''
        for i, record in enumerate(in_batch):
            input_str += record[0]  # [fix] - 複雑なrecorddefに対応してない
            input_str += in_record_sep   # [fix] - str is immutable, so addition is bad idea
        return input_str

    @staticmethod
    def _batches_to_file(in_record_sep, in_batches, in_batches_src):
        """Create files to store in-batches contents (if necessary)"""
        for i, in_src in enumerate(in_batches_src):
            if in_src[0] == 'FILE':
                (fd, path) = in_src[1]
                with fdopen(fd, 'w') as f:
                    input_str = BaseShellOperator._input_str(in_batches[i], in_record_sep)
                    f.write(input_str)

    @staticmethod
    def _batch_to_stdin(process, in_record_sep, in_batches, in_batches_src):
        """Write in-batch contents to `process` 's stdin (if necessary)

        :returns: True if stdin is used
        """
        for i, in_src in enumerate(in_batches_src):
            if in_src[0] == 'STDIN':
                input_str = BaseShellOperator._input_str(in_batches[i], in_record_sep)
                process.stdin.write(input_str)
                process.stdin.flush()
                return True
        return False

    @staticmethod
    def _output_str_stdout(process):
        process.stdout.flush()
        output_str = process.stdout.read()
        process.stdout.close()  # [fix] - 同期的な呼び出しならcloseしてもいいけど，daemonを考えるならcloseしないノリのメソッドにしたい
        return output_str

    @staticmethod
    def _out_str_to_batch(out_str, out_recdef, out_record_sep):
        out_recs = []
        for rec_str in out_str.split(out_record_sep):
            # ignore some string as record
            pat = BaseShellOperator._ignore_record_pat
            if pat and pat.match(rec_str):
                continue

            out_recs.append(Record(out_recdef, rec_str))   # これも複雑なrecdefには対応できてない

        out_batch = Batch(tuple(out_recs))
        return out_batch

    @staticmethod
    def _close_stdin(process):
        process.stdin.close()

    @staticmethod
    def _clean_in_files(in_batches_src):
        for in_src in in_batches_src:
            if in_src[0] == 'FILE':
                (fd, path) = in_src[1]
                remove(path)

    @staticmethod
    def _clean_out_file(out_batch_dest):
        if out_batch_dest[0] == 'FILE':
            (fd, path) = out_batch_dest[1]
            remove(path)