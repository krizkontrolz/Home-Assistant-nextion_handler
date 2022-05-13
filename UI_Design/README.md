# User Interface Design for Nextion devices
(_Last updated: 2022-05-13_)

_**... work in progress ...**_

These resources may be helpful for others designing the graphics for their interfaces on small HMI (human-machine interface) screens like Nextions.

The SVG files have full multi-page project examples (a lot more than the thumbnails), have template components that be easily adapted, and use named 'swatches' for easily changing the color scheme off all components.

The UI designs rely on [a robust implementation of 'gestures'](/Tips_and_Tricks), so that touch-interactive components can make full use of the entire small screen area.  The 'Minimilistic Design' is the main theme currently being used, but the two initial Material-based designs are also included.  (The Nextion Editor makes it easy to change the look-and-feel of a UI by swapping out graphics files, especially if you work on fixed grid reference for all components, as the themes below do).

## Design Styles
1) [Material Design](/UI_Design/Material_Bronze) - Dark Bronze theme (to match bronzed buttons and case - used in first HMI).
2) [Material Design](/UI_Design/Material_Neon) - Dark Neon theme (to use, instead of work against, the strong blue cast of Nextion screens - used in second HMI).
3) [Minimilist Design](/UI_Design/Minimalist) - adapted from Yuhang Lu's concept and related adaptations to Home Assistant - see credits below (used in current HMI).

### Design Goal and Principles
The guiding principles and needs that these UI styles aimed to meet were:
* Designed specifically to work well on small, low resolution HMI screens.
* Use modular UI components that fit flexibly and efficiently together to make full use of the limited screen/touch area available.
* UI elements sized/styled so that full details can be easily (without reading glasses) during close-range.
* Key status information is clearly legible from across a room (up to ~10 m, so that alerts can be clearly displayed with motion/presence triggers without the need for physical user interaction).
* Intuitive look, feel and functionality relative to the standard Home Assistant UIs that users are familiar with (within the contraints of the subset of functionality that can be sensibily duplicated on a small display).
* Adapted to work well on imperfect budget HMI displays (tolerant of the screen limitations of the Nextion display such 16-bit color (tends to cause banding across smooth color transitions), washed-out and distorted colors (especially when viewed from an oblique angle, once installed in a wall), inaccurate color rendering (16-bit color with strong blue cast)).

## Resources and Credits

### Material Design
  * [Reference](https://material.io/design)
  * [MDI Icons](https://materialdesignicons.com/)
  * [Google Fonts](https://fonts.google.com/specimen/Roboto+Condensed)

### Minimilist Design
  * [Minimilist Smart Home concept](https://www.behance.net/gallery/88433905/Redesign-Smart-Home) by [Yuhang Lu](https://www.behance.net/7ahang).
  * :sunflower: [Lovelace UI • Minimalist](https://ui-lovelace-minimalist.github.io/UI/) for Home Assistant by [tben](https://community.home-assistant.io/u/tben/summary).
  * 🍄 [Mushroom Cards](https://community.home-assistant.io/t/mushroom-cards-build-a-beautiful-dashboard-easily/388590) for Home Assistant by [piitaya](https://github.com/piitaya).

### Inkscape
(free cross-platform vector graphics editor - for UI SVG graphics in repository)
  * [software](https://inkscape.org/release/)
  * [tutorials](https://inkscape.org/learn/tutorials/)
   
