import os
import sqlite3

from nose.tools import assert_equal

from tellfl import add_to_db, get_user

csv_path = [
    os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'assets',
        'example.csv'
    ),
    os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        'assets',
        'example1.csv'
    )
]
conn = None


def setup():
    global conn
    conn = sqlite3.connect(':memory:')
    c = conn.cursor()
    for path in ['schema.sql']:
        with open(path, 'r') as fd:
            sql = fd.read()
            c.executescript(sql)
    c.execute('INSERT INTO users(email) VALUES("1@tellfl.co.uk")')
    uid = c.lastrowid
    c.execute('INSERT INTO users(email) VALUES("2@tellfl.co.uk")')
    vid = c.lastrowid
    add_to_db(c, uid, csv_path[0])
    add_to_db(c, vid, csv_path[1])
    c.close()


def test_journeys_exist():
    c = conn.cursor()
    q = 'SELECT COUNT(*) FROM journeys'
    c.execute(q)
    assert_equal(19, int(c.fetchone()[0]))


def test_journeys_to_user():
    c = conn.cursor()
    q = 'SELECT COUNT(*) FROM journeys WHERE user = ?'
    c.execute(q, (get_user(c, '1@tellfl.co.uk'), ))
    assert_equal(9, int(c.fetchone()[0]))


def test_bus_journey():
    pass


def test_inout_journey():
    pass


def test_free_journey():
    pass
