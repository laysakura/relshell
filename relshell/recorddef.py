# -*- coding: utf-8 -*-
"""
    relshell.recorddef
    ~~~~~~~~~~~~~~~~~~

    :synopsis: Provides DDL (like CREATE TABLE) information.
"""
from relshell.columndef import ColumnDef


class RecordDef(object):
    """Used as DDL (like CREATE TABLE) information."""
    # APIs
    def __init__(self, record_def):
        """Creates an object with each column property from `record_def`.

        :param record_def: list of column definition hash (see example below)

        *Example:*

        .. code-block:: python

            rdef = RecordDef(
                [
                    {'name'        : 'col1',
                     'type'        : 'STRING',
                     'primary_key' : True,
                    },
                    {'name'        : 'col2',
                     'type'        : 'INT',
                    },
                ]
            )
            rdef[1].name  # => 'col2'
            rdef[1].type  # => Type('INT')

        .. seealso::

            `ColumnDef.required_fields <#relshell.columndef.ColumnDef.required_fields>`_ and
            `ColumnDef.optional_fields <#relshell.columndef.ColumnDef.optional_fields>`_
            for each column's specification.

        :raises: `AttributeError` if `record_def` has invalid format
        """
        self._recdef = record_def
        self._set_coldefs()

    def __len__(self):
        """Returns number of columns"""
        return len(self._coldefs)

    def __getitem__(self, key):
        """Returns specified column definition.

        :param key: column index to get definition.
        :type key:  int (0-origin)
        :rtype:     `ColumnDef <#relshell.columndef.ColumnDef>`_
        """
        return self._coldefs[key]

    def __eq__(self, other):
        return self._recdef == other._recdef

    def __ne__(self, other):
        return not self.__eq__(other)

    def colindex_by_colname(self, colname):
        """Return column index whose name is :param:`column`

        :raises: `ValueError` when no column with :param:`colname` found
        """
        for i, coldef in enumerate(self):    # iterate each column's definition
            if coldef.name == colname:
                return i
        raise ValueError('No column named "%s" found' % (colname))

    # Private functions
    def _set_coldefs(self):
        self._coldefs = []
        for i, raw_coldef in enumerate(self._recdef):
            try:
                self._coldefs.append(ColumnDef(raw_coldef))
            except AttributeError as e:
                raise AttributeError("In column %d: %s" % (i, e))

    def __str__(self):
        return str(self._recdef)
