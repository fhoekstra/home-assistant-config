from appdaemontestframework import automation_fixture

from apps.update_watch import UpdateWatcher, MY_SETTINGS_LINK, NOTIFY_ME

OLD_VERSION = '1.0'
NEW_VERSION = '2.0'


@automation_fixture(UpdateWatcher)
def update_watcher():
    pass


# noinspection PyShadowingNames
def test_update_of_node_red_is_watched(given_that, update_watcher, assert_that):

    update_watcher.initialize()

    assert_that(update_watcher) \
        .listens_to.state('binary_sensor.node_red_update_available') \
        .with_callback(update_watcher.on_update_available)


# noinspection PyShadowingNames
def test_update_of_ha_core_is_watched(given_that, update_watcher, assert_that):
    update_watcher.initialize()

    assert_that(update_watcher) \
        .listens_to.state('sensor.latest_ha_version') \
        .with_callback(update_watcher.on_new_ha_version)


def test_update_message_sent_for_add_on(given_that, update_watcher, assert_that):
    given_that.state_of('sensor.node_red_version').is_set_to(OLD_VERSION)
    given_that.state_of('sensor.node_red_newest_version').is_set_to(NEW_VERSION)

    update_watcher.on_update_available('binary_sensor.node_red_update_available', 'state', 'off', 'on', {})

    assert_that(NOTIFY_ME).was.called_with(
        message=f'Upgrade node_red in {MY_SETTINGS_LINK}'
    )
