# -*- coding: utf-8 -*-
from nose.tools import *
from relshell.type import Type


def test_type_usage():
    eq_(str(Type('STRING')), 'STRING')
    eq_(Type.equivalent_relshell_type(-123), Type('INT'))


def test_cast():
    eq_(Type('INT').   python_cast('12345'), 12345)
    eq_(Type('STRING').python_cast(6789),    '6789')


@raises(NotImplementedError)
def test_unsupported_type_init():
    Type('UNSUPPORTED_TYPE')


@raises(NotImplementedError)
def test_unsupported_type_equivalent():
    class X:
        pass
    Type.equivalent_relshell_type(X())
