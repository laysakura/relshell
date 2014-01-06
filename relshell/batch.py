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
        :param records: records
        :type records:  instance of `tuple`
        :raises: `TypeError` when any record has mismatched type with :param:`record_def`
        """
        # check each record type
        map(lambda r: Record._chk_type(record_def, r), records)

        self._rdef         = record_def
        self._records      = records
        self._records_iter = iter(records)

    def record_def(self):
        """Return instance of :class:`RecordDef`"""
        return self._rdef

    def __iter__(self):
        return self

    def next(self):
        """Return one of record in this batch in out-of-order.

        :raises: `StopIteration` when no more record is in this batch
        """
        return next(self._records_iter)

    def __str__(self):
        ret_str_list = ['(%s' % (os.linesep)]
        for i in xrange(len(self._records)):
            ret_str_list.append('    %s%s' % (self._records[i], os.linesep))
        ret_str_list.append(')%s' % (os.linesep))
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
