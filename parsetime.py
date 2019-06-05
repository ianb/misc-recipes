"""
Parses time expressions into dateutil relative dates::

    >>> def rr(expr):
    ...     print rrule_repr(parse(expr))
    >>> rr('Wednesday 2am')
    rrule(HOURLY, byhour=2, byweekday=2)
    >>> rr('Wed 14:00')
    rrule(MINUTELY, byhour=14, byweekday=2)
    >>> rr('Wed(1)')
    rrule(WEEKLY, bysetpos=1, byweekday=2)
    >>> rr('5min')
    rrule(MINUTELY, interval=5)
    >>> rr('1 hour')
    rrule(HOURLY)
    >>> rr('1 hour 5 minute')
    rrule(MINUTELY, interval=65)
    >>> rr('1 day')
    rrule(DAILY)
    >>> rr('calendar day 1')
    rrule(MONTHLY, bymonthday=1)
"""

import re
import datetime
import dateutil.relativedelta as rel
from dateutil import rrule

days = 'monday|mon|mo|tuesday|tues|tue|tu|wednesday|wednseday|wednsday|wedsday|wedesday|wensday|wed|we|thursday|thurs|thur|thu|th|friday|frid|fri|fr|saturday|satur|sat|sa|sunday|sun|su'
day_map = {
    'mo': rel.MO, 'tu': rel.TU, 'we': rel.WE, 'th': rel.TH, 'fr': rel.FR, 'sa': rel.SA, 'su': rel.SU}
days_re = re.compile(days, re.I)

day_spec = '('+days+')[(](-?[0-9]+)[)]'
day_spec_re = re.compile(day_spec, re.I)

units = '([0-9]+)\s*(seconds|second|secs|sec|minutes|minute|mins|min|hours|hour|days|day|weeks|week|months|month|years|year|yrs|yr)'
unit_map = {
    'se': rrule.SECONDLY,
    'mi': rrule.MINUTELY,
    'ho': rrule.HOURLY,
    'da': rrule.DAILY,
    'we': rrule.WEEKLY,
    'mo': rrule.MONTHLY,
    'ye': rrule.YEARLY,
    'yr': rrule.YEARLY,
    }
units_re = re.compile(units, re.I)

unit_trans = {
    (rrule.SECONDLY, rrule.MINUTELY): 60,
    (rrule.SECONDLY, rrule.HOURLY): 60*60,
    (rrule.SECONDLY, rrule.DAILY): 60*60*24,
    (rrule.SECONDLY, rrule.WEEKLY): 60*60*24*7,
    (rrule.SECONDLY, rrule.MONTHLY): 60*60*24*30,
    (rrule.SECONDLY, rrule.YEARLY): 60*60*24*395,
    (rrule.MINUTELY, rrule.HOURLY): 60,
    (rrule.MINUTELY, rrule.DAILY): 60*24,
    (rrule.MINUTELY, rrule.WEEKLY): 60*24*7,
    (rrule.MINUTELY, rrule.MONTHLY): 60*24*30,
    (rrule.MINUTELY, rrule.YEARLY): 60*24*365,
    (rrule.HOURLY, rrule.DAILY): 24,
    (rrule.HOURLY, rrule.WEEKLY): 24*7,
    (rrule.HOURLY, rrule.MONTHLY): 24*30,
    (rrule.HOURLY, rrule.YEARLY): 24*365,
    (rrule.DAILY, rrule.WEEKLY): 7,
    (rrule.DAILY, rrule.MONTHLY): 30,
    (rrule.DAILY, rrule.YEARLY): 365,
    (rrule.WEEKLY, rrule.MONTHLY): 4,
    (rrule.WEEKLY, rrule.YEARLY): 52,
    (rrule.MONTHLY, rrule.YEARLY): 12,
    }

calendar = 'cal[ea]nd[ea]r\s+day\s+([0-9]+)'
calendar_re = re.compile(calendar, re.I)

time = '([0-9]{1,2}):([0-9][0-9])(?::([0-9][0-9]))?(?:(am|pm))?'
time_re = re.compile(time, re.I)

hour = '([0-9]{1,2})(am|pm)'
hour_re = re.compile(hour, re.I)

