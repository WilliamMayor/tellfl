import sqlite3

from pkg_resources import resource_string

from nose.tools import assert_equal

from tellfl import tellfl, reports

conn = None
data = None


def setup():
    global conn, data
    tellfl.DB_NAME = ':memory:'
    conn = sqlite3.connect(tellfl.DB_NAME)
    tellfl.install('')
    uid = tellfl.register('data_test', '')
    tellfl.add('data_test', resource_string(__name__, 'assets/data.csv'), '')
    data = reports.Data(conn.cursor(), uid)


def teardown():
    conn.close()


def test_total_credit():
    assert_equal(
        2000,
        data.total_credit
    )


def test_min_time():
    assert_equal(
        1381829940,
        data.min_time
    )
