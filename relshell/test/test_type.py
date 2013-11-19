# -*- coding: utf-8 -*-
from nose.tools import *
from relshell.type import Type


def test_type_usage():
    """Shows how to use Type class."""
    eq_(str(Type('STRING')), 'STRING')

    eq_(Type.equivalent_relshell_type(-123), Type('INT'))


@raises(NotImplementedError)
def test_unsupported_type_init():
    Type('UNSUPPORTED_TYPE')


@raises(NotImplementedError)
def test_unsupported_type_equivalent():
    class X:
        pass
    Type.equivalent_relshell_type(X())