def parse(expr):
    kw = {}
    kw['dtstart'] = datetime.datetime(1970, 1, 1, 0, 0, 0)
    while 1:
        expr = expr.strip()
        if not expr:
            break
        m = day_spec_re.search(expr)
        if m:
            day = day_map[m.group(1).lower()[:2]]
            spec = int(m.group(2))
            kw.setdefault('byweekday', []).append(day)
            kw['bysetpos'] = spec
            kw.setdefault('freq', rrule.WEEKLY)
            expr = expr[m.end():]
            continue
        m = days_re.search(expr)
        if m:
            day = day_map[m.group(0).lower()[:2]]
            kw.setdefault('byweekday', []).append(day)
            expr = expr[m.end():]
            continue
        m = units_re.search(expr)
        if m:
            v = int(m.group(1))
            unit = unit_map[m.group(2)[:2].lower()]
            if 'interval' in kw:
                old_unit = kw['freq']
                old_interval = kw['interval']
                if old_unit == unit:
                    # Just add more time...
                    v == old_interval
                elif (old_unit, unit) in unit_trans:
                    # Turn new unit into old unit
                    v *= unit_trans[(old_unit, unit)]
                    unit = old_unit
                    v += old_interval
                elif (unit, old_unit) in unit_trans:
                    # Turn old unit into new unit
                    old_interval *= unit_trans[(unit, old_unit)]
                    v += old_interval
                else:
                    raise ValueError(
                        "Cannot convert from unit %s to %s" % (old_unit, unit))
            kw['freq'] = unit
            kw['interval'] = v
            expr = expr[m.end():]
            continue
        m = calendar_re.search(expr)
        if m:
            day = int(m.group(1))
            kw['bymonthday'] = day
            expr = expr[m.end():]
            kw.setdefault('freq', rrule.MONTHLY)
            continue
        m = time_re.search(expr)
        if m:
            hour = int(m.group(1))
            minute = int(m.group(2))
            if m.group(3):
                second = m.group(3)
            else:
                second = None
            if m.group(4):
                ampm = m.group(4).lower()
                if ampm == 'pm' and hour != 12:
                    hour += 12
                elif ampm == 'am' and hour == 12:
                    hour = 0
            kw['byhour'] = hour
            kw['byminute'] = minute
            if second is not None:
                kw['bysecond'] = second
            kw.setdefault('freq', rrule.MINUTELY)
            expr = expr[m.end():]
            continue
        m = hour_re.search(expr)
        if m:
            hour = int(m.group(1))
            ampm = m.group(2).lower()
            if ampm == 'pm' and hour != 12:
                hour += 12
            elif ampm == 'am' and hour == 12:
                hour = 0
            kw['byhour'] = hour
            kw.setdefault('freq', rrule.HOURLY)
            expr = expr[m.end():]
            continue
        raise ValueError(
            "Cannot parse expression from: %r" % expr)
    return rrule.rrule(**kw)

freq_map = {
    rrule.SECONDLY: 'SECONDLY',
    rrule.MINUTELY: 'MINUTELY',
    rrule.HOURLY: 'HOURLY',
    rrule.DAILY: 'DAILY',
    rrule.WEEKLY: 'WEEKLY',
    rrule.MONTHLY: 'MONTHLY',
    rrule.YEARLY: 'YEARLY',
    }

def rrule_repr(rule):
    values = []
    freq = freq_map[rule._freq]
    values.append(freq)
    # This defaults to now(), which means it must always be filled
    # in, which I don't like:
    #   * _dtstart
    #   * _timeset
    for attr in ['_byeaster', '_byhour', '_byminute', '_bymonth',
                 '_bymonthday', '_bynmonthday', '_bynweekday',
                 '_bysecond', '_bysetpos', '_byweekday', '_byweekno',
                 '_byyearday', '_cache', '_count',
                 '_interval',
                 '_tzinfo', '_until', '_wkst']:
        val = getattr(rule, attr)
        if val is None or val == ():
            continue
        if isinstance(val, tuple) and len(val) == 1:
            val = val[0]
        if attr == '_interval' and val == 1:
            continue
        if attr == '_wkst' and val == 0:
            continue
        if attr in ('_byhour', '_byminute', '_bysecond') and val == 0:
            continue
        if attr.startswith('_'):
            attr = attr[1:]
        values.append('%s=%r' % (attr, val))
    return 'rrule(%s)' % ', '.join(values)
    
if __name__ == '__main__':
    import doctest
    doctest.testmod()
    
