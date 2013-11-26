# -*- coding: utf-8 -*-
from nose.tools import *
import shlex
from os import fdopen, remove
from relshell.cmdparser import parse, _parse_in_batches_src, _parse_out_batch_dest


def test__parser_in_batches_src_no_IN_BATCH():
    cmd_array = shlex.split('cat')
    (cmd_array, in_batches_src) = _parse_in_batches_src(cmd_array)
    eq_(' '.join(cmd_array), 'cat')
    eq_(in_batches_src, ())


def test__parser_in_batches_src_stdin():
    cmd_array = shlex.split('cat < IN_BATCH0')
    (cmd_array, in_batches_src) = _parse_in_batches_src(cmd_array)
    eq_(' '.join(cmd_array), 'cat')
    eq_(in_batches_src, (('STDIN', ), ))


def test__parser_in_batches_src_file():
    cmd_array = shlex.split('diff IN_BATCH0 IN_BATCH1')
    (cmd_array, in_batches_src) = _parse_in_batches_src(cmd_array)
    eq_(len(cmd_array), 3)
    eq_(' '.join(cmd_array)[:4], 'diff')
    for src in in_batches_src:
        eq_(src[0], 'FILE')
        (fd, path) = src[1]
        with fdopen(fd, 'w') as f:
            f.write('batch contents')
            ok_(isinstance(path, str))  # whether  is tmpfile path
        remove(path)  # tmpfile must be removed by caller


@raises(IndexError)
def test__parser_in_batches_src_bad_index():
    cmd_array = shlex.split('diff IN_BATCH1 IN_BATCH2')
    (cmd_array, in_batches_src) = _parse_in_batches_src(cmd_array)


@raises(IndexError)
def test__parser_in_batches_src_duplicated_index():
    cmd_array = shlex.split('diff IN_BATCH0 IN_BATCH0')
    (cmd_array, in_batches_src) = _parse_in_batches_src(cmd_array)


def test__parser_out_batch_dest_no_OUT_BATCH():
    cmd_array = shlex.split('cat')
    (cmd_array, out_batch_dest) = _parse_out_batch_dest(cmd_array)
    eq_(' '.join(cmd_array), 'cat')
    eq_(out_batch_dest, ())


def test__parser_out_batch_dest_stdout():
    cmd_array = shlex.split('cat a.txt > OUT_BATCH')
    (cmd_array, out_batch_dest) = _parse_out_batch_dest(cmd_array)
    eq_(' '.join(cmd_array), 'cat a.txt')
    eq_(out_batch_dest, ('STDOUT', ))


def test__parser_out_batch_dest_file():
    cmd_array = shlex.split('make -o OUT_BATCH')
    (cmd_array, out_batch_dest) = _parse_out_batch_dest(cmd_array)
    eq_(len(cmd_array), 3)
    eq_(' '.join(cmd_array)[:7], 'make -o')
    eq_(out_batch_dest[0], 'FILE')
    (fd, path) = out_batch_dest[1]
    with fdopen(fd, 'r') as f:
        f.read()
        ok_(isinstance(path, str))  # whether  is tmpfile path
    remove(path)  # tmpfile must be removed by caller


@raises(IndexError)
def test__parser_out_batch_dest_duplicated_OUT_BATCH():
    cmd_array = shlex.split('make -o OUT_BATCH > OUT_BATCH')
    (cmd_array, out_batch_dest) = _parse_out_batch_dest(cmd_array)


def test_parse_usage():
    eq_(
        parse('cat < IN_BATCH0 > OUT_BATCH'),
        {
            'cmd_array'      : ['cat'],
            'in_batches_src' : (('STDIN', ), ),
            'out_batch_dest' : ('STDOUT', ),
        }
    )


def test_parse_diff():
    cmddict = parse('diff IN_BATCH0 IN_BATCH1 > OUT_BATCH')
    eq_(cmddict['cmd_array'][0], 'diff')
    eq_(cmddict['in_batches_src'][0][0], 'FILE')
    eq_(cmddict['in_batches_src'][1][0], 'FILE')
    eq_(cmddict['out_batch_dest'], ('STDOUT', ))
