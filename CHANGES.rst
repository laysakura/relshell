Changelog for nextversion
=========================

0.3.2 (unreleased)
------------------

- Raises exception when weird regex pattern is given


0.3.1 (2014-01-23)
------------------

- Supports TIMESTAMP type further


0.3.0 (2014-01-23)
------------------

- Supports TIMESTAMP type


0.2.11 (2014-01-22)
-------------------

- Bugfix: bug when multiple DaemonShellOperator exist is fixed


0.2.10 (2014-01-21)
-------------------

- Escape `"` when Batch.__str__() transforms batch into csv or json


0.2.9 (2014-01-21)
------------------

- DEBUG: DaemonShellOperator can input large batch


0.2.8 (2014-01-18)
------------------

- Outputs log when executing commands


0.2.7 (2014-01-09)
------------------

- Makes Batch picklable


0.2.6 (2014-01-09)
------------------

- Bugfix on Batch.__str__()


0.2.5 (2014-01-08)
------------------

- Adds RecordDef.colindex_by_colname()


0.2.4 (2014-01-07)
------------------

- Supports JSON & CSV batch output format


0.2.3 (2014-01-06)
------------------

- Not Record but Batch has RecordDef


0.2.2 (2013-12-12)
------------------

- ShellOperators inherit environmental variables


0.2.1 (2013-12-06)
------------------

- Updates README style


0.2.0 (2013-12-06)
------------------

- Beta release

0.1.2 (2013-12-04)
------------------

- Uploaded API reference (http://packages.python.org/relshell)

0.1.1
-----

- bugfix on DaemonShellOperator's batch_done_output management

0.1.0
-----

- first working version

0.0.2
-----

- added 'under development' notice

0.0.1
-----

- just start development
