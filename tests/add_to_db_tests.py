import os
import sqlite3

from nose.tools import assert_equal, assert_in

from tellfl import add_to_db

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
    c.execute('INSERT INTO users(email) VALUES(1@tellfl.co.uk)')
    uid = c.lastrowid
    c.execute('INSERT INTO users(email) VALUES(2@tellfl.co.uk)')
    vid = c.lastrowid
    add_to_db(c, uid, csv_path[0])
    add_to_db(c, vid, csv_path[1])
    c.close()


def test_records_exist():
    c = conn.cursor()
    q = 'SELECT COUNT(*) FROM history'
    c.execute(q)
    assert_equal(21, int(c.fetchone()))
