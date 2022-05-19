# Minimalist Design
(_Last updated: 2022-05-19_)

**_documentation still in progress_**

This is the current UI design that I'm using on my NSPanels.  It is also the one that is easiest for others to use as a template because the vector graphics (SVG) have been set up with:
* 🔹 well structured and named object hiearchy (dock the 'Objects' tool to the Inkscape side bar to navigate);
* 🔹 UI components that are all built on a base of 40x40 px block multiples so that they cleanly snap together to fill a 320x480 NSPanel display;
* 🔹 a palette of named swatch colors (to easily change and tweak color themes across an entire project);
* 🔹 a well-defined set of composition rules (documented below), making it easy to use and customize UI 'cards' that have a coherent style and can convey dense information in an efficient and consistent manner.

🎉 Anyone, with a little planning and patience, can create stunningly beautiful UIs that are highly customised to their specific needs (without requiring much creative ability) by using this approach.


**Screenshot in Inkscape showing elements organised with named hierarchical grouping**.  Flexibly turning the visibility of individual graphical elements on/off within components allows them to be easily adapted for multiple UI functions.

![Inkscape screenshot of hiearachical organization](/UI_Design/Minimalist/InkScape_Object-Grouping-Hierarchy.png)

## Anatomy of a UI Card
A precise set of parametric rules define how UI components are constructed (although these are applied with the pragmatic Pythonic maxim,   _"A foolish consistency is the hobgoblin of little minds..." (Emerson)_.)  The rules are described sequentially for each element below, from the base layer upwards, noting that each individual UI card would ultimately only use a subset of these elements (and would hide the rest).  

<details>
  <summary>▶️ more ...</summary>


#### 🔸 EXTENT (structural foundation):
_The base foundation is a transparent rectangle that is a multiple of 20 x 20 px blocks (snapped to 20x20 grid)._  
The `EXTENT` sets the outer bounds of the component, ensures that all components will snap together cleanly, and maintains the reference for offsets by which each constituent element floats away from grid edges.  For a typical single entity card, with label, (like the `Garage` light example above) this would be 80px x 120px.

#### 🔸 shadow (beneath card):
_Offsets from the `EXTENT`: top = 3px, sides = 4px, bottom = 3px. Rectangle rounding radius (of corners) = 11px._  
No blurring is applied. (Sharp `shadow`s look cleaner on a low-resolution display.  If blurring is applied, then a 'clip mask' will be needed to keep the blurring with the bounds of EXTENT, otherwise snapping and page boundaries will be compromised).

#### 🔸 card (visible base):
_Offsets from the `EXTENT`: top = 3px, sides = 5px, bottom = 5px. Rectangle rounding radius = 10px._  
The `card` is the visible base on which all other elements are laid.  The `card` casts a `shadow` onto the background `wallpaper`.

#### 🔸 circle (icon background, full size):
_`Circle` radius = 30px. Offsets from the `EXTENT`: top = 10px, sides = 10px. (Centre snapped to 20x20 grid.)_  
`Circle`s are used as the background to `icon`s and convey the state and function of the entity associated with each card more clearly.

#### 🔸 icon (full size):
_Material Design Icon SVGs with 250% scaling fit in 30px radius background `circle`._  
Color conventions for `icon`s and background `circle`s are detailed futher down.

#### 🔸 bar (horizontal sliders and background for dynamic text):
_Rectangle height 28px, rounding radius 7px. Offsets from the `EXTENT`: top = ##px, bottom = ##px._  
Horizontal `bar`s typically require wider cards where they are used as sliders or as background for text that dynamically updates with changes to states/attributes.
An `icon` (with `circle` background) may be associated with a bar to indicate its function (following the color conventions below).

**'Interactive' `icon`s:** _`Circle` radius = ##px, with MDI `icon`s scaled to match (~##%), `EXTENT` height = ##px_  
  `Icon`s that are used to trigger an action when pressed (interactive), need to be large enough for reliable touch interactions.
  
**'Static' `icon`s:** _`Circle` radius = ##px, with MDI `icon`s scaled to match (~##%), `EXTENT` height = ##px_  
  `Icon`s that are only used to indicate the function of a bar (static), can to be smaller because they are not used for touch interactions.

