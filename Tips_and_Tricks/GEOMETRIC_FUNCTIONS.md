# Subrountines for Fast Approximations of Geometric Functions on Nextion Devices

Often in designing our Nextion UIs we run into situations where we need a common geometric fuction but it is not part of the Nextion Instruction set.  Two of the most common ones are arctans and square roots, that are helpful for processing interactions with colour wheels, round sliders or determining pixel distances for touch events.  Below are some handy fast integer approximation functions (sub routines) used in the demo HMI file in this folder.  (Nextion 'subroutines' are hidden `Hotspot` components that are called from other event code with the `click` instruction.)

**Integer precison (vs scale)**
Add...
Note about integer precison (at expense of scale scale) and multiplying/bit-shifting(<<) to keep intermediate working calculations making full use of as much possible of the Nextion integers 32 bits for as long as possible (only dividing/bit-shifting(>>) back again when final values are needed). 

## ATAN2 (Linear approximation, by paired quadrants)
Description of approach

Explantion of template page info (and paired quadrants)
>> expandable code example


## SQRT (Newton-Raphson / Babylonian / Heron iterative approximation)
Description of approach

>> expandable code example

