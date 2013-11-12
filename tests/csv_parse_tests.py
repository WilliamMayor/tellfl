import sqlite3

from pkg_resources import resource_string

from nose.tools import assert_equal

from tellfl import tellfl, csv_parse

conn = None


def setup():
    global conn
    sql = resource_string(tellfl.__name__, 'assets/schema.sql')
    conn = sqlite.connect(':memory:')
    c = conn.cursor()
    c.executescript(sql)
    conn.commit()
    
    
def make_row(t, sf, st, ti, to, c):
    return {
        'type': t,
        'station_from': sf,
        'station_to': st,
        'time_in': ti,
        'time_out': to,
        'cost': c
    }
    
    
def test_parse_bus_journey():
    csv = resource_string(__name__, 'assets/bus.csv')
    parsed = csv_parser.parse(csv)
    assert_equal(
        [make_row('journey', 'U1', None, 0, None, 100)],
        list(parsed)
    )