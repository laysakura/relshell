# -*- coding: utf-8 -*-
import nose.tools as ns
import datetime as dt
from relshell.type import Type
from relshell.timestamp import Timestamp


def test_type_usage():
    ns.eq_(str(Type('STRING')), 'STRING')
    ns.eq_(Type.equivalent_relshell_type(-123), Type('INT'))


def test_types():
    ns.eq_(Type.equivalent_relshell_type(-123)                         , Type('INT'))
    ns.eq_(Type.equivalent_relshell_type('123')                        , Type('STRING'))
    ns.eq_(Type.equivalent_relshell_type(Timestamp(dt.datetime.now())) , Type('TIMESTAMP'))


def test_cast():
    ns.eq_(Type('INT').   python_cast('12345'), 12345)
    ns.eq_(Type('STRING').python_cast(6789),    '6789')


@ns.raises(NotImplementedError)
def test_unsupported_type_init():
    Type('UNSUPPORTED_TYPE')


@ns.raises(NotImplementedError)
def test_unsupported_type_equivalent():
    class X:
        pass
    Type.equivalent_relshell_type(X())
