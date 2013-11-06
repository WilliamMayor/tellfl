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


def to_timestamp(date, _time):
    d_fmt = '%d-%b-%Y %X'
    tz = pytz.timezone('Europe/London')
    dt = datetime.datetime.strptime(
        '%s %s:00' % (date, _time),
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
    return int(dt.strftime('%s'))


def parse_csv(path):
    with open(path, 'rb') as fd:
        r = csv.reader(fd, skipinitialspace=True)
        for row in r:
            try:
                # date, start, end, action, charge, credit, balance, note
                row = map(lambda x: x.strip(), row)
                time_start = to_timestamp(row[0], row[1])
                time_end = None
                if row[2] != '':
                    time_end = to_timestamp(row[0], row[2])
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


def create_reports(cursor, uid):
    reports = []
    cursor.execute(PAYMENT_STATS, (uid, ))
    payment_stats = cursor.fetchone()
    p_total = payment_stats[0] or 0
    p_mean = payment_stats[1] or 0
    cursor.execute(JOURNEY_STATS, (uid, ))
    journey_stats = cursor.fetchone()
    j_min = journey_stats[0] or 0
    j_max = journey_stats[1] or 1
    j_count = journey_stats[2] or 1
    j_mean = journey_stats[3] or 0
    j_sum = journey_stats[4] or 1
    j_total = j_max - j_min
    reports.append(('total spend', '£%.2f' % (p_total / 100.00, )))
    reports.append(('mean spend', '£%.2f' % (p_mean / 100.00, )))
    reports.append(('# days', '%.2f' % (j_total / DAY, )))
    reports.append(('mean daily spend',
                    '£%.2f' % (p_total / (j_total / DAY) / 100.00, )))
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


class TellfLException(Exception):
    pass


class DB:

    def __init__(self, location):
        self.location = location

    def __enter__(self):
        self.conn = sqlite3.connect(os.path.join(self.location, DB_NAME))
        return self.conn.cursor()

    def __exit__(self, type, value, traceback):
        if traceback is not None:
            self.conn.commit()
        self.conn.close()


def report(username, location, as_html):
    with DB(location) as cursor:
        uid = find_user(cursor, username)
        create_reports(cursor, uid)


def add(username, csv_path, location):
    with DB(location) as cursor:
        uid = find_user(cursor, username)
        add_to_db(cursor, uid, csv_path)


def register(username, email, location):
    with DB(location) as cursor:
        try:
            q = 'INSERT INTO users(username, email) VALUES(?, ?)'
            cursor.execute(q, (username, email))
        except:
            raise TellfLException('A user with that username already exists')


def install(location):
    try:
        os.makedirs(location)
    except OSError:
        pass
    except Exception:
        raise TellfLException(
            'Cannot install to this location: ' % (location, )
        )
    with DB(location) as cursor:
        sql = resource_string(__name__, 'assets/schema.sql')
        cursor.executescript(sql)
