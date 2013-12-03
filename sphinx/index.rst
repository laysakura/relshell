relshell API Reference
======================

ShellOperator
-------------
.. toctree::
   :maxdepth: 1
   :hidden:

   api/shelloperator

:synopsis: Provides ways to instantiate shell commands which input/output batches of typed data.

* :ref:`api-ShellOperator` - One-time shell command's instantiater.
  Shell command's process is run/killed per 1 batch processing.

* :ref:`api-DaemonShellOperator` - Daemonized shell command's instantiater.
  Shell command's process is daemonized and repeatedly inputs multiple batches.

Input/Output Data Structure
---------------------------
.. toctree::
   :maxdepth: 1
   :hidden:

   api/data_structure

:synopsis: ShellOperator's input/output data structure.

* :ref:`api-Batch` - Unit of `ShellOperator`'s input/output, composed of set of `Record`'s.

* :ref:`api-Record` - Unit of information, composed of columns. Each column is typed (like RDBMS).
