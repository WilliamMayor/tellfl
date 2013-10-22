import os
import datetime

from nose.tools import assert_equal, assert_in

from tellfl import parse_csv

csv_path = os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    'assets',
    'example.csv'
)
records = []


def setup():
    global records
    records = list(parse_csv(csv_path))


def test_parse_time_start():
    assert_in(
        datetime.datetime(2013, 10, 7, 19, 26),
        [r['time_start'] for r in records]
    )


def test_parse_time_end():
    assert_in(
        datetime.datetime(2013, 10, 7, 13, 19),
        [r['time_end'] for r in records]
    )


def test_parse_time_end_none():
    assert_in(
        None,
        [r['time_end'] for r in records]
    )


def test_parse_action():
    assert_in(
        'Baker Street to Ruislip',
        [r['action'] for r in records]
    )


def test_parse_charge():
    assert_in(
        340,
        [r['charge'] for r in records]
    )
    assert_equal(9, len(filter(lambda x: x['charge'] is not None, records)))


def test_parse_credit():
    assert_in(
        2000,
        [r['credit'] for r in records]
    )
    assert_equal(1, len(filter(lambda x: x['credit'] is not None, records)))


def test_parse_balance():
    assert_in(
        1895,
        [r['balance'] for r in records]
    )
    assert_equal(
        len(records),
        len(filter(lambda x: x['balance'] is not None, records))
    )


def test_parse_note():
    assert_in(
        None,
        [r['note'] for r in records]
    )
    assert_in(
        ('The fare for this journey was capped as you reached the daily '
         'charging limit for the zones used'),
        [r['note'] for r in records]
    )
