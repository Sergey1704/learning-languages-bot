# file for timezone conversion functions


def convert_time_from_utc(utc_time: str, timezone: str) -> str:
    utc_time = utc_time[:5]
    utc_hours, utc_minutes = [int(t) for t in utc_time.split(':')]
    sign = 1 if timezone[3] == '+' else -1
    tz_hours, tz_minutes = [int(t) for t in timezone[-5:].split(':')]

    hours = utc_hours + sign * tz_hours
    minutes = utc_minutes + sign * tz_minutes

    if not 0 <= minutes <= 59:
        hours += minutes // 60
        minutes %= 60
    if not 0 <= hours <= 23:
        hours %= 24

    time = ':'.join([str(hours).zfill(2), str(minutes).zfill(2)])

    return time


def convert_time_to_utc(time: str, timezone: str) -> str:
    if timezone[3] == '+':
        inverse_timezone = timezone.replace('+', '-')
    else:
        inverse_timezone = timezone.replace('-', '+')

    utc_time = convert_time_from_utc(time, inverse_timezone)
    utc_time += ':00'

    return utc_time


def timezone_difference(timezone1: str, timezone2: str) -> str:
    sign1 = 1 if timezone1[3] == '+' else -1
    sign2 = 1 if timezone2[3] == '+' else -1
    tz1_hours, tz1_minutes = [int(t) for t in timezone1[-5:].split(':')]
    tz2_hours, tz2_minutes = [int(t) for t in timezone2[-5:].split(':')]

    tz_minutes = sign1 * (tz1_hours * 60 + tz1_minutes) - sign2 * (tz2_hours * 60 + tz2_minutes)
    sign = '+' if tz_minutes >= 0 else '-'

    tz_hours = abs(tz_minutes) // 60
    tz_minutes = abs(tz_minutes) % 60

    timezone = 'UTC' + sign + ':'.join([str(tz_hours).zfill(2), str(tz_minutes).zfill(2)])

    return timezone
