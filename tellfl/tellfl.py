import time
import csv
import datetime
import sqlite3
import os

from pkg_resources import resource_string

MINUTE = 60
HOUR = MINUTE * 60
DAY = HOUR * 24
WEEK = DAY * 7

DB_NAME = 'history.db'


def __get_spends(cursor, user_id, start, period):
    q = ('SELECT t.time_in, SUM(s.cost) AS sum '
         'FROM '
         '  journeys AS t, '
         '  (SELECT * FROM journeys) as s '
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


def get_user(cursor, email):
    q = 'SELECT id FROM users WHERE email = ?'
    cursor.execute(q, (email, ))
    row = cursor.fetchone()
    if row is None:
        return None
    return row[0]


def parse_csv(path):
    with open(path, 'rb') as fd:
        r = csv.reader(fd, skipinitialspace=True)
        for row in r:
            try:
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
            except:
                pass


def add_to_db(cursor, user_id, csv_path):
    payment_q = ('INSERT INTO '
                 '  payments(user, amount, time) '
                 'VALUES(?, ?, ?)')
    bus_q = ('INSERT INTO '
             ' journeys(user, station_from, time_in, cost) '
             'VALUES(?, ?, ?, ?)')
    tube_q = ('INSERT INTO '
              '  journeys('
              '    user, station_from, station_to, '
              '    time_in, time_out, cost '
              '  ) '
              'VALUES(?, ?, ?, ?, ?, ?)')
    bus_action = 'Bus journey, route '
    inout_action = 'Entered and exited '
    for record in parse_csv(csv_path):
        if record['credit'] is not None:
            cursor.execute(payment_q, (
                user_id,
                record['credit'],
                record['time_start']
            ))
        elif record['action'].startswith(bus_action):
            cursor.execute(bus_q, (
                user_id,
                record['action'].replace(bus_action, ''),
                record['time_start'],
                record['charge']
            ))
        elif record['action'].startswith(inout_action):
            cursor.execute(tube_q, (
                user_id,
                record['action'].replace(inout_action, ''),
                record['action'].replace(inout_action, ''),
                record['time_start'],
                record['time_end'],
                record['charge']
            ))
        else:
            a, b = record['action'].split(' to ')
            cursor.execute(tube_q, (
                user_id,
                a,
                b,
                record['time_start'],
                record['time_end'],
                record['charge']
            ))


def run(username, csv_path, location):
    conn = sqlite3.connect(os.path.join(location, DB_NAME))
    conn.cursor()


def install(location):
    try:
        os.makedirs(location)
    except:
        pass
    conn = sqlite3.connect(os.path.join(location, DB_NAME))
    c = conn.cursor()
    sql = resource_string(__name__, 'assets/schema.sql')
    c.executescript(sql)
    conn.commit()
    conn.close()
