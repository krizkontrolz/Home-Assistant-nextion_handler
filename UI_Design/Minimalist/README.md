# Minimalist Design
(_Last updated: 2022-05-13_)

**_work in progress_**

This is the current UI design that I'm using on my NSPanels.  It is also the one that is easiest for others to use as template because it has been set up with:
* 🔹 Well structured and named object hiearchy (dock the 'Objects' tool to the first side bar and use it as the main method for selecting groups/items to edit.  This is especially important for where in the hiearchy you copy from (the whole group from that level down will be copied) and where in the hiearchy you paste to (it will be inserted above the selected item)).
* 🔹 A selection of common UI component templates, all built on a base of 40x40 px block multiples to easily snap to a 40x40 grid (to cleanly fit together a 320x480 NSPanel display).
* 🔹 A palette of named swatch colors (to easily change and tweak color themes across the project).


**Screenshot in Inkscape showing elements organised with named hierarchical grouping**.  Flexible turning on/off visibility of individual graphical elements within components allows them to be easily adapted for multiple UI functions.

![Inkscape screenshot of hiearachical organization](/UI_Design/Minimalist/InkScape_Object-Grouping-Hierarchy.png)

## Anatomy of a UI Card
A precise set of parametric rules define how UI components are constructed (although these are applied with the pragmatic Pythonic maxim,   _"A foolish consistency is the hobgoblin of little minds..." (Emerson)_.)  The rules are described sequentially for each element below, from the base layer upwards, noting that each individual UI component would ultimately only use a subset of these elements (and would hide the rest).

### 🔸 EXTENT (structural foundation):
_The base foundation is a transparent rectangle that is a multiple of 20 x 20 px blocks (snapped to 20x20 grid)._

It sets the outer bounds of the component, ensures that all components will snap together, and maintains the reference for offsets by which each constituent element floats away from grid edges.  For a typical single entity card, with label, (like the `Garage` light example above) this would be 80px x 120px.

### 🔸 shadow (beneath card):
_Offsets from the EXTENT: top = 3px, sides = 4px, bottom = 3px. Rectangle rounding radius (of corners) = 11px._

No blurring is applied. (Sharp shadows look cleaner on a low-resolution display.  If blurring is applied, then a 'clip mask' will be needed to keep the blurring with the bounds of EXTENT, otherwise snapping and page boundaries will be compromised).

### 🔸 card (visible base):
_Offsets from the EXTENT: top = 3px, sides = 5px, bottom = 5px. Rectangle rounding radius = 10px._

...

### 🔸 circle (icon background, full size):
_Circle radius = 30px. Offsets from the EXTENT: top = 10px, sides = 10px. (Centre snapped to 20x20 grid.)_

...

### 🔸 icon (full size):
... 250% scaling of MDI icons fits in 30px radius circle.

### 🔸 labels:
_16pt Robotto Condensed. 15px below bottom of circle, centred. (Offset from EXTENT: bottom = 35px.)_  
(Secondary labels, such as units of measure: _14 pt Robotto Condensed_.)

### 🔸 bar (sliders and background for dynamic text)
_Rectangle height 28px, rounding radius 7px. Offsets from the EXTENT: top = 10px, sides = 10px. Circle radius = 30px. (Centre snaps to 20x20 grid.)_

... wide horizontal (full / half width)  (sizes of card, circ & icon for interactive & static icons)

### 🔸 button (modified bar)
_Variant of `bar` with rounding radius = 14px (so that rounding diameter = height = 28px to form semi-circluar end caps)._

The card behind a single row of buttons also has semi-circular end caps, with diameter = height, such that _card radius = 16px, shadow radius = 17px_.
Circ & icon sizes.

### 🔸 wallpaper (background)
_Master wallpaper covering full display (320px x 480px) CLONED for each page._

... master, cloned  (EU NSP template)

## Color Conventions
Consistently following a set of conventions for how UI elements are colored makes it much easier to interpret dense information on the display at a glance.

### States and Interaction
* 🔹 A `colored icon` indicates that it is `interactive` (it will trigger an action when touched), whereas grey-scale icons provide information that is not directly interactive (such as sensor information).
* 🔹 A `colored background` indicates that information for that entity is in an `active` state (it is 'on', the value exceeds a threshold, or it matches some criteria, such as tracker location matching "Home"), whereas a grey-scale background indicates that is in its non-active state.

### Icon and Background Colors (part of named 'swatch' palette)
* 🔹 Five colors are used to indicates states and interactive elements: orange, red, purple, blue, green (following [Lovelace Minimalist UI](https://ui-lovelace-minimalist.github.io/UI/) and [Mushroom Cards](https://community.home-assistant.io/t/mushroom-cards-build-a-beautiful-dashboard-easily/388590)).
* 🔹 Three variants are used for each color (ranked from brightest to darkest): Active_Icon (used when an interactive icon is in its active state, and blended into the grey background with transparency when in its inactive state); Active_Background (applied to an icon background when in its active state; also applied to the interactive state of other elements such as slider bars); and Dim (used for the slider background, the background of dynamic text).

### Example icon types coloring:
* 🔹 For an interactive icon (e.g. `Garage` light above): Active state (Active_Icon icon color on Active_Background background); Inactive state(Active_Icon semi-transparent icon on inactive grey background)
* 🔹 For an non-interactive icon (e.g. `Front` door contact sensor above): Active state (inactive grery icon color on Active_Background background); Inactive state(inactive grey semi-transparent icon on inactive grey background).
* 🔹 For static information icon (e.g. the temperature icon for above the `light color temperature` slider above): Enabled state (white icon on inactive grey background); Disabled state (dark disabled grey icon on inactive grey background).

### Buttons
...

## Variants and Editing
... 

### Resizing
... don't just resize whole object - resize each element invidually maintaining offsets above. (Extent, then shadow, then card: Adjust Rect height and width in multiples of 40px - offset from original will be maintained and keep everything correct).

### Grouped Cards
... (same card) - start with component for single entity/button; expand EXTENT, shadow and card (as for resizing); then duplicate the required elements (such as circle and icon) and align to where they would be positioned if in a separate adjacent component.  e.g. Bedroom card for 4 entities.

### Editing Tips
Side bar setup with docked tools...
Use 'Objects' hieararchy (rather than ungrouping then regrouping) to select, copy/duplicate and paste...
Parametric editing.... (transform to move, rectangle to resize)
Mouse quick selection: Select (objects) vs Node (elements) (and Rectangle, Text etc. when editing objects of those types).

_For credits and resources see main UI page_

