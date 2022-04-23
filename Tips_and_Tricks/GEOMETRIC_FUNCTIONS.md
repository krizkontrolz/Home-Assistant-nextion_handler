# 3) Subrountines for Fast Approximations of Geometric Functions on Nextion Devices (documentation in progress ...)

Often in designing our Nextion UIs we run into situations where we need a common geometric fuction but it is not part of the Nextion Instruction set.  Two of the most common ones are arctans and square roots, that are helpful for processing touch interactions with colour wheels, round sliders or determining pixel distances on screen.  Below are some handy fast integer approximation functions (subroutines) used in the demo HMI file in this folder.  (Nextion 'subroutines' are hidden `Hotspot` components that are called from other event code with the `click` instruction.)  These 'subroutine' are included in the demo HMI in this folder.

**Scaling Integers for fixed-point precison (vs range)**  
Nextions use 32-bit integers for numeric variables and calculations.  To maintain precision during calculations, numbers need to be rescaled (by bit-shifting(<<) or multiplying) during the working stages of calculations to allow some bits to store (fixed-point) fractional parts of values.  Clearly there is a trade-off between precision (the number of least-significant-bits allowed for storing the fractional parts of values) and range (the number of most-significant-bits out of the 31 available (1 bit used for sign) that determine the largest number that can be represented).  To preserve precision, rescaling (by bit-shifting(>>) or dividing) back to the final required integer value should happen as late as possible in the calculation steps.

**Screen (vs Cartesian) coordinates**  
For screen coordinates, y increases DOWNWARDS, unlike the more familiar Cartesian coordinate system (where y inreases UPWARDS along the y-axis).  
It is not necessary to convert touch (screen) coordinates to the Cartesian system during calculations, simply note that the y-axis is reveresed (so the geometry on screen is reflected top-to-bottom).  This has the effect of reversing angles in trigonometric functions: whereas angles increase ANTICLOCKWISE (from zero at 3 o'clock) for Cartesian coordinates, they increase CLOCKWISE (from zero at 3 o'clock) for screen coordinates.

**'Best' approximation functions**  
Multiple approximation algorithms for the same function have co-existed for millenia.  There is no single 'best' approximation for any function.  The choice of approximation depends on balancing compromises for specific applications among accuracy, error distributions across the supported range of the function, speed, resource use, processor capabilities etc.  The options I'm using below are sufficient given the crude input precision on an NSPanel Nextion device (touch interactions on a 320 x 480 screen).  I'm very happy for those who are more knowledgeable than me in this area to suggest better alternatives and improvements.


## ATAN2
(Linear approximation, by paired quadrants)
Description of approach

Explantion of template page info (and paired quadrants)
>> expandable code example


## SQRT
(Newton-Raphson / Babylonian / Heron iterative approximation)
Description of approach

>> expandable code example

## COS (based on Bhaskara I)
Description of [approach](https://en.wikipedia.org/wiki/Bhaskara_I%27s_sine_approximation_formula)

>> expandable code example
