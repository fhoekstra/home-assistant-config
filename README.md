# My Home Assistant configuration

Feel free to use whatever you find here for your own Home Assistant or other home automation.

## Use Cases

Includes automations for the following use cases:

* smart lights:
  * changing color temperature automatically based on time of day and of year
  * multi-stage wake-up light sequence, interruptable
  * Turning lights off while away from home
  * Putting lights in vacation mode, prompted when an appropriate calendar event is detected
* other:
  * Reminders for when the washing machine is finished can be scheduled through a button next to the washing machine
  * The admin user is prompted when there are available updates

## Components

I use the following components to implement this

### Devices

* 1 **Raspberry Pi 4B 4GB** with a 32GB high-quality microSD with Home Assistant OS
* Phoscon **ConBee 2** Zigbee USB gateway
* Zigbee devices:
  * 9 IKEA Trådfri lights (not RGB, but white to yellow)
  * 6 IKEA Trådfri remotes with 5 buttons each
  * 1 IKEA Trådfri wireless control outlet
  * 1 IKEA TrådFri on/off remote

### Integrations

* **deconz** for Zigbee connection to smart lights, switch and buttons
* **Telegram bot** for 2-way communication, not limited to the local network
* The Home Assistant **app** for other notifications
* Google for the **Calendar**

### Add-ons for automation logic

I still have some automations in the standard Home Assistant YAML format, but am planning to move most of the bigger ones to one of these platforms:

* **Node-Red** for flow-based automation
  * Contains all functions of all buttons
* **AppDaemon** for more programmatic automation using Python
  * Contains complex time logic
  * and the programmatic update notification logic

### Add-ons, other

* The **deconz** instance for the Zigbee network
* Some utility add-ons:
  * **VS Code** in front-end in browser
  * **Samba share** for easy access to the machine file from Windows pc

## Resources

To get started with Home Assistant, and for the documentation, visit: https://www.home-assistant.io/getting-started/

To see how other people have been using Home Assistant, have a look at the forums: https://community.home-assistant.io/
