from datetime import datetime, date, time

from appdaemontestframework import automation_fixture

from apps.autocolor_execution import AutoColorController, DESIRED_COLOR_ENTITY, LIGHTS_TO_CHANGE, AUTO_SET_TEMP_SWITCH, \
    EVE_START_TIME, NIGHT_START_TIME, MAX_COLOR_TEMP, MIN_COLOR_TEMP, MORNING_START_TIME


@automation_fixture(AutoColorController)
def color_controller(given_that):
    given_that.state_of('input_boolean.auto_color_enabled').is_set_to('on', attributes={'state': 'on'})
    for light in LIGHTS_TO_CHANGE:
        given_that.state_of(light).is_set_to('off', attributes={'state': 'off'})


# noinspection PyShadowingNames
def test_change_on_lights_does_not_turn_on_off_lights(given_that, color_controller, assert_that):
    given_that.state_of('light.woonkamer').is_set_to(
        'off', attributes={'state': 'off'})

    color_controller.change_color_of_on_lights(DESIRED_COLOR_ENTITY, 'state', '250.0', '255.0', {})

    assert_that('light.woonkamer').was_not.turned_on()


# noinspection PyShadowingNames
def test_change_on_lights_does_change_on_lights(given_that, color_controller, assert_that):
    desired_color = 255.0
    given_that.state_of('light.woonkamer').is_set_to(
        'on',
        attributes={'state': 'on',
                    'color_temp': 250.0})

    color_controller.change_color_of_on_lights(DESIRED_COLOR_ENTITY, 'state', '250.0', str(desired_color), {})

    assert_that('light.woonkamer').was.turned_on(color_temp=desired_color)


# noinspection PyShadowingNames
def test_on_light_turn_on_does_nothing_when_light_is_right_color(given_that, color_controller, assert_that):
    light_entity = 'light.woonkamer'
    desired_color = 250.0
    given_that.state_of(DESIRED_COLOR_ENTITY).is_set_to(desired_color)
    given_that.state_of(light_entity).is_set_to(
        'on',
        attributes={'state': 'on',
                    'color_temp': desired_color})

    color_controller.on_light_turn_on(light_entity, 'state', 'off', 'on', {})

    assert_that(light_entity).was_not.turned_on()


# noinspection PyShadowingNames
def test_on_light_turn_on_does_change_color_when_light_is_wrong_color(given_that, color_controller, assert_that):
    light_entity = 'light.woonkamer'
    desired_color = 255.0
    given_that.state_of(DESIRED_COLOR_ENTITY).is_set_to(desired_color)
    given_that.state_of(light_entity).is_set_to(
        'on',
        attributes={'state': 'on',
                    'color_temp': 250.0})

    color_controller.on_light_turn_on(light_entity, 'state', 'off', 'on', {})

    assert_that(light_entity).was.turned_on(color_temp=desired_color)


# noinspection PyShadowingNames
def test_set_color_interpolates_during_evening(given_that, color_controller, assert_that):
    expected_end_color = (MIN_COLOR_TEMP + MAX_COLOR_TEMP) / 2.
    eve_start = time(hour=18)
    test_time = time(hour=19)
    night_start = time(hour=20)
    given_that.state_of(AUTO_SET_TEMP_SWITCH).is_set_to('on', attributes={'state': 'on'})
    given_that.state_of(MORNING_START_TIME).is_set_to(time(hour=8).isoformat())
    given_that.state_of(EVE_START_TIME).is_set_to(eve_start.isoformat())
    given_that.state_of(NIGHT_START_TIME).is_set_to(night_start.isoformat())
    given_that.time_is(datetime.combine(date(year=2021, month=5, day=24),
                                        test_time))

    color_controller.set_desired_color({})

    assert_that('input_number/set_value').was.called_with(
        entity_id=DESIRED_COLOR_ENTITY,
        value=expected_end_color
    )
