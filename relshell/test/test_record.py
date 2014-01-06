# -*- coding: utf-8 -*-
from nose.tools import *
from relshell.record import Record


def test_record_usage():
    rec = Record('good evening')
    eq_(len(rec), 1)
    rec = Record('Hello', 'World')
    eq_(len(rec), 2)
    rec = Record('lucky', 777, 'number')
    eq_(len(rec), 3)

    # get column by index
    eq_(rec[0], 'lucky')

    # iterate all columns
    cols = []
    for col in rec:
        cols.append(col)
    eq_(cols, ['lucky', 777, 'number'])
