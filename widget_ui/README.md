# 🟠 Widget UI
(_Last updated 2022/06/29_)  
**Current Installation files v06_2022-06-03**

## Current Features and Status

The Widgets currently provide sufficient functionality for most of the every-day Home Assistant controls, allowing you to:

 <details>
  <summary>▶️ show current list of features ...</summary>
 

* 🔹 create a dashboard to easily view information about your smart home, and visually highlight anything needing attention;
* 🔹 'toggle' all Home Assistant entities that can be toggled (lights, media players, switches, scripts, automations, covers, fans, input_booleans, locks etc.);
* 🔹 use interactive widgets to control most of the common types of entities (as per the details in the Widget Card interactions list);
* 🔹 fully control lights (both through quick widget card interactions and a popup page with slider controls and color wheel);
* 🔹 read and dismiss HA notifications;
* 🔹 change NSPanel settings (including managing the linking/unlinking of NSPanel physical buttons to their respective relays).
  
The details of how information is displayed will continue to be fine tuned, and new functionality will be added as the supported capabilities of the underlying [Nextion Hanlder](https://github.com/krizkontrolz/Home-Assistant-nextion_handler/blob/main/HA_NEXTION_HANDLER_INSTRUCTIONS.md) are being developed and expanded.

🚧 New gesture and widget features are currently being documented for version 0.7 (but aren't supported in the currently available 0.6 version).
  
</details>
 
--- 

## Installing Widget UI

<details>
  <summary>▶️ show Installation steps and requirements ...</summary>

### Before you start
**🔹 Pre-requisites:**  Home Assistant (HA) with ESPHome installed, an NSPanel that has been flashed with ESPHome ([see Credits and Resources links](https://github.com/krizkontrolz/Home-Assistant-nextion_handler) at the bottom of the root repository README), and some basic familiarity with configuring HA.

**🔹 BACK UP your existing Nextion files:** in particular your device's ESPHome YAML configuration.  You will need to enter the details from that into the new template later (and will need your original ota password & other details to be able to upload any new configuration).

**🔹 File locations:** All installation files are in the same [folder as this README document](/widget_ui).
  
  
### Installation steps
(Nextion UI TFT is only available for US NSPanels only at this stage,  
_🔸EU version is available on request for testing_ - I don't have an EU model so need someone to confirm it works properly before it is uploaded for general access.)

<details>
  <summary>1️⃣ Fill and flash the ESPHome YAML template:</summary>   
 
  * Download the template `ESPHome_Nextion_Handler_template.yaml` configuration file and fill in your details from your backup configuration into the `substitutions:` section at the top of the file.  (Leaving `ha_prefix: nsp1` will make the automation template easier later on.)
  * Validate the file before installing it to the NSPanel (from the ESPHome addon page in Home Assistant).
  * Once the ESPHome installation is complete, check the NSPanel device page in HA to make sure the entities are showing up properly.  If you changed `ha_prefix: nsp1` (above), you will later need to get the enitity_ids for `Trigger`, `HA Act`, `HA Set1 & 2` (from the device page), and `ESPHome: nsp1_send_command` (from `Developer Tools | SERVICES`).  And you will use the `TFT upload button` to flash the Nextion TFT UI file.  
 (_If this is the first time using your NSPanel with ESPHome, there are some lines near the top of the YAML file, marked with `#! *** FIX ***...` that you will need to uncomment **once** to switch the panel from the special 'reparse' mode it uses for the original firmware to allow it work with ESPHome.  Comment those lines out again the next time you reflash your configuration - they only need to run once._)
 
**ESPHome fillable template:** you only have to fill in the `substitutions:` section at the top of the template with details specific to your device.  (You can tweak the template later to your liking _after_ you have everything up an running properly.)
```YAML
# v0.6_2022-06-03
#----------------------------------------
#* DEVICE/USER-SPECIFIC DETAILS (customize for each of your own Nextion Devices).
#! BACKUP YOUR ORIGINAL ESPHome YAML config for your device.
#! GET THE name, passwords etc from that config & enter them in the 'substitutions:' below:
  substitutions:
    ota_password: "from flashing initial config"     #<< replace with the one from you own device
    fallback_ap_password: "from initial config"
    esp_net_name: "from-config"                      # MUST MATCH your initial config (do not use '_', use '-' instead). (Sets device local network name & part of fallback AP name).
    esp_comment: NSPanel 1                           # descriptive name (only used for description in ESPHome Dashboard).
    ha_prefix: nsp1                                  # prefixed to HA entity_ids to make them unique (do not use '-' or spaces, use '_' instead: OPPOSITE of 'esp_net_name').
    tft_url: !secret nsp1_tft_url                    # path, including filename, where you put TFT file created in the Nextion Editor: e.g, "https://MY_URL:8123/local/nsp1.tft" if you put the file in the in the "/config/www/" folder of your HA device.
    wifi_ssid: !secret wifi_ssid                     # your home WiFi credentials.
    wifi_password: !secret wifi_password
  #  encr_key: "H0000000000000000000000000000000000000000000"  # Generate your own key here: https://esphome.io/components/api.html#configuration-variables (and uncomment the api: encrytion: key: "...") section below if you want encrypted HA communications.
  #----------------------------------------          # No editing of the YAML below is required to use Nextion Handler.
```

</details> 

<details>
  <summary>2️⃣ Copy and configure Home Assistant Python script:</summary>  
 
  * Download and copy the `nextion_handler.py` script into the `<config>/python_scripts/` folder of your Home Assistant device.
  * If you have never used Python scripts in Home Assistant before, you will have to add a line `python_script:` to your `configuration.yaml`.  ([See HA page on Python scripts](https://www.home-assistant.io/integrations/python_script/).)
  * Copy the automation template below to your own HA configuration (editing the NSPanel entity_ids to match those you noted in step 1️⃣ if you set a prefix other than `nsp1`).
  * In the `widgets:` section of the automation, add one of your own entities to the list as `  - entity: light.kitchen` (for example) to get started.  Start with just one to make sure the installation worked.  You can edit the `widget:` list whenever you want, then `reload automations` for HA to recognise the changes.  (If you get an entity configuration wrong, this will usually be indicated by a red and white ❗ _error symbol_ for that widget.) 

**Automation template:** If you left `ha_prefix: nsp1` unchanged in step 1️⃣ then you only need to change the `- entity: light.kitchen` line near the bottom to match a light of your own.  (_The downloadable `HA_automation.yaml` file for this template has more annotations and suggested examples of what you might add to your list later on._) 
```YAML
- alias: "NSP1 Nextion handler"
  mode: queued
  max: 5
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
          # Add a list of your entities here: only the "- entity: " config variable is mandatory,
          # but usually customise the "name:" and "icon:" too.
          - entity: persistent_notification.all  # special case
          #*** Edit for your own devices
          - entity: light.kitchen                # replace with your own light to start
            name: Kitchen
            icon: 50                             # see icon index
``` 
 
</details> 
 
<details>
  <summary>3️⃣ Flash Nextion Widget UI TFT file:</summary> 

  * Download the `Widget UI TFT file` then copy and rename it to the location and filename you specified in the `tft_url` of your ESPHome configuration in step 1️⃣.  Then press the `TFT upload button` on the NSPanel's device page in Home Assistant (that you located in step 1️⃣).
  * Wait for the NSPanel to flash and reboot with the new UI.  (You may have to reboot both HA and the NSPanel after the first installation.)

Whenever you change your widgets list (including the initial installation) it will take a little bit longer for each page to refresh the first time after that as it reconfigures itself.  If it gets stuck, open the settings menu (swipe down and close it by swiping down again), which will help to read the new list. 

</details> 
 
</details>

  ---

## UI Features
  
### Page Layout and Function
Each page is tiled with Widget cards, one per entity. Information and touch interactions adapt to the type of entity they are displaying.  
* **🔹 Main Pages:** The 'Main' content pages are filled completely with Widget cards (as shown in the example images below).  Navigation is by `swipe` gestures that cycles forwards and backwards through the main pages.
* **🔹 Popup Pages:** Some actions bring up 'popup' pages that provide added controls and information.  These are distinguished by a title bar at the top, and a back arrow in the top left corner for navigating back to the 'Main' page you came from.
* **🔹Widget Cards:** Each card has an icon (with circular background), then three rows of text: the 'title' at the top, a row of short 'alternate' text, and the main 'info' text along the width of the card at the bottom.  Users interact with Widgets by `press` and `nudge` gestures (described below).
* **🔹 Icons:** Icons and their coloring conventions [follow the detailed set of Minimilist Design UI standards for this project](/UI_Design/Minimalist/): cards with white/grey icons typically only provide information and will not trigger any actions when touched, whereas colored icons indicate that touch interactions with the card will trigger a range of actions (as detailed below).  A grey circle behind the icon indicates that the entity is in an off/inactive state, while a colored background highlights when entities are in an on/active/alert state.  The available icon pairs, currated and precompiled to these conventions, are indexed below. 
  

 **Screenshots of Widget UI** (3 'Main' pages, each tiled with 2x4 entity cards) showing how the appearance of cards adapts to the type of entity allocated to them.  
   
![Widgets UI screenshots](/widget_ui/Screenshots_Widgets.png "Widget UI screenshots")
 


## Gestures

The [gesture enginge](/Tips_and_Tricks/NEXTION_GESTURES.md) allows a wide range of user interactions in the compact space of the NSPanel display while filling that limited area with Widgets and useful information (rather than buttons and slider bars).  Different types of gestures are used to change pages (`swipes`), make multi-step incremental changes to Widget attributes (`nudges` + hold), and trigger actions specific to the type of entity on the Widget (`press` + hold).  When you touch the screen, a small `gesture indicator` pops up in the top left corner showing a `gesture icon` for the currently detected gesture (one of: swipes: `⬅` `➡` `⬆` `⬇`, nudges: `◀` `▶` `⯅` `⯆`, or presses: `◐` `◑` `◉` `◎` `✖`), and a `text description` of the `action` that will be triggered if you lift your finger at that moment.  If the gesture is held, then a `timer bar` will appear to the right of the gesture indicator (where the duration of the hold will modify the gesture and triggered action for `presses` and will increase the number of times a step increment/decrement is applied for `nudges`).	
  
<details>
  <summary>▶️ show gesture types ...</summary>
  
**Demonstration of the `gesture indicator` giving UI feedback on touch interactions.**	 
	
![Gesture UI demo](/widget_ui/DEMO_Gestures_Animation.gif)
	
	
#### Page Swipe Gestures  
`Swipe` gestures trigger as soon as a touch moves the trigger distance on the display (_before_ your finger is lifted): the trigger distance is about 1/3 the width of a US NSPanel, or 1/4 on the landscape EU NSPanel).  
* **🔹 `⬅` `➡` Left and Right swipes:** cycle forwards and backwards through 'Main' pages (for as many 'Main' pages as are required for the configured list of Widgets).
* **🔹 `⬇` Downward swipes:** will bring up the 'Settings' popup page from any 'Main' page (or will dismiss a popup page).  Opening the settings page will also fetch an updated count of the number of entities in your configured `widgets:` list (so the that correct number of pages can be allocated).
* **🔹 `⬆` Upward swipes:** force an immediate update of the widgets on the current page with current data from HA.

#### Widget Nudge (and hold) Gestures  
`Nudge` gestures are short movements on a Widget card (moving a distance about the width of an icon circle).  Nudges are a compact way of replacing slider bars to make incremental step increases/decreases to an entity attribute (such a lights brightness, color temperature and hue).  Holding a `nudge` will bring up the timer bar to trigger multiple step changes.
* **🔹 `◀` `▶` Left and Right nudges:** incrementally increase/decrease an entity attribute in step changes. 
* **🔹 `⯅` `⯆` Up and Down nudges:** incrementally increase/decrease a second entity attribute in step changes.  
To make a single `nudge` increment/decrement just use a quick short flick, and release before the `timer bar` appears.  If you hold until the timer first appears, that counts as a second `nudge`, and each subsequent step on the timer will result in an additional increment/decrement being applied.  The main thing to remember with `nudges` is that you increase the number of step adjustments by _holding_ the touch for a longer duration (rather than by _moving_ your finger further - if you move your finger beyond the trigger distance for a `stroke`, then that action will immediately be excecuted instead).  Alternatively, you can make multiple step adjustments by using several short flicks in a row at about 1 second intervals (if you go too fast, some ajdustments may be lost because of lags in the Home Assistant state machine not updating quickly enough).

#### Widget Press (and hold) Gestures  
* **🔹 `◐` LHS short tap:** A tap on the Widget icon (left half of card) performs the most common action for that type of entity, such a toggling it.  
	(Taps are of short duration, where you lift your finger _before the timer bar appears_.) 
* **🔹 `◑` RHS short tap:** will open the `popup card` for that entity (if it has one) or perform another common action for that entity. 
* **🔹 `◉` Long press:** performs the indicated alternate action for that type of entity. (Actions for LHS and RHS may be different.)  
	(Hold a press until the timer bar first appears to trigger the long-press action.) 
* **🔹 `◎` Very long press:** performs the indicated alternate action for that type of entity. (Actions for LHS and RHS may be different.)  
	(Hold a press until the timer bar increases by 2 more steps after first appearing to trigger the very-long-press action).
	
#### Cancelling after starting a Gesture  
* **🔹 `✖` Cancel gesture (and `✘` cancel action):** Cancels, without performing any action, when:  
	**a)** a press is held for long enough (6 timer bar step increases after first appearing),  
	**b)** any gesture is held long enough until the timer bar completely fills,  
	**c)** your finger moves only slightly from the starting point (either as an intential 'cancel' or an ambiguous slip of the finger where it is not clear whether a `press` or `nudge` is intended), or   
	**d)** the entity has no action for that gesture, indicated by `✘` in the text description.

The `gesture indicator` will update dynamically throughout touch events to give the user feedback on what gesture is currently being detected and what action will be performed if you lift your finger at that point.  You can safely explore the UI by trying out the different gestures and seeing how they are modified by the duration `timer`, then cancel by returning your finger close to the start of the stroke to make the `✖` (cancel) gesture icon appear if you want to avoid triggering any action at the end.	
	
 --- 
  
</details>  
  
  
## Popup Pages (incl. NSPanel Settings & Relays)
Popup pages provide additional detail and control, particularly where generic Widget cards are too limiting:  
  
<details>
  <summary>▶️ show details on Popups for Settings, Lights, and Notifications ...</summary>

  
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
  
 * **🔹 Notifications -** allows reading and dismissing Home Assistant persistent_notications.
   * 'Notifications' is a special type of Widget card because it uses _all_ the entities in the domain, not just a single notifiction entity.
   * Enter `entity: persistent_notification.all` to create a notifications UI card (then customise it as you wish).
   * This allows the NSPanel to be used as a convenient message board for HA (delivering messages to all rooms in the house with an NSPanel).  
  
  
As functionality is developed, more popups will be added to support some of the more complex entity types (such as media_players).  
  

 **Screenshots of current 'popup cards' to support widget entity cards.**  (Where available, popups are triggered by touching the top right quadrant of the enity card). 
   
![Widget Popups](https://github.com/krizkontrolz/Home-Assistant-nextion_handler/blob/main/widget_ui/Screenshots_Popups.png "Widget Popups")
  
  
  
 --- 
  
</details>  

  
## Widget Card Tap Interactions (by Entity type)
	
A set of `nudge` and `press` gestures allows users to interact with Widgets in different ways, as shown in the UI by the `gesture indicator` (`nudges`: `◀` `▶` `⯅` `⯆`, and `presses`: `◐` `◑` `◉` `◎` `✖`).  The `actions` that are triggered by each of those gestures adapt to the type of entity on that Widget card and are shown as a `text description` next to the `gesture icon` in the `gesture indicator`.  This makes it easy for users to learn all the possible Widget interactions from feedback displayed directly on the Nextion display - but the set of interactions for each entity type is also summarised below for reference: 

  

<details>
  <summary>▶️ show actions triggered by touch interactions with each type of Widget card ...</summary>


(Under construction: new v0.7 `tap` and `nudge` gestures follow the icons that appear in the UI `gesture indicator`, as desccribed in the Gestures section above)
```◐◑◉◎ ⦿⊙✖✘▲▼◀▶⬅⬆⬇➡ 🠖➞🠔🠕🠗◀▶⯅⯆◑◐◉⦿⊙✖```.
	
* 🔸 **Cards for Switch, Input boolean, Script, Siren, Group, Camera, Humidifier, and  Remote** (Toggle, On, Off) Entities.
  * `◐`, `◑`: Toggle (tap icon)
  * LHS & RHS `◉`: Turn OFF (long press)
  * LHS & RHS `◎`: Turn on (very long press)
  
* 🔸 **Light Cards:**
  * `◐`: Toggle light on/off  
  * LHS `◉`: Force turning light OFF (fix out of sync lights)  
  * LHS `◎`: Force turning light on  
  * `◑`: Brings up light Popup card with color wheel and slider controls  
  * RHS `◉`: Turn on/change the bulb to a supported white mode  
  * `◀`, `▶`: Adjust light Brightness.  If light is off:  
	`◀` will turn light on at Minimum (1%) brightness  
	`▶` will turn light on at Maximum (100%) brightness  
  * `⯅`, `⯆`: Adjust the light's Color Temperature (if it is in WW mode) or Hue (if it is in an RGB mode)  

* 🔸 **Media Player Cards:**
  * `◐`: Toggle media player on/off  
  * LHS `◉`: Toggle Play/Pause  
  * LHS `◎`: Source select (cycle backwards through source list)  
  * `◑`: (Placeholder to bring up future media player Popup)  
  * RHS `◉`: Toggle mute  
  * RHS `◎`: Source select (cycle forwards through source list)  
  * `◀`, `▶`: Skip Backwards/Forwards through tracks/channels/media list  
  * `⯅`, `⯆`: Increase/Decrease volume  

* 🔸 **Alarm Control Panel Cards:**
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
  * `◐`: Toggle cover open/closed  
  * LHS `◉`: Stop cover open/close  
  * LHS `◎`: Open cover  
  * `◑`: Toggle tilt  
  * RHS `◉`: Stop tilt  
  * RHS `◎`: Open tilt  
  * `◀`, `▶`: Reduce/Increase cover Tilt  
  * `⯅`, `⯆`: Reduce/Increase cover Position  
	
* 🔸 **Input Number Cards:**
  * LHS `◉`: Set to Minimum value  
  * LHS `◎`: Set to 25% (between Min and Max)  
  * RHS `◉`: Set to Maximum value  
  * RHS `◎`: Set to 75% (between Min and Max)  
  * `◀`, `▶`: Decrease/Increase value in increments of 10% of range  
  * `⯅`, `⯆`: Decrease/Increase value in increments of 1% of range  
	
* 🔸 **Input_Select and Select Cards:**
  * LHS `◉`: Set to First option in list  
  * RHS `◉`: Set to Last option in list  
  * `◀`, `▶`: Cycle backwards/forwards through the options list  
	
* 🔸 **Scene Cards:**
  * `◐`, `◑`: Turn on scene (there is no 'turn off' for scenes)  
	
* 🔸 **Update Cards:**
  * `◐`: Install latest Update  
  * `◑`: Skip this update  
  * RHS `◉`: Clear skipping of update  
	
* 🔸 **Vacuum Cards:**
  * `◐`: Toggle stop/start cleaning  
  * LHS `◉`: Return to base  
  * `◑`: Locate vacuum  


"🔺" indicates entity types I don't have so I need a volunteer to test.	
	
---	
	
**_OLD v0.6 quadrant touch interactions - currently being updated to the new gestures above._**
Each card has four quadrants for touch interactions, each of which can be given a short tap or a long press.  The [gesture processing subroutine](/main/Tips_and_Tricks) will reject any touches where your finger moves slightly (but not far enough to register a swipe).  This is to reject ambiguous gestures that could inadvertently trigger an action you didn't mean to (or ambiguous slips between hotspot quadrants).  So legitimate touches need to be precise (without finger movement) to trigger, and short taps should be fast so that they are clearly distinguishable from long presses.
	
*OLD 'quadrant' taps:* The following abbreviations are used as shorthand below for touch interactions:   
  &nbsp;&nbsp; `TL`: top left quadrant (tap icon)  
  &nbsp;&nbsp; `TR`: top right quadrant (title)  
  &nbsp;&nbsp; `BL`: bottom left quadrant  
  &nbsp;&nbsp; `BR`: bottom right quadrant  
  &nbsp;&nbsp; `BL_R`: bottom left-right paired interactions  
  &nbsp;&nbsp; `LHS`: left-hand-side 2 quadrants  
  &nbsp;&nbsp; `RHS`: right-hand-side 2 quadrants  
  &nbsp;&nbsp; `ALL`: all 4 quadrants (entire card, excl. margins between 'hotspots')  
  &nbsp;&nbsp; `-s`: suffix for a short tap  
  &nbsp;&nbsp; `-l`: suffix for a long-press  
	
  
* 🔸 **Light Cards:**
  * `TL-s`: toggle light on/off
  * `TL-l`: force turning light OFF (fix out of sync lights)
  * `TR-s`: brings up light popup card
  * `TR-l`: turn on/change the bulb to a supported white mode
  * `BL_R-s`: dim/brighten light (if already on), or turn on light at low/high brightness (if off)
  * `BL_R-l`: increase/decrease the color_temperature or hue of the light (according to its current color_mode)


  
  
* 🔸 **Media Player Cards:**
  * `TL-s`: toggle power on/off
  * `TL-l`: toggle pause/play
  * `TR-s`: _(placeholder for future media popup card)_
  * `TR-l`: mute/unmute the volume
  * `BL_R-s`: change the volume down/up
  * `BL_R-l`: change to the previous/next track or channel
 

* 🔸 **Automation Cards:**
  * `ALL-s`: toggle whether automation is enabled/disabled (if it will run when triggered)
  * `ALL-l`: trigger the automation (ignoring conditions) - execute its `action:`s immediately  
 (_As feedback, the info text on the card will show how many calls to the automation are currently running._)

* 🔸 **Button Cards:**
  * `ALL-s&l`: trigger the button actions
  
* 🔸 **Input Number Cards:**
  * `LHS-s`: decrease value by 5% of range
  * `LHS-l`: decrease value by 20% of range
  * `RHS-s`: inrease value by 5% of range
  * `RHS-l`: increase value by 20% of range  

* 🔸 **Scene Cards:**
  * `ALL-s&l`: turn scene on  
  (_Scenes cannot be turned off - the icon will highlight as 'on' for an hour after it was turned on._)
  
* 🔸 **Script Cards:**
  * `ALL-s`: toggle run/stop
  * `ALL-l`: (force) stop the script  
 (_As feedback, the info text on the card will show how many calls to the script are currently running._)

* 🔸 **Switch Cards:**
  * `ALL-s`: toggle switch on/off
  * `ALL-l`: force turning switch off

* 🔸 **Update Cards:**
  * `LHS-s`: install update
  * `RHS-s`: skip update (card status will show the installed vs current versions)
  * `RHS-l`: clear skipped update (icon state will become 'active' again)
  
* 🔸 **Vacuum Cards:** (only tested with Xiaomi vacuum so far)
  * `LHS-s`: toggle start(& turn_on)/stop (& turn_off) cleaning (commands for both types of vacuums are sent)
  * `LHS-l`: return to base
  * `RHS-s`: locate vaccum
  * `RHS-l`: spot clean
  
  
_(I have set up interactive cards for all the types of entities I currently use in Home Assistant. I can look at filling the gaps over time, but that will require input and testing from those who want them.)_
  
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

If you misconfigure a widget, the Nextion Handler will try to give you feedback on the Nextion display by showing the ❗ _error symbol_ (icon 47, highlighted), a red and white icon of an exclamation mark in a circle, and may show some additional information in the info text area (such as showing an invalid entity_id with '*' on either side), to guide you to what part of your `widget:` list needs fixing.  For more serious problems, check the Home Assistant error logs for Nextion Handler messages. 
  
_(I will likely add the ability to customise the actions that are triggered by each type of touch interaction on a Widget Card in future.)_


<details>
  <summary>▶️ advanced configuration example ...</summary>  
	
While the intention of the Widget UI is to keep configuration as simple as possible, it does still allow more advanced users who are comfortable with Home Assistant templating to do very detailed customisations of the dashboard information displayed, including some quite sophisticated dynamic behaviours.  If you are not comfortable with templating, you can safely ingnore it, and the defaults will do a good job for most people.  But if you like the creative opportunities that dynamic templating allows, then the example below gives an idea of how to get started with your own customisations.
	
**Demo example of customised card that templates everything** - shows the time and date, and changes the icon and alt text for weekends and holidays (using a 'workday' binary sensor):  
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
A currated set of icons is used on the cards.  These are paired (for off/unhighlighted and on/highlighted states), with icons and coloring already formatted to [follow the Minimilist Design UI standards](/UI_Design/Minimalist/).  A default icon will be allocated based on the entity type (domain and class).  But you can set a different one in your `widgets:` list by specifying the _number_ (not name) of the icon you want from the index below. (Default, automatically assigned, icons are in the first 6 rows.)  You can also use templating to dynamically change the `icon:` and the `icon_state:` in your your `widget:` list configuration.
  
<details>
  <summary>▶️ show Icon Index ...</summary>

 **Index numbers for available icon choices.**  Icons are paired - the off/unhighlighted state is on the left and the on/highlighted version is on the right.  Use the index number of the icon you want in the `icon:` setting of each `- entity:` in your `widget:` list (or omit this setting to accept the default for that entity type).  **Icon 47** is used in its unhighlighted state to blank out the icon area on 'blank' cards, and it is used in its highlighted state as the ❗ _error symbol_ to give users feedback that they need to fix a problem with their `widget:` config for that entity.
   
 ![Widget UI Icon index](https://github.com/krizkontrolz/Home-Assistant-nextion_handler/blob/main/widget_ui/Widget_Icons_Index.png "Icon numbering index")

### Icons are grouped as follows:
 * 🔵 0 .. 47 (6 rows): default and system.
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
 
 --- 
  
  
  
</details>


---
  
  
  
[▶️ Back to main repository root/README](https://github.com/krizkontrolz/Home-Assistant-nextion_handler)
