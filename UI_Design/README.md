# User Interface Design for HMI devices
(_Last updated: 2022-05-31_)

These resources may be helpful for others designing the graphics for their interfaces on small HMI (human-machine interface) displays like Nextions.

The SVG files have full multi-page project examples (a lot more than the preview thumbnails show), have template components that be can easily adapted to other projects, and use named 'swatches' for easily changing the color theme across all components in the project.

The UI designs rely on [a robust implementation of 'gestures'](/Tips_and_Tricks), so that touch-interactive components can make full use of the entire small screen area.  The 'Minimilast Design' is the main style that I'm currently using/developing, but the two initial Material-based designs (like the Home Assistant UI uses) are also included.  The Nextion Editor makes it easy to change the look-and-feel of a UI by swapping out graphics files, especially if you work on a consistent reference grid for all components, as the themes below do (multiples of 40 px x 40 px).

## Design Styles
* ▶️ [Material Design](/UI_Design/Material_Bronze) - Dark Bronze theme (similar to the Home Assistant UI style).  
This initial design was used to test the constraints of the Nextion display and find color themes that worked best within those constraints (once the designed graphics were moved from a high quality computer display and viewed on the actual NSPanel).  This page gives some tips on dealing with the display constraints using a bronzed color theme in this style as an example.  

* ▶️ ['Neon' Material Design](/UI_Design/Material_Neon) - Dark Neon theme (glowing edges, accentuated by the blue cast).  
This design shows an alternate approach to dealing with the display constraints by accentuating some of its flaws (strong blue cast and exagerated contrast) as a feature, rather than trying to minimise it.  In the example files, the blue cast and high contrast (when viewed from an oblique angle) is used to give a strong glowing effect around the edges of graphical elements.
  
* ▶️ [Minimalist Design](/UI_Design/Minimalist) - inspired by Yuhang Lu's concept and related adaptations to Home Assistant (see credits below).&nbsp;&nbsp;This clean, minimalist design is still mainly based on Material Design principles but uses thick bars/sliders and adds a flat circle background behind icons (as per Yuhang Lu's concept).  The circle allows extra information to be conveyed, by using combinations of colors for both icons and backgrounds, while adding some understated additional visual appeal.  Detailed design rules are documented in this folder together with a template SVG and other project example files.  The color themes and styles take their cues from [🌻tben's](https://ui-lovelace-minimalist.github.io/UI/) and [🍄piitaya's](https://community.home-assistant.io/t/mushroom-cards-build-a-beautiful-dashboard-easily/388590) popular Home Assistant UIs, but adapted to render well on an NSPanel ([and deal with its distortions](/UI_Design/Material_Bronze#dealing-with-some-of-the-main-constraints-of-the-nextion-display)).

**Example NSPanel pages using dark-themed Minimalist style.**
![Example dark Minimalist style](/UI_Design/Minimalist/ExampleM_IR_ST_LT_1280x640.png)


## Design Goal and Principles
The guiding principles and design requirements that these UI styles aimed to meet were:
* 🔹 Designed specifically to work well on small, low resolution HMI screens.  
* 🔹 Use modular UI components that fit flexibly and efficiently together to make full use of the limited screen/touch area available (snapping together like Tetris pieces to completely fill the available screen area).
* 🔹 UI elements sized/styled so that full details can be easily read (without reading glasses) during use (at close-range).
* 🔹 Key status information is clear at a glance from long range (across the room), so that entity states are obvious when the displays are flashed up in response to presence automations (without any need for direct user interaction).
* 🔹 Intuitive look, feel and functionality relative to the standard Home Assistant and other UIs that users are familiar with (within the contraints of the subset of functionality that can be sensibily duplicated on such small displays).
* 🔹 Make the most frequently-used controls and information easier to access than the standard Home Assistant interface, such as by reducing the number of user touch interactions required to perform an action.
* 🔹 Adapted to work well on imperfect HMI displays ([tolerant of the screen limitations of the Nextion display](/UI_Design/Material_Bronze#dealing-with-some-of-the-main-constraints-of-the-nextion-display) such 16-bit color (tends to cause banding across smooth color transitions), washed-out and distorted colors (especially when viewed from an oblique angle, when mounted in a wall), inaccurate color rendering (16-bit color with strong blue cast)).


## Basics of Nextion Editor Graphical UI

🔸 **The standard approach** for making graphical elements respond to user interactions (or data states) in the Nextion Editor is to prepare **two full images for each page:**
* 1️⃣ A primary background image, which will serve as the default background for the page (typically with all responsive graphical elements in their inactive state).
* 2️⃣ A secondary 'crop' image, from which rectangles will be cropped to override components with an alternate visual state (in the same display location) either automatically (as part the inbuilt function of some Nextion components) or through the HMI code you write to respond to user inputs and changes in data states.

The details are covered well in one of [Scargill's Tech Blogs here](https://tech.scargill.net/nextion-wifi-touch-display/).

🔸 **The main alternative approach** is to **dynamically compose the display in realtime** using graphical elements stored on the Nextion and sending Nextion Instructions that determine when and where the different elements are displayed.  The stock NSPanel firmware uses this approach, and the rendering rules can be offloaded to the ESP32 or another device.  This is better suited to generic 'adaptable' UIs that allow simpler, but limited, configuration of pre-defined Nextion UI components.  **The simplified [Widget UI](/widget_ui) uses this approach** by using special precompiled HMI templates to provide an extremely easy way to get started on integrating NSPanels into Home Assistant and only requires very basic configuration (providing a list of entities, each with a few optional customisation settings), and offloads most of the adaptable display rendering to the [Nextion Handler](/HA_NEXTION_HANDLER_INSTRUCTIONS.md) Python script.  


## Resources and Credits

### Material Design
  * [Reference](https://material.io/design)
  * [MDI Icons](https://materialdesignicons.com/)
  * [Google Fonts](https://fonts.google.com/specimen/Roboto+Condensed)

### Minimalist Design
  * ⚪ [Minimalist Smart Home concept](https://www.behance.net/gallery/88433905/Redesign-Smart-Home) by [Yuhang Lu](https://www.behance.net/7ahang).
  * 🌻 [Lovelace UI • Minimalist](https://ui-lovelace-minimalist.github.io/UI/) for Home Assistant by [tben](https://community.home-assistant.io/u/tben/summary).
  * 🍄 [Mushroom Cards](https://community.home-assistant.io/t/mushroom-cards-build-a-beautiful-dashboard-easily/388590) for Home Assistant by [piitaya](https://github.com/piitaya).

### Inkscape
(Free cross-platform vector graphics editor - for UI SVG graphics in repository.)
  * [software](https://inkscape.org/release/)
  * [tutorials](https://inkscape.org/learn/tutorials/)
   
