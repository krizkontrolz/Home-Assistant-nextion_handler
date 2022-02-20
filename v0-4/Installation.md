# Installation Instructions

## Prerequisites
* Home Assistant configured and running with data and devices you want to interact with through your Nextion device.
* A Nextion display with an ESP32 chip that has already been flashed with ESPHome and can be reconfigured through the ESPHome addon in Home Assistant.  The demo is specifically for the Sonoff NSPanel (US version), but can be adapted for other Nextion devices.

**BACK UP your existing Nextion files**, in particular your device's ESPHome YAML configuration.  You will need to enter the details from that into the new template later (and will need your original ota password & other details to be able to upload any new configuration).

---

## Installation steps
All files referred to are in the same Github folder as this installation document.
### ESPHome configuration:
* Download a copy of the template ESPHome YAML configuration file (```ESPHome_Demo_NSP1_v0-4_2022-02-20.yaml```).  Read through the instructions in the comments at the top of the file and fill in your details from your backup configuration into the ```substitutions:``` section near the top of the file.  (If you want to merge the template into your exiting configuration, pay particular attention to the sections marked ```#***nextion_handler requirement***``` throughout the template.)
* Add the new YAML configuration to your device through the ESPHome addon page in Home Assistant, then save it and validate it before installing it.
* Once the ESPHome installation is complete, go to its 'device' page in Home Assistant and check that you have all of the entities required for 2-way communication with the Nextion:
  * ```Trigger``` (state changes in this numeric value will drive the nextion_handler automation)
  * ```HA Act``` (a string that you will program in the Nextion to send commands to HA)
  * ```HA Set1..5``` (a set of 5 strings that you will configure with sequences of instructions on how HA should send and update data on each page of the Nextion)
  * ```TFT upload button``` (which is used to upload compiled TFT files created for customised Nextion UIs)
  * ```ESPHome: nsp1_send_command``` (you will need to check for this under ```Developer Tools | SERVICES```.
  
  **Make a note of all those entity_ids** because you will need to check/update them in the Home Assistant configuration for the service call to the nextion_handler.py script later).

### Nextion UI

* (You already backed up your existing TFT file, right?) Put the demo TFT file in the location you specified in the ```tft_url``` of your ESPHome configuration, and rename it to match the filename you set in ```tft_url```.  Then press the ```TFT upload button``` on the device's page in Home Assistant (that we referred to and located above).
* Wait for the NSPanel to reboot with the new demo UI.  It should look something like the image below.  It should gradually dim while not in use and then turn off after ~5 minutes.  Touching the display will wake it up again (but we have to add the HA components to make it do anything useful.) (The HMI file used to generate the demo TFT in the Nextion Editor is included here too - we'll get to that later.)

![Demo Nextion UI icon layout](https://github.com/krizkontrolz/Home-Assistant-nextion_handler/blob/main/v0-4/Demo_off.png)

### Home Assistant configuration:
* Copy the ```nextion_handler.py``` script into the ```<config>/python_scripts/``` folder of your Home Assistant device.
* If you have never used Python scripts in Home Assistant before, you will have to add a line ```python_script:``` to your ```configuration.yaml```.  ([See HA page on Python scripts](https://www.home-assistant.io/integrations/python_script/).)

* Add the automation template from the ```HA_automation.yaml``` file to your own HA configuration.
  * Check the entity_ids of all the ESPHome entity_ids (and send_command service name) match those in the template, and adjust to your set up as needed.
  * In the 'aliases' section, provide entity_ids for your own lights, switches, input_booleans, and binary sensors corresponding to the layout of tiles on the demo Nextion UI (as shown above).

* The ```HA_ui-lovelace.yaml``` file has a template Markdown card that you can add to your Home Assistant UI.  It is optional but very useful for checking what command_strings the Nextion is sending to the nextion_handler on HA, and for debugging once you start configuring these in your own HMI files in the Nextion Editor.  There is an example of what the card looks like in the main [readme.md](https://github.com/krizkontrolz/Home-Assistant-nextion_handler/blob/main/README.md#examples-with-shorthand-notation) on the first page.  Follow the instructions in the comments of the Markdown card to make sure the six entity_ids match those you took a note of earlier.

* You may need to restart Home Assistant for everything to start working.  You should start to see the Nextion making changes to sensor values of the Trigger, HA_Act and HA_Set1..5 strings as you tap icons on the Nextion, and the entities you asigned to those icons (via the aliases in the automation config) should respond accordingly.  If not, check the error logs and see if you need to correct any of the entity_ids in your automation config in HA.  

---
## Design your own
If you got the template demo going, then you should now be in a good position to design and customise something to your own needs and style.  The HMI is included to open yourself in the Nextion Editor.  All the boilerplate code is well commented to explain what it does, and you can start modifying the HA_Set1..5 strings to understand how Home Assistant data is pulled into a Nextion page, and start modifying the UI events to send different HA_Act strings (to get HA to control something).

The SVG file that was used to create the pair of UI images is also included.  This includes some annotations that may be useful for designing your own UI.  Inkscape is an excellent freeware program for editing vector files (and other design resources are linked on the main [readme.md](https://github.com/krizkontrolz/Home-Assistant-nextion_handler/blob/main/README.md#credits--related-resources)).

>**TIP**: Change the font of the Nextion Editor to a proper programming ```mono-space font``` (I like Consolas), and rearrange the panels to allocate most of the space to the 'Event' panel.  It makes writing bug-free code much easier.

Here is an example of my own set up, which is running very smoothly.  The HMI is included if you want to look at more examples of to use the nextion_handler in practice.

![Animated GIF of Nextion Handler example](https://github.com/krizkontrolz/Home-Assistant-nextion_handler/blob/main/v0-4/NextionHandlerExample.gif)
