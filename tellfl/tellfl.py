import datetime
import csv
import StringIO

import pytz


def parse_time(date, time_):
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


def parse_journey(journey):
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


def parse_cost(cost):
    try:
        c = int(cost.replace('.', ''))
    except:
        c = None
    return c


def parse_row(date, time_in, time_out, action, charge, credit, balance, note):
    time_in = parse_time(date, time_in)
    time_out = parse_time(date, time_out)
    station_in, station_out = parse_journey(action)
    charge = parse_cost(charge)
    credit = parse_cost(credit)
    if time_in is None or not any([charge, credit]):
        raise Exception('Could not prase row')
    return (time_in, time_out,
            station_in, station_out,
            charge, credit)


def parse_csv(data):
    rows = []
    for row in csv.reader(StringIO.StringIO(data)):
        try:
            rows.append(parse_row(*row))
        except:
            pass
    return rows


if __name__ == '__main__':
    import os
    import sys
    for root, dirs, files in os.walk(sys.argv[1]):
        for f in [f for f in files if f.endswith('.csv')]:
            with open(os.path.join(root, f), 'r') as fd:
                for r in parse_csv(fd.read()):
                    print(r)
