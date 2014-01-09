# -*- coding: utf-8 -*-
"""
    relshell.batch
    ~~~~~~~~~~~~~~

    :synopsis: Set of records.

    A `Batch` is passed to an operator at-a-time internally.
"""
import os
from relshell.record import Record


class Batch(object):
    """Set of records"""
    def __init__(self, record_def, records):
        """Create an *immutable* batch of records

        :param record_def: instance of `RecordDef <#relshell.recorddef.RecordDef>`_
        :param records: records. Leftmost element is oldest (has to be treated earlier).
        :type records:  instance of `tuple`
        :raises: `TypeError` when any record has mismatched type with :param:`record_def`
        """
        # check each record type
        map(lambda r: Record._chk_type(record_def, r), records)

        self._rdef         = record_def
        self._records      = records
        self._records_iter = 0    # column number to iterate over

    def record_def(self):
        """Return instance of :class:`RecordDef`"""
        return self._rdef

    def __iter__(self):
        return self

    def next(self):
        """Return one of record in this batch in out-of-order.

        :raises: `StopIteration` when no more record is in this batch
        """
        if self._records_iter >= len(self._records):
            raise StopIteration
        self._records_iter += 1
        return self._records[self._records_iter - 1]

    def __str__(self):
        return self.formatted_str('json')

    def formatted_str(self, format):
        """Return formatted str.

        :param format: one of 'json', 'csv' are supported
        """
        assert(format in ('json', 'csv'))
        ret_str_list = []
        for rec in self._records:
            if format == 'json':
                ret_str_list.append('{')
                for i in xrange(len(rec)):
                    colname, colval = self._rdef[i].name, rec[i]
                    ret_str_list.append('"%s":"%s"' % (colname, colval))
                    ret_str_list.append(',')
                ret_str_list.pop()  # drop last comma
                ret_str_list.append('}%s' % (os.linesep))
            elif format == 'csv':
                for i in xrange(len(rec)):
                    colval = rec[i]
                    ret_str_list.append('"%s"' % (colval))
                    ret_str_list.append(',')
                ret_str_list.pop()  # drop last comma
                ret_str_list.append('%s' % (os.linesep))
            else:
                assert(False)
        return ''.join(ret_str_list)

    def __eq__(self, other):
        if len(self._records) != len(other._records):
            return False
        for i in xrange(len(self._records)):
            if self._records[i] != other._records[i]:
                return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)
