# -*- coding: utf-8 -*-
from nose.tools import *
import shlex
from relshell.batch_command import BatchCommand


def test_batch_command_no_IN_BATCH():
    batcmd = BatchCommand('cat')
    eq_(batcmd.sh_cmd, 'cat')
    eq_(batcmd.batch_to_file_s, ())


def test_batch_command_stdin():
    batcmd = BatchCommand('cat < IN_BATCH0')
    eq_(batcmd.sh_cmd, 'cat')
    eq_(len(batcmd.batch_to_file_s), 1)
    assert_true(batcmd.batch_to_file_s[0].is_stdin())


def test_batch_command_input_file():
    batcmd = BatchCommand('diff IN_BATCH0 IN_BATCH1')

    cmd_array = shlex.split(batcmd.sh_cmd)
    eq_(len(cmd_array), 3)
    eq_(cmd_array[0], 'diff')

    assert_true(batcmd.batch_to_file_s[0].is_tmpfile())
    assert_true(batcmd.batch_to_file_s[1].is_tmpfile())

    for b2f in batcmd.batch_to_file_s:
        b2f.write_tmpfile('some batch contents')

    for b2f in batcmd.batch_to_file_s:
        b2f.finish()


@raises(IndexError)
def test_batch_command_bad_input_index():
    BatchCommand('diff IN_BATCH1 IN_BATCH2')


@raises(IndexError)
def test_batch_command_duplicated_input_index():
    BatchCommand('diff IN_BATCH0 IN_BATCH0')


# def test_batch_command_no_OUT_BATCH():
#     cmd_array = shlex.split('cat')
#     (cmd_array, out_batch_dest) = _parse_out_batch_dest(cmd_array)
#     eq_(' '.join(cmd_array), 'cat')
#     eq_(out_batch_dest, ())


# def test_batch_command_stdout():
#     cmd_array = shlex.split('cat a.txt > OUT_BATCH')
#     (cmd_array, out_batch_dest) = _parse_out_batch_dest(cmd_array)
#     eq_(' '.join(cmd_array), 'cat a.txt')
#     eq_(out_batch_dest, ('STDOUT', ))


# def test_batch_command_output_file():
#     batcmd = BatchCommand('make -o OUT_BATCH')
#     eq_(len(shlex.split(batcmd.sh_cmd)), 3)
#     eq_(batcmd.sh_cmd[:7], 'make -o')

#     assert_true(batcmd.out_batch_src.from_tmpfile())

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
# def test_batch_command_duplicated_OUT_BATCH():
#     cmd_array = shlex.split('make -o OUT_BATCH > OUT_BATCH')
#     (cmd_array, out_batch_dest) = _parse_out_batch_dest(cmd_array)
