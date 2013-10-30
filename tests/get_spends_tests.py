import sqlite3
import time
import inspect

from nose.tools import assert_equal

from tellfl import __get_spends, get_weekly_spends

conn = None

MINUTE = 60
HOUR = MINUTE * 60
DAY = HOUR * 24
WEEK = DAY * 7


def setup():
    global conn
    conn = sqlite3.connect(':memory:')
    c = conn.cursor()
    for path in ['schema.sql']:
        with open(path, 'r') as fd:
            sql = fd.read()
            c.executescript(sql)
    c.close()


def teardown():
    conn.close()


def add_user(email):
    c = conn.cursor()
    c.execute('INSERT INTO users(email) VALUES(?)', (email, ))
    return (c.lastrowid, email)


def add_journey(user, station_from, station_to, time_in, time_out, cost):
    c = conn.cursor()
    c.execute(('INSERT INTO '
               'journeys(user, station_from, station_to, '
               'time_in, time_out, cost) '
               'VALUES(?, ?, ?, ?, ?, ?)'),
             (user, station_from, station_to, time_in, time_out, cost))
    return c.lastrowid


def test_get_spend_nothing():
    c = conn.cursor()
    (uid, email) = add_user('%s@tellfl.co.uk' % inspect.stack()[0][3])
    spends = __get_spends(c, uid, 0, 52*WEEK)
    assert_equal([], spends)


def test_get_spend_one():
    c = conn.cursor()
    (uid, email) = add_user('%s@tellfl.co.uk' % inspect.stack()[0][3])
    add_journey(uid, 'A', 'B', 0, HOUR, 300)
    spends = __get_spends(c, uid, 0, WEEK)
    assert_equal([(0, 300)], spends)


def test_get_spend_two():
    c = conn.cursor()
    (uid, email) = add_user('%s@tellfl.co.uk' % inspect.stack()[0][3])
    add_journey(uid, 'A', 'B', 0, HOUR, 300)
    add_journey(uid, 'A', 'B', DAY, DAY + HOUR, 300)
    spends = __get_spends(c, uid, 0, WEEK)
    assert_equal([(0, 600), (DAY, 300)], spends)


def test_get_spend_fortnight():
    c = conn.cursor()
    (uid, email) = add_user('%s@tellfl.co.uk' % inspect.stack()[0][3])
    add_journey(uid, 'A', 'B', 0, HOUR, 300)
    add_journey(uid, 'A', 'B', DAY, DAY + HOUR, 300)
    add_journey(uid, 'A', 'B', WEEK, WEEK + HOUR, 300)
    spends = __get_spends(c, uid, 0, WEEK)
    assert_equal([(0, 600), (DAY, 600), (WEEK, 300)], spends)


def test_get_spend_ignore_past():
    c = conn.cursor()
    (uid, email) = add_user('%s@tellfl.co.uk' % inspect.stack()[0][3])
    add_journey(uid, 'A', 'B', 0, HOUR, 300)
    add_journey(uid, 'A', 'B', DAY, DAY + HOUR, 300)
    add_journey(uid, 'A', 'B', WEEK, WEEK + HOUR, 300)
    spends = __get_spends(c, uid, DAY, WEEK)
    assert_equal([(DAY, 600), (WEEK, 300)], spends)


def test_get_weekly_spend_ignore_past_default():
    c = conn.cursor()
    now = int(time.time())
    (uid, email) = add_user('%s@tellfl.co.uk' % inspect.stack()[0][3])
    add_journey(uid, 'A', 'B', now - 2*WEEK, HOUR, 300)
    add_journey(uid, 'A', 'B',
                now - DAY, now - DAY + HOUR, 300)
    add_journey(uid, 'A', 'B',
                now - WEEK, now - WEEK + HOUR, 300)
    spends = get_weekly_spends(c, uid)
    assert_equal([(now - WEEK, 600), (now - DAY, 300)], spends)
