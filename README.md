# My Home Assistant configuration

Feel free to use whatever you find here for your own Home Assistant or other home automation.

## Use Cases

Includes automations for the following use cases:

* [:zap:][4] smart lights:
  * Changing color temperature automatically based on time of day and of year [:snake:][2]
  * Turning lights on and off based on motion :camel:
  * Multi-stage wake-up light sequence, interruptable [![NR_icon_16px](https://user-images.githubusercontent.com/32362869/118363988-ff6d3100-b596-11eb-9eb8-c17dce3bda45.png)][3] [:camel:][5]
  * Turning lights off while away from home [![Telegram_2019_simple_logo](https://user-images.githubusercontent.com/32362869/118362883-f0d04b00-b591-11eb-998e-da7208dbcbe4.png)][1] [:camel:][5]
  * Putting lights in vacation mode, prompted when an appropriate calendar event is detected :calendar: :camel:
* other:
  * Reminders for when the washing machine is finished can be scheduled through a button next to the washing machine [:zap:][4] [![NR_icon_16px](https://user-images.githubusercontent.com/32362869/118363988-ff6d3100-b596-11eb-9eb8-c17dce3bda45.png)][3] [![Telegram_2019_simple_logo](https://user-images.githubusercontent.com/32362869/118362883-f0d04b00-b591-11eb-998e-da7208dbcbe4.png)][1] :camel:
  * The admin user is prompted when there are available updates [:snake:][2] :iphone:

## Components

I use the following components to implement this

### Devices

* 1 **Raspberry Pi 4B 4GB** with Home Assistant OS
* 1 WD Green 2.5" SATA SSD 120GB, connected with a Startech USB 3.0 to SATA 2.5" adapter
* :zap: Phoscon **ConBee 2** Zigbee USB gateway
* :zap: Zigbee devices:
  * 10 IKEA Trådfri lights (not RGB, but white spectrum 2200 K to 4000 K)
  * 6 IKEA Trådfri remotes with 5 buttons each
  * 1 IKEA Trådfri wireless control outlet
  * 1 IKEA TrådFri on/off remote
  * 1 IKEA TrådFri motion sensor

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
* Some utility add-ons:
  * **VS Code** in front-end in browser
  * **Samba share** for easy access to the machine file from Windows pc

## Node-Red demo

Node-Red is a simple yet powerful flow-based automation framework, but sharing what you're doing with it on Github can be difficult, because the json format is not human-readable.

So I decided to take some screenshots of my flows, and show a bit of code.

### Main buttons flow in Node-Red

I do 3 things with buttons: "normal" buttons that control lights, a button to set reminders next to the washing machine, and bedroom-specific things like turning off all lights in the evening, or interrupting the wake-up lights sequence in the morning.

![Main buttons flow](https://raw.githubusercontent.com/fhoekstra/home-assistant-config/master/node-red-pictures-and-examples/Normal-light-buttons-flow.png)

Especially interesting to share in this, is [the first node on the left](https://github.com/fhoekstra/home-assistant-config/blob/master/node-red-pictures-and-examples/translate-tradfri-remote-code.js). It contains the code I have pasted [here](https://github.com/fhoekstra/home-assistant-config/blob/master/node-red-pictures-and-examples/translate-tradfri-remote-code.js) and decouples the specific codes of the buttons from the logic of my automations.

### Wake-up lights flow in Node-Red

This flow toggles and monitors an `input_boolean` in HA to indicate whether the wake-up lights sequence is, and should be, in progress.
The total duration is set in another input in HA, and divided by the number of transitions of :zap: bulbs to set the transition per bulb. At the end, a switch is used to turn on a very bright white light.
![Wake-up lights](https://raw.githubusercontent.com/fhoekstra/home-assistant-config/master/node-red-pictures-and-examples/wake-up-lights-flow.png)

## Resources

To get started with Home Assistant, and for the documentation, visit: https://www.home-assistant.io/getting-started/

To see how other people have been using Home Assistant, have a look at the forums: https://community.home-assistant.io/

[1]: https://www.home-assistant.io/integrations/telegram/
[2]: https://appdaemon.readthedocs.io/en/latest/
[3]: https://nodered.org/
[4]: https://www.home-assistant.io/integrations/deconz/
[5]: https://www.home-assistant.io/docs/automation/
