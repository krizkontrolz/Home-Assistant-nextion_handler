# Widget UI

**🚧 under construction 🚧**

## Installation (HMI is only for US NSPanel only at this stage)
**Pre-requisites:**  Home Assistant (HA) with ESPHome installed, an NSPanel that has been flashed with ESPHome (add links), and some basic familiarity with configuring HA.

**BACK UP your existing Nextion files:** in particular your device's ESPHome YAML configuration.  You will need to enter the details from that into the new template later (and will need your original ota password & other details to be able to upload any new configuration).

**File locations:** The Widget UI TFT are in the same `widget_ui` [folder as this README document](/widget_ui), while the latest versions of the ESPHome YAML template and `nextion_handler.py` script are in the `current` [folder of this repository](/current).


#### Installation steps (NB: files have not been uploaded yet)

* Flashing the ESPHome YAML template:
  * Download a copy of the template ESPHome YAML configuration file and fill in your details from your backup configuration into the `substitutions:` section at the top of the file.
  * Using ESPHome addon page in Home Assistant validate the file before installing it to the NSPanel.
  * Once the ESPHome installation is complete, check that NSPanel entities are showing up properly in HA.  You will later need the enitity_ids for `Trigger`, `HA Act`, `HA Set1..5` (from the device page), and `ESPHome: nsp1_send_command` (from `Developer Tools | SERVICES`).  And you will use  `TFT upload button` (to flash the Nextion TFT UI file).

* Home Assistant python script:
  * Copy the `nextion_handler.py` script into the ```<config>/python_scripts/``` folder of your Home Assistant device.
  * If you have never used Python scripts in Home Assistant before, you will have to add a line ```python_script:``` to your ```configuration.yaml```.  ([See HA page on Python scripts](https://www.home-assistant.io/integrations/python_script/).)
  * Add the automation template from the `HA_automation.yaml` file to your own HA configuration (editing the NSPanel entity_ids to match those you noted above if you set a prefix other than `NSP1`).
  * In the `widgets:` section of the automation, add a couple of your own entities to the list as `  - entity: light.kitchen` to get started (you can edit these whenever you want) and `reload automations` for HA to recognise the changes.

* Nextion Widget UI TFT file:
  * Copy the Widget UI TFT file in the location you specified in the `tft_url` of your ESPHome configuration, and rename it to match the filename you set.  Then press the ```TFT upload button``` on the device's page in Home Assistant (that we referred to and located above).
  * Wait for the NSPanel to flash and reboot with the new UI.  (You may have to reboot both HA and the NSPanel after the first installation.)

TODO: Add screen shots.


## UI Features
...
### Entity Cards
Each page is tiled with cards, one per entity, that adapt to the type of entity they are displaying.  
Each card has four quadrants for touch interactions:
* Icon: primary touch interaction (such as toggle).
* Right of Icon: open a 'pop-up' page with more control options for that type of entity.  (Only lights supported for now, other pop-ups will be added).
* Bottom left & right: (feature to be added) most common secondary functions for that type of entity (such as decreasing/increasing brightness).

### Page Swipe Gestures
* Left and Right swipes: change pages forwards and backwards (for as many pages are required for the configured list of entities).
* Downward swipes: will bring up the 'Settings' pop-up page (or will dismiss a pop-up page).  Opening the settings page will also fetch an updated count of the number of entities in your configured `widgets:` list (so the that correct number of pages can be allocated).
* Upward swipes: force an immediate update of the widgets on the current page with data from HA.

