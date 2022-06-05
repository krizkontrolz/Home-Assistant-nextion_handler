# ✴️ Widget UI
(_Last updated 2022/06/05_)  
**🎺 v06_2022-06-03 files now uploaded and ready to install.**

## Current Features and Status

The Widgets currently provide sufficient functionality for most of the every-day Home Assistant controls, allowing you to:

 <details>
  <summary>▶️ show current list of features ...</summary>
 

* 🔹 create a dashboard to easily view information about your smart home, and visually highlight anything needing attention;
* 🔹 'toggle' all Home Assistant entities that can be toggled (lights, media players, switches, scripts, automations, covers, fans, input_booleans etc.);
* 🔹 use interactive widgets to control most of the common types of entities (as per the details in the Widget Card interactions list);
* 🔹 fully control lights (both through quick widget card interactions and a popup page with slider controls and color wheel);
* 🔹 read and dismiss HA notifications;
* 🔹 change NSPanel settings (including managing the linking/unlinking of NSPanel physical buttons to their respective relays).
  
The details of how information is displayed will continue to be fine tuned, and new functionality will be added as the supported capabilities of the underlying [Nextion Hanlder](https://github.com/krizkontrolz/Home-Assistant-nextion_handler/blob/main/HA_NEXTION_HANDLER_INSTRUCTIONS.md) are being developed and expanded.

  
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
(Nextion UI TFT is only available for US NSPanels only at this stage.)
  
*🔹 Flashing the ESPHome YAML template:
  * Download a copy of the template `ESPHome_Nextion_Handler_template.yaml` configuration file and fill in your details from your backup configuration into the `substitutions:` section at the top of the file.  (Leaving `ha_prefix: nsp1` will make the automation template easier later on.)
  * Validate the file before installing it to the NSPanel (from the ESPHome addon page in Home Assistant ).
  * Once the ESPHome installation is complete, check the NSPanel device page in HA to make sure the entities are showing up properly.  If you changed `ha_prefix: nsp1` (above), you will later need to get the enitity_ids for `Trigger`, `HA Act`, `HA Set1 & 2` (from the device page), and `ESPHome: nsp1_send_command` (from `Developer Tools | SERVICES`).  And you will use the `TFT upload button` to flash the Nextion TFT UI file.  
 (_If this is the first time using your NSPanel with ESPHome, there are some lines near the top of the YAML file, marked with `#! *** FIX ***...` that you will need to uncomment **once** to switch the panel from the special 'reparse' mode it uses for the original firmware to allow it work with ESPHome.  Comment those lines out again the next time you reflash your configuration - they only need to run once._)

*🔹 Home Assistant python script:
  * Copy the downloaded `nextion_handler.py` script into the `<config>/python_scripts/` folder of your Home Assistant device.
  * If you have never used Python scripts in Home Assistant before, you will have to add a line `python_script:` to your `configuration.yaml`.  ([See HA page on Python scripts](https://www.home-assistant.io/integrations/python_script/).)
  * Add the automation template from the `HA_automation.yaml` file to your own HA configuration (editing the NSPanel entity_ids to match those you noted above if you set a prefix other than `nsp1`).
  * In the `widgets:` section of the automation, add one of your own entities to the list as `  - entity: light.kitchen` (for example) to get started.  Start with just one to make sure the installation worked.  You can edit the `widget:` list whenever you want, then `reload automations` for HA to recognise the changes.  Some suggestions are already in the template, commented out, for you to replace with your own entities later on.  (If you get an entity configuration wrong, you can usually recoginise this as the first widget on a page that fails to load information properly.) 

*🔹 Nextion Widget UI TFT file:
  * Copy the downloaded `Widget UI TFT file` into the location you specified in the `tft_url` of your ESPHome configuration, and rename it to match the filename you set.  Then press the `TFT upload button` on the NSPanel's device page in Home Assistant (that you located before).
  * Wait for the NSPanel to flash and reboot with the new UI.  (You may have to reboot both HA and the NSPanel after the first installation.)

Whenever you change your widgets list (including the first start) it will take a little bit longer for each page to refresh the first time after that as it reconfigures itself.  If it gets stuck, open the settings menu (swipe down and close it by swiping down again), which will help to read the new list. 
  
</details>

  ---

## UI Features
  
### Page Layout and Function
Each page is tiled with Widget cards, one per entity each with four quadrants for touch interactions. Information and touch interactions adapt to the type of entity they are displaying.  
* **🔹 Main Pages:** The 'Main' content pages are filled completely with Widget cards (as shown in the example images below).  Navigation is by swipe gestures that cycles forwards and backwards through the main pages.
* **🔹 Popup Pages:** Some actions bring up 'popup' pages that provided added controls and information.  These are distinguished by a title bar at the top, and a back arrow in the top left corner for navigating back to the 'Main' page you came from.
* **Widget Cards:** Each card has an icon (with circular background), then three rows of text: the 'title' at the top, a row of short 'alternate' text, and the main 'info' text along the width of the card at the bottom.
* **🔹 Icons:** Icons and their coloring conventions [follow the detailed set of Minimilist Design UI standards for this project](/UI_Design/Minimalist/): cards with white/grey icons typically only provide information and will not trigger any actions when touched, whereas colored icons indicate that long and short presses in the four quadrants of the card will trigger a range of actions (as detailed below).  A grey circle behind the icon indicates that the entity is in an off/inactive state, while a colored background highlights when entities are in an on/active/alert state.  The available icon pairs, currated and precompiled to these conventions, are indexed below. 
  

 **Screenshots of Widget UI** (3 'Main' pages, each tiled with 2x4 entity cards) showing how the appearance of cards adapts to the type of entity allocated to them.  
   
![Widgets UI screenshots](/widget_ui/Screenshots_Widgets.png "Widget UI screenshots")
 


## Page Swipe Gestures
Navigation and other common functions use swipe gestures (rather than on-screen buttons) so that the limited area of the NSPanel display can be fully utilised by Widget cards.
  
<details>
  <summary>▶️ show navigation gestures ...</summary>

  
* **🔹 Left and Right swipes:** change pages forwards and backwards (for as many 'Main' pages as are required for the configured list of Widgets).
* **🔹 Downward swipes:** will bring up the 'Settings' popup page from any 'Main' page (or will dismiss a popup page).  Opening the settings page will also fetch an updated count of the number of entities in your configured `widgets:` list (so the that correct number of pages can be allocated).
* **🔹 Upward swipes:** force an immediate update of the widgets on the current page with current data from HA.

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
Each card has four quadrants for touch interactions, each of which can be given a short tap or a long press.  The [gesture processing subroutine](/main/Tips_and_Tricks) will reject any touches where your finger moves slightly (but not far enough to register a swipe).  This is to reject ambiguous gestures that could inadvertently trigger an action you didn't mean to (or ambiguous slips between hotspot quadrants).  So legitimate touches need to be precise (without finger movement) to trigger, and short taps should be fast so that they are clearly distinguishable from long presses.
  

<details>
  <summary>▶️ show actions triggered by touch interactions with each type of Widget card ...</summary>

  The following abbreviations are used as shorthand below for touch interactions:   
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
  

* 🔸 **_Cards for ALL entities that can be toggled:_**
  * `TL-s`: toggle (tap icon)
  
  
  
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
* 🔷 &nbsp;&nbsp;`icon:` a number (0.167) corresponding to the value of the selected icon-pair index (further below).
* 🔹 &nbsp;&nbsp;`icon_state:` True/'1' for the highlighted state of the icon-pair; False/'0' for the inactive state.
* 🔹 &nbsp;&nbsp;`alt:` The second, short row of (alternate) info text on the card, below the title.
* 🔹 &nbsp;&nbsp;`info:` The main informative text along the full width of the bottom of the card.
  
_(I will likely add the ability to customise the actions that are triggered by each type of touch interaction on a Widget Card in future.)_
  
  
  
 --- 
  
</details>    
  
  
## Icons (with Index Image)
A currated set of icons is used on the cards.  These are paired (for off/unhighlighted and on/highlighted states), with icons and coloring already formatted to [follow the Minimilist Design UI standards](/UI_Design/Minimalist/).  A default icon will be allocated based on the entity type (domain and class).  But you can set a different one in your `widgets:` list by specifying the _number_ (not name) of the icon you want from the index below. (Default, automatically assigned, icons are in the first 6 rows.)  You can also use templating to dynamically change the `icon:` and the `icon_state:` in your your `widget:` list configuration.
  
<details>
  <summary>▶️ show Icon Index ...</summary>

 **Index numbers for available icon choices.**  Icons are paired - the off/unhighlighted state is on the left and the on/highlighted version is on the right.  Use the index number of the icon you want in the `icon:` setting of each `- entity:` in your `widget:` list (or omit this setting to accept the default for that entity type).  **Icon 47** is used in its unhighlighted state to blank out the icon area on 'blank' cards, and it is used in its highlighted state as the ❗ _error symbol_ to give users feedback that they need to fix a problem with their `widget:` config for that entity.
   
 ![Widget UI Icon index](https://github.com/krizkontrolz/Home-Assistant-nextion_handler/blob/main/widget_ui/Widget_Icons_Index.png "Icon numbering index")

 --- 
  
  
  
</details>


---
  
  
  
[▶️ Back to main repository root/README](https://github.com/krizkontrolz/Home-Assistant-nextion_handler)
