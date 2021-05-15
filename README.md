# My Home Assistant configuration

Feel free to use whatever you find here for your own Home Assistant or other home automation.

## Use Cases

Includes automations for the following use cases:

* [:zap:][4] smart lights:
  * changing color temperature automatically based on time of day and of year [:snake:][2]
  * multi-stage wake-up light sequence, interruptable [![NR_icon_16px](https://user-images.githubusercontent.com/32362869/118363988-ff6d3100-b596-11eb-9eb8-c17dce3bda45.png)][3] [:camel:][5]
  * Turning lights off while away from home [![Telegram_2019_simple_logo](https://user-images.githubusercontent.com/32362869/118362883-f0d04b00-b591-11eb-998e-da7208dbcbe4.png)][1] [:camel:][5]
  * Putting lights in vacation mode, prompted when an appropriate calendar event is detected :calendar: :camel:
* other:
  * Reminders for when the washing machine is finished can be scheduled through a button next to the washing machine [:zap:][4] [![NR_icon_16px](https://user-images.githubusercontent.com/32362869/118363988-ff6d3100-b596-11eb-9eb8-c17dce3bda45.png)][3] [:snake:][7] [![mongo_icon_20px](https://user-images.githubusercontent.com/32362869/118363357-46a5f280-b594-11eb-9fe9-076f73f2528a.png)][6] [![Telegram_2019_simple_logo](https://user-images.githubusercontent.com/32362869/118362883-f0d04b00-b591-11eb-998e-da7208dbcbe4.png)][1]
  * The admin user is prompted when there are available updates [:snake:][2] :iphone:

## Components

I use the following components to implement this

### Devices

* 1 **Raspberry Pi 4B 4GB** with a 32GB high-quality microSD with Home Assistant OS
* :zap: Phoscon **ConBee 2** Zigbee USB gateway
* :zap: Zigbee devices:
  * 9 IKEA Trådfri lights (not RGB, but white to yellow)
  * 6 IKEA Trådfri remotes with 5 buttons each
  * 1 IKEA Trådfri wireless control outlet
  * 1 IKEA TrådFri on/off remote

### Integrations

* [:zap: **deconz**][4] for Zigbee connection to smart lights, switch and buttons
* [![Telegram_2019_simple_logo](https://user-images.githubusercontent.com/32362869/118362883-f0d04b00-b591-11eb-998e-da7208dbcbe4.png)
 **Telegram bot**][1] for 2-way communication, not limited to the local network
* :iphone: The Home Assistant **app** for other notifications
* :calendar: Google for the **Calendar**

### Add-ons for automation logic

* [Standard HA YAML (rhymes with :camel:)][5] still has many of my automations, but I intend to move the bigger ones to one of the other platforms:
* [![NR_icon_16px](https://user-images.githubusercontent.com/32362869/118363988-ff6d3100-b596-11eb-9eb8-c17dce3bda45.png)
 **Node-Red**][3] for flow-based automation
  * Contains all functions of all :zap: buttons
* [:snake: **AppDaemon**][2] for more programmatic automation using Python
  * Contains complex time logic
  * and the programmatic update notification logic

### Add-ons, other

* [:zap: The **deconz**][4] instance for the Zigbee network
* [![mongo_icon_20px](https://user-images.githubusercontent.com/32362869/118363357-46a5f280-b594-11eb-9fe9-076f73f2528a.png)
 MongoDB][6] as a lightweight persistence service [for reminders][7]. This ensures reminders do not get lost/forgotten when Home Assistant is restarted.
* Some utility add-ons:
  * **VS Code** in front-end in browser
  * **Samba share** for easy access to the machine file from Windows pc

## Resources

To get started with Home Assistant, and for the documentation, visit: https://www.home-assistant.io/getting-started/

To see how other people have been using Home Assistant, have a look at the forums: https://community.home-assistant.io/

[1]: https://www.home-assistant.io/integrations/telegram/
[2]: https://appdaemon.readthedocs.io/en/latest/
[3]: https://nodered.org/
[4]: https://www.home-assistant.io/integrations/deconz/
[5]: https://www.home-assistant.io/docs/automation/
[6]: https://www.mongodb.com/
[7]: https://github.com/fhoekstra/home-assistant-config/tree/master/appdaemon/apps/reminder_service.py
