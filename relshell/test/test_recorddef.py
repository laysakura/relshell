# -*- coding: utf-8 -*-
from nose.tools import *
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
    eq_(len(rdef), 2)
    eq_(rdef[0].name, 'col0')
    eq_(rdef[0].type, Type('STRING'))


@raises(AttributeError)
def test_recorddef_required_key_lacks():
    rdef = RecordDef([
        {
        },  # at least 'name' is required
    ])


@raises(AttributeError)
def test_recorddef_unsupported_key():
    rdef = RecordDef([
        {
            'name': 'col0',
            'xyz' : 'yeah',
        },
    ])


@raises(AttributeError)
def test_recorddef_name_invalid():
    rdef = RecordDef([
        {
            'name': 'invalid-col',
        },
    ])


@raises(AttributeError)
def test_recorddef_type_invalid():
    rdef = RecordDef([
        {
            'name': 'col0',
            'type': 'SUPER_TYPE'
        },
    ])
