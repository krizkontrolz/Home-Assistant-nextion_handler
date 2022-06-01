# Widget UI

**🚧 under construction 🚧**
(_Last updated 2022/06/01_)


## Installation (HMI is only for US NSPanel only at this stage)
**Pre-requisites:**  Home Assistant (HA) with ESPHome installed, an NSPanel that has been flashed with ESPHome (add links), and some basic familiarity with configuring HA.

**BACK UP your existing Nextion files:** in particular your device's ESPHome YAML configuration.  You will need to enter the details from that into the new template later (and will need your original ota password & other details to be able to upload any new configuration).

**File locations:** The Widget UI TFT are in the same `widget_ui` [folder as this README document](/widget_ui), while the latest versions of the ESPHome YAML template and `nextion_handler.py` script are in the `current` [folder of this repository](/current).


#### Installation steps (🚧 NB: files have not quite been uploaded yet 🚧)

<details>
  <summary>▶️ show Installation steps ...</summary>

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

 --- 
  
</details>


## UI Features
  
### Page Layout and Function
Each page is tiled with Widget cards, one per entity with four quadrants each for touch interactions. Information and touch interactions adapt to the type of entity they are displaying.  
* **Main Pages:** The 'main' content pages are filled completely by Widget cards (as shown in the example images below).  Navigation is by swipe gestures that cycles forwards and backwards through the main pages.
* **Popup Pages:** Some actions bring up 'popup' pages that provided added controls and information.  These are distinguished by a title bar at the top, and a back arrow in the top left corner for navigating back to the 'Main' page you came from.
* **Widget Cards:** Each card has an icon (with circular background), then three rows of text: the 'title' at the top, a row of short 'alt' text, and the main 'info' text along the width of the card at the bottom.
* **Icons:** Icons and their coloring conventions [follow the Minimilist Design UI standards](/UI_Design/Minimalist/): cards with white/grey icons typically only provide information and will not trigger any actions when touched, whereas colored icons indicate that long and short presses in the four quadrants of the card will trigger a range of responses (as detailed below).  A grey circle behind the icon indicates that the entity is in an off/inactive state, while a colored background highlights when entities are in an on/active state.  The available icon pairs, currated and precompiled to these conventions, are indexed below. 
  

 **Screenshots of Widget UI** (3 'Main' pages, each tiled with 2x4 entity cards) showing how the appearance of cards adapts to the type of entity allocated to them.  
   
![Widgets UI screenshots](/widget_ui/Screenshots_Widgets.png "Widget UI screenshots")
 


### Page Swipe Gestures
  
<details>
  <summary>▶️ show navigation gestures ...</summary>

  
* **Left and Right swipes:** change pages forwards and backwards (for as many 'Main' pages are required for the configured list of Widgets).
* **Downward swipes:** will bring up the 'Settings' popup page from any 'Main' page (or will dismiss a popup page).  Opening the settings page will also fetch an updated count of the number of entities in your configured `widgets:` list (so the that correct number of pages can be allocated).
* **Upward swipes:** force an immediate update of the widgets on the current page with current data from HA.

 --- 
  
</details>  
  
  
### Popup Pages
  
<details>
  <summary>▶️ show details on Popups for Settings, Lights, and Notifications ...</summary>

Popup pages provide additional detail and control, particularly where generic Widget cards are too limiting:
  
* **Settings Popup** shows system information and allows adjustment to the behaviour of the NSPanel:
  * Brightness max: the standard brightness that the display will revert to on any interaction.
  * Brightness min: the lowest brightness that the screen will gradually dim to before blacking out.
  * Update interval: the time inteval between NSPanel requests for refreshed page data from the Home Assistant Nextion Handler.
  * Sleep time: the time until the scree is blacked out.
  * Fast repeats: the number of times that data updates are requested after a touch action is triggered.  This addresses the issue that some states in HA can update very quickly after a service call, whereas others can have substantial lag (e.g., garage doors, some types of lights).
  * Fast slowdown: the amount by which fast repeats are progressively slowed down.  This amount of time is added to each subsequent repeat.
  * (Un)Linking or NSPanel relays to switches: _on device control disabled for now until ESPHome issues can be resolved._
  * Status information: Small text below the title bar shows the number of widgets read from the YAML configuration, and the version number of the TFT file.  The WiFi status and signal strenght are indicated in the top right corner.  
  
