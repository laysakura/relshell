# -*- coding: utf-8 -*-
from nose.tools import *
from relshell.record import Record
from relshell.recorddef import RecordDef
from relshell.batch import Batch


def test_batch_usage():
    # create batch
    batch = Batch(
        RecordDef([{'name': 'col0', 'type': 'INT'}]),
        (Record(123), Record(123), Record(123), )
    )

    # fetch records from batch
    for record in batch:
        eq_(record[0], 123)


def test_batch_equality():
    rdef = RecordDef([{'name': 'col0', 'type': 'INT'}])
    batch0 = Batch(rdef, (
        Record(123),
        Record(123),
        Record(123),
    ))
    batch1 = Batch(rdef, (
        Record(123),
        Record(123),
        Record(123),
    ))
    batch2 = Batch(rdef, (
        Record(123),
        Record(789),
        Record(123),
    ))
    batch4 = Batch(rdef, (
        Record(123),
        Record(123),
        Record(123),
        Record(123),
    ))
    ok_(batch0 == batch1)
    ok_(batch0 != batch2)
    ok_(batch0 != batch4)


def test_json_format():
    rdef  = RecordDef([{'name': 'col0', 'type': 'INT'}, {'name': 'col1', 'type': 'STRING'}])
    batch = Batch(rdef, (
        Record(123, 'abc'),
        Record(456, 'def'),
    ))
    eq_(batch.formatted_str('json'),
'''{"col0":"123","col1":"abc"}
{"col0":"456","col1":"def"}
''')


def test_csv_format():
    rdef  = RecordDef([{'name': 'col0', 'type': 'INT'}, {'name': 'col1', 'type': 'STRING'}])
    batch = Batch(rdef, (
        Record(123, 'abc'),
        Record(456, 'def'),
    ))
    eq_(batch.formatted_str('csv'),
'''"123","abc"
"456","def"
''')


def test_auto_typing():
    rdef = RecordDef([
        {'name': 'col0', 'type': 'STRING'},
        {'name': 'col1'},      # any basic type is allowed
    ])
    batch = Batch(
        rdef,
        (Record('Hello', 'World'), Record('Hello', 777))
    )


@raises(TypeError)
def test_batch_mismatch_length():
    rdef  = RecordDef([{'name': 'col0', 'type': 'STRING'}])
    batch = Batch(rdef, Record('Hello', 'World'))


@raises(TypeError)
def test_batch_mismatch_type():
    rdef  = RecordDef([{'name': 'col0', 'type': 'INT'}])
    batch = Batch(rdef, Record('not convertible to INT'))


@raises(TypeError)
def test_batch_non_basic_type():
    class C:
        pass
    c = C  # c has too complex type as stream record

    rdef  = RecordDef([{'name': 'col0'}])
    batch = Batch(rdef, Record(c))
