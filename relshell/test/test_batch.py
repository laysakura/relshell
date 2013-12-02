# -*- coding: utf-8 -*-
from nose.tools import *
from relshell.record import Record
from relshell.recorddef import RecordDef
from relshell.batch import Batch


def test_batch_usage():
    # create batch
    rdef = RecordDef([{'name': 'col0', 'type': 'INT'}])
    batch = Batch((
        Record(rdef, 123),
        Record(rdef, 123),
        Record(rdef, 123),
    ))

    # fetch records from batch
    for record in batch:
        eq_(record[0], 123)


def test_batch_equality():
    rdef = RecordDef([{'name': 'col0', 'type': 'INT'}])
    batch0 = Batch((
        Record(rdef, 123),
        Record(rdef, 123),
        Record(rdef, 123),
    ))
    batch1 = Batch((
        Record(rdef, 123),
        Record(rdef, 123),
        Record(rdef, 123),
    ))
    batch2 = Batch((
        Record(rdef, 123),
        Record(rdef, 789),
        Record(rdef, 123),
    ))
    batch4 = Batch((
        Record(rdef, 123),
        Record(rdef, 123),
        Record(rdef, 123),
        Record(rdef, 123),
    ))
    ok_(batch0 == batch1)
    ok_(batch0 != batch2)
    ok_(batch0 != batch4)
