import sqlite3

from nose.tools import assert_equal, assert_is_none

from tellfl import get_user

conn = None
uid = None


def setup():
    global conn, uid
    conn = sqlite3.connect(':memory:')
    c = conn.cursor()
    for path in ['schema.sql']:
        with open(path, 'r') as fd:
            sql = fd.read()
            c.executescript(sql)
    c.execute('INSERT INTO users(email) VALUES("1@tellfl.co.uk")')
    uid = c.lastrowid
    c.close()


def test_get_user():
    c = conn.cursor()
    assert_equal(uid, get_user(c, '1@tellfl.co.uk'))


def test_invalid_email():
    c = conn.cursor()
    assert_is_none(get_user(c, 'something@example.com'))
