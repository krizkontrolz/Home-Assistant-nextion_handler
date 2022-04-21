# Gesture Approaches for Nextion Devices (work in progress, incomplete ...)

Gestures are a useful way of adding functionality to your UI while saving space, particularly on small screens like [NSPanels](https://community.home-assistant.io/t/sonoff-nspanel-smart-scene-wall-switch-by-itead-coming-soon-on-kickstarter/332962) and other Nextion devices.   Implementing gestures allows you to reduce the number of graphical UI components by being able to trigger events such as page changes with **'swipes'** or attaching multiple functions to a single button with different types of **'presses'**.  The **demo HMI file in this folder** has examples of 2 ways of implementing gestures in the Nextion Editor.  The demo pages are designed so that you can test and experiment with gestures, inspect and debug realtime information to see how touch data is being generated and used during a gesture, and to illustrate some of the 'traps' (unintended Nextion code behaviour) that you need to be aware of when incorporating robust and reliable gestures into your own HMI projects. 

## Edge-Swipe Gestures
The simplest approach for adding swipe gestures to Nextion devices like NSPanels that have a large surrounding bezel is to use 'edge swipes'.  These are where you swipe from the bezel into the screen to trigger events such as cycling between pages.

Edge swipes are implemented in the Nextion Editor by 'fencing' each edge of the screen with a narrow `hotspot` (raised to the highest surface level) so that they are the first UI component that will be triggered whenever a user swipes from outside the touch-sensitive part of the screen.  You then attach your `swipe` actions to the event code of the hotspots on each edge.

The demo  will highlight each edge green as you swipe into it and **show the distance from the edge at which the swipe was first detected** so that you can calibrate how wide the hotspot needs to be.  On my NSPanels, swipes were consistently triggered within 7 pixels of the edge (~1 mm) and worked relibably with hotspots set to this width.  Note that while you can partly test this in the Nextion Editor simulator mouse swipes from outside the screen area don't register, so it is not a good representation of how the swipes work in practice - they work far better and more intuitively on a physical device.

>> Insert screeshot <<

The **advantages** of this approach are that it is very easy to implement, it makes for a very responsive UI (both the swipes and other UI interactions can be immediate 'on touch press' events), and there aren't many traps that you need to program around (in terms of non-obvious ways that the Nextion events trigger and run).

The **downside** is that it provides a limited set of features, it may not be intuitive to some users that swipes need to start from the bezel, and other UI elements can be accidently triggered if swipes start from within the screen borders (or if users fingers 'bounce' while swiping).



## Realtime Swipe and Press Gestures
A more advanced approach is to monitor touch events throughout their duration to process touch movements in realtime and interpret them to decode different types of gestures and trigger actions.  This is done by continually processing screen touch co-ordinates (`tch0` for x and `tch1` for y) in a rapidly looping (50 ms) timer component.  The timer loop for processing the gestures can either be triggered from the [on touch] event code specific UI components, or using the `Touch Component` (`tc0`) to trigger gesture processing for _all_ touch events on a page.

Some potential traps to be aware of:

* Screen touches will immediately generate 'on touch' events for **BOTH** `tc0` and the intial UI component that is touched.  Having gesture code that is triggered by the 'on touch' event for tc0 (the whole page), will not stop code from also running for the 'on touch' event of that component (which would likely give unintended results for your gestures where both sets of code run) - **SOLUTION:** a) UI components touch events need to be 'release events' not 'on touch' (any interface that uses gestures needs to interpret whether/how the user's finger moves during a touch event before it can determine how to respond). 
* Likewise, a user lifts their finger at the end of a touch interaction, this will generate a 'on release' event for **BOTH** `tc0` and the intial UI component that was touched.  As before, this could give unintended results if both the code for the tc0-linked gesture and the UI component are allowed to run 'on release' - **SOLUTION:** the gesture code should set a `gesture type` when it ends so that 'touch release' events can use this to only avoid unintentionally executing if a swipe or ambiguous gesture started on the the UI component.
* Horizontal/vertical sliders - **SOLUTION:** the gesture code needs to check for slider components and disable itself to allow sliders to be used (without unintenionally trigger other gesture actions too).
* If touch events are disabled for a UI component (with the `tsw` instruction) then the Nextion will not generate any data for **SOLUTION:**  Where possible, use `vis` (hides and disables) instead of `tsw` (disables touch without hiding) to disable/enable UI components, and/or use conditions in UI component touch event code to disable/bypass unintended execution (as in the previous.

The page for realtime swipe & press gestures in the demo HMI file show a roubust approach that deals with all these issues and has been set up with UI components that illustrate some of the traps illustrated above.  You can try out the interactions in the simulator, then read the comments in the code of the buttons that are giving the problems.  The template gesture code in the demo page includes the following:
* `tc0`: test for touches starting on horizontal sliders and skips gesture processing in such cases (and allows for exclusions/alternate gesture processing on other UI components).
* `GESTURE.tim`: pre-release actions (swipes and vlong press); `gest_type` for [on release] events in other UI components; coding includes tests for distinguish button presses from ambiguous gestures (such finger bounces or short movements) to help reduce unintentionally triggering touch events.  (`gest_type` list with encoding - commented in notes at top of template code below) ...
* [on release] events for all other UI elements:  All tests that `gest_type` is a legitamate 'press' event (and can trigger different actions for the different types of presses).

>> add expandable sections with template code for each of above components

>> add screen shot

Add advantages & disadvantages paras...

## More Creative Gestures
To add:
Processing touch events in realtime in fast timer loops provides a powerful engine for more creative ways of interpreting and responding to user touch interactions
The **round slider** (link to md doc) page in the demo HMI shows examples of this, with 2 different approaches to implementing round/circular sliders on Nextion screens.
