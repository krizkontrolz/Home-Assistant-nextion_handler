# 3) Subrountines for Fast Approximations of Geometric Functions on Nextion Devices

Often in designing our Nextion UIs we run into situations where we need a common geometric fuction but it is not part of the Nextion Instruction set.  Two of the most common ones are arctans and square roots, that are helpful for processing touch interactions with colour wheels, round sliders or determining pixel distances on screen.  Below are some handy fast integer approximation functions (subroutines) used in the demo HMI file in this folder.  (Nextion 'subroutines' are hidden `Hotspot` components that are called from other event code with the `click` instruction.)  These 'subroutine' are included in the demo HMI in this folder.

**Scaling Integers for fixed-point precison (vs range)**  
Nextions use 32-bit integers for numeric variables and calculations.  To maintain precision during calculations, numbers need to be rescaled (by bit-shifting(<<) or multiplying) during the working stages of calculations to allow some bits to store (fixed-point) fractional parts of values.  Clearly there is a trade-off between precision (the number of least-significant-bits allowed for storing the fractional parts of values) and range (the number of most-significant-bits out of the 31 available (1 bit used for sign) that determine the largest number that can be represented).  To preserve precision, rescaling (by bit-shifting(>>) or dividing) back to the final required integer value should happen as late as possible in the calculation steps.

**Screen (vs Cartesian) coordinates**  
For screen coordinates, y increases DOWNWARDS, unlike the more familiar Cartesian coordinate system (where y inreases UPWARDS along the y-axis).  
It is not necessary to convert touch (screen) coordinates to the Cartesian system during calculations, simply note that the y-axis is reveresed (so the geometry on screen is reflected top-to-bottom).  This has the effect of reversing angles in trigonometric functions: whereas angles increase ANTICLOCKWISE (from zero at 3 o'clock) for Cartesian coordinates, they increase CLOCKWISE (from zero at 3 o'clock) for screen coordinates.

**'Best' approximation functions**  
Multiple approximation algorithms for the same function have co-existed for millenia.  There is no single 'best' approximation for any function.  The choice of approximation depends on balancing compromises for specific applications among accuracy, error distributions across the supported range of the function, speed, resource use, processor capabilities etc.  The options I'm using below are sufficient given the crude input precision on an NSPanel Nextion device (touch interactions on a 320 x 480 screen).  I'm very happy for those who are more knowledgeable than me in this area to suggest better alternatives and improvements.


