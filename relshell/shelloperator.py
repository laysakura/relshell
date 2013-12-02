# -*- coding: utf-8 -*-
"""
    relshell.shelloperator
    ~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides `ShellOperator`
"""
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
        success_exitcodes=(0, ),
        cwd=None,
        env=None,
        in_record_sep='\n',
        ignore_record_pat=re.compile(r'^\s*$'),
        out_col_patterns=r'^.*$\n',

        # kw & original param
    ):
        """Constructor

            :param ignore_record_pat: ignore string which match w/ `ignore_record_pat` will not be output as record (can be `None`)
        """
        BaseShellOperator.__init__(
            self,
            cmd,
            out_record_def,
            success_exitcodes,
            cwd,
            env,
            in_record_sep,
            ignore_record_pat,
            out_col_patterns,
        )

    def run(self, in_batches):
        """Run shell operator synchronously to eat `in_batches`

        :param in_batches: `tuple` of batches to process
        """
        if len(in_batches) != len(self._batcmd.batch_to_file_s):
            BaseShellOperator._rm_process_input_tmpfiles(self._batcmd.batch_to_file_s)  # [todo] - Removing tmpfiles can be easily forgot. Less lifetime for tmpfile.
            raise AttributeError('len(in_batches) == %d, while %d IN_BATCH* are specified in command below:\n$ %s' %
                                 (len(in_batches), len(self._batcmd.batch_to_file_s), self._batcmd.sh_cmd))

        # prepare & start process
        BaseShellOperator._batches_to_tmpfile(self._in_record_sep, in_batches, self._batcmd.batch_to_file_s)
        process = BaseShellOperator._start_process(self._batcmd, self._cwd, self._env)
        BaseShellOperator._batch_to_stdin(process, self._in_record_sep, in_batches, self._batcmd.batch_to_file_s)

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
