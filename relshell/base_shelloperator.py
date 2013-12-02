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
from warnings import warn
from subprocess import Popen, PIPE
from relshell.record import Record
from relshell.batch import Batch
from relshell.batch_command import BatchCommand


class BaseShellOperator(object):
    """BaseShellOperator
    """
    __metaclass__ = ABCMeta

    def __init__(
        self,
        cmd,
        out_record_def,
        success_exitcodes,
        cwd,
        env,
        in_record_sep,  # [todo] - explain how this parameter is used (using diagram?)

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
        self._out_col_patterns  = out_col_patterns

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
        except OSError as e:
            raise OSError('Following command fails - %s:%s %s' % (e, os.linesep, batcmd.sh_cmd))

        if non_blocking_stdout:
            fcntl.fcntl(p.stdout.fileno(), fcntl.F_SETFL, os.O_NONBLOCK)

        return p

    @staticmethod
    def _input_str(in_batch, in_record_sep):
        input_str_list = []
        for i, record in enumerate(in_batch):
            input_str_list.append(record[0])   # [fix] - 複雑なrecorddefに対応してない
            input_str_list.append(in_record_sep)
        input_str_list[-1] = os.linesep   # remove last in_record_sep & adds newline at last (since POSIX requires it)
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
    def _out_str_to_batch(out_str, out_recdef, out_col_pat):
        print(out_str)
        out_recs = []

        # 1. out_col_patternsを使ってout_strから先頭一致していき，columnsを得る
        # 2. out_col_patternsが尽きたら，それがrecord．すなわち，out_record_sepなんていらない．
        pos = 0
        while pos < len(out_str):
            col_strs = []
            for col_def in out_recdef:
                col_name = col_def.name
                col_pat = out_col_pat[col_name]
                print('''Start matching ("%s"):%s
[pattern] %s

[output result]
%s
                    ''' % (col_name, os.linesep, col_pat.pattern, out_str[pos:]))
                mat = col_pat.search(out_str[pos:])  # [fix] - creating new string... any efficient way?
                if mat is None:
                    warn('''Following string does not match `out_col_patterns`, ignored:
%s''' % (out_str[pos:]))
#                     raise AttributeError('''Following pattern of column "%s" doesn\'t match to output result.
# [pattern]
# %s

# [output result]
# %s
#                     ''' % (col_name, col_pat.pattern, out_str))
                    break

                print('match!! => %s' % (mat.group()))
                pos = mat.end() + pos
                col_strs.append(mat.group())

            if len(col_strs) == 0:  # after skipping last redundunt strs
                break
            out_recs.append(Record(out_recdef, *col_strs))   # [fix] - これも複雑なrecdefには対応できてない

        # for rec_str in out_str.split(out_record_sep):
        #     # ignore some string as record
        #     pat = BaseShellOperator._ignore_record_pat
        #     if pat and pat.match(rec_str):
        #         continue

        #     out_recs.append(Record(out_recdef, rec_str, 'hoge'))   # [fix] - これも複雑なrecdefには対応できてない

        out_batch = Batch(tuple(out_recs))
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
