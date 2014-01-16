# flake8: NOQA
from nose.tools import assert_equals, assert_is_none

import tellfl

CSV = """
Date,Start Time,End Time,Journey/Action,Charge,Credit,Balance,Note
06-Dec-2013,17:30,18:12,"Euston Square to Ruislip",5.00,,17.85,""
06-Dec-2013,07:01,07:56,"Ruislip to Euston Square",5.00,,22.85,""
06-Dec-2013,07:01,,"Auto top-up, Ruislip",,20.00,27.85,""
05-Dec-2013,17:06,18:11,"Waterloo [London Underground / National Rail] to Ruislip",5.00,,7.85,""
05-Dec-2013,13:14,,"Bus journey, route 168",1.40,,12.85,""
05-Dec-2013,09:15,10:14,"Ruislip to Euston Square",5.00,,14.25,""
04-Dec-2013,15:59,16:53,"Waterloo [London Underground / National Rail] to Ruislip",3.00,,19.25,""
04-Dec-2013,06:57,07:48,"Ruislip to Waterloo [London Underground / National Rail]",5.00,,22.25,""
04-Dec-2013,06:57,,"Auto top-up, Ruislip",,20.00,27.25,""
03-Dec-2013,17:06,17:52,"Euston Square to Ruislip",5.00,,7.25,""
03-Dec-2013,06:57,07:44,"Ruislip to Euston Square",5.00,,12.25,""
02-Dec-2013,17:46,18:28,"Euston Square to Ruislip",5.00,,17.25,""
02-Dec-2013,06:58,07:47,"Ruislip to Euston Square",5.00,,22.25,""
02-Dec-2013,06:58,,"Auto top-up, Ruislip",,20.00,27.25,""
"""


def test_parse_time():
    assert_equals(1388577600, tellfl.parse_time('01-Jan-2014', '12:00'))


def test_parse_journey_x_to_y():
    assert_equals(
        ('Bank', 'Holborn'),
        tellfl.parse_journey('"Bank to Holborn"'))


def test_parse_journey_x_to_x():
    assert_equals(
        ('Bank', 'Bank'),
        tellfl.parse_journey('"Entered and exited Bank"'))


def test_parse_journey_bus():
    assert_equals(
        ('H1', None),
        tellfl.parse_journey('"Bus journey, route H1"'))


def test_parse_cost():
    assert_equals(1234, tellfl.parse_cost("12.34"))


def test_parse_no_cost():
    assert_is_none(tellfl.parse_cost(''))


def test_parse_row_journey():
    assert_equals(
        (1388577600, 1388577660, 'Bank', 'Holborn', 100, None),
        tellfl.parse_row('01-Jan-2014', '12:00','12:01','Bank to Holborn','1.00','','10.00',''))


def test_parse_row_topup():
    assert_equals(
        (1388577600, None, None, None, None, 1000),
        tellfl.parse_row('01-Jan-2014', '12:00','','Auto top-up, Bank','','10.00','10.00',''))


def test_parse_csv():
    assert_equals(
        [(1386351000, 1386353520, 'Euston Square', 'Ruislip', 500, None),
         (1386313260, 1386316560, 'Ruislip', 'Euston Square', 500, None),
         (1386313260, None, None, None, None, 2000),
         (1386263160, 1386267060, 'Waterloo [London Underground / National Rail]', 'Ruislip', 500, None),
         (1386249240, None, '168', None, 140, None),
         (1386234900, 1386238440, 'Ruislip', 'Euston Square', 500, None),
         (1386172740, 1386175980, 'Waterloo [London Underground / National Rail]', 'Ruislip', 300, None),
         (1386140220, 1386143280, 'Ruislip', 'Waterloo [London Underground / National Rail]', 500, None),
         (1386140220, None, None, None, None, 2000),
         (1386090360, 1386093120, 'Euston Square', 'Ruislip', 500, None),
         (1386053820, 1386056640, 'Ruislip', 'Euston Square', 500, None),
         (1386006360, 1386008880, 'Euston Square', 'Ruislip', 500, None),
         (1385967480, 1385970420, 'Ruislip', 'Euston Square', 500, None),
         (1385967480, None, None, None, None, 2000)],
        tellfl.parse_csv(CSV))
