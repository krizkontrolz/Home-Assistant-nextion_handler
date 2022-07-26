# Beta Testing Files

The files here are for those testing specific new features or bug fixes.  Not much use to anyone else.  
🔶 **_If a new EU version re-introduces the touch offset problem, remind me to fix it._**  
(I have to comment out the fix while testing on the US panel and sometimes forget to uncomment before uploading a TFT here.)

## Instructions for Updating from previous to Latest Beta:

 <details>
  <summary>▶️ expand instructions ...</summary>


* **Nextion TFT** (`NSP-EU*_YYYY-MM-YY_beta.TFT`) - copy the latest TFT and rename to overwirte your previous version, then upload to your NSPanel. (_Keep the path and name of the file and the `tft_url` the same when updating, something short and simple, so you don't have to keep editing and reflashing the ESPHome config._)
* **Python script** (`nextion_handler.py`) - copy and overwrite previous file in your `\config\python_scripts` directory in Home Assistant.
* **ESPHome config template** (`ESPHome_Nextion_Handler_template.yaml`) - This file will be updated far less frequently than the two above, but takes a bit more effort and care to update. **BACK UP** your original YAML file, copy and paste the _section below your customised `substitution:` block_ (into the standard 'boilerplate' section), edit back in parts of the template you customised before (see check list below), then flash with ESPHome.  (Keep the name and path of the YAML file the same when updating, just paste the new information into the existing (backed up) file).  After pasting in the new information you may need to edit back in any of your previous customisations:
  * make sure you keep your original customised `substitutions:` block at the top of the file (and check that the list of variables in that section has not changed in the new template).
  * comment out the 'reparse mode fix' near the top of the file.  (To make it easier for people flashing ESPHome for the first time, this is now uncommented by default.  It is not essential to comment the fix out after the first time, but it is no longer needed after that.)
  * uncomment the encryption section again (if you use it).
  * add back your custom on_boot settings (if you customised that).
  * edit back in any other custom parts of your previous config. (such as where there are comments in the template suggesting customisation options).
  * **fix any indentation problems after editing** - some YAML editors mess this up when copying and pasting (and I made this mistake in one of the previous beta templates - appologies).
  * if you are trying to merge large numbers of edits to a custom config file, you can use the GitHub `History` (button in top right corner when you open a tracked file in GitHub) to view commit details of all the changes between versions.
</details>
 
--- 

## 2022-07-25
Python script:
* Fixed typo bug in cl() (climate.* action function): `ent_state.get()` -> `ent_state.attributes.get()`.
* Added `adjust()` parsing of arguments for `brt`, `brtv` and `ct` in `lt()` (for easier _relative_ adjustments of light brightness and color temp.).

## EU and US beta 2022-07-24
TFT (HMI included too):
* US (portrait) version now added too.
* All 36 standard entity types (domains) now supported in Widget UI with new dashboard information and/or interactive controls now added for  `climate.*`, `fan.*`, `humidifier.*`, `lock.*`, and `water_heater.*` entities.  I don't own these myself so would appreciate any feedback on what works and what needs fixing for these.
* New detailed climate control 'popup' card (with controls for temperature (range & single), humidity, hvac modes, preset modes, fan modes, swing modes, aux heat).
* Improved gesture feedback that dynamically updates the actual cumulative step change that will be applied when making nudge/swipe adjustments on Widget cards (e.g. how much a light' brightness will change by).
* Gesture indicators _everywhere_ now (including 'popup' control cards, with added interactions now that there is clear UI feedback).
* For entity domains that have `class` subcategories (`cover.*`, `binary_sensor.*`, and `sensor.*`) the `class` is used to pick the default icon - the default icon should now be an informative option even without any user customisation.
* Dashboard information for `sensor`s now improved.
* Tweaks to UI graphics and interaction hotspots.
* Improved error messages on Settings and 'sleep' screens - now there are warnings if the Nextion TFT requires a later version of the `nextion_handler.py` or `ESPHome template`.
* Improved System Information screen (when you tap the blank screen to wake the NSPanel, don't lift your finger, and the information will keep displaying until you release).
* Performance and reliability improvements (although not perfect yet).

Python script (**needs updating too**):
* Backend support for all new Widget dashboard information and interactions.
* Improved list picking - can pick both by cycling (in multiple-step jumps) through lists, or directly picking by the number of item in lists (e.g., picking `input_select`s or `source`s for `media_player`s).  Selected list items now show the number of the item in the list too to help with this.
* Code clean-up and new/improved helper functions for reptitive code.

ESPHome config. (**no upgrad needed**):
* No upgrade needed if you already have a working version.  This config. is slightly modified to make it easier for first time users in the YAML sections that are uncommented/commented, e.g. the 'reparse mode fix' is uncommented by default.


## EU beta 2022-07-07
TFT (HMI included too):
* Widened margins for detecting 'edge swipes' especially on RHS for more robuts 'page swipes'.
* Widened hotspot areas beyond visual margins of all UI elements for more robust touch detection (Nextion precision is poor).
* Version checks now conducted whenever device sleeps and will display if ESPHome config or nextion_handler.py versions are too old for current TFT (with prompt to update).
* `⬅` and `➡` strokes on Popup pages now have actions assigned to them (e.g., put device to sleep from Settings page).

Python script:
* Fixed typo that stopped 'cover' code from working properly.
* Converts `\n\n` in Notification messages to single line break `\r` to render properly on Nextion.

## EU beta 2022-07-04
TFT:
* Changed gestures so that swipes on Widgets vs Pages are more distinct.  Now you must _swipe from the bezel into the display area_ for `⬅➡⬆⬇` gestures (to change pages etc.) and any swipes on Widget cards (starting away from the edges of the display) will be `⯇⯈⯅⯆` gestures (adjust enitity attributes for that Widget).  This makes it much easier to control the gestures you intend to send (and avoid triggering Widget actions unintentionally).
* Gesture indicator for popup pages too.
* (Hidden) System information on 'sleep' screen.  To force the display to blackout immediately, press the date-time in the title bar of the Settings screen.  On the blackout screen, when you press to wake the NSPanel back up again, _while you hold your finger on the screen_ the system information will display for the duration of your touch.  Displayed information is versions of TFT, ESPH config, Py script, together with Number of Widgets configured, Number of Widget pages they will fill, (and number of Aliases - only if you have customised pages by editing the HMI file). 

Python script:
* Fixed 'cover' attributes (_thanks to zigomatic_).
* Version number and system information reporting (with setsys()).
* Binary_sensor icons now pick better defaults according to device class.

ESPHome config.:
* Improved integration of ESP32 periphals with Nextion, and Nextion system information with ESP32.
* Pushing physical buttons will now immediately wake and refresh the display (including with the updated relay states).
* RTTTL strings (or preset shorthand codes) sent from the Nextion now automatically play.

## EU beta 2022-06-29
TFT:
* Start on/change to Settings screen (whenever there are no widgets detetected (yet))
* Pixel perfect text alignemnt on Widget Cards
* Larger font sizes (Info text reduces for long strings)
* Visual indicators for relays now implemented (sensor part of ESPHome code was already in place) 
_Still need to change ESPHome code to apply change immediately_ (can manual refresh for now, or just wait)
* Optimizations for gesture & update_loop timing

Python script:
* Inactivate 'unavailable' entities (no longer open popup pages)
* Code clean up and optimisations

## EU beta 2022-06-27b
TFT:
* Fixed EU offset (sorry, forgot to change back after testing on US NSPanel before)

## EU beta 2022-06-27
TFT:
* There is now an icon to show when entities are ‘unavailable’ (a crossed out eye).
* Dulled down the color of icons for lights etc. to make their off/unhighlighted state clearer (but still follows the documented UI Design color conventions).
* Shortened the Gesture indicator to the width of single Widget card. There are slightly different versions of the indicator to test balances of aeshetics, responsiveness and funtion.
* Fixed a bunch of bugs including one where you could get stuck on the light popup page after the screen was blanked.
* Added the initial version of popup card for media players.  Many media players work poorly in Lovelace, so won't work any better here.
* 🔶 Added controls for `cover` entities - I need some to test this (I don't have any `cover`s)
