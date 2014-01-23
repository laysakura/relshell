# -*- coding: utf-8 -*-
"""
    relshell.base_shelloperator
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides abstract `BaseShellOperator`
"""
from abc import ABCMeta, abstractmethod
import shlex
import os
import fcntl
from relshell.logger import Logger
from subprocess import Popen, PIPE
from relshell.record import Record
from relshell.batch import Batch
from relshell.batch_command import BatchCommand


class BaseShellOperator(object):
    """BaseShellOperator
    """
    __metaclass__ = ABCMeta

    _logger = None

    def __init__(
        self,
        cmd,
        out_record_def,
        success_exitcodes,
        cwd,
        env,
        in_record_sep,  # [todo] - explain how this parameter is used (using diagram?)
        in_column_sep,
        out_col_patterns,
    ):
        """Constructor
        """
        self._batcmd            = BatchCommand(cmd)
        self._out_recdef        = out_record_def
        self._success_exitcodes = success_exitcodes
        self._cwd               = cwd
        self._env               = env
        self._in_record_sep     = in_record_sep
        self._in_column_sep     = in_column_sep
        self._out_col_patterns  = out_col_patterns
        BaseShellOperator._logger = Logger.instance()

    @abstractmethod
    def run(self, in_batches):  # pragma: no cover
        """Run shell operator synchronously to eat `in_batches`

        :param in_batches: `tuple` of batches to process
        """
        pass

    @staticmethod
    def _start_process(batcmd, cwd, env, non_blocking_stdout=False):
        try:
            p = Popen(
                shlex.split(batcmd.sh_cmd),
                stdin  = PIPE if batcmd.has_input_from_stdin() else None,
                stdout = PIPE if batcmd.batch_from_file and batcmd.batch_from_file.is_stdout() else None,
                stderr = None,
                cwd    = cwd,
                env    = env,
                bufsize = 1 if non_blocking_stdout else 0,
            )
            BaseShellOperator._logger.info('[Command execution] $ %s' % (batcmd.sh_cmd))
        except OSError as e:
            raise OSError('Following command fails - %s:%s$ %s' % (e, os.linesep, batcmd.sh_cmd))

        if non_blocking_stdout:
            fcntl.fcntl(p.stdout.fileno(), fcntl.F_SETFL, os.O_NONBLOCK)

        return p

    @staticmethod
    def _input_str(in_batch, in_record_sep, in_column_sep):
        if len(in_batch) == 0:
            return ''

        input_str_list = []
        for record in in_batch:
            for col in record:
                input_str_list.append(str(col))
                input_str_list.append(in_column_sep)
            del input_str_list[-1]        # remove last in_column_sep
            input_str_list.append(in_record_sep)
        input_str_list[-1] = os.linesep   # remove last in_record_sep & adds newline at last (since POSIX requires it)
        return ''.join(input_str_list)

    @staticmethod
    def _batches_to_tmpfile(in_record_sep, in_column_sep, in_batches, batch_to_file_s):
        """Create files to store in-batches contents (if necessary)"""
        for i, b2f in enumerate(batch_to_file_s):
            if b2f.is_tmpfile():
                input_str = BaseShellOperator._input_str(in_batches[i], in_record_sep, in_column_sep)
                b2f.write_tmpfile(input_str)

    @staticmethod
    def _batch_to_stdin(process, in_record_sep, in_column_sep, in_batches, batch_to_file_s):
        """Write in-batch contents to `process` 's stdin (if necessary)
        """
        for i, b2f in enumerate(batch_to_file_s):
            if b2f.is_stdin():
                input_str = BaseShellOperator._input_str(in_batches[i], in_record_sep, in_column_sep)
                b2f.write_stdin(process.stdin, input_str)
                break  # at most 1 batch_to_file can be from stdin

    @staticmethod
    def _parse_record(str_to_parse, col_patterns, recdef):
        cols = []
        pos  = 0
        for col_def in recdef:
            col_name = col_def.name
            col_pat  = col_patterns[col_name]
            col_type = col_def.type
            mat = col_pat.search(str_to_parse[pos:])

            # no more record to parse
            if mat is None:
                BaseShellOperator._logger.debug('Following string does not match `out_col_patterns`, ignored: """%s"""'
                                                % (str_to_parse))
                return (None, None)

            # beginning substring is skipped
            if mat.start() > 0:
                BaseShellOperator._logger.debug('Following string does not match `out_col_patterns`, ignored: """%s"""'
                                                % (str_to_parse[:mat.start()]))

            pos += mat.end()
            col_str = mat.group()
            cols.append(col_type.python_cast(col_str))

        return (Record(*cols), pos)

    @staticmethod
    def _out_str_to_batch(out_str, out_recdef, out_col_patterns):
        out_recs = []
        pos = 0
        while True:
            (rec, rec_str_len) = BaseShellOperator._parse_record(out_str[pos:], out_col_patterns, out_recdef)
            if rec is None:
                break
            out_recs.append(rec)
            pos += rec_str_len
        out_batch = Batch(out_recdef, tuple(out_recs))
        return out_batch

    @staticmethod
    def _wait_process(process, sh_cmd, success_exitcodes):
        exitcode = process.wait()    # [todo] - if this call does not return, it means 2nd `constraints <relshell.daemon_shelloperator.DaemonShellOperator>`_ are not sutisfied => raise `AttributeError`
        if exitcode not in success_exitcodes:
            raise OSError('Following command ended with exitcode %d:%s$ %s' % (exitcode, os.linesep, sh_cmd))

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
