# -*- coding: utf-8 -*-
import csv
import datetime
import string

import pytz


def to_timestamp(date, _time):
    d_fmt = '%d-%b-%Y %X'
    tz = pytz.timezone('Europe/London')
    dt = datetime.datetime.strptime(
        '%s %s:00' % (date, _time),
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
    return int(dt.strftime('%s'))


def parse_values(row):
    time_start = to_timestamp(row[0], row[1])
    time_end = None
    if row[2] != '':
        time_end = to_timestamp(row[0], row[2])
    action = row[3]
    charge = None
    if row[4] != '':
        charge = int(row[4].replace('.', ''))
    credit = None
    if row[5] != '':
        credit = int(row[5].replace('.', ''))
    balance = int(row[6].replace('.', ''))
    note = None
    if row[7] != '':
        note = row[7]
    return {
        'time_in': time_start,
        'time_out': time_end,
        'action': action,
        'charge': charge,
        'credit': credit,
        'balance': balance,
        'note': note
    }


def parse_action(action):
    if action.startswith('Bus journey'):
        route = action.replace('Bus journey, route ', '')
        return route, None
    if ' to ' in action:
        return action.split(' to ')
    if action.startswith('Entered and exited '):
        station = action.replace('Entered and exited ', '')
        return station, station
    return None, None


def parse_row(row):
    if row['credit'] is not None:
        return {
            'type': 'payment',
            'amount': row['credit'],
            'time': row['time_in']
        }
    station_from, station_to = parse_action(row['action'])
    return {
        'type': 'journey',
        'station_from': station_from,
        'station_to': station_to,
        'time_in': row['time_in'],
        'time_out': row['time_out'],
        'cost': row['charge']
    }


def parse(pathorstring):
    try:
        with open(path, 'rb') as fd:
            csv = fd.read()
    except:
            csv = pathorstring
    for line in csv.reader(csv.splitlines(), skipinitialspace=True):
        try:
            # date, start, end, action, charge, credit, balance, note
            raw = map(string.strip, line)
            values = parse_values(raw)
            yield parse_row(values)
        except:
            pass    
