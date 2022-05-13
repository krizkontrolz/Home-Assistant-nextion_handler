# Material Design - Bronze theme

(_Last updated: 2022-05-13_)

This was the first UI for my own NSPanels.  The main aim was to replicate the familiar look and feel of the Home Assistant UI (Material Design), and try out a range of color 'themes' within that to match my Home Assistant UI themes and explore the type of themes that worked best on the NSPanel.

## Dealing with some of the main constraints of the Nextion display:

* ⛔ when mounted in a wall the display is viewed from an **oblique angle from above, which washes out colors and distorts hues and contrast**.  This effect is made worse on the US NSPanel by the Nextion screen being installed upside down (when the device is in its natural portrait orientation, with the buttons below) - pale/whitish color themes are so washed out and reduced in contrast that they are almost unusable in this orientation (although they can look very nice when viewed 'from below'.)

  ✅ **Dark color themes** greatly mitigate this problem (and are a better overall fit since it is less distracting when the screen turns on, e.g. when triggered as you walk past by a presence detection automation).
  
* ⛔ files are converted to a compressed 16-bit format for storage on the Nextion which can futher distort colors and create other **artefacts such as banding of smooth gradients** (you can dither the input graphics files to offset this problem visually, but at the expense of larger stored files).

  ✅ **'Flat' design systems**, such the Material Design framework, help mitigate these problems.
  
* ⛔ a **strong blue cast** that markedly changes the appearance of colors realtive to what they look like when creating them (on a PC monitor).

  ✅ **Shifting hues towards yellow** can help a bit (although the colors will look a bit off while viewing on a normal screen).
  
  
**Example color theme for Material-based UI applying the above principles:** dark (to avoid washed out colors); flat (to avoid banding and reduce the effects of 16-bit color distortions); bronzed color (to deal with the blue cast of the screen - on the actual NSPanel the colors match the bronzed case and look quite a bit different to what they do viewing on a typical computur/phone display.)

![Screenshot exampe](/UI_Design/Material_Bronze/NextionHandler_Usage_Example.gif)
