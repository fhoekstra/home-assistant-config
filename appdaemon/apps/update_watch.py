import appdaemon.plugins.hass.hassapi as hass

SYSTEMS_TO_WATCH = (
    'appdaemon_4',
    'home_assistant_operating_system',
    'deconz',
    'node_red'
)


class UpdateWatcher(hass.Hass):
    def initialize(self):
        self.listen_state(self.on_new_ha_version,
                          entity='sensors.latest_ha_version')
        for system in SYSTEMS_TO_WATCH:
            self.listen_state(
                self.on_update_available,
                entity=f'binary_sensor.{system}_update_available',
                new='on',
            )

    def on_new_ha_version(self, entity, attribute, old, new, kwargs):
        self.call_service(
            'notify.mobile_app_fp3',
            message=f'Update available for HA Core.'
                    f' Upgrade to {new} in Home Assistant'
        )

    def on_update_available(self, entity, attribute, old, new, kwargs):
        system = entity[len('binary_sensor.')
                        :-len('_update_available')]
        new_version = self.get_state(f'sensor.{system}_newest_version')
        current_version = self.get_state(f'sensor.{system}_version')
        self.call_service(
            'notify.mobile_app_fp3',
            message=f'Update available for {system}.'
                    f' Upgrade from {current_version}'
                    f' to {new_version} in Home Assistant'
        )
