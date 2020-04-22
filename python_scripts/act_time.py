
# define colors for each part of day
timecolor = {'Day': 4000, 'Evening': 2700, 'Night': 2200}
# define transition time in seconds
transitiontime = 180
# define which lights to adjust for each timeofday
normalgroups = ['slaapkamer', 'gang', 'gang', 'wc', 'badkamer', 'woonkamer']
excludes = {'Day': ['slaapkamer', 'gang'], 'Evening': [], 'Night':[]}
# brightness pattern
extremeadjust = {'Day': 100, 'Evening': 40, 'Night': 1, 'time': 10}
brightadjust = {'light.wc': extremeadjust}  # id: brightness pattern

# process settings, prepare dicts
adjustgroups = {}
for t in timecolor.keys():
    adjustgroups[t] = [gr for gr in normalgroups]
    for excl in excludes[t]:
        if excl in adjustgroups[t]:
            adjustgroups[t].pop(adjustgroups[t].index(excl))

# Get timeofday
timeofday = data.get('timeofday', None)

if timeofday is None:
    logger.warning("act_time/py: could not get timeofday!")
elif not timeofday in ('Day', 'Evening', 'Night'):
    logger.warning("act_time.py: Unexpected value for timeofday sensor state!")

offlights = []
onlights = []
for lightgroup in adjustgroups[timeofday]:
    entity_id = 'light.'+lightgroup
    state = hass.states.get(entity_id)
    if state.state == 'off':
        offlights.append(entity_id)
    elif state.state == 'on':
        onlights.append(entity_id)
    else:
        logger.warning("act_time.py: weird state "+str(state.state)+" of entity "+str(entity_id))

#logger.info("These lights are off: "+str(offlights))

# Turn on all lights (for partially on rooms and off lights)
hass.services.call('light', 'turn_on', {'entity_id': 'all'})
time.sleep(1.0)

# Change color of off lights
for entity_id in offlights:
    service_data = {'entity_id': entity_id, 'kelvin': timecolor[timeofday]}
    if entity_id in brightadjust:
        service_data['brightness_pct'] = brightadjust[entity_id][timeofday]
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
    service_data = {'entity_id': entity_id, 'kelvin': timecolor[timeofday],
                    'transition': transitiontime}
    if entity_id in brightadjust:
        pattern = brightadjust[entity_id]
        service_data['brightness_pct'] = pattern[timeofday]
        service_data['transition'] = pattern.get('time', transitiontime)
    hass.services.call('light', 'turn_on', service_data)
    time.sleep(1)
#logger.info("Done!")
