# -*- coding: utf-8 -*-
from nose.tools import *
import re
from relshell.recorddef import RecordDef
from relshell.record import Record
from relshell.batch import Batch
from relshell.shelloperator import ShellOperator


def _simple_recdef():
    return RecordDef([{'name': 'text', 'type': 'STRING'}])


def _diff_recdef():
    return RecordDef([
        {'name': 'position',
         'type': 'STRING',
        },
        {'name': 'diff',
         'type': 'STRING',
        },
    ])


def _create_batch():
    rdef = _simple_recdef()
    return Batch((
        Record(rdef, 'test1'),
        Record(rdef, 'test2'),
        Record(rdef, 'test3'),
        Record(rdef, 'test4'),
    ))


def _create_batch_diff():
    rdef = _simple_recdef()
    return Batch((
        Record(rdef, 'test1'),
        Record(rdef, 'test2xx'),
        Record(rdef, 'test3'),
        Record(rdef, 'test4yy'),
    ))


def test_output_2in_1out():
    batch0 = _create_batch()
    batch1 = _create_batch_diff()

    op = ShellOperator(
        'diff IN_BATCH0 IN_BATCH1 > OUT_BATCH',
        out_record_def=_diff_recdef(),
        success_exitcodes=(0, 1),
        out_col_patterns={   # defaultでは r'^.*$\n' にするって感じ
            'position': re.compile(r'''
                # diff position
                (
                    \d (,\d)? [acd] \d (,\d)?
                )
            ''', re.VERBOSE | re.MULTILINE),

            'diff': re.compile(r'''
                # diff content
                (
                    (^[<>] .*?$\n)+
                    (
                        ^---$\n
                        (^> .*?$\n)*
                    )?
                )
            ''', re.VERBOSE | re.MULTILINE)
        }
    )
    out_batch = op.run(in_batches=(batch0, batch1))
    eq_(out_batch,
        Batch((
            Record(
                _diff_recdef(),
                '2c2',
'''< test2
---
> test2xx
''',
            ),

            Record(
                _diff_recdef(),
                '4c4',
'''< test4
---
> test4yy
''',
            ),
        ))
    )


def test_output_batch_cascade():
    op = ShellOperator(
        'cat < IN_BATCH0 > OUT_BATCH',
        out_record_def=RecordDef([{'name': 'text', 'type': 'STRING'}]),
        out_col_patterns={'text': re.compile(r'^.+$', re.MULTILINE)},
    )
    batch_a = _create_batch()
    batch_b = op.run(in_batches=(batch_a, ))
    eq_(batch_b, batch_a)
