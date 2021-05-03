
# define colors for each part of day
time_color = {'Day': 4000, 'Evening': 2700, 'Night': 2200}

# define transition time in seconds
default_transition_time = 180

# define which lights to adjust for each time_of_day
slaapkamer_lights = ('slaapkamer_plafond', 'nachtkastje')
normal_groups = (*slaapkamer_lights, 'gang', 'gang', 'wc', 'badkamer', 'woonkamer')
excludes = {'Day': (*slaapkamer_lights, 'gang'), 'Evening': (), 'Night':()}

# brightness patterns
fast_transition_seconds = 10
dark_at_night = {'Day': 100, 'Evening': 40, 'Night': 1, 'transition_time': fast_transition_seconds}
morning_full = {'Day': 100, 'transition_time': fast_transition_seconds}
less_bright_at_night = {'Day': 100, 'Night': 70, 'transition_time': fast_transition_seconds}

# global entity_id : brightness pattern mapping
brightadjust = {
    'light.wc': dark_at_night,
    'light.nachtkastje': dark_at_night,
    'light.gang': dark_at_night,
    'light.badkamer': less_bright_at_night,
    'light.woonkamer': morning_full,
    }

# process settings, prepare dicts
adjust_groups = {}
for t in time_color.keys():
    adjust_groups[t] = list(normal_groups)
    for excl in excludes[t]:
        if excl in adjust_groups[t]:
            adjust_groups[t].pop(adjust_groups[t].index(excl))

# Get time_of_day
time_of_day = data.get('time_of_day', None)

if time_of_day is None:
    logger.error("act_time/py: could not get time_of_day!")
elif not time_of_day in ('Day', 'Evening', 'Night'):
    logger.error("act_time.py: Unexpected value for time_of_day sensor state!")


def set_brightness_pct(service_data, entity_id, set_time=False):

    if not entity_id in brightadjust:
        return

    pattern = brightadjust[entity_id]

    if not time_of_day in pattern:
        return

    service_data['brightness_pct'] = pattern[time_of_day]

    if set_time:
        service_data['transition'] = pattern.get('transition_time', default_transition_time)


offlights = []
onlights = []
for lightgroup in adjust_groups[time_of_day]:
    entity_id = 'light.'+lightgroup
    state = hass.states.get(entity_id)
    if state.state == 'off':
        offlights.append(entity_id)
    elif state.state == 'on':
        onlights.append(entity_id)
    else:
        logger.warning(f"act_time.py: weird state {state.state} of entity {entity_id}")

logger.debug(f"These lights are off: {offlights}")

# Turn on all lights (for partially on rooms and off lights)
hass.services.call(
    'light', 'turn_on',
    {'entity_id': 'light.all_lights_except_ochtend_lamp'})
time.sleep(1.0)

# Change color of off lights
for entity_id in offlights:
    service_data = {'entity_id': entity_id, 'kelvin': time_color[time_of_day]}
    set_brightness_pct(service_data, entity_id)  # and brightness optionally
    hass.services.call('light', 'turn_on', service_data)
    time.sleep(0.4)

time.sleep(3)
# Turn them back off
for entity_id in offlights:
    service_data = {'entity_id': entity_id}
    hass.services.call('light', 'turn_off', service_data) # turn them back off
    time.sleep(0.2)
    if (offlights.index(entity_id) >= (len(offlights) - 2)):
        hass.services.call('light', 'turn_off', service_data)
        time.sleep(0.2)
hass.services.call('light', 'turn_off', {'entity_id': offlights})

time.sleep(5)

# Start transitioning the color of the on lights
for entity_id in onlights:
    service_data = {
        'entity_id': entity_id,
        'kelvin': time_color[time_of_day],
        'transition': default_transition_time
        }
    set_brightness_pct(service_data, entity_id, set_time=True)
    hass.services.call('light', 'turn_on', service_data)
    time.sleep(1)
#logger.info("Done!")
