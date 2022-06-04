# Home Assistant Nextion Handler
(_Version 0.6; Last updated: 2022-06-04_)  
**✴️ Widget UI v06_2022-06-03 files now uploaded, with installation instructions.**

'Nextion Handler' allows you to use a Nextion touch screen device (NSPanels in particular) to interact with Home Assistant (HA).  It uses a supporting Python script in Home Assitant to interpret and respond to instructions programmed into the Nextion device.  You can either use the full framework to create your own fully customised UIs in the Nextion Editor, or you can use specially pre-compiled files that don't require any programing and just some very basic configuration (or you can mix the two).


## ✴️ Widget UI
There is now an ultra easy way to connect your NSPanel device to Home Assistant that doesn't require any programming or complex configuring.  The new ✴️ Widget UI blends elements of the original NSPanel widgets, the Home Assistant 'glance' cards, and some of the graphical and functional aspects of Mushroom cards and Minimalist UI (popular UI mods for HA).  After installation, customising your Widgets is as simple as setting up an HA glance card - you simply provide a list of entities (and optionally a name and icon to go with them).  The Widget UI uses a group of pages tiled with a set of adaptable generic cards that are populated sequentially with information from your list of HA entities.  The information displayed and tap interactions adapt to the type of entity being displayed so that it shows useful information from a range of attributes specific to that type of entity, not just its 'state', as in the example below.

The Widget UI uses:
* 🔹 an ESPHome template (flashed to Nextion's  ESP32 chip);
* 🔹 an HA Python script (placed in your `/python_scripts` folder and configured with a YAML automation template);
* 🔹 a precompiled 'TFT' Nextion UI file (that you upload to the Nextion UI chip).

Further details for the Widget UI, including installation instructions and list of current features, [see the `widget_ui` folder](/widget_ui). 

**Demo page for Widget UI showing some of the different types of entity cards.**  
  

![Nextion Handler Widget UI photo](/widget_ui/ScreenPhoto_Widgets_0396_small.JPG "Example photo of Widget UI")

---

## 🔶 Full Nextion Handler instruction set
If you want full control of how your Nextion UI looks and interacts with HA, then you can use the full Nextion Handler framework (that the Widget UI is based on) and include its instructions in your own  Nextion HMI files.  Full details of the this framework, and the instruction set it makes available to program HA interactions into your HMI files, are documented [in HA_NEXTION_HANDLER_INSTRUCTIONS.md](/HA_NEXTION_HANDLER_INSTRUCTIONS.md).  There are also resources below to assist with building attractive and effective user interfaces for your project - some of these will be useful to those designing graphics and touch interactions in their own HMI projects (not just on NSPanels or using Nextion Handler). 

**Screnshot examples of some pages in a customised Nextion Handler UI:**  
  
![Nextion Handler screenshots](/current_version/images/Screenshots_MinimDark_b.png "Nextion Hanlder Screenshots")


---

## 🔷 Graphical UI design for HMIs
The **[UI_Design](/UI_Design) folder** has information to help design beautiful graphics for your HMI projects (and working around some of the flaws/limitations of Nextion displays).  A set of **very detailed design rules for the Minimalist-style design** (as shown above) allow _**anyone, with a bit of patience, to create stunning graphics for their displays by methodically applying and adapting the rules.**_  Template vector graphics files include a set of prebuilt modular UI components, that can be snapped together to design a UI page, together with example pages built with these components.

---

## 🔷 Nextion Touch UI Tips, Tricks & Traps
The **[Tips_and_Tricks](/Tips_and_Tricks) folder** has guides and example files for enhancing the built-in capabilities of Nextion displays with more advanced processing of touch gestures and interactions. This includes HMI code and examples for robust gestures, circular sliders, and geometric functions.

---


## 🔷 Credits & Related Resources:

### ESPHome: Flashing, Base Configuration, Functionality
* [ESPHome Nextion device](https://www.esphome.io/components/display/nextion.html).
* [ESPHome Nextion class](https://esphome.io/api/classesphome_1_1nextion_1_1_nextion.html).
* Masto [Github config](https://github.com/masto/NSPanel-Demo-Files/blob/main/Dimming%20Update/Screensaver%20Page/nspanel-demo.yaml) and [video](https://www.youtube.com/watch?v=Kdf6W_Ied4o&t=2341s).
* [Fix for Sonoff NSPanel display](https://github.com/esphome/esphome/pull/2956) to escape Protocol Reparse Mode so standard communication protocol will work.

### Material Design
  * [Reference](https://material.io/design)
  * [MDI Icons](https://materialdesignicons.com/)
  * [Google Fonts](https://fonts.google.com/specimen/Roboto+Condensed)

### Minimalist Design
  * ⚪ [Minimalist Smart Home concept](https://www.behance.net/gallery/88433905/Redesign-Smart-Home) by [Yuhang Lu](https://www.behance.net/7ahang).
  * 🌻 [Lovelace UI • Minimalist](https://ui-lovelace-minimalist.github.io/UI/) for Home Assistant by [tben](https://community.home-assistant.io/u/tben/summary).
  * 🍄 [Mushroom Cards](https://community.home-assistant.io/t/mushroom-cards-build-a-beautiful-dashboard-easily/388590) for Home Assistant by [piitaya](https://github.com/piitaya).

### Nextion
* Nextion 
  [HMI editor](https://nextion.tech/nextion-editor/),
  [Editor Guide](https://nextion.tech/editor_guide/),
  [Nextion Instruction Set](https://nextion.tech/instruction-set/),
  [Blog examples](https://nextion.tech/blogs/).
* Unofficial Nextion [user forum](https://unofficialnextion.com/).


### Project Forum Pages
If you want to leave suggestions, comments, or feature requests there are online forum pages for this project at:
* ✴️ Home Assistant Community Forum [project page](https://community.home-assistant.io/t/nextion-handler-for-home-assistant-for-nspanels/394858/4).
* ✴️ Unofficial Nextion User Forum [projgect page](https://unofficialnextion.com/t/nextion-gesture-tips-tricks/1585).
---



  
