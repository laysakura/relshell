# -*- coding: utf-8 -*-
"""
    relshell.batch
    ~~~~~~~~~~~~~~

    :synopsis: Set of records.

    A `Batch` is passed to an operator at-a-time internally.
"""


class Batch(object):
    """Set of records"""
    def __init__(self, records):
        """Create an *immutable* batch of records

        :param records: records
        :type records:  instance of `tuple`
        """
        assert(isinstance(records, tuple))

        self._records      = records
        self._records_iter = iter(records)

    def __iter__(self):
        return self

    def next(self):
        """Return one of record in this batch in out-of-order.

        :raises: `StopIteration` when no more record is in this batch
        """
        return next(self._records_iter)

    def __str__(self):
        ret = '(\n'
        for i in xrange(len(self._records)):
            ret += '    %s\n' % (self._records[i])
        ret += ')\n'
        return ret

    def __eq__(self, other):
        if len(self._records) != len(other._records):
            return False
        for i in xrange(len(self._records)):
            if self._records[i] != other._records[i]:
                return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)
