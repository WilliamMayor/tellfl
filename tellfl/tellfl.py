# -*- coding: utf-8 -*-
import time
import csv
import datetime
import sqlite3
import os
import pytz

from pkg_resources import resource_string

MINUTE = 60.0
HOUR = MINUTE * 60.0
DAY = HOUR * 24.0
WEEK = DAY * 7.0
YEAR = WEEK * 52.0
MONTH = YEAR / 12.0

DB_NAME = 'history.db'

INSERT_PAYMENT = 'INSERT INTO payments(user, amount, time) VALUES(?, ?, ?)'
INSERT_JOURNEY = 'INSERT INTO journeys(user, station_from, station_to, time_in, time_out, cost) VALUES(?, ?, ?, ?, ?, ?)' # NOQA
PAYMENT_STATS = 'SELECT SUM(amount), AVG(amount) FROM payments WHERE user=?'
JOURNEY_STATS = 'SELECT MIN(time_in), MAX(time_out), COUNT(*), AVG(time_out - time_in), SUM(time_out - time_in) FROM journeys WHERE user=?' # NOQA


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
                tz = pytz.timezone('Europe/London')
                dt = datetime.datetime.strptime(
                    '%s %s:00' % (row[0], row[1]),
                    d_fmt
                )
                dt = datetime.datetime(
                    dt.year,
                    dt.month,
                    dt.day,
                    dt.hour,
                    dt.minute,
                    tzinfo=tz
                )
                time_start = int(dt.strftime('%s'))
                time_end = None
                if row[2] != '':
                    dt = datetime.datetime.strptime(
                        '%s %s:00' % (row[0], row[2]),
                        d_fmt
                    )
                    dt = datetime.datetime(
                        dt.year,
                        dt.month,
                        dt.day,
                        dt.hour,
                        dt.minute,
                        tzinfo=tz
                    )
                    time_end = int(dt.strftime('%s'))
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


def find_user(cursor, username):
    q = 'SELECT id FROM users WHERE username=?'
    cursor.execute(q, (username, ))
    try:
        return int(cursor.fetchone()[0])
    except:
        raise Exception('No user with that username')


def add_user(cursor, username, email):
    try:
        q = 'INSERT INTO users(username, email) VALUES(?, ?)'
        cursor.execute(q, (username, email))
        return cursor.lastrowid
    except:
        raise Exception('A user with that username already exists')


def split_stations(action):
    return 'Ruislip', None


def add_to_db(cursor, uid, csv_path):
    for record in parse_csv(csv_path):
        if record['credit'] is not None:
            cursor.execute(
                INSERT_PAYMENT,
                (uid, record['credit'], record['time_start'])
            )
        else:
            s_from, s_to = split_stations(record['action'])
            cursor.execute(
                INSERT_JOURNEY,
                (uid, s_from, s_to,
                 record['time_start'], record['time_end'], record['charge'])
            )


def report(cursor, uid, most_recent):
    reports = []
    cursor.execute(PAYMENT_STATS, (uid, ))
    payment_stats = cursor.fetchone()
    p_total = payment_stats[0]
    p_mean = payment_stats[1]
    cursor.execute(JOURNEY_STATS, (uid, ))
    journey_stats = cursor.fetchone()
    j_min = journey_stats[0]
    j_max = journey_stats[1]
    j_count = journey_stats[2]
    j_mean = journey_stats[3]
    j_sum = journey_stats[4]
    j_total = j_max - j_min
    if payment_stats[0] is not None:
        reports.append(('total spend', '£%.2f' % (p_total / 100.00, )))
        reports.append(('mean spend', '£%.2f' % (p_mean / 100.00, )))
    if journey_stats[0] is not None:
        reports.append(('# weeks', '%.2f' % (j_total / WEEK, )))
        reports.append(('mean weekly spend',
                        '£%.2f' % (p_total / (j_total / WEEK) / 100.00, )))
        reports.append(('# months', '%.2f' % (j_total / MONTH), ))
        reports.append(('mean monthly spend',
                        '£%.2f' % (p_total / (j_total / MONTH) / 100.00, )))
        reports.append(('# years', '%.2f' % (j_total / YEAR), ))
        reports.append(('mean annual spend',
                        '£%.2f' % (p_total / (j_total / YEAR) / 100.00, )))
        reports.append(('# journeys', '%d' % (j_count, )))
        reports.append(('mean journey cost',
                        '£%.2f' % (p_total / (j_count * 100.00), )))
        reports.append(('mean journey time',
                        '%d minutes' % (j_mean / MINUTE, )))
        reports.append(('cost per minute',
                        '£%.2f' % (p_total / (j_sum / MINUTE * 100.00), )))

    for r in reports:
        print '%s: %s' % (r[0], r[1])


def run(username, csv_path, location, new_user, email):
    conn = sqlite3.connect(os.path.join(location, DB_NAME))
    cursor = conn.cursor()
    if new_user:
        uid = add_user(cursor, username, email)
    else:
        uid = find_user(cursor, username)
    most_recent = None
    if csv_path is not None:
        most_recent = add_to_db(cursor, uid, csv_path)
    report(cursor, uid, most_recent)
    conn.commit()
    conn.close()


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
