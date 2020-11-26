import pytest

from timezone import convert_time_from_utc, convert_time_to_utc, timezone_difference

time_from_utc_examples = [
    ('12:30', 'UTC+03:00', '15:30'),
    ('00:01', 'UTC+05:45', '05:46'),
    ('23:59', 'UTC+14:00', '13:59'),
    ('08:29', 'UTC−12:00', '20:29'),
    ('00:00', 'UTC±00:00', '00:00'),
    ('15:30', 'UTC+26:00', '17:30'),
]


@pytest.mark.parametrize('utc_time, timezone, expected_time', time_from_utc_examples)
def test_convert_time_from_utc(utc_time, timezone, expected_time):
    time = convert_time_from_utc(utc_time, timezone)
    assert time == expected_time


time_to_utc_examples = [
    ('15:30', 'UTC+03:00', '12:30:00'),
    ('05:46', 'UTC+05:45', '00:01:00'),
    ('13:59', 'UTC+14:00', '23:59:00'),
    ('20:29', 'UTC−12:00', '08:29:00'),
    ('00:00', 'UTC±00:00', '00:00:00'),
    ('15:30', 'UTC+26:00', '13:30:00'),
]


@pytest.mark.parametrize('time, timezone, expected_time', time_to_utc_examples)
def test_convert_time_to_utc(time, timezone, expected_time):
    utc_time = convert_time_to_utc(time, timezone)
    assert utc_time == expected_time


timezone_difference_examples = [
    ('UTC+03:00', 'UTC+03:00', 'UTC+00:00'),
    ('UTC+14:00', 'UTC+05:45', 'UTC+08:15'),
    ('UTC+05:45', 'UTC+14:00', 'UTC-08:15'),
    ('UTC+08:45', 'UTC−09:30', 'UTC+18:15'),
    ('UTC−09:30', 'UTC+08:45', 'UTC-18:15'),
    ('UTC−12:00', 'UTC+14:00', 'UTC-26:00'),
    ('UTC+14:00', 'UTC−12:00', 'UTC+26:00'),
]


@pytest.mark.parametrize(
    'timezone1, timezone2, expected_timezone', timezone_difference_examples
)
def test_timezone_difference(timezone1, timezone2, expected_timezone):
    timezone = timezone_difference(timezone1, timezone2)
    assert timezone == expected_timezone
