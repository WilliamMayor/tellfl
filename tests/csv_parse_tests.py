import sqlite3

from pkg_resources import resource_string

from nose.tools import assert_equal

from tellfl import tellfl, csv_parser

conn = None


def setup():
    global conn
    sql = resource_string(tellfl.__name__, 'assets/schema.sql')
    conn = sqlite3.connect(':memory:')
    c = conn.cursor()
    c.executescript(sql)
    conn.commit()


def make_journey(t, sf, st, ti, to, c):
    return {
        'type': 'journey',
        'station_from': sf,
        'station_to': st,
        'time_start': ti,
        'time_end': to,
        'cost': c
    }


def make_payment(amount, time):
    return {
        'type': 'payment',
        'amount': amount,
        'time': time
    }


def make_bus(route, time_in, cost):
    return make_journey(
        'journey',
        route,
        None,
        time_in,
        None,
        cost
    )


def make_tube(station_from, station_to, time_in, time_out, cost):
    return make_journey(
        'journey',
        station_from,
        station_to,
        time_in,
        time_out,
        cost
    )


def test_parse_bus_journey():
    csv = resource_string(__name__, 'assets/bus.csv')
    parsed = csv_parser.parse(csv)
    assert_equal(
        [make_bus('U1', 1385380320, 100)],
        list(parsed)
    )


def test_parse_tube_journey():
    csv = resource_string(__name__, 'assets/tube.csv')
    parsed = csv_parser.parse(csv)
    assert_equal(
        [make_tube('Ruislip', 'Ruislip Manor', 1385380320, 1385383920, 100)],
        list(parsed)
    )


def test_parse_payment():
    csv = resource_string(__name__, 'assets/payment.csv')
    parsed = csv_parser.parse(csv)
    assert_equal(
        [make_payment(100, 1385380320)],
        list(parsed)
    )
