from datetime import datetime, date, timedelta, timezone
from datetime import time
from math import cos, pi
from typing import Callable, Any

import hassapi as hass

MIN_EVENING_TIME_UTC = time(hour=18)
MAX_EVENING_TIME_UTC = time(hour=22)

SHORTEST_DAY_OF_MONTH = 21
SHORTEST_DAY_MONTH = 12
YEAR = timedelta(days=365)
HOUR = timedelta(hours=1)


# noinspection PyAttributeOutsideInit
class ColorChangeTimer(hass.Hass):

    def initialize(self):
        self.max_evening_time_utc = to_timedelta(MAX_EVENING_TIME_UTC)
        self.min_evening_time_utc = to_timedelta(MIN_EVENING_TIME_UTC)

        self._my_run_every(callback=self.set_times,
                           start=self.datetime() + timedelta(minutes=1),
                           interval=timedelta(minutes=5))

    def set_times(self, kwargs):
        if not self.is_switched_on():
            return
        evening_time = self.set_evening_time()
        self.set_night_time(evening_time)

    def is_switched_on(self):
        switch_state = self.get_state(
            entity_id='input_boolean.automatic_color_time_adjustment',
            attribute='state')
        self.log(f'{switch_state=}')
        return switch_state == 'on'

    def set_evening_time(self) -> datetime:
        now = self._get_now_with_timezone()
        self.evening_time = self.get_evening_time(now)
        formatted_time = self.evening_time.strftime('%H:%M:00')
        self.call_service(
            'input_datetime/set_datetime',
            entity_id='input_datetime.early_eve_start_time',
            time=formatted_time)
        self.log(f'Set evening time to {formatted_time}')
        return self.evening_time

    def get_evening_time(self, now: datetime) -> datetime:
        """
        now as datetime in the local timezone, and aware, i.e. have the local
            timezone as tzinfo attribute
        min_time_utc and max_time_utc time at which to change color on shortest
            and longest day, in utc
        """
        time_since_solstice = now.date() - get_shortest_day_in(now.year)

        desired_time_in_utc: timedelta = \
            self.evening_average \
            + self.evening_amplitude * cos(2 * pi * time_since_solstice / YEAR)

        evening_time_utc = to_midnight_utc(now) + desired_time_in_utc
        evening_time_local = evening_time_utc.astimezone(now.tzinfo)
        return evening_time_local

    def set_night_time(self, evening_time: datetime):
        self.night_time = self.get_night_time(evening_time)
        formatted_time = self.night_time.strftime('%H:%M:00')
        self.call_service(
            'input_datetime/set_datetime',
            entity_id='input_datetime.night_start_time',
            time=formatted_time)
        self.log(f'Set night time to {formatted_time}')

    def get_night_time(self, evening_time: datetime) -> datetime:
        today = evening_time.date()
        time_since_solstice: timedelta = today - get_shortest_day_in(today.year)

        offset = 1.25*HOUR + 0.75*HOUR * cos(2*pi*time_since_solstice/YEAR)
        return self.evening_time + offset

    @property
    def evening_amplitude(self) -> timedelta:
        return (self.max_evening_time_utc - self.min_evening_time_utc) / 2

    @property
    def evening_average(self) -> timedelta:
        return (self.max_evening_time_utc + self.min_evening_time_utc) / 2

    def _get_now_with_timezone(self):
        return self.datetime().astimezone()

    def _my_run_every(self, callback: Callable[[dict], Any], start: datetime,
                      interval: timedelta, **kwargs):
        self.run_every(callback, start=start,
                       interval=interval.total_seconds(), **kwargs)


def to_midnight_utc(now: datetime) -> datetime:
    return datetime(year=now.year, month=now.month, day=now.day,
                    tzinfo=timezone.utc)


def get_shortest_day_in(year: int) -> date:
    return date(year=year,
                month=SHORTEST_DAY_MONTH,
                day=SHORTEST_DAY_OF_MONTH)


def to_timedelta(naive_time: time) -> timedelta:
    return timedelta(hours=naive_time.hour,
                     minutes=naive_time.minute,
                     seconds=naive_time.second)
