# -*- coding: utf-8 -*-
"""
    relshell.daemon_shelloperator
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides `DaemonShellOperator`
"""
import re
from relshell.base_shelloperator import BaseShellOperator


class DaemonShellOperator(BaseShellOperator):
    """DaemonShellOperator"""

    def __init__(  # [fix] - how to be in-sync w/ parameters of ShellOperator.__init__
                   # [fix] - (when new parameters are added to ShellOperator.__init__)?
        self,

        # non-kw & common w/ BaseShellOperator param
        cmd,
        out_record_def,

        # non-kw & original param
        in_batch_sep,
        batch_done_output,      # バッチの終わりに in_batch_sep をあえて入れさせて，
                                # それに対するprocessの出力をみてやり，バッチ処理が終わったかを判定
                                # (enjuの場合は'Empty Line\n\n'ってのが出る)

        # kw & common w/ BaseShellOperator param
        cwd=None,
        env=None,
        in_record_sep='\n',
        out_record_sep='\n',
        ignore_record_pat=re.compile(r'^\s*$'),

        # kw & original param
   ):
        self._in_batch_sep      = in_batch_sep
        self._batch_done_output = batch_done_output
        self._process = None

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

        # check if DaemonShellOperator's constraints are satisfied
        # ここらでself._cmddict['in_batches_src']を見て，ちゃんとSTDINからとるものがあるのかってのを見るのかな

    def run(self, in_batches):
        """Run shell operator synchronously to eat `in_batches`

        :param in_batches: `tuple` of batches to process
        """
        if len(in_batches) != len(self._cmddict['in_batches_src']):
            raise AttributeError('len(in_batches) == %d, while %d IN_BATCH* are specified in command below:\n$ %s' %
                                 (len(in_batches), len(self._cmddict['in_batches_src']), self._orig_cmd))

        # prepare & start process (if necessary)
        BaseShellOperator._batches_to_file(self._in_record_sep, in_batches, self._cmddict['in_batches_src'])
        if self._process is None:
            self._process = BaseShellOperator._start_process(
                self._cmddict['cmd_array'],
                self._cmddict['in_batches_src'],
                self._cmddict['out_batch_dest'],
                self._cwd, self._env,
            )
        using_stdin = BaseShellOperator._batch_to_stdin(self._process, self._in_record_sep, in_batches, self._cmddict['in_batches_src'])
        # assert(using_stdin)  # [fix] - initのparse方でちゃんと見てるので，ほんとはここで見る必要なし
        self._process.stdin.write(self._in_batch_sep)

        # wait for batch separator & get its output
        # ここで，stdoutの結果をpollして，文字列の終わりが`batch_done_output`に一致しているかどうかを見る
        import time
        out_str = ''  # [fix] - addition to str
        while True:
            # time.sleep(0.1)
            self._process.stdout.flush()
            out_str += self._process.stdout.read(1)
            mat_idx = out_str.rfind(self._batch_done_output)
            if mat_idx >= 0 and mat_idx + len(self._batch_done_output) == len(out_str):
                break
        out_batch = BaseShellOperator._out_str_to_batch(out_str[:mat_idx],
                                                        self._out_recdef, self._out_record_sep)
        return out_batch

        # if using_stdin:  # これいらなくなる
        #     BaseShellOperator._close_stdin(self._process)  # stdin has to recieve EOF explicitly (unlike file)



        # self._process.wait()  # [todo] - check if process has successfully exited
        # BaseShellOperator._clean_in_files(self._cmddict['in_batches_src'])  # [fix] - この辺はやる必要あるはず
        # if self._cmddict['out_batch_dest'][0] == 'STDOUT':
        #     out_str   = BaseShellOperator._output_str_stdout(self._process)
        #     out_batch = BaseShellOperator._out_str_to_batch(out_str, self._out_recdef, self._out_record_sep)
        #     return out_batch
        # else:
        #     raise NotImplementedError

    def kill(self):
        BaseShellOperator._close_stdin(self._process)
        self._process = None

    def getpid(self):
        return self._process.pid if self._process else None