* **Light Popup**: This provides full control of light settings:
  * Available controls will be enabled/disabled according to the capabilities of the currently selected (once that data has been received from HA).
  * All controls relevant to the current light are available irrespective of the current color mode, or whether the light is off (which gives faster access to controls than the HA UI approach).
  * Long pressing on the color wheel will switch the light to a supported white/color_temperature mode.
  * Long pressing the icon in the top right corner will force the bulb off.  (This is a useful fix for when some lights in a group get their Home Assistant state out of phase, which causes toggling fails.)  
  
 * **Notifications**: This allows reading and dismissing Home Assistant persistent_notications.
   * Notifications are special type of entity card because it uses _all_ the entities in the domain, not just one.
   * Enter `entity: persistent.all` to create a notifications UI card (then customise it as you wish).
   * This allows the NSPanel to be used as a convenient message board (delivered to all rooms in the house with an NSPanel).  
  
  
As functionality is added, more popups will be added to support some of the more complex entity types (such as media_players).  
  

 **Screenshots of current 'popup cards' to support widget entity cards.**  (Where available, popups are triggered by touching the top right quadrant of the enity card). 
   
![Widget Popups](https://github.com/krizkontrolz/Home-Assistant-nextion_handler/blob/main/widget_ui/Screenshots_Popups.png "Widget Popups")
  
  
  
 --- 
  
</details>  

  
### Widget Card Tap Interactions (by Entity type)
Each card has four quadrants for touch interactions, each of which can be given a short tap or a long press.  The [gesture processing subroutine](/main/Tips_and_Tricks) will reject any touches where your finger moves, but not far enough to register a swipe.  This is to reject ambiguous gestures that could inadvertently trigger an action you didn't mean to.  So legitimate touches need to be precise (without finger movement) to trigger.
  

<details>
  <summary>▶️ show actions triggered by touch interactions with each type of Widget card ...</summary>

  The following abbreviations are used as shorthand below for touch interactions:
  &nbsp;&nbsp; `TL`: top left quadrant (icon)
  &nbsp;&nbsp; `TR`: top right quadrant (title)
  &nbsp;&nbsp; `BL`: bottom left quadrant
  &nbsp;&nbsp; `BR`: bottom right quadrant
  &nbsp;&nbsp; `BL_R`: bottom left-right paired interactions
  &nbsp;&nbsp; `LHS`: left-hand-side 2 quadrants
  &nbsp;&nbsp; `RHS`: right-hand-side 2 quadrants
  &nbsp;&nbsp; `ALL`: all 4 quadrants (entire card, excl. margins between 'hotspots')
  &nbsp;&nbsp; `-s`: suffix for a short-press
  &nbsp;&nbsp; `-l`: suffix for a long-press
  

* 🔸 **_Cards for ALL entities that can be toggled:_**
  * `TL-s`: toggle
  
  
  
* 🔸 **Light Cards:**
  * `TL-s`: toggle on/off
  * `TL-l`: toggle pause/play
  * `TL-l`: off (fix out of sync lights)
  * `TR-s`: brings up light popup card
  * `TR-l`: turn on/change the bulb to a supported white mode
  * `BL_R-s`: dim/brighten light (if already on), or turn on light at low/high brightness (if off)
  * `BL_R-l`: increase/decrease the color_temperature or hue of the light (according to current light_mode)
  
  
  
* 🔸 **Media Player Cards:**
  * `TL-s`: toggle power on/off
  * `TL-l`: toggle pause/play
  * `TR-s`: _(placeholder for future media popup card)_
  * `TR-l`: mute/unmute the volume
  * `BL_R-s`: change the volume down/up
  * `BL_R-l`: change to the previous/next track or channel

 

* 🔸 **Automation Cards:**
  * `ALL-s`: toggle enabled/disabled
  * `ALL-l`: trigger the automation (ignore conditions)

* 🔸 **Button Cards:**
  * `ALL-s&l`: trigger the button actions

* 🔸 **Scene Cards:**
  * `ALL-s&l`: turn scene on  
  (Scenes cannot be turned off - the icon will highligh as 'on' for an hour afterwards.)
  
* 🔸 **Script Cards:**
  * `ALL-s`: toggle run/stop
  * `ALL-l`: stop the script

* 🔸 **Switch Cards:**
  * `ALL-s`: toggle on/off
  * `ALL-l`: turn off

* 🔸 **Update Cards:**
  * `LHS-s`: install update
  * `RHS-s`: skip update (card status will show the installed vs current versions)
  * `RHS-l`: clear skipped update (icon state will become 'active' again)
  
* 🔸 **Vacuum Cards:** (only tested with Xiaomi so far)
  * `LHS-s`: toggle start(& turn_on)/stop (& turn_off) cleaning
  * `LHS-l`: return to base
  * `RHS-s`: locate vaccum
  * `RHS-l`: spot clean
  
  
_(I have set up interactive cards for all the types of entities I have. I can look at filling the gaps over time, but that will require input and testing from those who want them.)_
  
 --- 
  
</details>  
  
  

### Customising Widget Card Dashboard Information

All cards without interactions still report useful 'dashboard' information, and this information adapts to the the domain, class and reported attributes of the entity.  All aspects of the information a card can be customised in the entities YAML configuration to override defaults, and **this can include dynamic information using standard Home Assistant templating** (Jinja):


<details>
  <summary>▶️ show widget card configuration details ...</summary>  
  
Only the `- entity:` is mandatory to specifiy in the YAML list under the `widgets:` section of your automation configuration for the Nextion Handler.  The `tile:` is the most likely optional thing you will want to use (to replace the entity's truncated friendly_name with something that fits in the limited space on the card).  The default icons for each card should be reasonable, but you will likely want to pick something (from the icon index further below) that is more informative. 

_**I do not recommend changing the other options** until you have everything else working well_ (and then you will likely want to use dynamic data generated by template).  The first of these to consider templating should probably be `icon_state:` for entities such as numeric sensors where there is no default way to decide when the card should be highlighted with the 'active' version of its icon (such as setting a rule for when to highlight a gas sensor, or when to highlight high power consumption etc.)
  
* 🔸 `- entity:` the Home Assistant entity_id.  Special cases are `persitent_notications.all` (for a notifications widget), and `template` (or `blank`) for a widget that is filled entirely with custom dynamic (templated), static, or blank information.
* 🔸 &nbsp;&nbsp;`title:` the top row of text on the card
* 🔸 &nbsp;&nbsp;`icon:` a number (0.167) corresponding to the value of the selected icon-pair index (further below)
* 🔸 &nbsp;&nbsp;`icon_state:` True/'1' for the highlighted state of the icon-pair; False/'0' for the inactive state
* 🔸 &nbsp;&nbsp;`alt:` The second, short row of (alternate) text on the card, below the title
* 🔸 &nbsp;&nbsp;`info:` The main informative text along the full width of the bottom of the card
  
_(I may look at adding a way to customise the actions that are triggered by each type of touch event in future.)_
  
  
  
 --- 
  
</details>    
  
  
### Icons (with Index Image)
A currated set of icons is used on the cards.  These are paired, with icons and coloring already formatted to [follow the Minimilist Design UI standards](/UI_Design/Minimalist/).  A default icon will allocated based on the entity type (domain and class).  But you set a different one in your `widgets:` list you by specifying the _number_ (not name) of the icon you want from the index below. (Default icons are in the first 4 rows.)  
  
<details>
  <summary>▶️ show Icon Index ...</summary>

 **Index of numbering for available icon choices.**  Icons are paired - the off/unhighlighted state is on the left and the on/highlighted version is on the right.  
   
 ![Widget UI Icon index](https://github.com/krizkontrolz/Home-Assistant-nextion_handler/blob/main/widget_ui/Widget_Icons_Index.png "Icon numbering index")

 --- 
  
  
  
</details>



  
## 🚧 Current Status 🚧

The details of how information is displayed is still being fine tuned, and functionality is still being added for the types of things you can control in HA.

 <details>
  <summary>▶️ show development status ...</summary>
 
 At this stage you can use the Widgets to:
* 🔸 create a dashboard easily view information about your smart home, and highlight anything abnormal;
* 🔸 'toggle' all Home Assistant entities that can be toggled (lights, media players, switches, scripts, automations, covers, fans, input_booleans etc.);
* 🔸 fully control lights (with a 'pop-up card');
* 🔸 use interactive widgets to control most of the common types of entities (as per the details in the entity cards interactions list);
* 🔸 read and dismiss HA notifications;
* 🔸 change NSPanel settings.
  
More features are continually being added (as the supported capabilities of the underlying Nextion Hanlder are being developed and expanded).


 --- 
  
</details>
 


