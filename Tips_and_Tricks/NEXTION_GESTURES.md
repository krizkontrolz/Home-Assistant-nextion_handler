# Gesture Approaches for Nextion Devices

Given the small screen sizes of Nextion devices, gestures are a useful way of adding functionality to UI while saving space.   They allow you to reduce the number of graphical UI elements by being able to trigger events such as page changes with **'swipes'** or attaching multiple functions to a single button with different types of **'presses'**.  The demo HMI file in this directory has examples of 2 ways of implementing gestures in the Nextion Editor.  The demo pages are designed to be able to test and experiment with gestures, display realtime information to show how touch data is being used during a gesture, and to illustrate some the 'traps' that you need to be aware of when incorporating gestures into your own HMI projects. 

## Side-Swipe Gestures
The simplest approach for swipe gestures on Nextion devices like NSPanels that have a large surrounding bezel is to use 'side swipes'.  These are where you swipe from the bezel into the screen to trigger events such as cycling between pages.

These are implemented in the Nextion Editor by 'fencing' each edge of the screen with a narrow `hotspot` (raised to the highest surface level) so that they are the first UI element that will be triggered whenever a user swipes from outside the touch-sensitive part of the screen.  You then attach your `swipe` actions to the event code of the hotspots on each edge.

The demo template will highlight each edge green as you swipe into it and **show the distance from the edge at which the swipe was first detected** so that you can calibrate how wide the hotspot needs to be.  On my NSPanels, swipes were consistently triggered within 7 pixels of the edge (~1 mm) and worked relibably with hotspots set to this width.

>> Insert screeshot

The advantages of this approach are that it is very easy to implement, it makes for a very responsive UI (both the swipes and other UI interactions can be immediate 'on touch press' events), and there aren't many traps that you need to program around (in terms of non-obvious ways that the Nextion events trigger and run).

The downside are that it provides a limited set of features, it may not be intuitive to some users that swipes need to start from the edge, and other UI elements can be accidently triggered if swipes start from within the screen borders (or if users swipes 'bounce' while swiping).



## Realtime Swipe and Press Gestures
A more advanced approach is to monitor touch events throughout their duration to process touch movements in realtime and interpret them to decode different types of gestures and trigger actions.
