from datetime import timedelta

import appdaemon.plugins.hass.hassapi as hass


class SimpleForTesting(hass.Hass):
    def initialize(self):
        self.run_every(
            callback=self.do_thing,
            start=self.datetime() + timedelta(minutes=1),
            interval=timedelta(hours=2, minutes=7)
                .total_seconds())

    def do_thing(self, kwargs):
        self.turn_on('this_id')
