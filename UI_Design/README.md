# User Interface Design for Nextion devices
(_Last updated: 2022-05-13_)

These resources may be helpful for others designing the graphics for their interfaces on small HMI (human-machine interface) screens like Nextions.

The SVG files have full multi-page project examples (a lot more than the preview thumbnails show), have template components that be can easily adapted to other projects, and use named 'swatches' for easily changing the color theme off all components.

The UI designs rely on [a robust implementation of 'gestures'](/Tips_and_Tricks), so that touch-interactive components can make full use of the entire small screen area.  The 'Minimilast Design' is the main style that I'm currently using/developing, but the two initial Material-based designs (like the Home Assistant UI uses) are also included.  The Nextion Editor makes it easy to change the look-and-feel of a UI by swapping out graphics files, especially if you work on consistent reference grid for all components, as the themes below do (multiples of 40 px x 40 px).

## Design Styles
* :arrow_forward: [Material Design](/UI_Design/Material_Bronze) - Dark Bronze theme (similar to the Home Assistant UI style).

  This initial design was used to test the constraints of the Nextion display and find color themes that worked best within those constraints (once the designed graphics were moved from a high quality computer display and viewed on the actual NSPanel).  This gives some tips on dealing with the display constraints using a bronzed color theme in this style as an example.  

* :arrow_forward: [Material Design](/UI_Design/Material_Neon) - Dark Neon theme (glowing edges, accentuated by the blue cast).

  This design shows an alternate approach to dealing with the display constraints by accentuating one of its flaws (the strong blue cast) as a feature, rather than trying to minimise it.  In the example files, the blue cast is used to give a strong glowing effect around the edges of graphical elements.
  
* :arrow_forward: [Minimalist Design](/UI_Design/Minimalist) - adapted from Yuhang Lu's concept and related adaptations to Home Assistant (see credits below).

  This clean, minimalist design is still mainly based on Material Design principles but uses thick bars/sliders and adds a flat circle background behind icons (as per Yuhang Lu's concept).  The circle allows extra information to be conveyed, by using combinations of colors for both icons and backgrounds, while adding some understated additional visual appeal.

**Example NSPanel pages using dark-themed Minimalist style.**
![Example dark Minimalist style](/UI_Design/Minimalist/ExampleM_IR_ST_LT_1280x640.png)

### Design Goal and Principles
The guiding principles and needs that these UI styles aimed to meet were:
* :small_blue_diamond: Designed specifically to work well on small, low resolution HMI screens.  
* :small_blue_diamond: Use modular UI components that fit flexibly and efficiently together to make full use of the limited screen/touch area available.
* :small_blue_diamond: UI elements sized/styled so that full details can be easily read (without reading glasses) during use (at close-range).
* :small_blue_diamond: Key status information is clearly legible at long range (from across the room), so that alerts are clearly visible when the display is turned on with presence automations, without the need for physical user interaction.
* :small_blue_diamond: Intuitive look, feel and functionality relative to the standard Home Assistant and other UIs that users are familiar with (within the contraints of the subset of functionality that can be sensibily duplicated on such small displays).
* :small_blue_diamond: Adapted to work well on imperfect budget HMI displays ([tolerant of the screen limitations of the Nextion display](/UI_Design/Material_Bronze#dealing-with-some-of-the-main-constraints-of-the-nextion-display) such 16-bit color (tends to cause banding across smooth color transitions), washed-out and distorted colors (especially when viewed from an oblique angle, once installed in a wall), inaccurate color rendering (16-bit color with strong blue cast)).

## Resources and Credits

### Material Design
  * [Reference](https://material.io/design)
  * [MDI Icons](https://materialdesignicons.com/)
  * [Google Fonts](https://fonts.google.com/specimen/Roboto+Condensed)

### Minimilist Design
  * :white_circle: [Minimalist Smart Home concept](https://www.behance.net/gallery/88433905/Redesign-Smart-Home) by [Yuhang Lu](https://www.behance.net/7ahang).
  * :sunflower: [Lovelace UI • Minimalist](https://ui-lovelace-minimalist.github.io/UI/) for Home Assistant by [tben](https://community.home-assistant.io/u/tben/summary).
  * 🍄 [Mushroom Cards](https://community.home-assistant.io/t/mushroom-cards-build-a-beautiful-dashboard-easily/388590) for Home Assistant by [piitaya](https://github.com/piitaya).

### Inkscape
(free cross-platform vector graphics editor - for UI SVG graphics in repository)
  * [software](https://inkscape.org/release/)
  * [tutorials](https://inkscape.org/learn/tutorials/)
   
