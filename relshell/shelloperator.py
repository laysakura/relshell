# -*- coding: utf-8 -*-
"""
    relshell.shelloperator
    ~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides `ShellOperator`
"""
import shlex
import re
from relshell.base_shelloperator import BaseShellOperator


class ShellOperator(BaseShellOperator):
    """ShellOperator

    :param ignore_record_pat: ignore string which match w/ `ignore_record_pat` will not be output as record
    """

    _ignore_record_pat = None

    def __init__(
        self,

        # non-kw & common w/ BaseShellOperator param
        cmd,
        out_record_def,

        # non-kw & original param

        # kw & common w/ BaseShellOperator param
        cwd=None,
        env=None,
        in_record_sep='\n',
        out_record_sep='\n',  # [todo] - explain how this parameter is used (using diagram?)
                              # [todo] - in_record_sepの方が入力Recordを文字列にする際のもので，out_record_sepの方が出力文字列をRecordにする際のもの
        ignore_record_pat=re.compile(r'^\s*$')

        # kw & original param
    ):
        """Constructor

            :param ignore_record_pat: ignore string which match w/ `ignore_record_pat` will not be output as record (can be `None`)
        """
        BaseShellOperator.__init__(
            self,
            cmd,
            out_record_def,
            cwd,
            env,
            in_record_sep,
            out_record_sep,
            ignore_record_pat,
        )

    def run(self, in_batches):
        """Run shell operator synchronously to eat `in_batches`

        :param in_batches: `tuple` of batches to process
        """
        if len(in_batches) != len(self._batcmd.batch_to_file_s):
            for b2f in self._batcmd.batch_to_file_s:
                if b2f.is_tmpfile():
                    b2f.finish()  # [todo] - Removing tmpfiles can be easily forgot. Less lifetime for tmpfile.
            raise AttributeError('len(in_batches) == %d, while %d IN_BATCH* are specified in command below:\n$ %s' %
                                 (len(in_batches), len(self._batcmd.batch_to_file_s), self._orig_cmd))

        # prepare & start process
        BaseShellOperator._batches_to_tmpfile(self._in_record_sep, in_batches, self._batcmd.batch_to_file_s)
        process = BaseShellOperator._start_process(
            shlex.split(self._batcmd.sh_cmd),
            self._batcmd.batch_to_file_s,
            self._batcmd.batch_from_file,
            self._cwd, self._env,
        )
        BaseShellOperator._batch_to_stdin(process, self._in_record_sep, in_batches, self._batcmd.batch_to_file_s)

        # wait process & get its output
        for b2f in self._batcmd.batch_to_file_s:
            if b2f.is_stdin():
                b2f.finish()
        process.wait()  # [todo] - check if process has successfully exited
        for b2f in self._batcmd.batch_to_file_s:
            if b2f.is_tmpfile():
                b2f.finish()

        if self._batcmd.batch_from_file.is_stdout():
            out_str   = self._batcmd.batch_from_file.read_stdout(process.stdout)
            out_batch = BaseShellOperator._out_str_to_batch(out_str, self._out_recdef, self._out_record_sep)
            self._batcmd.batch_from_file.finish()
            return out_batch
        else:
            raise NotImplementedError
