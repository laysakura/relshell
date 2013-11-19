# -*- coding: utf-8 -*-
"""
    relshell.batch
    ~~~~~~~~~~~~~~

    :synopsis: Set of records.

    A `Batch` is passed to an operator at-a-time internally.
"""
try:
    from Queue import Queue
except ImportError:
    from queue import Queue


class Batch(object):
    """Set of records"""
    def __init__(self, record_q):
        """Create an *immutable* batch of records

        :param record_q: records
        :type record_q:  instance of `Queue.Queue`
        """
        assert(isinstance(record_q, Queue))

        self._record_q = record_q
        self._record_q.put(None)  # last element must be `None`

    def __iter__(self):
        return self

    def next(self):
        """Return one of record in this batch in out-of-order.

        :raises: `StopIteration` when no more record is in this batch
        """
        record = self._record_q.get()
        if record is None:
            raise StopIteration
        return record
