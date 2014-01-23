# -*- coding: utf-8 -*-
import nose.tools as ns
from relshell.type import Type
from relshell.timestamp import Timestamp


def test_type_usage():
    ns.eq_(str(Type('STRING')), 'STRING')
    ns.eq_(Type.equivalent_relshell_type(-123), Type('INT'))


def test_types():
    ns.eq_(Type.equivalent_relshell_type(-123)                   , Type('INT'))
    ns.eq_(Type.equivalent_relshell_type('123')                  , Type('STRING'))
    ns.eq_(Type.equivalent_relshell_type(Timestamp('2014-04-05')), Type('TIMESTAMP'))


def test_int_cast():
    ns.eq_(Type('INT').python_cast('12345'), 12345)


def test_str_cast():
    ns.eq_(Type('STRING').python_cast(6789), '6789')


def test_timestamp_cast():
    ns.eq_(Type('TIMESTAMP').python_cast('2014-08-27'),
           Timestamp('2014-08-27'))
    ns.eq_(Type('TIMESTAMP').python_cast('2014-08-27 19:30:00'),
           Timestamp('2014-08-27 19:30:00'))


@ns.raises(NotImplementedError)
def test_unsupported_type_init():
    Type('UNSUPPORTED_TYPE')


@ns.raises(NotImplementedError)
def test_unsupported_type_equivalent():
    class X:
        pass
    Type.equivalent_relshell_type(X())
