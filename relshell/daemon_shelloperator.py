# -*- coding: utf-8 -*-
"""
    relshell.daemon_shelloperator
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides `DaemonShellOperator`
"""
from relshell.shelloperator import ShellOperator


class DaemonShellOperator(ShellOperator):
    """DaemonShellOperator"""

    def __init__(  # [fix] - how to be in-sync w/ parameters of ShellOperator.__init__
                   # [fix] - (when new parameters are added to ShellOperator.__init__)?
        cmd,
        out_record_def,
        cwd=None,
        env=None,
        in_record_sep='\n',
        out_record_sep='\n',

            # バッチの終わりに in_batch_sep をあえて入れさせて，それに対するprocessの出力をみてやり，バッチ処理が終わったかを判定 (enjuの場合は'Empty Line\n\n'ってのが出る)
   ):
        pass
