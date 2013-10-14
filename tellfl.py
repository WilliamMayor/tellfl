#!/usr/bin/env python
import time

MINUTE = 60
HOUR = MINUTE * 60
DAY = HOUR * 24
WEEK = DAY * 7


def __get_spends(cursor, user_id, start, period):
    q = ('SELECT t.time_in, SUM(s.cost) AS sum '
         'FROM '
         '  history AS t, '
         '  (SELECT * FROM history) as s '
         'WHERE '
         '  t.time_in >= ? AND '
         '  t.user == ? AND '
         '  t.user == s.user AND '
         '  t.time_in < s.time_out AND '
         '  t.time_in + ? > s.time_out '
         'GROUP BY t.time_in')
    return list(cursor.execute(q, (start, user_id, period)))


def get_weekly_spends(cursor, user_id, start=None):
    if start is None:
        start = int(time.time()) - 2*WEEK
    return __get_spends(cursor, user_id, start, WEEK)
