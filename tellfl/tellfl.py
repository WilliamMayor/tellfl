# -*- coding: utf-8 -*-
import sqlite3
import os

from pkg_resources import resource_string

from csv_parser import parse_csv
import reports

DB_NAME = 'tellfl.db'

INSERT_PAYMENT = 'INSERT INTO payments(user, amount, time) VALUES(?, ?, ?)'
INSERT_JOURNEY = 'INSERT INTO journeys(user, station_from, station_to, time_in, time_out, cost) VALUES(?, ?, ?, ?, ?, ?)' # NOQA


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
                 record['time_in'], record['time_out'], record['cost'])
            )


class TellfLException(Exception):
    pass


class DB:

    def __init__(self, location):
        self.location = location

    def __enter__(self):
        self.conn = sqlite3.connect(os.path.join(self.location, DB_NAME))
        return self.conn.cursor()

    def __exit__(self, type, value, traceback):
        if traceback is None:
            self.conn.commit()
        self.conn.close()


def report(username, location, as_html):
    with DB(location) as cursor:
        uid = find_user(cursor, username)
        r = reports.create(cursor, uid)
        if as_html:
            print reports.asHtml(r)
        else:
            print reports.asText(r)


def add(username, csv_path, location):
    with DB(location) as cursor:
        uid = find_user(cursor, username)
        add_to_db(cursor, uid, csv_path)


def register(username, location):
    with DB(location) as cursor:
        try:
            q = 'INSERT INTO users(username) VALUES(?)'
            cursor.execute(q, (username, ))
        except:
            raise TellfLException('A user with that username already exists')


def install(location):
    os.makedirs(location)
    with DB(location) as cursor:
        sql = resource_string(__name__, 'assets/schema.sql')
        cursor.executescript(sql)
