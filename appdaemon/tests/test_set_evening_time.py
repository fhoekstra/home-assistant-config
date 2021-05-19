from datetime import datetime

from appdaemontestframework import automation_fixture

from apps.autocolor_set_times import ColorChangeTimer, SHORTEST_DAY_MONTH, SHORTEST_DAY_OF_MONTH, ON_OFF_SWITCH, \
    EVE_START_TIME, MIN_EVENING_TIME_UTC


@automation_fixture(ColorChangeTimer)
def color_change_timer(given_that):
    pass


# noinspection PyShadowingNames
def test_midwinter_evening_time_is_set(given_that, color_change_timer, assert_that):
    given_that.time_is(datetime(
        year=2020, month=SHORTEST_DAY_MONTH, day=SHORTEST_DAY_OF_MONTH,
        hour=12, minute=0, second=0, microsecond=0))
    given_that.state_of(ON_OFF_SWITCH).is_set_to('on')

    color_change_timer.set_times({})

    assert_that('input_datetime/set_datetime').was.called_with(
        entity_id=EVE_START_TIME,
        time=MIN_EVENING_TIME_UTC.isoformat()
    )
