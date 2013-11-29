# -*- coding: utf-8 -*-
"""
    relshell.daemon_shelloperator
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides `DaemonShellOperator`
"""
import shlex
import re
import os
import fcntl
import time
from subprocess import Popen, PIPE
from relshell.base_shelloperator import BaseShellOperator


class DaemonShellOperator(BaseShellOperator):
    """Instanciate process and keep it running.

    `DaemonShellOperator` can instanciate processes which satisfy the following constraints:

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
        batch_done_indicator,
        batch_done_output,

        # kw & common w/ BaseShellOperator param
        cwd=None,
        env=None,
        in_record_sep='\n',
        out_record_sep='\n',
        ignore_record_pat=re.compile(r'^\s*$'),

        # kw & original param
   ):
        """Constuctor

        :raises: `AttributeError` if `cmd` doesn't seem to satisfy `constraints <relshell.daemon_shelloperator.DaemonShellOperator>`_
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

        self._batch_done_indicator = batch_done_indicator
        self._batch_done_output    = batch_done_output
        self._process = None

        if not self._batcmd.has_input_from_stdin():
            raise AttributeError('Following command doesn\'t have input from stdin:\n$ %s' %
                                 (self._batcmd.sh_cmd))

    def run(self, in_batches):
        """Run shell operator synchronously to eat `in_batches`

        :param in_batches: `tuple` of batches to process
        """
        if len(in_batches) != len(self._batcmd.batch_to_file_s):
            raise AttributeError('len(in_batches) == %d, while %d IN_BATCH* are specified in command below:\n$ %s' %
                                 (len(in_batches), len(self._batcmd.batch_to_file_s), self._orig_cmd))

        # prepare & start process (if necessary)
        BaseShellOperator._batches_to_tmpfile(self._in_record_sep, in_batches, self._batcmd.batch_to_file_s)
        if self._process is None:
            self._process = DaemonShellOperator._start_process(self._batcmd, self._cwd, self._env)
        BaseShellOperator._batch_to_stdin(self._process, self._in_record_sep, in_batches, self._batcmd.batch_to_file_s)

        # pass batch-done indicator
        self._process.stdin.write(self._batch_done_indicator)

        # wait for batch separator & get its output
        out_str_list = []
        while True:
            self._process.stdout.flush()
            # stdout is set non-blocking in `DaemonShellOperator._start_process()`
            try:
                out_str_list.append(self._process.stdout.read())
            except IOError:  # no character available from stdout
                time.sleep(1e-3)
            if DaemonShellOperator._batch_done(''.join(out_str_list), self._batch_done_indicator):
                break
        out_str = ''.join(out_str_list)
        out_batch = BaseShellOperator._out_str_to_batch(out_str[:-(len(self._batch_done_indicator))],
                                                        self._out_recdef, self._out_record_sep)
        return out_batch

    def kill(self):
        """Kill instanciated process

        :raises: `AttributeError` if instanciated process doesn't seem to satisfy `constraints <relshell.daemon_shelloperator.DaemonShellOperator>`_
        """
        for b2f in self._batcmd.batch_to_file_s:
            if b2f.is_stdin():
                b2f.finish()
        self._process.wait()  # [todo] - check if process has successfully exited
                              # [todo] - if this call does not return, it means 2nd `constraints <relshell.daemon_shelloperator.DaemonShellOperator>`_ are not sutisfied => raise `AttributeError`
        for b2f in self._batcmd.batch_to_file_s:
            if b2f.is_tmpfile():
                b2f.finish()
        self._process = None

    def getpid(self):
        return self._process.pid if self._process else None

    @staticmethod
    def _start_process(batcmd, cwd, env):
        # using non-blocking stdout w/ buffer size 1.
        # See: http://stackoverflow.com/questions/8980050/persistent-python-subprocess
        p = Popen(
            shlex.split(batcmd.sh_cmd),
            stdin   = PIPE if batcmd.has_input_from_stdin() else None,
            stdout  = PIPE if batcmd.batch_from_file.is_stdout() else None,
            stderr  = None,
            cwd     = cwd,
            env     = env,
            bufsize = 1,
        )
        fcntl.fcntl(p.stdout.fileno(), fcntl.F_SETFL, os.O_NONBLOCK)
        return p

    @staticmethod
    def _batch_done(process_output_str, batch_done_indicator):
        mat_idx = process_output_str.rfind(batch_done_indicator)
        return mat_idx >= 0 and mat_idx + len(batch_done_indicator) == len(process_output_str)
