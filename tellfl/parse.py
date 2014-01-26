import datetime
import csv as csv_

import pytz

from models import History


def _time(date, time_):
    try:
        d_fmt = '%d-%b-%Y %X'
        tz = pytz.timezone('Europe/London')
        dt = datetime.datetime.strptime(
            '%s %s:00' % (date, time_),
            d_fmt
        )
        dt = datetime.datetime(
            dt.year,
            dt.month,
            dt.day,
            dt.hour,
            dt.minute,
            tzinfo=tz
        )
        t = int(dt.strftime('%s'))
    except:
        t = None
    return t


def _journey(journey):
    journey = journey.strip('"')
    a, b = None, None
    if journey.startswith('Bus journey'):
        a = journey.replace('Bus journey, route ', '')
    elif ' to ' in journey:
        a, b = journey.split(' to ')
    elif journey.startswith('Entered and exited '):
        a = journey.replace('Entered and exited ', '')
        b = a
    return a, b


def _cost(cost):
    try:
        c = int(cost.replace('.', ''))
    except:
        c = None
    return c


def _row(date, time_in, time_out, action, charge, credit, balance, note):
    time_in = _time(date, time_in)
    time_out = _time(date, time_out)
    station_in, station_out = _journey(action)
    charge = _cost(charge)
    credit = _cost(credit)
    if time_in is None or not any([charge, credit]):
        raise Exception('Could not prase row')
    return (time_in, time_out,
            station_in, station_out,
            charge, credit)


def _iterate(file_, func):
    rows = []
    reader = csv_.reader(file_)
    row = reader.next()
    while 'Date' not in row:
        row = reader.next()
    for row in reader:
        rows.append(func(row))
    return rows


def csv(file_):
    return _iterate(file_, lambda r: _row(*r))


def history(file_):
    return _iterate(file_, lambda r: History(None, *r))
