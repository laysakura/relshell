# -*- coding: utf-8 -*-
from nose.tools import *
import shlex
from os import fdopen
from relshell.shelloperator import ShellOperator
from relshell.batch_command import BatchCommand


def test__parser_in_batches_src_no_IN_BATCH():
    batcmd = BatchCommand('cat')
    eq_(batcmd.sh_cmd, 'cat')
    eq_(batcmd.batch_srcs, ())


def test__parser_in_batches_src_stdin():
    batcmd = BatchCommand('cat < IN_BATCH0')
    eq_(batcmd.sh_cmd, 'cat')
    eq_(len(batcmd.batch_srcs), 1)
    assert_true(batcmd.batch_srcs[0].from_stdin())


def test__parser_in_batches_src_file():
    batcmd = BatchCommand('diff IN_BATCH0 IN_BATCH1')

    cmd_array = shlex.split(batcmd.sh_cmd)
    eq_(len(cmd_array), 3)
    eq_(cmd_array[0], 'diff')

    assert_true(batcmd.batch_srcs[0].from_tmpfile())
    assert_true(batcmd.batch_srcs[1].from_tmpfile())

    for src in batcmd.batch_srcs:
        src.write_tmpfile('some batch contents')

    for src in batcmd.batch_srcs:
        src.finish()


@raises(IndexError)
def test__parser_in_batches_src_bad_index():
    BatchCommand('diff IN_BATCH1 IN_BATCH2')


@raises(IndexError)
def test__parser_in_batches_src_duplicated_index():
    BatchCommand('diff IN_BATCH0 IN_BATCH0')


# def test__parser_out_batch_dest_no_OUT_BATCH():
#     cmd_array = shlex.split('cat')
#     (cmd_array, out_batch_dest) = _parse_out_batch_dest(cmd_array)
#     eq_(' '.join(cmd_array), 'cat')
#     eq_(out_batch_dest, ())


# def test__parser_out_batch_dest_stdout():
#     cmd_array = shlex.split('cat a.txt > OUT_BATCH')
#     (cmd_array, out_batch_dest) = _parse_out_batch_dest(cmd_array)
#     eq_(' '.join(cmd_array), 'cat a.txt')
#     eq_(out_batch_dest, ('STDOUT', ))


# def test__parser_out_batch_dest_file():
#     batcmd = BatchCommand('make -o OUT_BATCH')
#     eq_(len(shlex.split(batcmd.sh_cmd)), 3)
#     eq_(batcmd.sh_cmd[:7], 'make -o')

#     assert_true(batcmd.to_file())

#     cmd_array = shlex.split('make -o OUT_BATCH')
#     (cmd_array, out_batch_dest) = _parse_out_batch_dest(cmd_array)
#     eq_(len(cmd_array), 3)
#     eq_(' '.join(cmd_array)[:7], 'make -o')
#     eq_(out_batch_dest[0], 'FILE')
#     (fd, path) = out_batch_dest[1]
#     with fdopen(fd, 'r') as f:
#         f.read()
#         ok_(isinstance(path, str))  # whether  is tmpfile path
#     ShellOperator._clean_out_file(out_batch_dest)


# @raises(IndexError)
# def test__parser_out_batch_dest_duplicated_OUT_BATCH():
#     cmd_array = shlex.split('make -o OUT_BATCH > OUT_BATCH')
#     (cmd_array, out_batch_dest) = _parse_out_batch_dest(cmd_array)


# def test_parse_usage():
#     eq_(
#         parse('cat < IN_BATCH0 > OUT_BATCH'),
#         {
#             'cmd_array'      : ['cat'],
#             'in_batches_src' : (('STDIN', ), ),
#             'out_batch_dest' : ('STDOUT', ),
#         }
#     )


# def test_parse_diff():
#     cmddict = parse('diff IN_BATCH0 IN_BATCH1 > OUT_BATCH')
#     eq_(cmddict['cmd_array'][0]         , 'diff')
#     eq_(cmddict['in_batches_src'][0][0] , 'FILE')
#     eq_(cmddict['in_batches_src'][1][0] , 'FILE')
#     eq_(cmddict['out_batch_dest']       , ('STDOUT', ))
#     ShellOperator._clean_in_files(cmddict['in_batches_src'])
