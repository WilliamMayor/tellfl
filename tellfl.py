#!/usr/bin/env python
import time
import csv
import datetime

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


def parse_csv(path):
    with open(path, 'rb') as fd:
        r = csv.reader(fd, skipinitialspace=True)
        r.next()
        for row in r:
            # date, start, end, action, charge, credit, balance, note
            row = map(lambda x: x.strip(), row)
            d_fmt = '%d-%b-%Y %X'
            time_start = datetime.datetime.strptime(
                '%s %s:00' % (row[0], row[1]),
                d_fmt
            )
            time_end = None
            if row[2] != '':
                time_end = datetime.datetime.strptime(
                    '%s %s:00' % (row[0], row[2]),
                    d_fmt
                )
            action = row[3]
            charge = None
            if row[4] != '':
                charge = int(row[4].replace('.', ''))
            credit = None
            if row[5] != '':
                credit = int(row[5].replace('.', ''))
            balance = int(row[6].replace('.', ''))
            note = None
            if row[7] != '':
                note = row[7]
            yield {
                'time_start': time_start,
                'time_end': time_end,
                'action': action,
                'charge': charge,
                'credit': credit,
                'balance': balance,
                'note': note
            }
