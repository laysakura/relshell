# -*- coding: utf-8 -*-
"""
    relshell.timestamp
    ~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides efficient data structure to represent timestamp
"""
import datetime as dt


class Timestamp(object):
    """Provides efficient data structure to represent timestamp
    """
    def __init__(self, timestamp_str):
        """Constructor

        :param timestamp_str: timestamp string
        :type timestamp_str: `%Y-%m-%d %H:%M:%S` or `%Y-%m-%d`
        """
        try:
            t = dt.datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            t = dt.datetime.strptime(timestamp_str, '%Y-%m-%d')
        except ValueError:
            raise ValueError('"%s" does not have appropreate format' % (timestamp_str))

        # year=2013, month=10, day=29, hour=01, minute=04, second=12, microsecond=123456
        # => 20131029010412123  (microsecond is cut to millisecond)

        # [todo] - compress encoded timestamp (might be better to use `datetime.datetime` as-is)
        self._ts = (long(t.microsecond * 1e-3) +
                    long(t.second * 1e3) + long(t.minute * 1e5) + long(t.hour * 1e7) +
                    long(t.day * 1e9)    + long(t.month * 1e11) + long(t.year * 1e13))

    def year(self):
        """Return year"""
        return int(str(self._ts)[0:4])

    def month(self):
        """Return month"""
        return int(str(self._ts)[4:6])

    def day(self):
        """Return day"""
        return int(str(self._ts)[6:8])

    def hour(self):
        """Return hour"""
        return int(str(self._ts)[8:10])

    def minute(self):
        """Return minute"""
        return int(str(self._ts)[10:12])

    def second(self):
        """Return self"""
        return int(str(self._ts)[12:14])

    def millisecond(self):
        """Return millisecond"""
        return int(str(self._ts)[14:17])

    def datetime(self):
        """Return `datetime` object"""
        return dt.datetime(
            self.year(), self.month(), self.day(),
            self.hour(), self.minute(), self.second(),
            int(self.millisecond() * 1e3))

    def runoff_lower(self, timespan):
        """Check if this timestamp is lower than t0 of [t0, t1]"""
        return self < timespan.get_start()

    def runoff_higher(self, timespan):
        """Check if this timestamp is higher than t1 of [t0, t1]"""
        return self > timespan.get_end()

    def between(self, timespan):
        """Check if this timestamp is between t0 and t1 of [t0, t1]"""
        return timespan.get_start() <= self <= timespan.get_end()

    def __eq__(self, other):
        return self._ts == other._ts

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        return self._ts < other._ts

    def __gt__(self, other):
        return self._ts > other._ts

    def __le__(self, other):
        return self._ts <= other._ts

    def __ge__(self, other):
        return self._ts >= other._ts

    def __add__(self, sec):
        """Add `sec` to this timestamp"""
        return Timestamp(timestamp_str=(self.datetime() + dt.timedelta(seconds=sec)).strftime('%Y-%m-%d %H:%M:%S'))

    def __sub__(self, sec):
        """Subtract `sec` to this timestamp"""
        return Timestamp(timestamp_str=(self.datetime() - dt.timedelta(seconds=sec)).strftime('%Y-%m-%d %H:%M:%S'))

    def __long__(self):
        """Return long representation of this timestamp"""
        return self._ts

    def __str__(self):  # pragma: no cover
        """Return str representation of this timestamp"""
        return "%04d-%02d-%02d %02d:%02d:%02d" % (
            self.year(), self.month(),  self.day(),
            self.hour(), self.minute(), self.second())
