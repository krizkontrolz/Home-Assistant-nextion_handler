# 2) Dynamic Round Sliders on Nextion Devices (documentation in progress ...)

The [first tips and tricks page](/Tips_and_Tricks/NEXTION_GESTURES.md) showed different ways of implementing gestures on Nextion devices, and the realtime touch information on the 'swipe and press' gestures page started to give some idea of the opportunities for being more creative in using that data during data events.

Here, as an examples to illustrate some of that potential, are two implementations of a **round/circular slider** that use that information in different ways.
Both examples are included on a single page in the demo HMI file in this folder, and you press the button next to the slider to toggle between the different `Timer`s used to process the gestures.  The 'swipe and press' gestures from the the previous page are also implemented on the circular sliders page (so `tc0` selects which gesture processor to use based on which UI component is initially touched).  You can get a good feeling for how these sliders work by using the HMI file in the Nextion Editor simulator.  The main differences when using this on a physical device are: 1) the slider might be a bit small for your use case (although you can get very fine control by using the whole screen once you have started the round slider - you don't have to keep your finger on the visible arc); 2) there will be some screen flicker on the physical device and you need to take some steps to reduce this (to demonstrate this the first 'progressive arc' approach described below only updates UI elements when a step change in value occurs, while 'moving dot' implementation updates whever touch movement is detected).

## Progressive arc slider (xpic, ATAN2)

![Edge swipe demo page](/Tips_and_Tricks/images/ROUND-SLIDER_Progressive-Anim.gif)

## Moving dot slider (cirs, ATAN2, SQRT)

![Edge swipe demo page](/Tips_and_Tricks/images/ROUND-SLIDER_Moving-Dot-Anim.gif)
