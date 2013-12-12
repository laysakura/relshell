# -*- coding: utf-8 -*-
"""
    relshell.daemon_shelloperator
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides `DaemonShellOperator`
"""
import os
import logging
import time
from relshell.base_shelloperator import BaseShellOperator


class DaemonShellOperator(BaseShellOperator):
    """Instantiate process and keep it running.

    `DaemonShellOperator` can instantiate processes which satisfy the following constraints:

    1. Inputs records from `stdin`
    2. Safely dies when `EOF` is input
    3. Outputs deterministic string when inputting a specific record string.
       Pair of "specific record string" & "deterministic string" is used as a separtor to distinguish each batch.
       e.g. `cat` process outputs *LAST_RECORD_OF_BATCH\n* when inputting *LAST_RECORD_OF_BATCH\n*

    Future support
    --------------

    Above constraints are losen like below in future:

    1. Support input-records from file if file is only appended
    2. Support non-`EOF` process terminator (e.g. `exit\n` command for some intreractive shell)
    """

    def __init__(
        self,

        # non-kw & common w/ BaseShellOperator param
        cmd,
        out_record_def,

        # non-kw & original param
        out_col_patterns,
        batch_done_indicator,
        batch_done_output,

        # kw & common w/ BaseShellOperator param
        success_exitcodes=(0, ),
        cwd=None,
        env=os.environ,
        in_record_sep=os.linesep,
        in_column_sep=' ',

        # kw & original param
   ):
        """Constuctor

        :raises: `AttributeError` if `cmd` doesn't seem to satisfy `constraints <relshell.daemon_shelloperator.DaemonShellOperator>`_
        """
        BaseShellOperator.__init__(
            self,
            cmd,
            out_record_def,
            success_exitcodes,
            cwd,
            env,
            in_record_sep,
            in_column_sep,
            out_col_patterns,
        )

        self._batch_done_indicator = batch_done_indicator
        self._batch_done_output    = batch_done_output
        self._process = None

        if not self._batcmd.has_input_from_stdin():
            BaseShellOperator._rm_process_input_tmpfiles(self._batcmd.batch_to_file_s)  # [todo] - Removing tmpfiles can be easily forgot. Less lifetime for tmpfile.
            raise AttributeError('Following command doesn\'t have input from stdin:%s$ %s' %
                                 (os.linesep, self._batcmd.sh_cmd))

    def run(self, in_batches):
        """Run shell operator synchronously to eat `in_batches`

        :param in_batches: `tuple` of batches to process
        """
        if len(in_batches) != len(self._batcmd.batch_to_file_s):
            BaseShellOperator._rm_process_input_tmpfiles(self._batcmd.batch_to_file_s)  # [todo] - Removing tmpfiles can be easily forgot. Less lifetime for tmpfile.
            raise AttributeError('len(in_batches) == %d, while %d IN_BATCH* are specified in command below:%s$ %s' %
                                 (len(in_batches), len(self._batcmd.batch_to_file_s), os.linesep, self._batcmd.sh_cmd))

        # prepare & start process (if necessary)
        BaseShellOperator._batches_to_tmpfile(self._in_record_sep, self._in_column_sep, in_batches, self._batcmd.batch_to_file_s)
        if self._process is None:
            self._process = BaseShellOperator._start_process(
                self._batcmd, self._cwd, self._env,
                non_blocking_stdout=True)
        BaseShellOperator._batch_to_stdin(self._process, self._in_record_sep, self._in_column_sep, in_batches, self._batcmd.batch_to_file_s)

        # pass batch-done indicator
        self._process.stdin.write(self._batch_done_indicator)

        # wait for batch separator & get its output
        out_str_list = []
        while True:
            self._process.stdout.flush()
            try:
                out_str_list.append(self._process.stdout.read())
            except IOError:  # no character available from stdout
                time.sleep(1e-3)
            batch_done_output_spos = DaemonShellOperator._batch_done_start_pos(''.join(out_str_list), self._batch_done_output)
            if batch_done_output_spos >= 0:
                break
        out_str = ''.join(out_str_list)
        out_batch = BaseShellOperator._out_str_to_batch(out_str[:batch_done_output_spos],
                                                        self._out_recdef, self._out_col_patterns)
        return out_batch

    def kill(self):
        """Kill instantiated process

        :raises: `AttributeError` if instantiated process doesn't seem to satisfy `constraints <relshell.daemon_shelloperator.DaemonShellOperator>`_
        """
        BaseShellOperator._close_process_input_stdin(self._batcmd.batch_to_file_s)
        BaseShellOperator._wait_process(self._process, self._batcmd.sh_cmd, self._success_exitcodes)
        BaseShellOperator._rm_process_input_tmpfiles(self._batcmd.batch_to_file_s)
        self._process = None

    def getpid(self):
        return self._process.pid if self._process else None

    @staticmethod
    def _batch_done_start_pos(process_output_str, batch_done_output):
        return process_output_str.rfind(batch_done_output)
