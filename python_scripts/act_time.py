
# define colors for each part of day
time_color = {'Day': 4000, 'Evening': 2700, 'Night': 2200}

# define transition time in seconds
transition_time = 180

# define which lights to adjust for each time_of_day
normal_groups = ['slaapkamer', 'gang', 'gang', 'wc', 'badkamer', 'woonkamer']
excludes = {'Day': ['slaapkamer', 'gang'], 'Evening': [], 'Night':[]}

# brightness patterns
extreme_adjust = {'Day': 100, 'Evening': 40, 'Night': 1, 'time': 10}
morning_full = {'Day': 100}

# global entity_id : brightness pattern mapping
brightadjust = {
    'light.wc': extreme_adjust,
    'light.woonkamer': morning_full,
    'light.badkamer': morning_full,
    }

# process settings, prepare dicts
adjust_groups = {}
for t in time_color.keys():
    adjust_groups[t] = [gr for gr in normal_groups]
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
        service_data['transition'] = pattern.get('time', transition_time)


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

logger.debug("These lights are off: "+str(offlights))

# Turn on all lights (for partially on rooms and off lights)
hass.services.call('light', 'turn_on', {'entity_id': 'all'})
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

# Wait 10 seconds
time.sleep(10)

# Start transitioning the color of the on lights
for entity_id in onlights:
    service_data = {
        'entity_id': entity_id,
        'kelvin': time_color[time_of_day],
        'transition': transition_time
        }
    set_brightness_pct(service_data, entity_id, set_time=True)
    hass.services.call('light', 'turn_on', service_data)
    time.sleep(1)
#logger.info("Done!")
