# -*- coding: utf-8 -*-
"""
    relshell.base_shelloperator
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides abstract `BaseShellOperator`
"""
from abc import ABCMeta, abstractmethod
import shlex
from subprocess import Popen, PIPE
from relshell.record import Record
from relshell.batch import Batch
from relshell.batch_command import BatchCommand


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
        self._batcmd     = BatchCommand(cmd)
        self._out_recdef = out_record_def
        self._cwd        = cwd
        self._env        = env
        self._in_record_sep  = in_record_sep
        self._out_record_sep = out_record_sep
        if ignore_record_pat: BaseShellOperator._ignore_record_pat = ignore_record_pat

    @abstractmethod
    def run(self, in_batches):  # pragma: no cover
        """Run shell operator synchronously to eat `in_batches`

        :param in_batches: `tuple` of batches to process
        """
        pass

    @staticmethod
    def _start_process(batcmd, cwd, env):
        return Popen(
            shlex.split(batcmd.sh_cmd),
            stdin  = PIPE if batcmd.has_input_from_stdin() else None,
            stdout = PIPE if batcmd.batch_from_file.is_stdout() else None,
            stderr = None,
            cwd    = cwd,
            env    = env,
        )

    @staticmethod
    def _input_str(in_batch, in_record_sep):
        input_str_list = []
        for i, record in enumerate(in_batch):
            input_str_list.append(record[0])   # [fix] - 複雑なrecorddefに対応してない
            input_str_list.append(in_record_sep)
        return ''.join(input_str_list)

    @staticmethod
    def _batches_to_tmpfile(in_record_sep, in_batches, batch_to_file_s):
        """Create files to store in-batches contents (if necessary)"""
        for i, b2f in enumerate(batch_to_file_s):
            if b2f.is_tmpfile():
                input_str = BaseShellOperator._input_str(in_batches[i], in_record_sep)
                b2f.write_tmpfile(input_str)

    @staticmethod
    def _batch_to_stdin(process, in_record_sep, in_batches, batch_to_file_s):
        """Write in-batch contents to `process` 's stdin (if necessary)
        """
        for i, b2f in enumerate(batch_to_file_s):
            if b2f.is_stdin():
                input_str = BaseShellOperator._input_str(in_batches[i], in_record_sep)
                b2f.write_stdin(process.stdin, input_str)
                break  # at most 1 batch_to_file can be from stdin

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
    def _wait_process(process, sh_cmd):
        exitcode = process.wait()    # [todo] - if this call does not return, it means 2nd `constraints <relshell.daemon_shelloperator.DaemonShellOperator>`_ are not sutisfied => raise `AttributeError`
        if exitcode != 0:
            raise OSError('Following command ended with exitcode %d:\n$%s' % (exitcode, sh_cmd))

    @staticmethod
    def _close_process_input_stdin(batch_to_file_s):
        for b2f in batch_to_file_s:
            if b2f.is_stdin():
                b2f.finish()

    @staticmethod
    def _rm_process_input_tmpfiles(batch_to_file_s):
        for b2f in batch_to_file_s:
            if b2f.is_tmpfile():
                b2f.finish()
