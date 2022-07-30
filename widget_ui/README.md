# 🟠 Widget UI
(_Last updated 2022/07/30_)  
**🔸 Current Installation files v07_2022-07-30**  

## Current Features and Status

The Widgets cards now support, and automatically configure themselves, to all 36 types of entities in Home Assistant, with extra 'Popup Control' pages to provide more detailed information and control for the all the more complex device types:

 <details>
  <summary>▶️ show list of features for v0.7 ...</summary>
 

* 🔹 Widget UI supports all 36 standard Home Assistant entity types (domains) showing you Widget card information that adapts to the type of entity;  
* 🔹 Entity types that have 'classes' adapt the information they show to the class of entity (e.g., a temperature sensor will show you a thermometer as the default icon and the text information will indicate the class of sensor);  
* 🔹 All devices that support interactive control in Home Assistant can now be controlled with 'gestures' that adapt to the type of Widget card, giving you quick access to common controls (such as swiping to adjust a light's brightness);  
* 🔹 When you swipe or tap on a Widget card a 'gesture indicator' will pop up in the top left of the screen to show what action that gesture will perform for that device.  If you hold a press or swipe, a timer bar will appear next to the gesture indicator and the gesture action will be modified.  The gesture indicator will give you visual feedback on these changes during the gesture.  For example if you swipe to the left on a light card the gesture indicator will initially show `▶ Brightness% +20`, and this will update with each timer step before you remove your finger (e.g., hold for 3 timer steps to increase brightness by 60%: `▶ Brightness% +60`);  
* 🔹 For entity types with more complex information or controls, tapping on the right half of the card will bring up a detailed `Popup Control` page. This currently works for lights, HVAC/climate devices, media players, and notifications;  
* 🔹 The settings page can be accessed by swiping down from the bezel/edge on any Widget page.  This is also the boot-up page for Widget UI (while it reads your configured list of `widgets:` from your Home Assistant `automation.yaml`).  You can manage linking/unlinking of your NSPanel physical buttons to their respective relays from here;  
* 🔹 Two small indicator bars across the bottom of the display indicate the status of the 2 relays.  There are multiple ways for you to control linking/unlinkingg of the relays from the physical buttons without having to reconfigure the device (through the settings menu, Home Assistant, or holding down the physical buttons until you get audio feedback - see the docs below);  
* 🔹 System information is available from the blank sleep screen.  The information will display when you touch the screen to wake the device up, and will remain on the display until you lift your finger;  
* 🔹 You can quickly put the display to sleep by swiping down from the top bezel/edge on any 'popup page'.  Swiping down and holding until the gesture timer appears will put the screen to sleep from any Widget page;  
* 🔹 System checks will let you know when the Nextion TFT requires a later version of the `nextion_handler.py` script (or `ESPHome template` configuration).
  
  
</details>
 
--- 

## Installing Widget UI

<details>
  <summary>▶️ show Installation steps and requirements ...</summary>

### Before you start
**🔹 Pre-requisites:**  Home Assistant (HA) with ESPHome installed, an NSPanel that has been flashed with ESPHome (see [Masto's](https://www.youtube.com/watch?v=Kdf6W_Ied4o) or [EverythingSmartHome's](https://www.youtube.com/watch?v=sCrdiCzxMOQ) video instructions), and some basic familiarity with configuring HA.  
**🔹 BACK UP your existing Nextion files:** in particular your device's ESPHome YAML configuration.  You will need to enter the details from that into the new template later (and will need your original ota password & other details to be able to upload any new configuration).  
**🔹 File locations:** All installation files are in the same [folder as this README document](/widget_ui).
  
  
### Installation steps
🔸v0.7 Files are now available: `ESPHome_Nextion_Handler_template.yaml`, `nextion_handler.py`, `nsp1_*.tft` (for both EU & US NSPanels). 

<details>
  <summary>1️⃣ Fill and flash the ESPHome YAML template:</summary>   
 
  * Download and open the template `ESPHome_Nextion_Handler_template.yaml` configuration file (or open it in your browser here).  
  * From the ESPHome Dashboard page in Home Assistant, paste the template into the top of your original (backed up) configuration for your NSPanel (_keeping the filename and location of the your original `yaml` configuration unchanged_).  **Check** that copying and pasting the template did not change the indentation of the pasted text.  
  * Fill in your details from your backup configuration into the `substitutions:` section at the top of the file (and then delete all the old YAML).  This block of the template is shown below.  
  * Following the default settings, paths and filenames in the template will make the initial install easier - you can come back later once everything is working to customise your configuration.  
  (Leaving `ha_prefix: nsp1` will mean that you can use the `automation.yaml` template without editing later on.)  
  (Setting `tft_url:` to `https://MY_URL:8123/local/nsp/nsp1.tft` means that when you download the Nextion TFT file later (3️⃣) you will name it `nsp1.tft` and place it in the `<config>/www/nsp/` folder on Home Assistant device.  Get the `https://MY_URL:8123` part of `tft_url:` from the URL in your web browser when you have your Home Assistant interface open.)  
  * `Validate` the file (from the ESPHome Dashboard `⋮` menu for your NSPanel) before your `Install` it.
  * Once the ESPHome installation is complete, check the NSPanel `Device` page in HA to make sure the entities are showing up properly.  If you changed `ha_prefix: nsp1` (above), you will later need to get the enitity_ids for `Trigger`, `HA Act`, `HA Set1 & 2` (from the NSPanel `Device` page), and `ESPHome: nsp1_send_command` (from `Developer Tools | SERVICES`).  You will later use the `TFT upload button` on the `Device` page to flash the Nextion TFT UI file.  
 
 
**ESPHome fillable template:** you only have to fill in the `substitutions:` section at the top of the template with details specific to your device.  (You can tweak the template later to your liking _after_ you have everything up an running properly.)
```YAML
#----------------------------------------
#* DEVICE/USER-SPECIFIC DETAILS (customize for each of your own Nextion Devices).
#! BACKUP YOUR ORIGINAL ESPHome YAML config for your device.
#! GET THE name, passwords etc from that config & enter them in the 'substitutions:' below:
substitutions:
  ota_password: "from flashing initial config"       #<< replace with the one from you own device
  fallback_ap_password: "from initial config"
  esp_net_name: "from-config"                        # MUST MATCH your initial config (do not use '_', use '-' instead). (Sets device local network name & part of fallback AP name).
  esp_comment: NSPanel 1                             # descriptive name (only used for description in ESPHome Dashboard).
  ha_prefix: nsp1                                    # prefixed to HA entity_ids to make them unique (do not use '-' or spaces, use '_' instead: OPPOSITE of 'esp_net_name').
  tft_url: "https://MY_URL:8123/local/nsp/nsp1.tft"  # You will place your TFT file at "/config/www/nsp/nsp1.tft" on your HA device and
                                                     # the "https://MY_URL:8123/" part of the tft_url matches the URL to your HA broswer interface.
  wifi_ssid: !secret wifi_ssid                       # your home WiFi credentials.
  wifi_password: !secret wifi_password
#  encr_key: "H0000000000000000000000000000000000000000000"  # Generate your own key here: https://esphome.io/components/api.html#configuration-variables (and uncomment the api: encrytion: key: "...") section below if you want encrypted HA communications.
#----------------------------------------            # No editing of the YAML below is required to use Nextion Handler.
...
...
```

</details> 

<details>
  <summary>2️⃣ Copy and configure Home Assistant Python script:</summary>  
 
  * Download and copy the `nextion_handler.py` script into the `<config>/python_scripts/` folder of your Home Assistant device.
  * If you have never used Python scripts in Home Assistant before, you will have to add a line `python_script:` to your `configuration.yaml`.  ([See HA page on Python scripts](https://www.home-assistant.io/integrations/python_script/).)  
  * Create an automation in Home Assistant to link this script to your NSPanel using the YAML template below (usually in your `automation.yaml` file).  
  * In the `widgets:` section of the automation, add one of your own entities to the list as `  - entity: light.kitchen` (for example).  Start with just one as a quick test to make sure the installation worked.  You can edit the `widget:` list whenever you want, then `reload automations` (type `cr` in HA as the command palette shortcut) for HA to recognise the changes.  (If you get an entity configuration wrong, this will usually be indicated by a red and white ❗ _error icon_ for that Widget on the NSPanel.)  

**Automation template:** If you left `ha_prefix: nsp1` unchanged in step 1️⃣ then you only need to change the `- entity: light.kitchen` line near the bottom to match a light of your own.  (_The downloadable `HA_automation.yaml` file for this template has more annotations and suggested examples of what you might add to your list later on._) You can have up to 6 pages of Widgets on your NSPanels which allows **36 entities in your list for the EU version** and **48 entities for the US version**.
```YAML
# Home Assistant automation for NSPanel 1
- alias: "NSP1 Nextion handler"
  mode: queued
  max: 3
  trigger:
    - platform: state
      entity_id: sensor.nsp1_trigger
  action:
    - service: python_script.nextion_handler
      data:
        trig_val: sensor.nsp1_trigger
        nx_cmd_service: esphome.nsp1_send_command
        action_cmds:
          - sensor.nsp1_ha_act
        update_cmds:
          - sensor.nsp1_ha_set1
          - sensor.nsp1_ha_set2
        widgets: #______________________________________________________________
          # Add a list of your entities: only the "- entity: " config variable is mandatory,
          # but usually customise the "name:" too.
          # (Later customise the "icon:" if you want to override the default).
          # *** Edit for your own devices ***
          - entity: light.kitchen                # replace with your own light to start
            name: Kitchen
            icon: 50                             # see icon index
          # - entity: ...                        # add up to 36(EU) or 48(US) entities in a LIST

``` 
 
</details> 
 
<details>
  <summary>3️⃣ Flash Nextion Widget UI TFT file:</summary> 

  * Download the `Widget UI TFT file` for your NSPanel (EU or US) then rename it `nsp1.tft`.
  * In the main `<config>` folder on your Home Assistant device create the `/www/nsp/` folders and place the `nsp1.tft` file in that folder (so the full path to the TFT file will be `<config>/www/nsp/nsp1.tft`, which is a special location where HA allows local access without login credentials using the default `tft_url` from your ESPHome configuration in step 1️⃣).
  * Then press the `TFT upload button` on the NSPanel's `Device` page in Home Assistant (that you located in step 1️⃣).  
  * Wait for the NSPanel to flash and reboot with the new UI.  (You may have to reboot both HA and the NSPanel after the first installation.)  
  
👉  Make sure that the path where you place the `TFT file` matches the `tft_url:` you set in your ESPHome configuration in step 1️⃣.  When you enter the `tft_url` into your browser, it should download the TFT file - if not you have probably put the file in the wrong path or got the TFT URL wrong.  There are more notes on configuring the `tft_url` to match a locally-accessible file path on your HA device [here, on the HA formums](https://community.home-assistant.io/t/nextion-handler-for-home-assistant-for-nspanels/394858/5?u=krizkontrolz).)
  
👉 Whenever you change your `widgets:` list (including the initial installation) it will take a little bit longer for each page to refresh the first time after that as it reconfigures itself.  If it gets stuck, open the settings menu (swipe down and close it by swiping down again), which will help to read the new list. 

</details> 
 
</details>

  ---

## UI Features
  
### Page Layout and Function
Each 'Main' Widget page is tiled with Widget cards, one per entity. Information and touch interactions adapt to the type of entity they are displaying.  
* **🔹 Main Pages:** The 'Main' content pages are filled completely with Widget cards (as shown in the example images below).  Navigation is by `edge swipe` gestures (from the bezel/edge into the display) that cycle forwards and backwards through the main pages.
* **🔹 Popup Pages:** Some actions bring up 'popup' pages that provide added controls and information.  These are distinguished by a title bar at the top, and a back arrow in the top left corner for navigating back to the 'Main' page you came from.
* **🔹Widget Cards:** Each card has an icon (with circular background), then three rows of text: the 'title' at the top, a row of short 'alternate' text, and the main 'info' text along the width of the card at the bottom.  Users interact with Widgets by `press` and `nudge` (swipes starting on the Widget card) gestures (described below).
* **🔹 Icons:** Icons and their coloring conventions [follow the detailed set of Minimilist Design UI standards for this project](/UI_Design/Minimalist/): cards with white/grey icons typically only provide information and will not trigger any actions when touched, whereas colored icons indicate that touch interactions with the card will trigger a range of actions (as detailed below).  A grey circle behind the icon indicates that the entity is in an off/inactive state, while a colored background highlights when entities are in an on/active/alert state.  The available icon pairs, currated and precompiled to these conventions, are indexed below. 
* **🔹 Gesture Indicator:**  When you tap the screen, a gesture indicator will pop up in the top left corner and dynamically update as the gesture is modified by holding the touch for longer.

 **Screenshots of Widget UI** (3 'Main' pages, each tiled with 2x4 entity cards) showing how the appearance of cards adapts to the type of entity allocated to them.  
   
![Widgets UI screenshots](/widget_ui/Screenshots_Widgets.png "Widget UI screenshots")
 


## Gestures

The [gesture enginge](/Tips_and_Tricks/NEXTION_GESTURES.md) allows a wide range of user interactions in the compact space of the NSPanel display while filling that limited area with Widgets and useful information (rather than buttons and slider bars).  Different types of gestures are used to change pages (`edge swipes`), make multi-step incremental changes to Widget attributes (`nudges` + hold), and trigger actions specific to the type of entity on the Widget (`press` + hold).  When you touch the screen, a small `gesture indicator` pops up in the top left corner showing a `gesture icon` for the currently detected gesture (one of: edge swipes: `⬅` `➡` `⬆` `⬇`, nudges: `◀` `▶` `▲` `▼`, or presses: `◐` `◑` `◉` `◎` `✖`), and a `text description` of the `action` that will be triggered if you lift your finger at that moment.  If the gesture is held, then a `timer bar` will appear to the right of the gesture indicator.  For `presses` the action perfomred will change as the timer bar increases for short presses (`◐` and `◑`), long presses (`◉`), and very long presses (`◎`)  (and will cancel `✖` if you continue to hold the press any longer).  `Nudges` work like slider bars to control attributes that you can gradually adjust, so each step of the timer bar lets you the amount of the change you make (such as to a light's brightness) - the gesture indicator will update to show what attribute is being adjusted for that Widget and by how much it will be changed if you release your finger at that point.	
  
<details>
  <summary>▶️ show gesture types ...</summary>
  
**Demonstration of the `gesture indicator` giving UI feedback on touch interactions.**	 
	
![Gesture UI demo](/widget_ui/DEMO_Gestures_Animation.gif)
	
	
#### Page/Edge Swipe Gestures  
 
* **🔹 `⬅` `➡` Left and Right `edge swipes`:** cycle forwards and backwards through 'Main' pages (for as many 'Main' pages as are required for the configured list of Widgets).  If you hold the gesture until the timer bar appears, you can skip forward/backward multiple pages at a time (as shown on the gesture indicator).
* **🔹 `⬇` Downward `edge swipes`:** will bring up the 'Settings' popup page from any 'Main' page (or will dismiss a popup page).  Opening the settings page will also fetch an updated count of the number of entities in your configured `widgets:` list (so the that correct number of pages can be allocated). Holding `⬇` until the timer bar appears will put the screen to sleep immediately from any Widget page.
* **🔹 `⬆` Upward `edge swipes`:** force an immediate update of the Widget information on the current page by fetching refreshed data from HA.

#### Widget Swipe/Nudge (and hold) Gestures  
`Nudge` gestures are swipes that start on a Widget card (away from the edge of the screen).  Nudges are a compact way of replacing slider bars to make incremental step increases/decreases to an entity attribute (such a lights brightness, color temperature and hue).  Holding a `nudge` will bring up the timer bar to trigger multiple step changes.  The gesture indicator will show what attribute would be changed and progressively updates the amount of change with each step in the timer bar.
* **🔹 `◀` `▶` Left and Right `nudges`:** progessively adjust a value by the amount shown in the gesture indicator. 
* **🔹 `▲` `▼` Up and Down `nudges`:** progressively adjust another value in step changes.  
To make a single `nudge` increment/decrement, release before the `timer bar` appears.  
👉  The main thing to remember with `nudges` is that you increase the size of step adjustments by _holding_ the touch for a longer duration (rather than by _moving_ your finger further).

#### Widget Press (and hold) Gestures  
* **🔹 `◐` LHS press:** A short press on the Widget icon (left half of Widget card) performs the most common action for that type of entity, such a toggling it.  
	(For short presses, lift your finger _before the timer bar appears_.) 
* **🔹 `◑` RHS press:** opens the `Popup Control` page for that entity (if it has one) or perform another common action for that entity. 
* **🔹 `◉` Long press:** performs the indicated alternate action for that type of entity. (Actions for LHS and RHS may be different.)  
	(Hold a press until the timer bar first appears to trigger the long-press action.) 
* **🔹 `◎` Very long press:** performs the indicated alternate action for that type of entity. (Actions for LHS and RHS may be different.)  
	(Hold a press until the `◎` gesture icon appears to trigger the very-long-press action).
	
#### Cancelling after starting a Gesture  
* **🔹 `✖` Cancel gesture (and `✘` cancel action):** Cancels, without performing any action, when:  
	**a)** a press is held for long enough (until the `✖` appears),  
	**b)** any gesture is held long enough until the timer bar completely fills,  
	**c)** you move finger your to a point a short distance from your starting position, or   
	**d)** the entity has no action for that gesture, indicated by `✘` in the text description.
	
#### Popup Press (and hold) Adjustors
* **🔹 `⮜`, `⮞` Press and hold:** Incrementally adjust a value or option number.
	This functions similarly to `nudge` swipes but works by pressing and holding selector arrow buttons or values in Popup Control pages.


The `gesture indicator` will update dynamically throughout touch events to give the user feedback on what gesture is currently being detected and what action will be performed if you lift your finger at that point.  You can safely explore the UI by trying out the different gestures and seeing how they are modified by the duration `timer`, then cancel by returning your finger close to the start of the stroke to make the `✖` (cancel) gesture icon appear if you want to avoid triggering any action at the end.	
	
 --- 
  
</details>  
  
  
## Popup Control Pages (including NSPanel Settings)
Popup Controls provide additional detail and control, particularly where generic Widget cards are too limiting:  
  
<details>
  <summary>▶️ show details on Popups for Settings, Lights, Media Players, HVAC/Climate Controls, and Notifications ...</summary>
  
  
* **🔹 Settings Popup -** shows system information and allows adjustment to the behaviour of the NSPanel:
  * Brightness max: the standard brightness that the display will revert to on any interaction.
  * Brightness min: the lowest brightness that the screen will gradually dim to before blacking out.
  * Update interval: the time inteval between NSPanel requests for refreshed page data from the Home Assistant Nextion Handler.
  * Sleep time: the time until the screen is blacked out.
  * Fast repeats: the number of times that data updates are requested after a touch action is triggered.  This addresses the issue that some states in HA can update very quickly after a service call, whereas others can have substantial lag (e.g., garage doors, some types of lights).
  * Fast slowdown: the amount by which fast repeats are progressively slowed down.  This amount of time is added to each subsequent repeat.
  * Status information: Small text below the title bar shows the number of widgets read from the YAML configuration, and the version number of the TFT file.  The WiFi status and signal strength are indicated in the top right corner.  
  * Pressing on the date-time in the title bar will immediately put the device to 'sleep' (blacked out screen).
  * **🔸 Linking/Unlinking of NSPanel physical buttons to relays.**  This linking _**can  also be done in Home Assistant**_ via the UI switches that ESPHome creates  _**or by holding down one of the buttons for ~6 seconds**_ to link/unlink it from its respective relay.  When linked, pushing the physical NSPanel buttons will toggle their respective relays (as with the original firmware).  When unlinked, you can use the buttons to trigger other automations in Home Assistant.  Even when unlinked, holding a button for 3 to 5 seconds will still toggle the relays (so that there is always a way to turn the relay off).  
 The device will provide audible feedback with:
    * 🎵 a beep (after ~3 seconds) to let you know you when to release the button to cause an 'override' relay toggle;
    * 🎶 rising notes (after ~6 seconds) when you LINK the button to its relay;
    * 🎶 descending notes (after ~6 seconds) when you UNLINK the button from its relay.

  
Be conservative with the update settings initially, then tweak them when your configuration is working well.  There is a trade-off between how fast and frequently you initiate data updates after a touch interaction, and how responsive the NSPanel will be to multiple successive touch interactions (such as multiple taps for triggerig quick increase/decrease step changes to light brightness).  
  
* **🔹 Light Popup -** provides full control of light settings:
  * Available controls are enabled/disabled according to the capabilities of the currently selected light (once that data has been received from HA).
  * All controls relevant to the current light are immediately available irrespective of the current color mode, or whether the light is off (which allows making some changes faster than the HA UI approach).
  * Long pressing on the color wheel will switch the light to a supported white/color_temperature mode. (This is mainly useful for RGBW bulbs that don't have color_temperature control).
  * Long pressing the icon in the top right corner will force the bulb off.  (This is a useful fix when toggling fails, such as when some lights in a group get out of sync with their registered state in Home Assistant.)  

* **🔹 Media Player Popup -** provides full control of media players:
  * Controls for Volume, Mute, Power, Play, Pause, Forward, Back, and Select Source.
  * Shows information on current state, media/track information, and track position and duration (if available for device).

* **🔹 Climate Control Popup -** provides full control of HVAC devices:
  * Temperature controls for devices both with single set points and those which set the targets as a range with lower and upper bounds.  For devices that set a temperature range, the set point will show in blue for the lower bound and red for the upper bound - tap the temperature value to toggle between which set point you want to view and adjust.
  * Humidity slider (for devices with this feature). 
  * Icon buttons for controlling the four main HVAC modes.  (Long pressing the buttons gives access to less common modes, such as drying - see the gesture indicator when you long press the buttons).
  * Selector controls for preset modes, fan modes and swing modes.  Use the arrows to cycle forwards and backwards (in multiple steps) through the available options.  Press and hold the text describing the current mode to directly select an option by its numbered position in the available list of options.
	
* **🔹 Notifications -** allows reading and dismissing Home Assistant persistent_notications.
   * 'Notifications' is a special type of Widget card because it uses _all_ the entities in the domain, not just a single notifiction entity.
   * Enter `entity: persistent_notification.all` to create a notifications UI card (then customise it as you wish).
   * This allows the NSPanel to be used as a convenient message board for HA (delivering messages to all rooms in the house with an NSPanel).  
  
  
As functionality is developed, more popups will be added to support some of the more complex entity types (such as media_players).  
  

 **Screenshots of some of the current 'Popup Pages'.**  Where available, popups are triggered by touching the top right quadrant of the enity card.  The gesture indicator will show when a popup control is available for a Widget Card. 
   
![Widget Popups](https://github.com/krizkontrolz/Home-Assistant-nextion_handler/blob/main/widget_ui/Screenshots_Popups.png "Widget Popups")
  
  
  
 --- 
  
</details>  

  
## Widget Card Touch Interactions (by Entity type)
	
A set of `nudge` and `press` gestures allows users to interact with Widgets in different ways, as shown in the UI by the `gesture indicator` (`nudges`: `◀` `▶` `▲` `▼`, and `presses`: `◐` `◑` `◉` `◎` `✖`).  The `actions` that are triggered by each of those gestures adapt to the type of entity on that Widget card and are shown as a `text description` next to the `gesture icon` in the `gesture indicator`.  This makes it easy for users to learn all the possible Widget interactions from feedback displayed directly on the Nextion display - but the set of interactions for each entity type is also summarised below for reference: 

  

<details>
  <summary>▶️ Full ist of gesture controls for each type of Widget card ...</summary>


(Icons for `press` and `nudge` gestures follow those that appear in the UI `gesture indicator`, as desccribed in the list of Gesture types above.)


* 🔸 **Light Cards:**
  * `◐`: Toggle light On/Off  
  * LHS `◉`: Force turning light Off (fix out of sync lights)  
  * LHS `◎`: Force turning light On  
  * `◑`: Detailed Popup Control (with color wheel and slider controls etc.)  
  * RHS `◉`: Turn on/change the bulb to a supported white mode  
  * `◀`, `▶`: Adjust light Brightness (20% steps).  
  	If the light is off:  
	`◀` will turn light on at Minimum (1%) brightness  
	`▶` will turn light on at Maximum (100%) brightness  
  * `▲`, `▼`: Adjust the light's Color Temperature (if it is in WW mode) or Hue (if it is in an RGB mode) (in steps of 20)

* 🔸 **Media Player Cards:**
  * `◐`: Toggle media player On/Off  
  * LHS `◉`: Toggle Play/Pause  
  * LHS `◎`: Source select (cycle backwards through source list)  
  * `◑`: Detailed Popup Control (with volume slider, source selector etc.) 
  * RHS `◉`: Toggle Mute  
  * RHS `◎`: Select Source (cycle forwards through source list)  
  * `◀`, `▶`: Skip Backwards/Forwards through tracks/channels/media list  
  * `▲`, `▼`: Adjust Volume (5% steps) 

* 🔸 **Climate/HVAC Cards:**
  * `◐`: Toggle HVAC device on/off  
  * LHS `◉`: Cool mode  
  * LHS `◎`: Auto mode  
  * `◑`: Detailed Popup Control (with temperature and humidity sliders, mode selectors etc.) 
  * RHS `◉`: Heat mode  
  * RHS `◎`: Heat-Cool mode  
  * `◀`, `▶`: Adjust Humidity (5% steps)  
  * `▲`, `▼`: Adjust Temperature (1° steps) 

* 🔸 **Persistent Notifications Cards:**
  * `◐`, `◑`: Detailed Popup Control (cycle through and delete HA notifictions)

---

* 🔺 **Alarm Control Panel Cards:**
  * `◐`: Arm - Night  
  * LHS `◉`: Arm - Home  
  * `◑`: Arm - Away  
  * RHS `◉`: Arm - Vaction  
  * LHS & RHS `◎`: DISARM  

* 🔸 **Automation Cards:**
  * `◐`, `◑`: Toggle automation Active/Inactive  
  * LHS & RHS `◉`: Trigger automation  
	
* 🔸 **Button Cards:**
  * `◐`, `◑`: Execute Button actions  
	
* 🔺 **Cover Cards:**
  * `◐`: Toggle cover Open/Closed position 
  * LHS `◉`: Stop cover open/close  
  * LHS `◎`: Fully Open cover  
  * `◑`: Toggle Tilt (for slats in blinds) 
  * RHS `◉`: Stop Tilt  
  * RHS `◎`: Open Tilt  
  * `◀`, `▶`: Adjust Tilt of slats (10% steps)  
  * `▲`, `▼`: Adjust ▲Open/▼Close position (20% steps)  

* 🔺 **Fan Cards:**
  * `◐`: Toggle fan On/Off 
  * LHS `◉`: Oscillate On  
  * LHS `◎`: Oscillate Off  
  * `◑`: Toggle tilt (for slats in blinds) 
  * RHS `◉`: Set Direction to Foward  
  * RHS `◎`: Set Direction to Reverse  
  * `◀`, `▶`: Adjust fan speed (1 repeat per step)  
  * `▲`, `▼`: Adjust fan speed (1 repeat per step)  

* 🔺 **Humidifier Cards:**
  * `◐`, `◑`: Toggle humidfier On/Off 
  * LHS & RHS `◉`: Turn Off  
  * LHS & RHS `◎`: Turn On  
  * `◀`, `▶`: Adjust Humiity (5% steps)  

* 🔸 **Input Number Cards:**
  * LHS `◉`: Set to Minimum value  
  * LHS `◎`: Set to 25% (between Min and Max)  
  * RHS `◉`: Set to Maximum value  
  * RHS `◎`: Set to 75% (between Min and Max)  
  * `◀`, `▶`: Adjust Number (Coarse: 10% steps between Min and Max)  
  * `▲`, `▼`: Adjust Number (Fine: 1% steps)  
	
* 🔸 **Input_Select and Select Cards:**
  * LHS `◉`: Set to First option in list  
  * RHS `◉`: Set to Last option in list  
  * `◀`, `▶`: Cycle backwards/forwards through the options list (1 repeat per step)  
  * `▲`, `▼`: Directly pick the nth option in the list (where n is set from the timer steps)   
  	`▲` picks directly counting from the end of the list _backwards_

* 🔺 **Lock Cards:**
  * `◐`, `◑`: Lock 
  * LHS & RHS `◉`: Unlock  
  * LHS & RHS `◎`: Open lock  

* 🔸 **Scene Cards:**
  * `◐`, `◑`: Turn On scene (there is no 'turn off' for scenes)  

* 🔸 **Timer Cards:**
  * `◐`, `◑`: Start/Continue timer 
  * LHS & RHS `◉`: Pause timer  
  * LHS `◎`: Cancel timer (_without_ triggering)  
  * RHS `◎`: Finish timer (_triggers timer complete_)  

* 🔸 **Update Cards:**
  * `◐`: Install latest Update  
  * `◑`: Skip this update  
  * RHS `◉`: Clear skipping of update  
	
* 🔸 **Vacuum Cards:**
  * `◐`: Toggle Start/Stop cleaning  
  * LHS `◉`: Return to Dock  
  * `◑`: Locate vacuum  
  * RHS `◉`: Spot clean  

* 🔺 **Water Heater Cards:**
  * `◐`, `◑`: Toggle Away Mode  
  * LHS & RHS `◉`: Turn Away Mode On  
  * LHS & RHS `◎`: Turn Away Mode Off  
  * `▲`, `▼`: Adjust temperature (1° steps)  


* 🔸 **Cards for Switch, Script, Input boolean, Siren, Group, Camera, and  Remote**   
(_All entity types that only have Toggle, On, and Off_)
  * `◐`, `◑`: Toggle (tap icon)
  * LHS & RHS `◉`: Turn Off (long press)
  * LHS & RHS `◎`: Turn On (very long press)

"🔺" indicates entity types where I'm particularly after more feedback (because I don't have these devices to test myself).	
	
---	

  
 --- 
  
</details>  
  
  

## Customising Widget Card Dashboard Information

Widget cards for all types of entities (whether they support interactions or not) report useful 'dashboard' information, and this information adapts to the the domain, class and reported attributes of the entity.  All aspects of the information on a card can be customised in the entities YAML configuration to override defaults, and **this can include dynamic information using standard Home Assistant templating**:


<details>
  <summary>▶️ show Widget card configuration details ...</summary>  
  
Only the `- entity:` is mandatory to specifiy for each of your Widget cards in the list under the `widgets:` section of your NSPanels YAML configuration (the Nextion Handler automation for that device).  The `name:` is the most likely optional thing you will want to customise (to override the default, which uses the entity's truncated friendly_name) with something that fits better in the limited space on the card.  The default icons for each card should be reasonable to get started, but you will likely want to pick something (from the icon index further below) that is more informative. 

_**I do not recommend changing the other options** until you have everything else working well_ (and then you will likely want to use dynamic data generated by templates).  The first of these to consider templating should probably be `icon_state:` for entities such as numeric sensors where there is no default way to decide when the card should be highlighted with the 'active' version of its icon (such as setting a rule for when to highlight a GDACs alert (see example in template), a gas sensor reading, or high power consumption etc.).  You can also override text with a space string (`" "`) to remove it from a card.  If you only want to replace/blank text under some conditions, then have the template return `{{ None }}` the remainder of the time (which will revert it to showing the defaults again).
  
* 🔶 `- entity:` the Home Assistant entity_id.  Special cases are `persitent_notications.all` (for a notifications widget), and `template` (or `blank`) for a widget that is filled entirely with custom dynamic (templated), static, or blank information.
* 🔷 &nbsp;&nbsp;`name:` the title/top row of text on the card.
* 🔷 &nbsp;&nbsp;`icon:` a number (0 to 167) corresponding to the value of the selected icon-pair index (further below).
* 🔹 &nbsp;&nbsp;`icon_state: use `True/'1' to specify the highlighted state of the icon-pair; otherwise (False/'0', etc.) the inactive state will be used.
* 🔹 &nbsp;&nbsp;`alt:` The second, short row of (alternate) info text on the card, below the title.
* 🔹 &nbsp;&nbsp;`info:` The main informative text along the full width of the bottom of the card.

If you misconfigure a widget, the Nextion Handler will try to give you feedback on the Nextion display by showing the ❗ _error symbol_ (**icon 47**, highlighted), a red and white icon of an exclamation mark in a circle, and may show some additional information in the info text area (such as showing an invalid entity_id with '*' on either side), to guide you to what part of your `widget:` list needs fixing.  For more serious problems, check the Home Assistant error logs for Nextion Handler messages. 
  
_(I will likely add the ability to customise the actions that are triggered by each type of touch interaction on a Widget Card in future.)_


<details>
  <summary>▶️ advanced configuration example ...</summary>  
	
While the intention of the Widget UI is to keep configuration as simple as possible, it does still allow more advanced users who are comfortable with Home Assistant templating to do very detailed customisations of the dashboard information displayed, including some quite sophisticated dynamic behaviours.  If you are not comfortable with templating, you can safely ingnore it, and the defaults will do a good job for most people.  But if you like the creative opportunities that dynamic templating allows, then the example below gives an idea of how to get started with your own customisations.
	
**Demo example of a customised card that templates everything** - shows the time and date, and changes the icon and alt text for weekends and holidays (using a 'workday' binary sensor):  
```YAML
  widgets: #______________________________________________________________
    - entity: template    # Demo Time & Date template card
      name: "{{ now().strftime('%Hh%M') }}"  # time customise to your liking
      # Usually use the time_and_date icon; except on weeday holidays, use the Sunny icon instead.
      icon: "{{ 118 if states('binary_sensor.workday_today') == 'on' or now().strftime('%a') in ['Sat','Sun'] else 26}}"  
      icon_state: "{{ now().strftime('%a') in ['Sat','Sun'] }}"  # highlight on weekends
      alt: "{{ 'Day off' if states('binary_sensor.workday_today') == 'off' else 'Work day' }}"  # customise to match your work_day binary_sensor
      info: "{{ now().strftime('%a %d %b %Y') }}"  # date - customise to your liking
 
 
 ```

</details>    

 
 --- 
  
</details>    
  
  
## Icons (with Index Image)
A currated set of precompiled icon images is used on the cards.  These are paired (for off/unhighlighted and on/highlighted states), with icons and coloring already formatted to [follow the Minimilist Design UI standards](/UI_Design/Minimalist/).  A default icon will be allocated based on the entity type (domain and class).  But you can set a different one in your `widgets:` list by specifying the _number_ (not name) of the icon you want from the index below.  You can also use templating to dynamically change the `icon:` and the `icon_state:` (0/1) in your your `widget:` list configuration.
  
<details>
  <summary>▶️ show Icon Index ...</summary>

 **Index numbers for available icon choices.**  The off/unhighlighted state is on the left and the on/highlighted version is on the right.  Use the index number of the icon you want in the `icon:` setting of each `- entity:` in your `widget:` list (or omit this setting to accept the default for that entity type).  **Icon 47** is used in its unhighlighted state to blank out the icon area on 'blank' cards, and it is used in its highlighted state as the ❗ _error icon_ to give users feedback that they need to fix a problem with their `widget:` config for that entity.  **Icon 46** is used to show when an entity is unavailable.
   
 ![Widget UI Icon index](https://github.com/krizkontrolz/Home-Assistant-nextion_handler/blob/main/widget_ui/Widget_Icons_Index.png "Icon numbering index")

### Icons are grouped as follows:
 * 🔵 0 .. 47 (6 rows): domain default icons and system.
 * 🟠 48 .. 71 (3 rows): lights (orange for indoor, green for outdoor).  
   (_spare row_.)
 * 🔴 80 .. 87 (1 row): media players.
 * 🔵 88 .. 95 (1 row): presence for 'person' and 'device_tracker' entities.
 * 🔵 96 .. 103 (1 row): binary sensors (representing most device classes).  
   (_spare row_.)
 * 🟣 112 .. 135 (3 rows): sensors (numeric) (representing most device classes).
 * 🔵 136 .. 143 (1 row): 'cover' entities (representing most device classes: automatic blinds, curtains, doors, windows etc.).
 * 🔵 144 .. 151 (1 row): Controls for indoor appliances.
 * 🔴 152 .. 159 (1 row): HVAC 'climate' entities.
 * 🟢 160 .. 167 (1 row): Controls for outdoor devices.
 
 Remaining slots are spares for future additions.  The images (pair) are the maximum size that the Nextion Editor will compile and store in a TFT file.
 
	
(gesture icons): ```◐◑◉◎ ⦿⊙✖✘▲▼◀▶⬅⬆⬇➡ 🠖➞🠔🠕🠗◀▶⯅⯆◑◐◉⦿⊙✖```
 --- 
  
  
  
</details>


---
  
  
  
[▶️ Back to main repository root/README](https://github.com/krizkontrolz/Home-Assistant-nextion_handler)
