from datetime import timedelta, time, datetime, date
from typing import Callable, Any

import hassapi as hass


class WakeUpLightsTimer(hass.Hass):
    def initialize(self):
        self._my_run_every(callback=self.set_times,
                           start=self.datetime() + timedelta(seconds=10),
                           interval=timedelta(seconds=3))

    def set_times(self, kwargs):
        """(states('input_number.morning_start_hour') | int  * 3600 )
                  + (states('input_number.morning_start_minutes') | int * 60)"""
        hour = self.get_basic_state('input_number.morning_start_hour')
        minute = self.get_basic_state('input_number.morning_start_minutes')
        morning_time = time(hour=int(float(hour)), minute=int(float(minute)))

        self.call_service('input_datetime/set_datetime',
                          entity_id='input_datetime.morning_start_time',
                          time=morning_time.strftime('%H:%M'))

        self.schedule_trigger(morning_time)

    def schedule_trigger(self, morning_time: time):
        morning_time = time(21, 30)
        duration_of_wake_up_sequence = self.get_basic_state('input_number.wakeup_time_transition')
        morning_start_datetime = datetime.combine(self.datetime().date(), morning_time)
        trigger_datetime = morning_start_datetime - timedelta(minutes=duration_of_wake_up_sequence)
        if trigger_datetime < self.datetime():
            yesterday = self.datetime() - timedelta(days=1)
            trigger_datetime = datetime.combine()  # TODO

        self.run_at(callback=self.fire_event_if_conditions_met,
                    start=datetime.combine(date.today(),
                                           time(hour=21, minute=25))
                    )

    def fire_event_if_conditions_met(self, kwargs):
        self.log('Run the scheduled trigger callback')

    def get_basic_state(self, entity_id):
        return self.get_state(entity_id=entity_id, attribute='state')

    def _my_run_every(self, callback: Callable[[dict], Any], start: datetime,
                      interval: timedelta, **kwargs):
        self.run_every(callback, start=start,
                       interval=interval.total_seconds(), **kwargs)