## ATAN2
The arctan subroutine uses a linear approximation for the first octant (0 —— π/4) and then extends that by symmetry over all other octants (paired into quadrants).  The approach follows 'equation 2' in the set of approximations evaluated [in this paper](https://www-labs.iro.umontreal.ca/~mignotte/IFT2425/Documents/EfficientApproximationArctgFunction.pdf).

One of the advantages of using a linear approximation is that calculation steps can be saved by adjusting multipliers and offsets to return the arctan value directly in a the form that is required in the HMI (with angular, precision, and scaling adjustments already included).  The example below is for how the arctan was used on the [round slider page](/Tips_and_Tricks/ROUND_SLIDERS.md), with the value returned already with the angular offset to start at 0 at the start of the circular slider, scaling up to 9999 a the end of the sliders three-quarter arc (which would give a scaling of 13333 for the full circle).  The two botton octants, which are not part of the slider arc, are coded to return min (0 for octant 3) and max (9999 for octant 2) values. 

<details>
  <summary>Code for `ATAN2` subroutine …</summary>

```
//~~~~~~ boilerplate~~~~ v0.5.00*3 ***DEMO/DEBUG mods
//ATAN2 - fast integer linear approximation by paired quadrants.
//~~~~~~~~~~~~~~~~~~~~~
//Input arguments:
//  dx: current x touch delta from centre of circular slider
//  dy: current y touch delta from centre of circular slider
//Returns:
//  tmp: 0..9999 (across 3/4 arc as noted below)
//
// ArcTan linear approximation (by paired pi/4 (45deg) Octants)
// Using eq2 from: https://www-labs.iro.umontreal.ca/~mignotte/IFT2425/Documents/EfficientApproximationArctgFunction.pdf
// Note: Screen y increases DOWNWARDs so unadjusted angles are CLOCKWISE from 3o'clock
// (vs Cartesian = upwards & anticlockwise).
// Note: Offsets & multipliers below have been pre-adjusted to give
// 0 at 3o'clock +3/4pi (135deg) ... 9999 at 3o'clock + 1/4pi (45deg)
//---------------------------------------------------------------------------------------
//
tmp=0-dy //negative y
if(dx>=tmp)
{
  if(dx>dy)
  {
    //Slice A: Octants 1&8
    tmp=1666*dy/dx-5000
    if(dy>0)
    {
      t6.txt="A-1" //debug display
    }else
    {
      t6.txt="A-8" //debug display
    }
  }else
  {
    //bottom 2 octants (not part of slider)
    if(dx>0)
    {
      //Octant 2 (set to max)
      t6.txt="B-2" //debug display
      tmp=9999 //10000
    }else
    {
      //Octant 3 (set to min)
      t6.txt="B-3" //debug display
      tmp=0
    }
  }
}else
{
  if(dx<dy)
  {
    //Octants 4&5
    tmp=1666*dy/dx+1666
    if(dy>0)
    {
      t6.txt="C-4" //debug display
    }else
    {
      t6.txt="C-5" //debug display
    }
  }else
  {
    //Octants 6&7
    tmp=1667*dx/dy
    tmp=-8334-tmp
    //tmp=0-tmp
    //tmp-=8334
    if(dx<0)
    {
      t6.txt="D-6" //debug display
    }else
    {
      t6.txt="D-7" //debug display
    }
  }
}
if(tmp<0)
{
  tmp+=13333  // 0..9999 for 3/4 arc => full arc is 13333
}else if(tmp>13333)
{
  tmp-=13333
}

```

--- 
  
</details>


## SQRT
The square root subroutine uses [Newton-Raphson](https://en.wikipedia.org/wiki/Newton%27s_method) / [Babylonian / Heron's](https://en.wikipedia.org/wiki/Methods_of_computing_square_roots#Babylonian_method) iterative approximation, adapted from this [Stack Exchange example](https://stackoverflow.com/a/45744558/18837118).

It has been tuned to work well for square roots in the range 10 — 500, typical of what is used for processing Nextion touch interactions, and gives a maximum error of < 2.2% over this range.  It assumes the incoming squared value has already had an effective q<sup>2</sup><<14 bit-shift adjustment to allow 7 (rooted) fixed-point fractional bits for precision.  The iterations converge more slowly if there are rounding errors from lower precision in intermediate calculations.  (Extra iterations can be added to increase accuracy if required).  Final values that use the returned rooted number need to apply a q>>7 bit-shift (to remove the 7 bits of fractional precision used in the intermediate calculations).
  
<details>
  <summary>Code for `SQRT` subroutine …</summary>

```
//~~~~~~ boilerplate~~~~ v0.5.00*3 ***DEMO/DEBUG mods
//SQUARE ROOT - fast integer approximation
//Calibrated for roots in range 10(*2^7)..500(*2^7)) to give max error < 2.2%
//~~~~~~~~~~~~~~~~~~~~~
//Input arguments:
//  tmp: incoming of val to be rooted (WITH precision mult ^2).
//  NB: *** tmp should be multipled by 2^14 beforehand
//  (for better working interger precision & faster convergence).
//Returns:
//  tmp: the rooted value of original tmp (WITH precision mult).
//Scratch variables (altered during calcs): tmp1, tmp2
//
//Newton-Raphson (=Babalonion/Heron) iterative method: https://stackoverflow.com/a/45744558/18837118
//Scratch variables:
//  tmp1(for a: current iterative estimate of root),
//  tmp2(for b = val/a = bracketing estimate).
//Based on the principle that for any arbritary estimate (a),
// the actual sqrt(val) (where 'val' is positive & real) will fall between a and val/a (=b),
// so the arithmetic mean of a & b will be a better estimate (for the next iteration).
//---------------------------------------------------------------------------------------
//
//***Precision multiper of ~128*128 expected to already be applied in the preceding
// calcs in your code for incoming SQUARED values (otherwise, uncomment line below).
//
//tmp=tmp<<14 //multipy by 128 squared
//
if(tmp>595)  //below 595 the starting value gives a better estimate than iterations below
{
  tmp1=9000 //starting guess optimized for roots in range 10(*2^7)..500(*2^7): max error = 2.18%.
  // 10..500 range represents typical screen pixel distances & HA state values.
  //iteration 1: tmp1 converges on root with each iteration
  tmp2=tmp/tmp1  // b = val/a: root falls between a & b
  tmp1+=tmp2     // get mean of a & b as next improved estimate of root (sum & divide by 2)
  tmp1=tmp1>>1
  //iteration 2
  tmp2=tmp/tmp1
  tmp1+=tmp2
  tmp1=tmp1>>1
  //iteration 3
  tmp2=tmp/tmp1
  tmp1+=tmp2
  tmp1=tmp1>>1
  //iteration 4
  tmp2=tmp/tmp1
  tmp1+=tmp2
  tmp1=tmp1>>1
  //Done
  tmp=tmp1  //Returns root of starting tmp value (WITH root of precision multiplier)
}
//***Remove perecision multiper (as previously applied to tmp) from SQRT value AFTER
//it has been used in final calcs in your code (otherwise uncomment line below).
//NB: remove integer precision multipliers as late as possible in your code
// (to maintain precision) (otherise, uncoment line below).
//tmp=tmp>>7  //divide by 128

```

--- 
  
</details>

## COS
The cosine approximation subroutine will be based on the [Bhaskara I approach](https://en.wikipedia.org/wiki/Bhaskara_I%27s_sine_approximation_formula).  

<details>
  <summary>Final code to be added …</summary>

To be added ...

--- 
  
</details>
