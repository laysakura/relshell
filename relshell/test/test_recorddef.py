# -*- coding: utf-8 -*-
import nose.tools as ns
from relshell.recorddef import RecordDef
from relshell.type import Type


def test_recorddef_usage():
    """Shows how to use RecordDef class."""
    rdef = RecordDef([
        {'name': 'col0',
         'type': 'STRING',
        },
        {'name': 'col1',
        },
    ])
    ns.eq_(len(rdef), 2)
    ns.eq_(rdef[0].name, 'col0')
    ns.eq_(rdef[0].type, Type('STRING'))


@ns.raises(AttributeError)
def test_recorddef_required_key_lacks():
    rdef = RecordDef([
        {
        },  # at least 'name' is required
    ])


@ns.raises(AttributeError)
def test_recorddef_unsupported_key():
    rdef = RecordDef([
        {
            'name': 'col0',
            'xyz' : 'yeah',
        },
    ])


@ns.raises(AttributeError)
def test_recorddef_name_invalid():
    rdef = RecordDef([
        {
            'name': 'invalid-col',
        },
    ])


@ns.raises(AttributeError)
def test_recorddef_type_invalid():
    rdef = RecordDef([
        {
            'name': 'col0',
            'type': 'SUPER_TYPE'
        },
    ])


def test_recorddef_equality():
    rdef0 = RecordDef([
        {
            'name': 'col0',
            'type': 'STRING',
        },
    ])
    rdef1 = RecordDef([
        {
            'type': 'STRING',
            'name': 'col0',
        },
    ])
    rdef2 = RecordDef([
        {
            'name': 'col0',
            'type': 'STRING'
        },
        {
            'name': 'col1',
            'type': 'STRING'
        },
    ])
    ns.ok_(rdef0 == rdef1)
    ns.ok_(rdef0 != rdef2)


def test_colindex_by_colname():
    rdef = RecordDef([{'name': 'col0'}, {'name': 'col1'}])
    ns.eq_(rdef.colindex_by_colname('col0'), 0)
    ns.eq_(rdef.colindex_by_colname('col1'), 1)


@ns.raises(ValueError)
def test_colindex_by_colname_invalid():
    rdef = RecordDef([{'name': 'col0'}, {'name': 'col1'}])
    i    = rdef.colindex_by_colname('invalid_name')
