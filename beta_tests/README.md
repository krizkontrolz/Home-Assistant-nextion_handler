# Beta Testing Files

The files here are for those testing specific new features or bug fixes.  Not much use to anyone else.  
🔶 **_If a new EU version re-introduces the touch offset problem, remind me to fix it._**  
(I have to comment out the fix while testing on the US panel and sometimes forget to uncomment before uploading a TFT here.)

## Instructions for Updating from previous to Latest Beta:
* **Nextion TFT** - copy latest TFT and rename to overwirte previous version, then upload to NSPanel.
* **Python script** (nextion_handler) - copy and overwrite previous file.
* **ESPHome config template** - BACK UP original YAML file, copy and paste the _section below your customised substitutions_ (into the standard 'boilerplate' section), uncomment the encryption section (if you use it), customise the boot settings (if you use that part), then flash with ESPHome.

## EU beta 2022-07-07
TFT (HMI included too)
* Widened margins for detecting 'edge swipes' especially on RHS for more robuts 'page swipes'.
* Widened hotspot areas beyond visual margins of all UI elements for more robust touch detection (Nextion precision is poor).
* Version checks now conducted whenever device sleeps and will display if ESPHome config or nextion_handler.py versions are too old for current TFT (with prompt to update).
* `⬅` and `➡` strokes on Popup pages now have actions assigned to them (e.g., put device to sleep from Settings page).

Python script:
* Fixed typo that stopped 'cover' code from working properly.
* Converts `\n\n` in Notification messages to single line break `\r` to render properly on Nextion.

## EU beta 2022-07-04
TFT
* Changed gestures so that swipes on Widgets vs Pages are more distinct.  Now you must _swipe from the bezel into the display area_ for `⬅➡⬆⬇` gestures (to change pages etc.) and any swipes on Widget cards (starting away from the edges of the display) will be `⯇⯈⯅⯆` gestures (adjust enitity attributes for that Widget).  This makes it much easier to control the gestures you intend to send (and avoid triggering Widget actions unintentionally).
* Gesture indicator for popup pages too.
* (Hidden) System information on 'sleep' screen.  To force the display to blackout immediately, press the date-time in the title bar of the Settings screen.  On the blackout screen, when you press to wake the NSPanel back up again, _while you hold your finger on the screen_ the system information will display for the duration of your touch.  Displayed information is versions of TFT, ESPH config, Py script, together with Number of Widgets configured, Number of Widget pages they will fill, (and number of Aliases - only if you have customised pages by editing the HMI file). 

Python script
* Fixed 'cover' attributes (_thanks to zigomatic_).
* Version number and system information reporting (with setsys()).
* Binary_sensor icons now pick better defaults according to device class.

ESPHome config.
* Improved integration of ESP32 periphals with Nextion, and Nextion system information with ESP32.
* Pushing physical buttons will now immediately wake and refresh the display (including with the updated relay states).
* RTTTL strings (or preset shorthand codes) sent from the Nextion now automatically play.

## EU beta 2022-06-29
TFT
* Start on/change to Settings screen (whenever there are no widgets detetected (yet))
* Pixel perfect text alignemnt on Widget Cards
* Larger font sizes (Info text reduces for long strings)
* Visual indicators for relays now implemented (sensor part of ESPHome code was already in place) 
_Still need to change ESPHome code to apply change immediately_ (can manual refresh for now, or just wait)
* Optimizations for gesture & update_loop timing

Python script
* Inactivate 'unavailable' entities (no longer open popup pages)
* Code clean up and optimisations

## EU beta 2022-06-27b
* Fixed EU offset (sorry, forgot to change back after testing on US NSPanel before)

## EU beta 2022-06-27
* There is now an icon to show when entities are ‘unavailable’ (a crossed out eye).
* Dulled down the color of icons for lights etc. to make their off/unhighlighted state clearer (but still follows the documented UI Design color conventions).
* Shortened the Gesture indicator to the width of single Widget card. There are slightly different versions of the indicator to test balances of aeshetics, responsiveness and funtion.
* Fixed a bunch of bugs including one where you could get stuck on the light popup page after the screen was blanked.
* Added the initial version of popup card for media players.  Many media players work poorly in Lovelace, so won't work any better here.
* 🔶 Added controls for `cover` entities - I need some to test this (I don't have any `cover`s)
