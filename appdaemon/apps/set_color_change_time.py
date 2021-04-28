from datetime import datetime, date, timedelta, timezone
from datetime import time
from math import cos, pi
from typing import Tuple

import hassapi as hass


SHORTEST_DAY_OF_MONTH = 21
SHORTEST_DAY_MONTH = 12
YEAR = timedelta(days=365)
HOUR = timedelta(hours=1)


class ColorChangeTimer(hass.Hass):

    def initialize(self):
        in_one_minute = self.datetime() + timedelta(minutes=1)
        one_minute_in_seconds = 60
        self.run_every(self.set_times,
                       start=in_one_minute,
                       interval=5*one_minute_in_seconds)

    def set_times(self, kwargs):
        self.set_evening_time(kwargs)
        self.set_night_time(kwargs)

    def set_evening_time(self, kwargs):
        self.max_evening_time_utc = time(hour=22)
        self.min_evening_time_utc = time(hour=18)
        now = get_now_with_timezone()
        self.evening_time = self.get_evening_time(now)
        formatted_time = self.evening_time.strftime('%H:%M:00')
        self.call_service(
            'input_datetime/set_datetime',
            entity_id='input_datetime.early_eve_start_time',
            time=formatted_time)

    def get_evening_time(self, now: datetime) -> datetime:
        """
        now as datetime in the local timezone, and aware, i.e. have the local 
            timezone as tzinfo attribute
        min_time_utc and max_time_utc time at which to change color on shortest
            and longest day, in utc
        """
        time_since_solstice = now.date() - get_shortest_day_in(now.year)
        amplitude, average = get_amplitude_and_average_from_extrema(
            self.max_evening_time_utc,
            self.min_evening_time_utc)

        desired_time_in_utc: timedelta = \
            average + amplitude * cos(2 * pi * time_since_solstice / YEAR)

        evening_time_utc = to_midnight_utc(now) + desired_time_in_utc
        evening_time_local = evening_time_utc.astimezone(now.tzinfo)
        return evening_time_local

    def set_night_time(self, kwargs):
        now = get_now_with_timezone()
        self.night_time = self.get_night_time(now)
        formatted_time = self.night_time.strftime('%H:%M:00')
        self.call_service(
            'input_datetime/set_datetime',
            entity_id='input_datetime.night_start_time',
            time=formatted_time)
        
    def get_night_time(self, now: datetime) -> time:
        today = now.date()
        time_since_solstice: timedelta = today - get_shortest_day_in(today.year)

        offset = 1.25*HOUR + 0.75*HOUR * cos(2*pi*time_since_solstice/YEAR)
        return self.evening_time + offset


def get_now_with_timezone():
    return datetime.now().astimezone()


def to_midnight_utc(now: datetime) -> datetime:
    return datetime(year=now.year, month=now.month, day=now.day,
                    tzinfo=timezone.utc)


def get_shortest_day_in(year: int) -> date:
    return date(year=year,
                month=SHORTEST_DAY_MONTH,
                day=SHORTEST_DAY_OF_MONTH)


def get_amplitude_and_average_from_extrema(max_time: time, min_time: time) -> Tuple[timedelta, timedelta]:
    max_time = to_timedelta(max_time)
    min_time = to_timedelta(min_time)
    average: timedelta = (max_time + min_time) / 2
    amplitude: timedelta = (max_time - min_time) / 2
    return amplitude, average


def to_timedelta(naive_time: time) -> timedelta:
    return timedelta(hours=naive_time.hour,
                     minutes=naive_time.minute,
                     seconds=naive_time.second)
