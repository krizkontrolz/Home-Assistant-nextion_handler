# 1) Gesture Approaches for Nextion Devices

Gestures are a useful way of adding functionality to your UI while saving space, particularly on small screens like [NSPanels](https://community.home-assistant.io/t/sonoff-nspanel-smart-scene-wall-switch-by-itead-coming-soon-on-kickstarter/332962) (which uses a  [Nextion Discovery Series 3.5″ NX4832F035 display](https://itead.cc/product/nx4832f035-nextion-3-5-discovery-series-hmi-touch-display/)) and other Nextion devices.   Implementing gestures allows you to reduce the number of graphical UI components by being able to trigger events such as page changes with **'swipes'** or attaching multiple functions to a single button with different types of **'presses'** (adding extra user functionality without the need for more buttons).  The **demo HMI file in this folder** has examples of two ways of implementing gestures in the Nextion Editor.  The demo pages are designed so that you can test and experiment with gestures, inspect and debug realtime information to see how touch data is being generated and used _during_ a gesture, and to illustrate some of the 'traps' (unintended Nextion code behaviour) that you need to be aware of when incorporating robust and reliable gestures into your own HMI projects. 

## Edge-Swipe Gestures
The simplest approach for adding swipe gestures to Nextion devices like NSPanels that have a large surrounding bezel is to use 'edge swipes'.  These are where you swipe from the (non-touch) bezel into the (touch) screen area to trigger actions such as cycling between pages.

Edge swipes are implemented in the Nextion Editor by 'fencing' each edge of the screen with a narrow `Hotspot` (raised to the highest surface level) so that they are the first UI component that will be triggered whenever a user swipes from outside the touch-sensitive part of the screen.  You then attach your `swipe` actions to the event code of the hotspots on each edge.

The demo page will highlight each edge green as you swipe into it and **show the distance from the edge at which the swipe was first detected** so that you can calibrate how wide the hotspot needs to be.  On my NSPanels, swipes were consistently triggered within 7 pixels of the edge (~1 mm: the width of the visual feedback green bars is greatly exagerated for clarity) and worked relibably with hotspots set to this width.  Note that while you can partly test this in the Nextion Editor simulator, mouse swipes from outside the screen area don't register, so it is not a good representation of how the swipes work in practice - they work far better and more intuitive on a physical device.

![Edge swipe demo page](/Tips_and_Tricks/images/GESTURE_edge-swipe.png)

:heavy_plus_sign: The **advantages** of this approach are that it is very easy to implement, it makes for a very responsive UI (both the swipes and other UI interactions can be immediate [Touch Press Event]s), and there aren't many traps that you need to program around (in terms of non-obvious ways that the Nextion events trigger and run).

:heavy_minus_sign: The **downside** is that it provides a limited set of features, it may not be intuitive to some users that swipes need to start from the bezel, and other UI elements can be accidently triggered if swipes start from within the screen borders (or if users fingers 'bounce' while swiping).



## Realtime Swipe and Press Gestures
A more advanced approach is to monitor touch events throughout their duration by interpretting touch movements in real time to classify different types of gestures and trigger actions.  This is done by continuously processing screen touch coordinates ([`tch0`, `tch1`] for realtime [`x`, `y`] while a touch event is active) in a rapidly looping (50 ms) timer component.  The timer loop for processing the gestures can either be triggered from the [Touch Release Event] code for specific UI components, or using the `TouchCap` component (`tc0`) to trigger gesture processing for _all_ touch events on a page.

Some **potential traps to be aware of**:
<details>
  <summary>expand …</summary>

* Screen touches will immediately generate [Touch Press Event]s for **BOTH** `tc0` and the intial UI component that is touched (_before_ `tc0` has a chance to gain exclusive control).  Having gesture code that is triggered by the [Touch Press Event] for `tc0` (the whole page), will not stop code from also running for the [Touch Press Event] of that component, which would likely give unintended results for your gestures where both sets of event code are triggered.  
✅ _**SOLUTION:**_ The code you attach to UI components needs to be assigned to their [Touch Release Event]s not [Touch Press Event]s. 
* Likewise, when a user lifts their finger at the end of a touch interaction, this will generate a [Touch Release Event] for **BOTH** `tc0` and the intial UI component that was touched.  As before, this could give unintended results if both the code for the `tc0`-linked gesture and the UI component are allowed to be triggered from the same user input.  
✅ _**SOLUTION:**_ the gesture code should set a `gesture type` when it ends that [Touch Release Event]s can use in a test condition to only execute their code on designated 'gesture types' (while avoiding running if a 'swipe' gesture is already triggering another action or if the touch interaction is too ambiguous to be reliably interpreted).
* Swipe Gestures can potentially have conflicts with the use of horizontal/vertical sliders.  
✅ _**SOLUTION:**_ The gesture code needs to check whether the touch event started on a slider component and, if so, disable itself so that sliders have exclusive control of these touch interactions.  This avoids unintenionally triggering both swipe and slider actions from the same touch interaction.  To accomplish this, test the condition `if(b[tc0.val].type==1)`, where `tc0.val` stores the `id` of the component that the touch event started on, `b[...]` gives the `type` of that component, and sliders have a component `type` of 1.
* If touch events are disabled for a UI component (with the `tsw` instruction) then the Nextion will not generate _any_ data for touch events that start on that component - so `tc0` will also be 'blind' to such touches and unable to respond.   
✅ _**SOLUTION:**_  Instead of using `tsw` (disables touch without hiding) to disable/enable UI components, either use `vis` (hides and disables), or use conditions in UI component touch event code to disable/bypass unintended execution (such as using the gesture type that the gesture interpreter code produces).

--- 
  
</details>
  
  
  
The demo page for realtime swipe & press gestures shows a roubust approach that deals with all these issues and has been set up with UI components to illustrate the way some of the traps listed above can interfere with your gesture-related code.  You can try out the interactions in the simulator, then read the comments in the event code of the buttons that are giving the problems.  The template gesture code in the demo page includes the following:

<details>
  <summary>expand …</summary>

* :arrow_forward: `tc0`: The `TouchCap` [Touch Press Event] code tests for touches starting on horizontal sliders and skips gesture processing in such cases. (Additional exclusions can be made where alternate gesture processing is required, such as in the more advanced [Round slider gesture example](/Tips_and_Tricks/ROUND_SLIDERS.md).)
* :arrow_forward: `GESTURE.tim`: The `Timer` component that does the gesture processing allows gestures to trigger actions in two ways: gestures that trigger once a condition is met during the touch event _before_ it is complete (swipe and very-long-press gestures), and by generating a `gest_type` code that can be used _after_ the touch event is complete as part of a condition to modify what the code in [Touch Release Event]s does.  The code for `GESTURE.tim` is shown below.
* :arrow_forward: `gest_type` coding: The comment at the top of the code below lists the different `gest_type` values that `GESTURE.tim` returns.  This includes a `gest_type` of "0" where some movement is detected, but not enough to trigger a 'swipe' action.  Using `gest_type` in event code allows inadvertent/ambiguous user touches to be filtered out, for legitimate button 'presses' to be distinguished by the condition `if(gest_type>90)`, and then the type of press (short, long, and very-long) can be used to modify what actions are performed.

--- 
  
</details>

![Swipe and Press Gestures demo page](/Tips_and_Tricks/images/GESTURE_swipe_and_press.png)

[Timer Event] code used to interpret gestures in realtime in `GESTURE.tim`:

<details>
  <summary>expand …</summary>

```
//~~~~~~ boilerplate~~~~ v0.5.05 (Main pages swipe cycling)
// GESTURE intpreter (press duration & swipes) (timer).
//~~~~~~~~~~~~~~~~~~~~~
//*** CUSTOMIZE immediate (before realease) actions below for each page ***
// Works with tc0 to continually poll gesture x,y,distance,duration
// while a touch gesture is occurring (BEFORE Touch Release Event).
// Gestures are decoded below 'live' and can be used to either:
//  * execute an immediate action (before Touch Release Events), or
//  * use `gest_type` as a condition/modifier in Touch Release Events.
//---------------------
//GESTURE list (returned in `gest_type` Global variable):
//  -1: excluded UI component - sliders (+ custom***)
//   0: invalid gesture (movement, but too short for swipe)
//   1: right swipe
//   2: left swipe
//   3: down swipe
//   4: up swipe
//  91: short press (>90 => Press without x,y movement)
//  92: long press
//  93: very long press
//---------------------
//
if(tch0>0)  //Skip last timer cycle where stroke ends (tch0=0) BEFORE tc0 stops this timer.
{
  //
  // Monitor duration of gesture (using count of cycles of this timer)
  gest_time++
  //
  // Monitor distance of gesture movement (in pixels squared)
  dx=tch0-tch2
  dy=tch1-tch3
  dsq=dx*dx
  tmp=dy*dy
  dsq+=tmp  // easier to work with square of distance - no need to sqrt
  //
  //
  // Gesture interpretation
  gest_type=0  // not a valid gesture (yet)
  // Movement < 10px => PRESS(click) component
  if(dsq<100)
  {
    if(gest_time<10)
    {
      // o
      gest_type=91 // short press
    }else if(gest_time<30)
    {
      // oo
      gest_type=92 // long press
    }else
    {
      // ooo
      gest_type=93 // vlong press
      //page 0  // <- CUSTOM*** live action here
    }
  }
  //
  // Movement > 100px => SWIPE
  if(dsq>10000)
  {
    if(dx>100)
    {
      //>>
      gest_type=1 // right
      //page 0  // <- CUSTOM*** live action here
      // cycle through 'Main' pages (0..page_max)
      tmp=dp-1
      if(tmp<0)
      {
        tmp=page_max
      }
      page tmp
    }else if(dx<-100)
    {
      //<<
      gest_type=2 // left
      //page 0  // <- CUSTOM*** live action here
      // cycle through 'Main' pages (0..page_max)
      tmp=dp+1
      if(tmp>page_max)
      {
        tmp=0
      }
      page tmp
    }else if(dy>100)
    {
      //vv
      gest_type=3 // down
      //page 0  // <- CUSTOM*** live action here
      page CFG // configure settings
    }else if(dy<-100)
    {
      //^^
      gest_type=4 // up
      //page 0  // <- CUSTOM*** live action here
      loop_cnt=sleep_cnt+1 // force 1 fast data refresh
      UPDATE_LOOP.tim=50
    }
  }
}


```

--- 
  
</details>

                      
:heavy_plus_sign: The **advantage** of realtime gesture processing is it that opens more powerful opportunities for interpreting gestures, and for getting these to work in a more intuitive way for users (matching more closely how most other touch screen devices work).

:heavy_minus_sign: The main **downside** is that coding is more complicated (it's a bit more of learning curve initially), particularly making sure that you are coding around all the quirky issues noted above (to avoid touch events unintentionally triggering or not triggering code from other UI components).

## More Creative Gestures
Processing touch events in realtime in fast timer loops provides a powerful engine for more creative ways of interpreting and responding to user touch interactions.  
The [Round slider](/Tips_and_Tricks/ROUND_SLIDERS.md) page in the demo HMI shows more advanced examples of realtime gesture processing, with two different approaches to implementing round/circular sliders on Nextion screens.
