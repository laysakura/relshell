# -*- coding: utf-8 -*-
from nose.tools import *
try:
    from Queue import Queue
except ImportError:
    from queue import Queue
from relshell.record import Record
from relshell.recorddef import RecordDef
from relshell.batch import Batch


def test_batch_usage():
    # create batch
    rdef = RecordDef([{'name': 'col0', 'type': 'INT'}])

    q = Queue()
    q.put(Record(rdef, 123))
    q.put(Record(rdef, 123))
    q.put(Record(rdef, 123))

    batch = Batch(q)

    # fetch records from batch
    for record in batch:
        eq_(record[0], 123)
