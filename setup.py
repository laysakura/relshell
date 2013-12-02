#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup


setup(
    name             = 'relshell',
    description      = '[under development] A framework to manage shell commands\' inputs/outputs as relational data.',
    long_description = open('README.rst').read(),
    url              = 'https://github.com/laysakura/relshell',
    license          = 'LICENSE.txt',
    version          = '0.0.2',
    author           = 'Sho Nakatani',
    author_email     = 'lay.sakura@gmail.com',
    test_suite       = 'nose.collector',
    install_requires = [
    ],
    tests_require    = [
        'nose',
        'coverage',
        'nose-cov',
        'nose-parameterized',
    ],
    packages         = [
        'relshell',
        'relshell.test'
    ],
    scripts          = [
    ],
    classifiers      = '''
Programming Language :: Python
Development Status :: 1 - Planning
License :: OSI Approved :: Apache Software License
Programming Language :: Python :: 2.7
Operating System :: POSIX :: Linux
'''.strip().splitlines()
)
