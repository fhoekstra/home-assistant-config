from collections import defaultdict
from datetime import time, datetime, date

import appdaemon.plugins.hass.hassapi as hass


# noinspection PyAttributeOutsideInit
class AutoColorController(hass.Hass):
    def initialize(self):
        self.run_once_at = defaultdict(set)
        self.listen_event(self.schedule_on_event, event='testing')

    def schedule_on_event(self, event_name, data, kwargs):
        start_time = time(hour=int(data['hour']),
                          minute=int(data['minute']))
        self.schedule_single_run_at(start_time, self.do_on_schedule)

    def schedule_single_run_at(self, start_time, callback):
        start_dt = datetime.combine(date.today(), start_time)

        self.run_once_at[self.get_name(callback)].add(start_time)
        self.run_at(callback, start=start_dt)

    def do_on_schedule(self, kwargs):
        if self.has_run(self.do_on_schedule):
            return
        self.do_stuff('scheduled')

    def has_run(self, callback) -> bool:
        current_time = self.get_current_time()
        cb_name = self.get_name(callback)
        if current_time not in self.run_once_at[cb_name]:
            return True
        self.run_once_at[cb_name].remove(current_time)
        return False

    def get_current_time(self):
        current_time = self.datetime().time().replace(second=0, microsecond=0)
        return current_time

    @staticmethod
    def get_name(callback):
        return str(callback).split()[1]

    def do_stuff(self, arg):
        self.toggle('light.bureau')
        self.log('toggled')
