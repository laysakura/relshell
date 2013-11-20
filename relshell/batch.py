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

        self._records = iter(records)

    def __iter__(self):
        return self

    def next(self):
        """Return one of record in this batch in out-of-order.

        :raises: `StopIteration` when no more record is in this batch
        """
        return next(self._records)
