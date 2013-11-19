relshell
~~~~~~~~

.. image:: https://travis-ci.org/laysakura/relshell.png?branch=master
   :target: https://travis-ci.org/laysakura/relshell

A framework to manage shell commands' inputs/outputs as relational data.

TODO
====

- record, batch を timestamp から切り離す
- relshellプロセス ===(thread)===> シェルオペレータ ===(fork)===> シェルコマンドプロセス という流れを作る(Queueもいるね)
- shellstreaming/README.rst にあるような感じで，batchをop間でやりとりできるようにする
