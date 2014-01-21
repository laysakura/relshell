#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup


setup(
    name             = 'relshell',
    description      = '''A framework to manage shell commands\' inputs/outputs as relational data.''',
    long_description = open('README.rst').read(),
    url              = 'https://github.com/laysakura/relshell',
    license          = 'LICENSE.txt',
    version          = '0.2.10',
    author           = 'Sho Nakatani',
    author_email     = 'lay.sakura@gmail.com',
    test_suite       = 'nose.collector',
    install_requires = [
        'rainbow_logging_handler',
    ],
    tests_require    = [
        'nose',
        'coverage',
        'nose-cov',
        'nose-parameterized',
    ],
    packages         = [
        'relshell',
        'relshell.test',
    ],
    scripts          = [
    ],
    classifiers      = '''
Programming Language :: Python
Development Status :: 4 - Beta
License :: OSI Approved :: Apache Software License
Programming Language :: Python :: 2.6
Programming Language :: Python :: 2.7
Programming Language :: Python :: Implementation :: PyPy
Operating System :: POSIX :: Linux
'''.strip().splitlines()
)
