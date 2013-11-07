# -*- coding: utf-8 -*-
import time
import sqlite3
import os

from pkg_resources import resource_string

from tellfl.csv_parser import parse_csv

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


def find_user(cursor, username):
    q = 'SELECT id FROM users WHERE username=?'
    cursor.execute(q, (username, ))
    try:
        return int(cursor.fetchone()[0])
    except:
        raise Exception('No user with that username')


def add_to_db(cursor, uid, csv_path):
    for record in parse_csv(csv_path):
        if record['type'] == 'payment':
            cursor.execute(
                INSERT_PAYMENT,
                (uid, record['amount'], record['time'])
            )
        elif record['type'] == 'journey':
            cursor.execute(
                INSERT_JOURNEY,
                (uid, record['station_from'], record['station_to'],
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
