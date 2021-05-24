from datetime import datetime, date, timedelta, timezone
from datetime import time
from math import cos, pi
from typing import Callable, Iterable

import appdaemon.plugins.hass.hassapi as hass

MIN_EVENING_TIME_UTC = time(hour=17)  # local_time is this + 1
MAX_EVENING_TIME_UTC = time(hour=20, minute=0)  # local_time is this + 2
MIDSUMMER_DURATION = timedelta(minutes=15)
MIDWINTER_DURATION = timedelta(hours=3, minutes=30)

NIGHT_START_TIME = 'input_datetime.night_start_time'
EVE_START_TIME = 'input_datetime.early_eve_start_time'
ON_OFF_SWITCH = 'input_boolean.automatic_color_time_adjustment'
INPUTS = ON_OFF_SWITCH, EVE_START_TIME, NIGHT_START_TIME

SHORTEST_DAY_OF_MONTH = 21
SHORTEST_DAY_MONTH = 12


# noinspection PyAttributeOutsideInit
class ColorChangeTimer(hass.Hass):

    def initialize(self):
        self.max_evening_time_utc = self.to_timedelta(MAX_EVENING_TIME_UTC)
        self.min_evening_time_utc = self.to_timedelta(MIN_EVENING_TIME_UTC)

        self.run_callback_on_change_of_any(self.on_input_change, INPUTS)

        self.run_every(
            callback=self.set_times,
            start=self.datetime() + timedelta(minutes=1),
            interval=timedelta(hours=2, minutes=7
                               ).total_seconds())

    def run_callback_on_change_of_any(self, callback: Callable, entity_ids: Iterable[str]):
        for entity_id in entity_ids:
            self.listen_state(callback, entity_id)

    def on_input_change(self, entity, attribute, old, new, kwargs):
        self.set_times(kwargs)

    def set_times(self, kwargs):
        if not self.is_switched_on():
            return
        evening_time = self.set_evening_time()
        self.set_night_time(evening_time)

    def is_switched_on(self):
        switch_state = self.get_state(
            entity_id=ON_OFF_SWITCH,
            attribute='state')
        self.log(f'{switch_state=}')
        return switch_state == 'on'

    def set_evening_time(self) -> datetime:
        now: datetime = self.datetime()
        self.evening_time = self.get_evening_time(now)
        formatted_time = self._format_in_hours_minutes(self.evening_time)
        self.call_service(
            'input_datetime/set_datetime',
            entity_id=EVE_START_TIME,
            time=formatted_time)
        self.log(f'Set evening time to {formatted_time}')
        return self.evening_time

    def get_evening_time(self, now: datetime) -> datetime:
        """
        now as datetime in the local timezone
        min_time_utc and max_time_utc time at which to change color on shortest
            and longest day, in utc
        """
        time_since_solstice = now.date() - self.get_shortest_day_in(now.year)

        desired_time_in_utc: timedelta = \
            self.evening_average \
            - self.evening_amplitude * cos(2 * pi
                                           * time_since_solstice / timedelta(days=365))

        evening_time_utc = self.to_midnight_utc(now) + desired_time_in_utc
        evening_time_local = evening_time_utc.astimezone()
        return evening_time_local

    def set_night_time(self, evening_time: datetime):
        self.night_time = self.get_night_time(evening_time)
        formatted_time = self._format_in_hours_minutes(self.night_time)
        self.call_service(
            'input_datetime/set_datetime',
            entity_id=NIGHT_START_TIME,
            time=formatted_time)
        self.log(f'Set night time to {formatted_time}')

    def get_night_time(self, evening_time: datetime) -> datetime:
        today = evening_time.date()
        time_since_solstice: timedelta = today - self.get_shortest_day_in(today.year)

        hour = timedelta(hours=1)
        offset = (
            self.duration_average
            + self.duration_amplitude * cos(2*pi
                                            * time_since_solstice / timedelta(days=365)))
        self.duration = offset
        return evening_time + self.duration

    @property
    def evening_amplitude(self) -> timedelta:
        return abs(self.max_evening_time_utc - self.min_evening_time_utc) / 2

    @property
    def evening_average(self) -> timedelta:
        return (self.max_evening_time_utc + self.min_evening_time_utc) / 2

    @property
    def duration_amplitude(self) -> timedelta:
        return abs(MIDWINTER_DURATION - MIDSUMMER_DURATION) / 2

    @property
    def duration_average(self) -> timedelta:
        return (MIDWINTER_DURATION + MIDSUMMER_DURATION) / 2

    @staticmethod
    def _format_in_hours_minutes(dt: datetime) -> str:
        """ Add half a minute for rounding """
        return (dt + timedelta(minutes=0.5)).strftime('%H:%M:00')

    @staticmethod
    def to_midnight_utc(now: datetime) -> datetime:
        return datetime(year=now.year, month=now.month, day=now.day,
                        tzinfo=timezone.utc)

    @staticmethod
    def get_shortest_day_in(year: int) -> date:
        return date(year=year,
                    month=SHORTEST_DAY_MONTH,
                    day=SHORTEST_DAY_OF_MONTH)

    @staticmethod
    def to_timedelta(naive_time: time) -> timedelta:
        return timedelta(hours=naive_time.hour,
                         minutes=naive_time.minute,
                         seconds=naive_time.second)
