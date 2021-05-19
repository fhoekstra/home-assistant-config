from datetime import datetime, timedelta, date, time

import pytest
from appdaemontestframework import automation_fixture

from apps.autocolor_set_times import ColorChangeTimer, SHORTEST_DAY_MONTH, SHORTEST_DAY_OF_MONTH, ON_OFF_SWITCH, \
    EVE_START_TIME, MIN_EVENING_TIME_UTC, MAX_EVENING_TIME_UTC, MIDWINTER_DURATION, MIDSUMMER_DURATION, NIGHT_START_TIME

WINTER_TIME_LOCAL_UTC_OFFSET = timedelta(hours=1)
SUMMER_TIME_LOCAL_UTC_OFFSET = timedelta(hours=2)


@automation_fixture(ColorChangeTimer)
def color_change_timer(given_that):
    pass


# noinspection PyShadowingNames
def test_midwinter_evening_time_is_set(given_that, color_change_timer, assert_that):
    expected_time = (datetime.combine(date.today(),
                                      MIN_EVENING_TIME_UTC)
                     + WINTER_TIME_LOCAL_UTC_OFFSET
                     ).time()
    given_that.time_is(get_shortest_day_noon())
    given_that.state_of(ON_OFF_SWITCH).is_set_to('on', attributes={'state': 'on'})

    color_change_timer.set_times({})

    assert_that('input_datetime/set_datetime').was.called_with(
        entity_id=EVE_START_TIME,
        time=expected_time.isoformat(),
    )


# noinspection PyShadowingNames
def test_midsummer_evening_time_is_set(given_that, color_change_timer, assert_that):
    expected_time = _add_to_time_timedelta(
        MAX_EVENING_TIME_UTC,
        SUMMER_TIME_LOCAL_UTC_OFFSET)
    given_that.time_is(get_longest_day())
    given_that.state_of(ON_OFF_SWITCH).is_set_to('on', attributes={'state': 'on'})

    color_change_timer.set_times({})

    assert_that('input_datetime/set_datetime').was.called_with(
        entity_id=EVE_START_TIME,
        time=expected_time.isoformat(),
    )


# noinspection PyShadowingNames
def test_duration_midwinter(given_that, color_change_timer, assert_that):
    given_that.time_is(get_shortest_day_noon())
    given_that.state_of(ON_OFF_SWITCH).is_set_to('on', attributes={'state': 'on'})

    color_change_timer.set_times({})

    assert color_change_timer.duration == MIDWINTER_DURATION


# noinspection PyShadowingNames
def test_duration_midsummer(given_that, color_change_timer, assert_that):
    given_that.time_is(get_longest_day())
    given_that.state_of(ON_OFF_SWITCH).is_set_to('on', attributes={'state': 'on'})

    color_change_timer.set_times({})

    assert are_timedeltas_approx_equal(MIDSUMMER_DURATION, color_change_timer.duration)


# noinspection PyShadowingNames
def test_night_time_is_set(given_that, color_change_timer, assert_that):
    expected_time = _add_to_time_timedelta(
        _add_to_time_timedelta(
            MAX_EVENING_TIME_UTC,
            SUMMER_TIME_LOCAL_UTC_OFFSET),
        MIDSUMMER_DURATION)
    given_that.time_is(get_longest_day())
    given_that.state_of(ON_OFF_SWITCH).is_set_to('on', attributes={'state': 'on'})

    color_change_timer.set_times({})

    ass_obj = assert_that('input_datetime/set_datetime')
    assert_that('input_datetime/set_datetime').was.called_with(
        entity_id=NIGHT_START_TIME,
        time=expected_time.isoformat()
    )


def are_timedeltas_approx_equal(td_0: timedelta, td_1: timedelta) -> bool:
    return (td_0.total_seconds()
            == pytest.approx(td_1.total_seconds(), 1.))


def get_shortest_day_noon() -> datetime:
    return datetime(
        year=2020, month=SHORTEST_DAY_MONTH, day=SHORTEST_DAY_OF_MONTH,
        hour=12, minute=0, second=0, microsecond=0)


def get_longest_day() -> datetime:
    return get_shortest_day_noon() + timedelta(days=(365.25 / 2))


def _add_to_time_timedelta(t: time, td: timedelta) -> time:
    return (
            datetime.combine(
                date.today(),
                t)
            + td).time()
