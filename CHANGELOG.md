## CHANGELOG:

--- 


## ✴️ [0.7 EU & US release version]  2022-07-30
Incorporates all changes below from beta testing

## 2022-07-30 v0.7 release
TFTs:
* Final tweaks to Widget actions, especially water heaters.

Python script:
* Final tweaks to Widget actions, especially water heaters.
* gact() wrapper for wdact() to allow directly calling gesture actions from custom HMI code.
* sub Nx (x) : now allows optional argument x=0 to trigger click release event for Nextion component Nx.

## 2022-07-27
Python script and TFTs:
* Small fix for toggling HVAC (climate.*) devices (created a custom toggle action because they cannot be used with the standard toggle).

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


## ✴️ [0.6] 2022-06-03

### Added

- ✴️ New simplified Widget UI option (using special pre-compiled TFT).
- 🔸 SET & ACT NH commands to support widgets: `setwd` (supported by get_widget_info()) and `wact`.
- 🔸 Improved 'Minimalist'-style graphical UI (with separate documentation folder, detailed design rules and SVG templates).
- 🔸 SET & ACT NH commands for media_players: `setmp` and `mp`.
- 🔸 Many ACT commands will now take _detla_ (specified by `+`/`-` prefix and optional `%` suffix) values to allow easier increase/decrease controls (light brightness, volume etc.)
- 🔆 Lots of improvements to the ESPHome configuration making ESP32 peripherals more directly accessible to the Nextion display (and your HMI code) _without_ the need for a WiFi connection or Home Assistant.  Most importantly, this means there is _always_ a way to control relays (link/unlink and overrride toggle) independently of Home Assistant.

### Changed

- ❗ BREAKING CHANGE: All `lt_xxx args` instructions are now `lt xxx args` (a single function with service/action component separated out as the first argument - just replace the `_` with a `space` in exisiting instructions in your HMI code).  This is consistent with how `mp` instructions work (and how all future new instructions will work).
- 🔺 Reduced standard configuration to using just `HA_SET1` and `HA_SET2` (down from 5 strings: command strings 3..5 are commented out throughout template code (HMI, ESPH, HA) and be restored if extras are needed).
- 🔹 Cleaned up code, particularly to read and use HA states... and automation YAML data structures more effectively.


## [0.5.0] - 2022-04-02

### Added

- SET & ACT NH commands for Lights: setlt, `lt_brt`, `lt_ct`, `lt_rgb`, `lt_hs`, `lt_cw`, `lt_wt`.
- SET & ACT commands for Persistent Notifications: `setntf`, `ntf`, `ntfx`.
- SET command for fetching Home Assistant date_time: `setdt`.
- Full GESTURE controls in HMI (with new separate documentation and template HMI).

### Changed

- Added flexibility/efficiency to NH commands by making more arguements optional.
- Added optional argument in some SET NH commands to specify default value (to return when HA doesn't return a valid state for an entity). 
- TRIGGER was 'overworked' in HMI, trying to cover functions of both trigger & counter. Now Separated into TRIGGER (just state toggle and status) & LOOP_CNT (fast & slow refreshes).
- Updated all template files

### Fixed

- Tested and debugged all NH commands.
- Improved UPDATE_LOOP timing.


## [0.4.0] - 2022-02-18
### Added
- First public release of all Python script initial Nextion Handler Instruction Set
- First public release of Nextion Editor HMI template with Customizable & Template code   
### Changed
- Return to a single automation in HA YAML
- Nx UPDATE_LOOP now controls timing of: slow UPDATEs, ACTIONs, fast UPDATEs (with delays & repeats) after user interactions
- Fast update speed & repeat settings can now override the defaults in SEND_ACTIONS (to allow customized updates after actions involving high-lag devices, e.g., garage door, blinds, etc.)
- The 'sub APPLY_VARS' NhCmd (which should be at the end of HA_SET1...) gives the nextion_handler control of timing of Nx UI updates (to immediately follow sending the update data requested in HA_SET1...)
- Key default parameters controlling UPDATE_LOOP move to Global_Settings in Program.s* (so that they can be adjusted/tweaked live from HA by sending Nextion Instructions).
- Started marking '**boilerplate**' parts of HMI code more clearly & consistently.

## [0.3.0 unreleased] - 2022-02-14
### Changed
- Separated lists of ACTION & UPDATE command strings (for easier separation in triggering, processing and delay between them)
- Simplified main program loop to only Actions OR Update (based on trigger)
- Removed delays & repeats from this script (processing them in a Py script is not a good fit with HA multithreaded Py environment)
- Use THREE separate HA YAML components (call this script from separate places):
    * ACTION automation (... -> delayed update script)
    * UPDATE automation
    * DELAYED update script (with repeats) - called at the end of this Py script IF it was an ACTION

## [0.2.0 unreleased] - 2022-02-10
### Changed
- Transferred  control of  looping and sequencing from Nx to this script (with new sub, rpt and noupdt NHCmds)

## [0.1.0 unreleased] - 2022-01-01
- First version where all loop/sequencing control was attempted on the Nextion (double inter-linked timer loops)

------------------------------------------------------------------------------
Based on [juampynr's template](https://gist.github.com/juampynr/4c18214a8eb554084e21d6e288a18a2c)
The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).  
