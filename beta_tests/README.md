# Beta Testing Files

The files here are for those testing specific new features or bug fixes.  Not much use to anyone else.  
🔶 **_If a new EU version re-introduces the touch offset problem, remind me to fix it._**  
(I have to comment out the fix while testing on the US panel and sometimes forget to uncomment before uploading a TFT here.)

## EU beta 2022-06-29
TFT
* Start on Settings screen (whenever their are no widgets detetected (yet))
* Pixel perfect text alignemnt on Widget Cards
* Larger font sizes (Info text reduces for long strings)
* Visual indicators for relays now implemented (ESPHome code was already in place) 
_Still need to change ESPHome code to apply change immediately_ (can manual refresh for now, or wait)
* Optimizations for gesture & update_loop timing

Python script
* Inactivate 'unavailable' entities
* Code clean up and optimisations

## EU beta 2022-06-27b
* Fixed EU offset (sorry, forgot to change back after testing on US NSPanel before)

## EU beta 2022-06-27
* There is now an icon to show when entities are ‘unavailable’ (a crossed out eye).
* Dulled down the color of icons for lights etc. to make their off/unhighlighted state clearer (but still follows the documented UI Design color conventions).
* Shortened the Gesture indicator to the width of single Widget card. There are slightly different versions of the indicator to test balances of aeshetics, responsiveness and funtion.
* Fixed a bunch of bugs including one where you could get stuck on the light popup page after the screen was blanked.
* Added the initial version of popup card for media players.  Many media players work poorly in Lovelace, so won't work any better here.