#### 🔸 button (modified bar):
_Variant of `bar` with rounding radius = 14px (so that rounding diameter = height = 28px to form semi-circluar end caps)._  
The card behind a single row of buttons should also have semi-circular end caps, with diameter = height, such that _`card` rectangle radius = 16px, `shadow` rectangle radius = 17px, and `EXTENT` height = 40px_ (e.g.  `Rain delay` card above). Buttons may include an icon with a `circle` _radius 16px_ aligned to fit exactly in the half-round left end cap, and _`icon` scaled to match (~##%)_.

#### 🔸 scenes (unique options):
_Variant of standard `icon`s with enlarged `circle` background that merges with a small `bar` below as background for a text label._  
Multiple mutually-exclusive scenes are placed next to each other - the selected scene is highlighted (using the active color coding for interactive icons described below) while all other related scene options are colored in their inactive state.

#### 🔸 labels:
_16pt Robotto Condensed. 15px below bottom of circle, centred. (Offset from `EXTENT`: bottom = 35px.)_  
(Secondary labels, such as units of measure: _14 pt Robotto Condensed_.)

#### 🔸 wallpaper (page background):
_Master wallpaper covering full display (320px x 480px) CLONED for each page._  
Using 'clones' of a 'master' `wallpaper` makes it much easier to manage the background on each page.  This way, any edits made to the master will automatically flow through to every page (and makes it much more convenient if you want to test textured backgrounds, in place of a solid color, in a later theme).

#### 🔸 EU NSPanel template (landscape with covered strip down right edge):
For the **EU NSPanel**, the right hand edge of the display is hidden by the case, which has to be taken into account when creating HMI images (that still need to be 480x320, but with the covered part of the display blacked out).  The SVG file includes a _500x320 template_ for this which allows cards to be snapped to grid while editing and still maintain their final alignment.  Marked areas on each edge show what needs to be clipped to recentre the grid-aligned cards and the 'clip mask' rectangle between these marked areas can be applied to the final HMI page image to extract the properly-centred 480x320 image (including the black strip for the covered area on the right).
  
--- 
  
</details>


## Color Conventions
Consistently following a set of conventions for how UI elements are colored makes it much easier to interpret dense information on the display at a glance.

<details>
  <summary>▶️ more ...</summary>


#### States and Interaction
* 🔹 A `colored icon` indicates that it is `interactive` (it will trigger an action, such as toggling, when touched), whereas grey-scale icons provide information that is not directly interactive (such as sensor information).
* 🔹 A `colored background` indicates that information for that entity is in an `active` state (it is 'on', the value exceeds a threshold, or it matches some criteria, such as tracker location matching "Home"), whereas a grey-scale background indicates that is in its non-active state.

Note that this convention declutters the interface by obviating the need for 'toggle buttons' that are so ubiquitous in other UIs - simply coloring the `icon` indicates that pressing it will trigger a toggle (where that is the expected effect, and/or it may trigger other single-click, or long-click actions).

#### Icon and Background Colors (part of named 'swatch' palette)
* 🔹 Five colors are used to indicates states and interactive elements: `orange`, `red`, `purple`, `blue`, `green` (following [Lovelace Minimalist UI](https://ui-lovelace-minimalist.github.io/UI/) and [Mushroom Cards](https://community.home-assistant.io/t/mushroom-cards-build-a-beautiful-dashboard-easily/388590)).  (These colors have been modified from Material Design standards to work well on a Nextion NSPanel display.)
* 🔹 Three variants are used for each color (ranked from brightest to darkest): `Active_Icon` (used when an interactive icon is in its active state, and blended into the grey background with transparency when in its inactive state); `Active_Background` (applied to an icon background when in its active state; also applied to the interactive state of other elements such as slider bars); and `Dim` (used for the slider background, the background of dynamic text).

#### Example icon types coloring:
* 🔹 For an **interactive icon** (e.g. `Garage` light in screenshots):  
  Active state (`Active_Icon` icon color on `Active_Background` background);  
  Inactive state (`Active_Icon` semi-transparent icon on `Inactive_Backround` grey background).
* 🔹 For an **non-interactive icon** (e.g. `Front` door contact sensor in screenshots):  
  Active state (`Inactive_Grey` icon color on `Active_Background` background);  
  Inactive state(`Inactive_Grey` semi-transparent icon on `Inactive_Backround` grey).
* 🔹 For a **static icon** (e.g. the temperature icon for above the `light color temperature` slider in screenshots):  
  Enabled state (`white` icon on `Inactive_Background` grey);  
  Disabled state (dark `Disabled` grey icon on `Inactive_Backround` grey).

#### Buttons
`Button`s use white `label`s and `icon`s on a `button-colored` background that is slightly darker than the `Active_Icon` blue (so that white text remains legible when the display is viewed at an oblique angle and the blue color becomes washed out).

#### Labels
Lables have a bright grey for showing text associated with active UI elements, and a darker grey to designate inactive or disabled elements.  
(Text on `buttons` is white.)

#### 'Structural' elements
All the static non-interactive 'structural' components of the UI are distinguised by using greyscale (or very low saturation) colors.
  

--- 
  
</details>


## Creating Customised/Variant Cards
Although the included SVG file has many cards and components that you can use in your projects, you will likely want to create some of your own custom cards as the templates that you repeatedly duplicate and modify for your own projects.  In these cases it will often be easiest to start from a similar basic card (like and 80x120 entity card or a slider card) and customise it to your needs. 


<details>
  <summary>▶️ more ...</summary>


#### Resizing
Do not resize cards by simply scaling the whole grouped object(s) - that will mess up the consistency of offsets and component sizes relative to other cards.  
Instead, work through each element in the object hierarchy and resize them invidually, maintaining offsets specified above. The design rules make this much easier than it sounds - with the rectangle tool selected, start with the `EXTENT` and adjust the rectangle width and height in multiples of 40px.  Then make use the same multiples of 40px to adjust the width and height of the `shadow` and `card` rectangles (and their offsets and corner-rounding will be maintained correctly).  Do the same for any `bar` and `button` rectangles you want to use, then check if you need to change the alignment of any `label`s, `icon`s and/or `circle`s.  (For more complicated changes, such as `Grouped Cards` described below, duplicate any elements you require extra copies of, arrange them properly in the object hierarchy tree, align and color them as needed).

#### Grouped Cards
For a grouped card, that combines multiple entities, it is **easier to expand an indvidual card** (than to try merging multiple individual cards).  Start with a basic card for an individual entity that you want to group and expand it (by **resizing the rectangles for the EXTENT, shadow and card** elements, as described above).  **Then duplicate the elements you want multiples of** in the group (circles, icons, bars, buttons) and rearrange those duplicated elements (aligned to where they would of been if they had remained part of separate, adjacent, ungrouped cards).  The `Bedroom` card above shows an example thats groups four entities together on one card.


#### Editing Tips
* Use the 'Objects' hieararchy (rather than ungrouping then regrouping) to select, copy/duplicate and paste elements.
* It is especially important to keep the object tree properly organised by being precise about where in the hiearchy you copy from (the whole group from that level down will be copied), where in the hiearchy you paste to (it will be inserted above the selected item)), and which individual element (and which LHS selection tool you have active) when editing.
* It helps if you dock the 'Object' and the other key object property tools (`Transform`, `Fill and stroke`, `Swatch`, `Export PNG`, `Align` etc.) to the two sidebars on the right hand side.
* To maintain precision it helps to do most editing parametrically (entering exact pixel values numericaly) using the `Rectangle` and `Circle` tools (on the LHS) and the object properties docked to the RHS sidebars: `Transform` (to move objects and resize icons). 
* For quick mouse selection the main 'select' tool (top LHS) selects whole groups and the finer 'node' tool beneath it selects objects within groups.  (Although, once selected, you then need to pick the appropriate 'select', 'rectangle', 'circle', 'text' tool to make the specific types of edits each of those tools allows - the top toolbar changes to reflect the currently available editing options.) 

--- 
  
</details>

  
---  
_For credits and resources [see the main UI page](/UI_Design)._

