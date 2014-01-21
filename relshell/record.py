# -*- coding: utf-8 -*-
"""
    relshell.record
    ~~~~~~~~~~~~~~~

    :synopsis: Provides (typed|untyped) record structure.
"""
from relshell.type import Type


class Record(object):
    """Record."""

    # APIs
    def __init__(self, *columns):
        """Creates a record with `record_def` constraints.

        :param \*columns:     contents of columns
        """
        self._rec     = Record._internal_repl(columns)
        self._cur_col = 0  # Used for `next()`

    def __str__(self):
        """Returns string representation of record"""
        retstr_list = ['(']
        for i in xrange(len(self._rec)):
            retstr_list.append('"%s", ' % (self._rec[i]))
        retstr_list.append(')')
        return ''.join(retstr_list)

    def __len__(self):
        """Returns number of columns in record"""
        return len(self._rec)

    def __getitem__(self, index):
        """Returns column data specified by `index`"""
        return self._rec[index]

    def __iter__(self):
        return self

    def next(self):
        """Return a column one by one

        :raises: StopIteration
        """
        if self._cur_col >= len(self._rec):
            self._cur_col = 0
            raise StopIteration
        col = self._rec[self._cur_col]
        self._cur_col += 1
        return col

    def __eq__(self, other):
        return self._rec == other._rec

    def __ne__(self, other):
        return not self.__eq__(other)

    # Private functions
    @staticmethod
    def _internal_repl(columns):
        return tuple(columns)

    @staticmethod
    def _chk_type(recdef, rec):
        """Checks if type of `rec` matches `recdef`
        :param recdef: instance of RecordDef
        :param rec:    instance of Record
        :raises:       `TypeError`
        """
        if len(recdef) != len(rec):
            raise TypeError("Number of columns (%d) is different from RecordDef (%d)" % (len(rec), len(recdef)))

        for i in xrange(len(recdef)):
            try:
                def_type = recdef[i].type
                col_type = Type.equivalent_relshell_type(rec[i])
                if col_type != def_type:
                    raise TypeError("Column %d has mismatched type:  Got '%s' [%s] ; Expected [%s]" %
                                    (i, rec[i], col_type, def_type))
            except AttributeError as e:
                # recdef[i].type is not defined, then any relshell type is allowed
                try:
                    Type.equivalent_relshell_type(rec[i])
                except NotImplementedError as e:
                    raise TypeError("%s" % (e))
