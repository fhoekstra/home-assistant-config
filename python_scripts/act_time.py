
# define colors for each part of day
timecolor = {'Day': 4000, 'Evening': 2700, 'Night': 2200}

# define excluded lights for each timeofday
day_exclude = ['nachtkastje', 'slaapkamer_plafond']
excludes = {'Day': day_exclude, 'Evening': [], 'Night':[]}

# Get timeofday
timeofday = data.get('timeofday', None)

if timeofday is None:
    logger.warning("act_time/py: could not get timeofday!")
elif not timeofday in ('Day', 'Evening', 'Night'):
    logger.warning("act_time.py: Unexpected value for timeofday sensor state!")

# Get lights, remove excludes
all_lights = hass.states.entity_ids('light')
lights = []
for li in all_lights:
    if not li in excludes[timeofday]:
        lights.append(li)

if not lights:
    logger.warning("act_time.py: could not get any light ids!")
    
offlights = []
onlights = []
for entity_id in lights:
    state = hass.states.get(entity_id)
    if state.state == 'off':
        offlights.append(entity_id)
    elif state.state == 'on':
        onlights.append(entity_id)
    else:
        logger.warning("act_time.py: weird state "+str(state.state)+" of entity "+str(entity_id))
    
#logger.info("These lights are off: "+str(offlights))
                   
# Change color of off lights
for entity_id in offlights:
    service_data = {'entity_id': entity_id, 'kelvin': timecolor[timeofday]}
    hass.services.call('light', 'turn_on', service_data)
    time.sleep(0.2)

time.sleep(2)
# Turn them back off
for entity_id in offlights:
    service_data = {'entity_id': entity_id}
    hass.services.call('light', 'turn_off', service_data) # turn them back off
    time.sleep(0.2)
    if (offlights.index(entity_id) >= (len(offlights) - 2)):
        hass.services.call('light', 'turn_off', service_data)
        time.sleep(0.2)

# Wait 10 seconds
time.sleep(10)

# Start transitioning the color of the on lights
for entity_id in onlights:
    service_data = {'entity_id': entity_id, 'kelvin': timecolor[timeofday], 'transition': 600}
    hass.services.call('light', 'turn_on', service_data)
    time.sleep(1)
#logger.info("Done!")
