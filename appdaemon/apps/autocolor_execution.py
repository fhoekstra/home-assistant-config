from datetime import time, timedelta, datetime, date
from typing import Tuple, Iterable

import appdaemon.plugins.hass.hassapi as hass

LIGHT_NAMES = ('woonkamer', 'gang', 'wc', 'badkamer', 'nachtkastje', 'slaapkamer_plafond')
LIGHTS_TO_CHANGE = tuple(f'light.{name}' for name in LIGHT_NAMES)

MIN_COLOR_TEMP = 250.
MAX_COLOR_TEMP = 455.
DESIRED_COLOR_ENTITY = 'input_number.desired_color_temperature'
MORNING_START_TIME = 'input_datetime.morning_start_time'
EVE_START_TIME = 'input_datetime.early_eve_start_time'
NIGHT_START_TIME = 'input_datetime.night_start_time'
AUTO_SET_TEMP_SWITCH = 'input_boolean.automatic_color_temp_adjustment'
AUTO_COLOR_SWITCH = 'input_boolean.auto_color_enabled'


# noinspection PyAttributeOutsideInit
class AutoColorController(hass.Hass):
    def initialize(self):
        # set color entity
        self.run_every(
            callback=self.set_desired_color,
            start=self.datetime() + timedelta(seconds=1),
            interval=timedelta(seconds=5).total_seconds())
        self.listen_state(self.on_input_change, AUTO_SET_TEMP_SWITCH)
        self.listen_state(self.on_input_change, AUTO_COLOR_SWITCH)
        self.listen_state(self.on_input_change, DESIRED_COLOR_ENTITY)
        # set color of lights
        self.listen_state(self.on_auto_color_turn_on, AUTO_COLOR_SWITCH)
        self.listen_state(self.change_color_of_on_lights, DESIRED_COLOR_ENTITY)
        self.listen_state(self.on_light_turn_on, 'light')

    def on_auto_color_turn_on(self, entity, attribute, old, new, kwargs):
        if attribute == 'state' and new == 'on':
            self.change_color_of_on_lights(None, None, None,
                                           self.get_state(DESIRED_COLOR_ENTITY), kwargs)

    def change_color_of_on_lights(self, entity, attribute, old, new, kwargs):
        if not self._is_state_on(AUTO_COLOR_SWITCH):
            return
        for light in LIGHTS_TO_CHANGE:
            if not self._is_state_on(light):
                continue
            self.call_service('light/turn_on',
                              entity_id=light,
                              color_temp=float(new))

    def on_light_turn_on(self, entity, attribute, old, new, kwargs):
        if entity not in LIGHTS_TO_CHANGE:
            return
        if not self._is_state_on(AUTO_COLOR_SWITCH):
            return
        if not (attribute == 'state' and new == 'on'):
            return
        desired_color_temp = float(self.get_state(DESIRED_COLOR_ENTITY))
        current_color_temp = float(self.get_state(entity, attribute='color_temp'))
        if current_color_temp == desired_color_temp:
            self.log(f'{entity} is already {desired_color_temp=}')
            return
        self.log(f'Changing {entity} to {desired_color_temp}')
        self.call_service(
            'light/turn_on',
            entity_id=entity,
            color_temp=desired_color_temp)

    def on_input_change(self, entity, attribute, old, new, kwargs):
        self.set_desired_color(kwargs)

    def set_desired_color(self, kwargs):
        if not self._is_state_on(AUTO_SET_TEMP_SWITCH):
            self.log('Automatic color temp adjustment is not turned on')
            return
        current_time = self._get_current_time()
        color = self.get_desired_color(current_time)
        self.call_service(
            'input_number/set_value',
            entity_id=DESIRED_COLOR_ENTITY,
            value=color)

    def get_desired_color(self, current_time: time) -> float:
        morning_start, evening_start, night_start = self.get_morning_evening_night_times()
        if current_time < self.subtract(morning_start, timedelta(minutes=30)):
            return MAX_COLOR_TEMP
        if current_time <= evening_start:
            return MIN_COLOR_TEMP
        if current_time < night_start:
            return self._get_interpolated_color(current_time, (evening_start, night_start))
        return MAX_COLOR_TEMP

    def get_morning_evening_night_times(self) -> Iterable[time]:
        for entity in (MORNING_START_TIME, EVE_START_TIME, NIGHT_START_TIME):
            yield time.fromisoformat(self.get_state(entity))

    def _get_interpolated_color(self, current_time: time, limits: Tuple[time, time]) -> float:
        start, end = (self._to_timedelta(t) for t in limits)
        current = self._to_timedelta(current_time)

        fraction_passed = (current - start) / (end - start)
        self.log(f'{fraction_passed}')
        mireds_to_add = fraction_passed * self.mired_difference()
        return MIN_COLOR_TEMP + mireds_to_add

    @staticmethod
    def mired_difference() -> float:
        return MAX_COLOR_TEMP - MIN_COLOR_TEMP

    def _is_state_on(self, entity: str) -> bool:
        return self.get_state(entity, attribute='state') == 'on'

    def _get_current_time(self) -> time:
        current_time = self.datetime().time()
        return current_time

    @staticmethod
    def subtract(t: time, d: timedelta) -> time:
        return (datetime.combine(date.today(), t) - d).time()

    @staticmethod
    def _to_timedelta(t: time) -> timedelta:
        return timedelta(hours=t.hour,
                         minutes=t.minute,
                         seconds=t.second)
