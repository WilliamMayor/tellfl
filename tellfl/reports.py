# -*- coding: utf-8 -*-
import time
import datetime

import pytz

MINUTE = 60.0
HOUR = MINUTE * 60.0
DAY = HOUR * 24.0
WEEK = DAY * 7.0
YEAR = WEEK * 52.0
MONTH = YEAR / 12.0

PAYMENT_STATS = 'SELECT SUM(amount), AVG(amount) FROM payments WHERE user=?'
JOURNEY_STATS = 'SELECT MIN(time_in), MAX(time_out), COUNT(*), AVG(time_out - time_in), SUM(time_out - time_in) FROM journeys WHERE user=?' # NOQA


def __get_spends(cursor, user_id, start, period):
    q = ('SELECT t.time_in, SUM(s.cost) AS sum '
         'FROM '
         '  journeys AS t, '
         '  (SELECT * FROM journeys) as s '
         'WHERE '
         '  t.time_in >= ? AND '
         '  t.user == ? AND '
         '  t.user == s.user AND '
         '  t.time_in < s.time_out AND '
         '  t.time_in + ? > s.time_out '
         'GROUP BY t.time_in')
    return list(cursor.execute(q, (start, user_id, period)))


def get_weekly_spends(cursor, user_id, start=None):
    if start is None:
        start = int(time.time()) - 2*WEEK
    return __get_spends(cursor, user_id, start, WEEK)


def from_timestamp(timestamp):
    tz = pytz.timezone('Europe/London')
    return datetime.datetime.fromtimestamp(timestamp, tz)


def create_raw(cursor, uid, reports):
    cursor.execute(
        ('SELECT SUM(amount), AVG(amount), COUNT(amount) '
         'FROM payments '
         'WHERE user=?'),
        (uid, )
    )
    pstats = cursor.fetchone()
    cursor.execute(
        ('SELECT '
         '    MIN(time_in), MAX(time_out), '
         '    COUNT(*), AVG(time_out - time_in) '
         '    SUM(time_out - time_in) '
         'FROM journeys '
         'WHERE user=?'),
        (uid, )
    )
    jstats = cursor.fetchone()
    return dict(
        total_spend=pstats[0] or 0,
        mean_spend=pstats[1] or 0,
        spend_count=pstats[2] or 0,
        min_time=from_timestamp(jstats[0] or 0),
        max_time=from_timestamp(jstats[1] or 0),
        journey_count=jstats[2] or 1,
        mean_journey_length=jstats[3] or 0,
        total_journey_time=jstats[4] or 1
    )


def create_daily(cursor, uid, reports):
    t_in = reports['min_time'].date()
    t_out = reports['max_time'].date() + datetime.timedelta(days=1)
    delta = t_out - t_in
    mds = float(reports['total_spend']) / delta.days
    return dict(
        days_count=delta.days,
        mean_daily_spend=mds
    )


def create_weekly(cursor, uid, reports):
    t_in = reports['min_time'].date()
    t_out = reports['max_time'].date() + datetime.timedelta(days=1)
    delta = t_out - t_in
    weeks = delta.days / 7.0
    return dict(
        weeks_count=weeks,
        mean_weekly_spend=reports['total_spend'] / weeks
    )


def create_monthly(cursor, uid, reports):
    t_in = reports['min_time'].date()
    t_out = reports['max_time'].date() + datetime.timedelta(days=1)
    delta = t_out - t_in
    months = delta.days / 365.2425 * 12
    mms = reports['total_spend'] / months
    return dict(
        months_count=months,
        mean_monthly_spend=mms
    )


def create_annually(cursor, uid, reports):
    t_in = reports['min_time'].date()
    t_out = reports['max_time'].date() + datetime.timedelta(days=1)
    delta = t_out - t_in
    years = delta.days / 365.2425
    mas = reports['total_spend'] / years
    return dict(
        years_count=years,
        mean_annual_spend=mas
    )


def create_journey(cursor, uid, reports):
    mjc = float(reports['total_spend']) / reports['journey_count']
    cps = float(reports['total_spend']) / reports['total_journey_time']
    return dict(
        mean_journey_cost=mjc,
        cost_per_second=cps
    )


def create(cursor, uid):
    reports = {}
    reports.update(create_raw(cursor, uid, reports))
    reports.update(create_daily(cursor, uid, reports))
    reports.update(create_weekly(cursor, uid, reports))
    reports.update(create_monthly(cursor, uid, reports))
    reports.update(create_annually(cursor, uid, reports))
    reports.update(create_journey(cursor, uid, reports))
    return reports


def asText(r):
    return '\n'.join(['%s: %s' % (k, v) for k, v in r.iteritems()])


def asHtml(r):
    return ''
