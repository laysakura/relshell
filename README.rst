relshell
~~~~~~~~

.. image:: https://travis-ci.org/laysakura/relshell.png?branch=master
   :target: https://travis-ci.org/laysakura/relshell

A framework to manage shell commands' inputs/outputs as relational data.

For developers
==============

API documents
-------------

Sphinx-powered documents are available on http://packages.python.org/relshell


Building and uploading documents
--------------------------------

.. code-block:: bash

    $ ./setup.py build_sphinx
    $ browser doc/html/index.html
    $ ./setup.py upload_sphinx

Testing
-------

.. code-block:: bash

    $ ./setup.py nosetests
    $ browser htmlcov/index.html  # check coverage

Uploading packages to PyPI
--------------------------

.. code-block:: bash

    $ emacs setup.py   # edit `version` string
    $ emacs CHANGES.txt
    $ ./setup.py sdist upload


TODO
====

- relshellプロセス ===(thread)===> シェルオペレータ ===(fork)===> シェルコマンドプロセス という流れを作る(Queueもいるね)
- shellstreaming/README.rst にあるような感じで，batchをop間でやりとりできるようにする
- シェルプロセスは非同期でも扱いたい．そもそもpopenとかがそういうインターフェースだし．

- EOFを送る以外の終了方法もサポートする?
  - ファイルから読む系のプロセスは，普通にprocess.wait()だけで終わるはずなのでOK
  - いや，それ以外なら「ラッパー書いてね」でとりあえず済ませるか

- デバッグオプションをonにしたらどんな動作しているのかくらい出力してあげたい

- daemonizeできる条件
  - in_batchをstdinからとり，out_batchを(stdout|file)に出す
  - 「in_batch_xに対する出力分out_batch_xがここまでですよ」と定義できる(例えば，空行はout_batch_xの終わりですよ，とか)
    - enjuには使える
