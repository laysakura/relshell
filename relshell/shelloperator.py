# -*- coding: utf-8 -*-
"""
    relshell.shelloperator
    ~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides `ShellOperator`
"""
import os
from relshell.base_shelloperator import BaseShellOperator


class ShellOperator(BaseShellOperator):
    """ShellOperator
    """

    def __init__(
        self,

        # non-kw & common w/ BaseShellOperator param
        cmd,
        out_record_def,

        # non-kw & original param
        out_col_patterns,

        # kw & common w/ BaseShellOperator param
        success_exitcodes=(0, ),
        cwd=None,
        env=os.environ,
        in_record_sep=os.linesep,
        in_column_sep=' ',

        # kw & original param
    ):
        """Constructor
        """
        BaseShellOperator.__init__(
            self,
            cmd,
            out_record_def,
            success_exitcodes,
            cwd,
            env,
            in_record_sep,
            in_column_sep,  # [fix] - 複数カラムを1レコードに(文字列に)落し込むとき，各カラムの区切りが同一である必要はない．sprintfみたいにformat指定できるべき．
            out_col_patterns,
        )

    def run(self, in_batches):
        """Run shell operator synchronously to eat `in_batches`

        :param in_batches: `tuple` of batches to process
        """
        if len(in_batches) != len(self._batcmd.batch_to_file_s):
            BaseShellOperator._rm_process_input_tmpfiles(self._batcmd.batch_to_file_s)  # [todo] - Removing tmpfiles can be easily forgot. Less lifetime for tmpfile.
            raise AttributeError('len(in_batches) == %d, while %d IN_BATCH* are specified in command below:%s$ %s' %
                                 (len(in_batches), len(self._batcmd.batch_to_file_s), os.linesep, self._batcmd.sh_cmd))

        # prepare & start process
        BaseShellOperator._batches_to_tmpfile(self._in_record_sep, self._in_column_sep, in_batches, self._batcmd.batch_to_file_s)
        process = BaseShellOperator._start_process(self._batcmd, self._cwd, self._env)
        BaseShellOperator._batch_to_stdin(process, self._in_record_sep, self._in_column_sep, in_batches, self._batcmd.batch_to_file_s)

        # wait process & get its output
        BaseShellOperator._close_process_input_stdin(self._batcmd.batch_to_file_s)
        BaseShellOperator._wait_process(process, self._batcmd.sh_cmd, self._success_exitcodes)
        BaseShellOperator._rm_process_input_tmpfiles(self._batcmd.batch_to_file_s)

        if self._batcmd.batch_from_file.is_stdout():
            out_str = self._batcmd.batch_from_file.read_stdout(process.stdout)
        elif self._batcmd.batch_from_file.is_tmpfile():
            out_str = self._batcmd.batch_from_file.read_tmpfile()
        else:  # pragma: no cover
            assert(False)

        out_batch = BaseShellOperator._out_str_to_batch(out_str, self._out_recdef, self._out_col_patterns)
        self._batcmd.batch_from_file.finish()
        return out_batch
