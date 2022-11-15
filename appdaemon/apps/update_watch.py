import appdaemon.plugins.hass.hassapi as hass

NOTIFY_ME = 'notify/teledobbyme'

MY_SETTINGS_LINK = 'https://my.home-assistant.io/redirect/config'
HA_CHANGE_LOG = 'http://home-assistant.io/latest-release-notes/'


class UpdateWatcher(hass.Hass):
    def initialize(self):
        self.listen_state(self.on_new_ha_version,
                          'sensor.latest_ha_version')
        self.listen_state(
            self.on_update,
            'update.home_assistant_core_update',
        )
        self.listen_state(
            self.on_update,
            'update.appdaemon_update',
        )
        self.listen_state(
            self.on_update,
            'update.home_assistant_operating_system_update',
        )
        self.listen_state(
            self.on_update,
            'update.node_red_update',
        )

    def on_update(self, entity, attribute, old, new, kwargs):
        self.log(f'{entity=} \n {new=} \n {old=} \n {attribute=}')
        system_ = entity[len('update.')
                         :-len('_update')]
        new_version = self.get_attribute(
            f'update.{system_}_update',
            'latest_version')
        current_version = self.get_attribute(
            f'update.{system_}_update',
            'installed_version')
        message = (
            f'Upgrade {str(system_)} in {MY_SETTINGS_LINK}\n'
            + self.get_attribute(f'update.{system_}', 'release_summary')
        )
        self.log(message)
        self.call_service(NOTIFY_ME, message=message)

    def on_new_ha_version(self, entity, attribute, old, new, kwargs):
        self.call_service(
            NOTIFY_ME,
            message=f'Update available for HA Core. Change log:{HA_CHANGE_LOG}'
                    f' Upgrade to {new} in {MY_SETTINGS_LINK}',
            data=dict(parse_mode='html'),
        )
