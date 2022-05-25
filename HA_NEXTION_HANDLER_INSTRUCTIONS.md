# Home Assistant nextion_handler.py Instruction Set
(_Version 0.5; Last updated: 2022-05-25_)

Nextion Handler allows you to program a Nextion touch screen device (NSPanels in particular) to interact with Home Assistant (HA) **without having to do any coding in ESPHome YAML or Home Assistant automations**.  It uses a supporting Python script (to handle '**command_strings**' that you program into your HMI files) together with some boilerplate code (that does the routine parts of executing your programmed commands).

* :arrow_forward: **ESPhome** acts as a passive conduit tranferring command_strings from the Nextion to HA and Nextion Instructions back from HA to the Nextion (standarized boilerplate YAML configuration).

* :arrow_forward: **Home Assistant** configuration is a single automation to confgure the `nextion_handler.py` service (and includes a dictionary of entity_id aliases to help manage which Home Assitant entity you associate with each Nextion variable).

* :arrow_forward: All programming logic is kept together in one place, the **Nextion Editor** HMI files, supported by standardized boilerplate code to handle the HA interaction loop.

------------------------------------------------------------------------------
## Nextion Handler Framework Overview
There are only 3 places where you need to add customized code to your Nextion Editor HMI file to link it to HA: 2 types of Nextion Handler commands (**NHCmds**), and 1 'subroutine'.

:arrow_forward: '**SET**' commands assign Nextion variables the values of data you request from Home Assistant.


SET commands are entered into text variables on each page as **command strings** (which are lists of NHCmds separated by commas or linebreaks, with arguements separated by spaces). The **boilerplate [Postinit]** event of each page sends the HA_Set command_strings to HA.


:arrow_forward: '**ACTION**' commands perform actions you request in HA (to control lights, scenes, scripts,  etc.).

Your Events in Nextion Editor need to assign a sequence of ACTION NHCmds to a command_string string. You then send the commands with the **boilerplate** '**SEND_ACTIONS**' subroutine, which temporarilly speeds up the **boilerplate** '**UPDATE_LOOP**' (a Nextion timer that enforces state changes to a **TRIGGER** value to signal how Home Assistant should respond).


:arrow_forward: '**APPLY_VARS**' is a Nextion 'subroutine' where you place your code for visualising changes in data and refreshing the UI.

------------------------------------------------------------------------------

![Nextion handler framework](/current_version/images/nextion_handler_framework_dark.png "Nextion handler framework")

See expandable details and examples for each **CUSTOMIZABLE** and **BOILERPLATE** component below.

------------------------------------------------------------------------------
## Getting Started: Template and Demo Files
If you would rather not do any programing at all, the pre-complied Widget UI NSPanel templates provide a very easy starting point for linking your NSPanels to Home Assistant (but with the trade-off that there is less room to customise the UI).

If you want full control of how your Nextion UI looks and interacts with HA, then you can use the instruction set below in your Nextion HMI files to do that (and you can mix your customised pages with the generic/adaptable Widget UI pages in the same project, which lets you gradually customise the parts of the UI that are most important to you).
The easiest way to get started is to use some of the example files (included in this repository) as templates, try out the debug page in the Nextion Editor, then play with customizing the UI components to create a test page that fits your own project to try out on your own device.

The documentation below should help in exploring the example HMI files and creating/adapting your own.

------------------------------------------------------------------------------
## Nextion Handler Instruction Set
▶️ `Nx` = Nextion variable name
 
<details>
  <summary>as a shorthand ...</summary>

... for `Nx` you can _exclude_ the '.val'/'.txt' suffix if you have included the page prefix with the variable name;

--- 
  
</details>

▶️ `E` = $alias or HA entity_id;

<details>
  <summary>as a shorthand ...</summary>

... for `E`: _a)_ in Set commands `$` alone can be used for `E` to indicate the alias should be the same as the associated `Nx` (shorthand) variable name; _b)_ in Action commands the entity class can be ommited where it is implicit, e.g. you can drop `script.` from `E` when calling the `scpt E` command).

--- 
  
</details>


### 🔺 SET COMMAND LIST
You enter SET commands in the Nextion Editor text variables `HA_SET1` .. `HA_SET5` on each page.  You use them to configure how you want to pull data from Home Assistant each time that the Nextion page is updated and what HA data you want assigned to each Nextion variable.

<details>
  <summary>more ...</summary>

🔺 SET commands typically perform the following steps:
 
- Expand the shorthand Nextion variable (`Nx`) to the full variable name.
- Look up the entity $alias  (`E`) in the alias dictionary to retrieve the full HA entity_id.
- Get the required state and/or attributes of the HA entity and post-process these as required to return the value(s) in a form that is directly useable in the Nextion code.
- Assign the value to the Nextion variable by sending a Nextion Instruction to make the assignement (using the ESPHome `send_command_printf()` command configured in ESPHome to be available as a service to HA) - so the ultimate assignent is executed as an instruction on the Nextion device itself, while the `nextion_handler` determines exactly what instruction needs to be sent.

--- 
  
</details>

🔺 `sett Nx len E`  (assign `len` chars of state of `E`, as string/text, to `Nx`).

🔺 `setn Nx scale E (d)` (assign `Nx` the integer value of `scale` * state of `E`)

<details>
  <summary>  more ...</summary>

  The scaling factor (`scale`) can cater for the way `Nx` uses ints to represent floats (stored as int(val * num_dps) and for changing of units, e.g. for energy, 1dp kW fits better on small display than Watts, so HA state in Watts * scalefactor of 0.01 gives `Nx` 1 dp float in kW (divide by 1000 to convert Watts to kW, then multiply by 10 to store as Nextion 1dp float): `setn EN.sol 0.1 $ 0`.
 
  Optionally specify a value, `d`, to return if state of E is not numeric, otherwise the setn commands will be skipped on errors.

--- 
  
</details>


🔺 `setb Nx E` (assign `Nx` 0 or 1 based whether the state of `E` is in FALSE_STATES)).

🔺 `setb Nx E cp x` (assign `Nx` 0 or 1 based on comparing (`cp`) the state of `E` to `x`)
<details>
      <summary>more ...</summary>
    
   The comparitor, `cp`, must be  in   `[eq, ne, lt, le, gt, ge, =, !=, <, <=, >, >=]`.
 
   Optionally specify a value, `d`, to return if state of E is not numeric, otherwise the setb command will be skipped on errors.

--- 
  
</details>


🔺 `setlt Nx_state Nx_tp Nx_brt Nx_ct Nx_rgb565 E` (assign `Nx` variables the state,
    'type', brightness, color temperature and color of light `E`).
    
<details>
      <summary>more ...</summary>

   'type' is a bit-encoded value of the supported modes of light `E`: bits are 1:brightness, 2:color_temp, 3:rgb.

    The light color is converted to Nextion 16-bit RGB565 format (to assign directly to color attributes of Nextion UI components).

    Use '_' in place of `Nx` variable names to skip assignments for those attributes.

--- 
  
</details>

🔺 `setntf Nx_count (Nx_title) (Nx_msg) (n) (chars_title) (chars_msg)` (assign 3 `Nx` variables the Count, Title and Message of the `n`th Persistent Notification.)
<details>
      <summary>more ...</summary>

   Use '_' in place of `Nx` variable names, or omit them, to skip assignments for those attributes.
 
   Default numeric arguments (if unassigned) are 1, for message num, and 255 for string len.)


--- 
  
</details>


🔺 `setdt Nx` (assign `Nx` current data-time as "dd/mm HHhMM").

<details>
  <summary>▶️ EXAMPLE: `setn IR.nRN_DL 1 $` (using shorthand notation).</summary>

(Equivalent to long form of `setn IR.nRN_DL.val 1 sensor.rain_delay`.)
Set the Nextion variable `IR.nRN_DL.val` to the integer value of the state of the HA entity with the alias `IR.nRN_DL` after multiplying by a scaling factor of 1.
 
In this example, assuming `sensor.rain_delay` was the entity_id associated with the alias `IR.nRN_DL` and had a value of "3" at the time the command was called, the `setn` commands would perform the following steps:

- Expand the shorthand Nextion variable (`Nx`) from `IR.nRN_DL` to `IR.nRN_DL.val`.
- Look up the HA entity_id  by translating the shorthand alias (`E`) from `$` (short for `$IR.nRN_DL`, from prepending `$` to the shorthand `Nx` argument) to the alias dictionary key `IR.nRN_DL`, and then retrieving the value of the entity_id associated with that key, `sensor.rain_delay` (configured in the alias dictionary section of the `nextion_handler` automation YAML - see the _alias example_ below for more detail).
- Get the state of `sensor.rain_delay` (assumed to be "3" in this example) and return the integer value of multiplying this by a scaling factor of 1.
- Assign the final value (3) to `IR.nRN_DL.val` by sending the Nextion Instruction `IR.nRN_DL.val=3` to make the assignement (via the service that uses the ESPHome `send_command_printf()`).

--- 
  
</details>


### 🔻 ACTION COMMAND LIST
You assign ACTION commands to the `HA_ACT` string in your Nextion Editor 'events'.  You use them to configure the service calls that you want Home Assistant to execute when triggered by Nextion touch events, such as UI button clicks.


🔻 `tgl E` (toggle `E`).

🔻 `ton E` (turn on `E`).

🔻 `tof E` (turn off `E`).

🔻 `inps E string` (set value of input_select `E` to `string`).

🔻 `inpb E b` (turn input_binary `E` `on` if `b`!=0 otherwise turn `off`).

🔻 `inpn E x` (set value of input_number `E` to `x`).

🔻 `lt_brt E x` (set brightness percent of light `E` to `x` (0..100)).

🔻 `lt_brtv E x` (set brightness value of light `E` to `x` (0..255)).

🔻 `lt_ct E x` (set colour temperature of light `E` to `x` mireds).

🔻 `lt_rgb E r g b` (set colour of light `E` to RGB = `r`, `g`, `b`).

🔻 `lt_hs E h s` (set colour of light `E` to Hue = `h`, Saturation = `s`).

🔻 `lt_cw E dx dy r` (set color of light `E` to Color-Wheel location `dx`, `dy` from centre of wheel radius `r`).

<details>
  <summary>more (color wheel example) ...</summary>

Assumes a Home-Assistant-style color-wheel with red (hue 0) at 3 o'clock, increasing CLOCKWISE to 360.
 
(CLOCKWISE accounts for display y increasing downwards, which reverses angle of Cartesian ArcTan. So hue=90, with a greenish color, is at the 6 o'clock position.)

The Nexion Editor example below shows a template generic 'pop-up' light control page (that can be called for an abritrary light entity) together with the event for tapping on the color wheel to build the `HA_ACT.txt` command_string to call the `lt_cw` NH command.
 
![Color wheel example in HMI](/current_version/images/LT_colorwheel_event.png)

--- 
  
</details>


🔻 `lt_wt E` (set light `E` to a supported white/color_temp mode).

🔻 `scn E` (turn on scene `E`).

🔻 `scpt E` (call script `E`).

🔻 `say E string` (Play TTS of message `string` to media player `E`).

🔻 `ntf title|message` (Create a Persistent Notification in HA with strings `title` & `message` (separated by '|')).

🔻 `ntfx n` (Dismiss the `n`th Persistent Notification in HA).

🔻 `sub Nx` ('click' the Nextion (hidden) hotspot `Nx` to execute a 'subroutine': sends `click Nx,1` instruction to Nextion).

<details>
  <summary>▶️ EXAMPLE: `scpt $rain+7` (using shorthand notation).</summary>

(Equivalent to long form of `scpt script.rain_delay_incr`.)
Calls a script to increase the 'rain delay' for suspending automated irrigation by 7 days.

---

</details>

------------------------------------------------------------------------------
## CUSTOMIZABLE components (with shorthand notation)

Click to expand sections below for an example of **how each of the 3 customized components were added to a Nextion page** to integrate it with HA.

![Example dark Minimalist style](/UI_Design/Minimalist/ExampleM_IR_ST_LT_1280x640.png)

<details>
  <summary>▶️ Example NEXTION EVENT to SEND ACTION commands to Home Assistant (Nextion Editor - event tab, HA_ACT)</summary>
  
---

>You assign ACTION NHCmds to  `HA_Act.txt` in Nextion events, then send the commands with  `SEND_ACTIONS` (see **boilerplate SEND_ACTIONS** 'subroutine' code & details below).

This example shows how to program calling Home Assistant actions from within Nextion Editor Events.  The code is for the orange [+7] button at the bottom of a page for controlling irrigation automations.  The [Touch Release Event] has been programmed so that when this button is given a short press, a script will be called in Home Assistant to add 7 days to the 'rain delay' until automatic scheduling resumes.  Long-pressing the button is programmed instead to call a script that reduces this delay by 7 days.  (See **boilerplate GESTURE**s code & details below if you want to use `gest_type` swipe & press UI gestures.)
 
**TIP:** Change the font in the Nextion Editor to [a proper programming mono-spaced font](https://hadrysmateusz.medium.com/best-free-programming-fonts-2020-f243a6b4749a) (as below) - it makes reading and editing your code _much_ easier.
 

<img src="https://github.com/krizkontrolz/Home-Assistant-nextion_handler/blob/main/current_version/images/HA_ACT_example.png" alt="HA_ACT example">



---
  
</details>



<details>
  <summary>▶️ Example HA_SET string for pulling required HA data into Nextion pages (Nextion Editor - string, HA_SET1)</summary>
  
---

>You assign SET NHCmds directly to `HA_SET1.txt` (and up to 4 more) local text variables on each page.  The Page [Post Initialization Event] will then send the strings to HA to store for use in future page updates. (See **boilerplate Page PostInit** code & details below).

This example shows the `HA_SET1.txt` string to bring in the data required for a page that controls irrigation automations.  It fetches 6 numeric values (`setn`: for irrigation duration sliders and the rain delay), 5 binary values (`setb`: for the 5 toggle switches), and one text value (`sett`: for the `input_select` in HA that indicates the current status of the irrigation system.)  For all SET commands the enitity_id is specified with `$` which means they use a dictionary to look up the HA entity_id based on the Nextion variable name. (See the _aliases & automation example_ below, matching this `HA_SET1` string.)

<img src="https://github.com/krizkontrolz/Home-Assistant-nextion_handler/blob/main/current_version/images/HA_SET_example.png" alt="HA_SET example">


---
  
</details>


<details>
  <summary>▶️ Example APPLY_VARS to update Nextion UI with returned data from HA (Nextion Editor - APPLY_VARS 'subroutine')</summary>

---

>You put your Nextion code for modifying any UI components that use HA data in a 'subrountine' (a hidden `Hotspot`).  You will likely have this code already in your HMI file, you just have to place the UI refresh code in a subroutine.  Doing this allows HA to apply the UI changes immediately after sending updated data by sending the Nextion Instruction "`click APPLY_VARS,1`".

This example shows part of the `APPLY_VARS` subroutine for applying updates to the display of 'rain delay' information on a Nextion page for controlling irrigation automations.  The code updates the numeric value displayed then also: _a)_ changes a `Crop` image to show the cloud icon and label in a highlighted color if the rain delay is greater than 0; _b)_ changes the background image for the displayed number to match (so the number seems transparent as the background changes); and _c)_ changes the font color for displaying the number.  (The complete subroutine applies updates to all the other UI components too.  This code is typical of any HMI project - the only additional step is putting it in a subroutine.)
 
**Note on global scope, variables, persistence, and memory use:**  For changes in data to persist after switching pages in the Nextion, the data scope has to be made `global`.  For simple small projects it may be easier to make the whole button (or other UI component) `global` to be able to write updates directly to the UI component attributes (which could avoid the need for `APPLY_VARS` in a basic UI, but at the expense of being [very wasteful of the extremely restricted (3584 bytes) global SRAM memory on your Nextion](https://unofficialnextion.com/t/updating-fields-before-page-is-displayed/791/5)).  It is _much_ more efficient to write data updates to Nextion `variables` (which only use the `global` SRAM memory to store their value, without the overhead of storing multiple other UI component attributes too).  This however requires an `APPLY_VARS` step to apply the upated data in the `variables` to the appropriate UI attributes for the changes to become visible on the display.
 
  
<img src="https://github.com/krizkontrolz/Home-Assistant-nextion_handler/blob/main/current_version/images/APPLY_VARS_example.png" alt="APPLY_VARS example">

---
  
</details>




------------------------------------------------------------------------------
## BOILERPLATE components

Click to expand sections below for boilerplate code (this is standardized code that you can copy and paste, without editing. It performs the routine tasks required to execute the NH commands you program in your CUSTOMIZED components.)

The details below help explain what the code is doing and how the pieces fit together.  But the easiest way to include the boilerplate components into your own projects is to use a page from one of the example HMI files as a template (and copy the set of components from there rather than trying to recreate them from the code below).

<details>
  <summary>▶️ UPDATE_LOOP (Nextion Editor - timer)</summary>
  
---
> The `UPDATE_LOOP` is attached to a timer on each Nextion page to control the timing and scheduling of most important tasks (polling, updates, queues, dimming, sleeping: as detailed in the comments at the top of the standardized boilerplat code below) including fetching your data from Home Assistant in an orderly and efficient way.

You can modify the behaviour of the `UPDATE_LOOP` through Nextion Global Settings variables (see the **boilerplate `Program.s`** details below), without having to edit the code.  The example HMI files in this repository include a Nextion page that can adjust most of these settings from on the device (and you can use this as a template to adapt to your own HMI and UI style.)

<img src="https://github.com/krizkontrolz/Home-Assistant-nextion_handler/blob/main/current_version/images/Settings_CFG_example.png" alt="APPLY_VARS example">

```
//~~~~~~boilerplate~~~~ v0.502
// UPDATE LOOP controls:
//  1) Slow passive polling for data updates from Home Assistant.
//  2) Temporary fast updates after user Actions (incl. page change).
//  3) Manage fast repeated update queue (and stop overloading data exchange).
//  4) Progressively dim the display with inaction (and brighten on interaction).
//  5) Sleep (after loop count down completes).
//  6) Prepare state for waking from sleep (for controlled/predictable behaviour on waking).
// by controlling values of TRIGGER,loop_cnt (count down), *.tim (loop rate), dim.
// See Program.s* --GlobalSettings-- for variables that control default loop behaviour.
// The CFG page has sliders for adjusting the loop control variables.
//~~~~~~~~~~~~~~~~~~~~~
// 'TRIGGER' state changes are responded to by HA nextion_handler
// to send the updates specified in the the list of
// HA_Set(1..5) command_strings (text variables configured on each page).
// (HA_SET cmds are sent to HA, via ESPHome, in each Page's Postintialize Event).
//
//
// COUNT-DOWN loop_cnt and perform indicated UPDATE (using NH_Cmds in HA_SET1..5 strings):
// Force a DATA UPDATE from HA (based on HA_SET cmds)
// by Enforcing a TRIGGER state change (where TRIGGER also indicates loop status):
// - FAST (additional) UPDATES: loop_cnt > sleep_cnt;
//   TRIGGER toggles -3,-4
// - STANDARD UPDATES: 0 < loop_cnt <= sleep_cnt;
//   TRIGGER toggles -1,-2
// - SLEEP: loop_cnt == 0  (countdown completed sleep_cnt update loops without interaction);
//   TRIGGER toggles 0
//(- Positive TRIGGER vals signal ACTION requests (sent from UI Events via SEND_ACTIONS 'subroutine').
loop_cnt-=1
if(loop_cnt>=sleep_cnt)  //FAST UPDATES (after user interaction)
{
  //Enforce TRIGGER state change (-3, -4)
  if(TRIGGER!=-3)
  {
    TRIGGER=-3
  }else
  {
    TRIGGER=-4
  }
  //Restore Nextion display brightness (after progressive dimming)
  dim=dim_default
  //Progressively Slow down rate of fast updates with each rpt
  UPDATE_LOOP.tim=UPDATE_LOOP.tim+fastupdate_tim
  //
}else
{
  if(loop_cnt>0)  //STANDARD UPDATES
  {
    //Enforce TRIGGER state change (-1,-2)
    if(TRIGGER!=-1)
    {
      TRIGGER=-1
    }else
    {
      TRIGGER=-2
    }
    //Restore default upate interval (in microsecs) after fast update repeats are complete
    tmp=upate_secs*1000
    UPDATE_LOOP.tim=tmp
    //Progressive dimming (from dim_default to dim_min over interval until sleep)
    tmp=dim_default-dim_min
    tmp*=loop_cnt
    tmp/=sleep_cnt
    tmp+=dim_min
    dim=tmp
    //
  }else
  {
    //SLEEP PREPARATION (sleep execution occurs AFTER writing TRIGGER)
    TRIGGER=0
  }
}
//
//
// SEND TRIGGER Integer value (to HA via ESPhome)
// Nextion Custom Sensor Protocol - see: https://www.esphome.io/components/sensor/nextion.html
printh 91            //Tells the ESPHome library this is a sensor (int) data
prints "TRIGGER",0   //Sends the name that matches ESPHome component_name or variable_name
printh 00            //Sends a NULL
prints TRIGGER,0     //The actual value to send. For a variable use the Nextion variable name temperature without .val
printh FF FF FF      //Nextion command ack (termination string: HA nextion_handler needs to remove these)
//
//
//SLEEP EXCECUTION
if(TRIGGER==0)
{
  //PREPARE WAKE STATE (fast update etc. on wake)
  UPDATE_LOOP.tim=500
  loop_cnt=sleep_cnt+2
  dim=dim_default
  sleep=1
}
```

---
  
</details>

<details>
  <summary>▶️ SEND_ACTIONS (Nextion Editor - hidden hotspot 'subroutine')</summary>
  
---

> `SEND_ACTIONS` is a subroutine (the code attached to a `Touch Press Event` for a hidden hotspot on each Nextion page) that sends ACTION command_strings to Home Assistant and intiates rapid updates to return the resulting (delayed) sequence of changes in states of HA entities linked to the page.


Each Nextion Event should first add the sequence of ACTION NH commands to the `HA_ACT.txt` string on that page, followed by `click SEND_ACTIONS,1` (which then sends the Action commands to the nextion_handler on Home Assistant to be excecuted).
(See the example Nextion Event above for how ACTION command_strings are programmed the Nextion Editor.)

```
//~~~~~~boilerplate~~~~ v0.501
// SEND ACTION HaCmds (CSV sequencence set in HA_Act string by calling Event)
//~~~~~~~~~~~~~~~~~~~~~
// This subroutine is called by each Nextion UI Event programmed to interact with Home Assistant.
// The HA_Act string_commands are sent to the HA nextion_handler, which performs the
// actions and then conducts fast/repeated data updates.
// The default number and speed of fast repeat updates follow global settings (set in the [Program.s] tab).
// (Events can override these defaults by setting override_frpts=1 before calling SEND_ACTIONS.)
//
//Send HA_Act command_string (to HA via ESPhome Custom Nextion Text)
printh 92
prints "HaAct",0  // need to remove '_' to create a component_name that ESPhome will accept!!
printh 00
prints HA_ACT.txt,0
printh 00
printh FF FF FF
//
//
// Force a DATA UPDATE from HA (based on HA_ACT cmds)
// by Enforcing a TRIGGER state change with POSITIVE value.
// - Positive TRIGGER vals signal ACTION requests to nextion_handler (sent below);
// - Negative TRIGGER vals signal UPDATE requests (sent from UPDATE_LOOP timer).
if(TRIGGER!=1)
{
  TRIGGER=1
}else
{
  TRIGGER=2
}
//
//
// Send TRIGGER Integer value (to HA via ESPhome using Nextion Custom Sensor Protocol)
printh 91
prints "TRIGGER",0
printh 00
prints TRIGGER,0
printh FF FF FF
//
//
// Set UPDATE_LOOP for fast repeated updates from Home Assistant
// (to retrieve data changes that result from the HA_ACT ACTIONs that HA performs.)
if(override_frpts==0)
{
  // Initialize UPDATE_LOOP for DEFAULT fast updates (unless override flag is set by calling Event)
  loop_cnt=sleep_cnt+fastupdate_rpt //sets how many time fast updates are repeated
  UPDATE_LOOP.tim=faststart_tim  //UPDATE_LOOP will gradually slow down, then reset to slow polling when fast updates complete
}else
{
  //Allow OVERRIDES from calling Events to set Action-specific update behaviour (then revert to defaults)
  override_frpts=0
}
```


---
  
</details>




<details>
  <summary>▶️ Global settings (Nextion Editor - Program.s tab)</summary>
  
---
  
> Nextion Global Settings are configured in the `Program.s` tab in the Nextion Editor.  These include settings that can be used to fine tune the behaviour of the boilerplate `UPDATE_LOOP` code.

A template Nextion configuration page (CFG) in the working example HMI file shows how to adjust the main settings from on the device using sliders.

(Alternatively, the variables can be changed by assigning new values with Nextion Instructions sent from Home Assistant using the `send_command` service (configured in ESPHome for the device).)


```
//~~~~~~boilerplate~~~~ v0.5.003
// DEVICE CONFIG & GLOBAL SETTINGS (directly controllable from HA)
//~~~~~~~~~~~~~~~~~~~~~
//
// ----- Global Settings controlling UPDATE_LOOP behaviour ------
int dim_default=100       //Default display brightness when there is activity
int dim_min=80            //Minimum display brightness dims to without actvity
int upate_secs=15         //Passive polling interval when inactive
int sleep_cnt=20          //Inactivity refresh cycles before sleeping (also see thsp and ussp below)
int fastupdate_rpt=3      //Default number of fast repeats after SEND_ACTIONS
int faststart_tim=1000    //Default initial fast update delay (need to wait for state changes in HA to occur)
int fastupdate_tim=2000   //Default amount fast update are slowed by for each repeat (after SEND_ACTIONS etc.)
int wake_page=255         //Sets Power on start page (255 = last page)
int page_max=3            //Last page for automatic cycling (put all main pages (0..page_max) at top of list)
//
// ----- Internal Working Variables ------
int TRIGGER=0,loop_cnt=99,override_frpts=0
int tmp=0,flag1=0,flag2=0
int prev_page=0
int gest_dx=0,gest_dy=0,gest_dsq=0,gest_time=0,gest_type=0
//
// ----- Device Config ------
//ESPHome Nextion config - as stated at https://esphome.io/components/display/nextion.html
baud=115200   // Sets the baud rate to 115200
bkcmd=0       // Tells the Nextion to not send responses on commands. This is the current default but can be set just in case
//
// ----- Sleep/Wake Settings ------
// see: https://nextion.tech/2021/08/02/the-sunday-blog-energy-efficient-design-with-nextion-hmi-portable-and-wearable-designs/
thsp=7200  //Sleep after this many secs without touch (!NX BUG: not currently functional)
thup=1     //Enables(1) touch to wake device
ussp=7200  //Sleep after this many secs without serial port activity
usup=0     //Disable(0) wake on serial data - NB*** will still wake if command string "sleep=1ÿÿÿ" is sent over serial
page wake_page   //Power on start page (255 = last page)
```
---
  
</details>

<details>
  <summary>▶️ Page PostInitialize Event (Nextion Editor - Page tab)</summary>
  
---

> The [PostIntialize Event] on each page sends the HA_ACT command_strings to Home Assistant and intializes the `UPDATE_LOOP`.

```
//~~~~~~boilerplate~~~~ v0.5
// INITIALIZE UPDATE settings by sending list of HA_Set command_strings to HA nextion_handler
//~~~~~~~~~~~~~~~~~~~~~
// Enter the sequence of HaCmds required to update this page with data from HA
// in the text field of the list of HA_Set (1..5) local text variables (for each page).
// HA nextion_handler will then use the command_strings when triggered
//   by state changes sent using the TRIGGER variable either by the
//   polling UPDATE_LOOP or after a Nx UI Event that sends an HA_Act
//   command_string with the SEND_ACTION subroutine.
//
// Hide 'subroutine' hotspots
vis APPLY_VARS,0
vis SEND_ACTIONS,0
//
//Send 'Set' commands to HA (via ESP32 strings) with commands for retrieving HA data
//ESPhome Nextion Custom Text Sensor Protocol, following: https://esphome.io/components/text_sensor/nextion.html
//1
printh 92            //Tells the ESPHome library this is text sensor
prints "HaSet1",0    //Sends the name that matches the ESPHome component_name or variable_name
printh 00            //Sends a NULL
prints HA_SET1.txt,0 //The actual text to send. For a variable use the Nextion variable name text0 without .txt
printh 00            //Sends a NULL
printh FF FF FF      //Nextion command ack
//2
printh 92
prints "HaSet2",0    // <<< NB ESPhome cannot accept '_' in 'component_name'
printh 00            // (need to adjust to ESPHome names to ones it will accept)!
prints HA_SET2.txt,0 // (then configure the 'name' for the sensor ESPHome to what you want the entity_id to be in HA)
printh 00
printh FF FF FF
//3
printh 92
prints "HaSet3",0
printh 00
prints HA_SET3.txt,0
printh 00
printh FF FF FF
//4
printh 92
prints "HaSet4",0
printh 00
prints HA_SET4.txt,0
printh 00
printh FF FF FF
//5
printh 92
prints "HaSet5",0
printh 00
prints HA_SET5.txt,0
printh 00
printh FF FF FF
//
// Re-initialize UPDATE_LOOP
loop_cnt=sleep_cnt+2 //forces 2 FAST updates
UPDATE_LOOP.tim=faststart_tim  //UPDATE_LOOP will gradually slow down, then reset to slow polling when fast updates complete
//
// Call subroutine to Apply (stale) variables to UI elements while waiting for data update
click APPLY_VARS,1
```

---
  
</details>

<details>
  <summary>▶️ ESPHome configuration to send commands & data between HA and Nextion (ESPHome YAML file)</summary>
  
---
  
  > ESPHome has to be configured to transfer `TRIGGER`, `HA_ACT.txt`, and `HA_SET1.txt` .. `HA_SET5.txt` to Home Assistant.  It also needs to provide the `esphome.nsp1_send_command` service for HA to be able to send Nextion Instructions back to the Nextion device.

A template ESPHome YAML configuration is provided in the repository (where you just have to fill in the variables in the `substitutions:` section at the top of the file, shown in the YAML extract below).  The main components that you need to add to your ESPHome YAML configuration are shown below (and are marked with `***nextion_handler requirement***` throughout the full version of the template).

```YAML
# Nextion Handler template for ESPHome (v0.5.002)
#----------------------------------------
#* DEVICE/USER-SPECIFIC DETAILS (customize for each of your own Nextion Devices).
#! BACKUP YOUR ORIGINAL ESPHome YAML config for your device.
#! GET THE PASSWORDS etc from that config & enter them in the 'substitutions:' below:
substitutions:
  ota_password: "from flashing initial config"
  fallback_ap_password: "from flashing initial config"
  short_name: nsp1   #from your initial  config    # prefixed to HA entity_ids (to make them unique for each device)
  long_name: My NSPanel                            # descriptive name
  tft_url: !secret nsp1_tft_url                    # path, including filename, where you put TFT files
  wifi_ssid: !secret wifi_ssid                     # your home wifi
  wifi_password: !secret wifi_password
#----------------------------------------

# Enable Home Assistant API.
api:
  # Configure some useful NSP services to be able to control from HA.
  services:
    #***nextion_handler requirement***
    # the 'send_command' allows nextion_handler to send Instructions back to the Nextion device.
    - service: send_command
      variables:
        cmd: string
      then:
        - lambda: 'id(nx1).send_command_printf("%s", cmd.c_str());'
    #* Service to upload cutom TFT files (created in the Nextion Editor)
    - service: upload_tft
      then:
        - lambda: 'id(nx1).upload_tft();'

#***nextion_handler requirement***
# Text sensors for transferring 'HA command strings' (comma separated sequences of HaCmds).
text_sensor:
  # All strings are to sent by the Nextion to the ESP32 using 'Nextion Custom Text Sensor Protocol':
  # https://esphome.io/components/text_sensor/nextion.html#nextion-custom-text-sensor-protocol
  - platform: nextion
    name: $short_name HA Act
    component_name: HaAct
  - platform: nextion
    name: $short_name HA Set1
    component_name: HaSet1
  - platform: nextion
    name: $short_name HA Set2
    component_name: HaSet2
  - platform: nextion
    name: $short_name HA Set3
    component_name: HaSet3
  - platform: nextion
    name: $short_name HA Set4
    component_name: HaSet4
  - platform: nextion
    name: $short_name HA Set5
    component_name: HaSet5

sensor:
  #***nextion_handler requirement***
  # nextion_handler variables - written to ESP32 by Nx using 'Nextion Custom Sensor Protocol':
  # https://esphome.io/components/sensor/nextion.html
  - platform: nextion
    name: $short_name Trigger
    component_name: TRIGGER

```

---
  
</details>

<details>
  <summary>▶️ Nextion Handler (Home Assistant - Python script)</summary>
  
---
  
  > The **Nextion Handler** provides Home Assistant with the service that responds to TRIGGER state changes sent from the Nextion device and responds by executing the NhCmds that you program into your HMI code.  (You can download the Python script from this repository.)

To enable Python scripts in your Home Assistant add the line: `python_script:` to your `configuration.yaml` file. Then create the folder `<config>/python_scripts/` and and place the Python scripts you want to run there.  (You may need to restart for them to become available.) (See [Home Assistant Python Script documentation](https://www.home-assistant.io/integrations/python_script/).)

The `automation.yaml` required to configure the `nextion_handler.py` script is shown next.

---
  
</details>


<details>
  <summary>▶️ Nextion Handler service configuration and alias 'dictionary' (Home Assistant - automation.yaml)</summary>
  
---
  
>Below is a **Home Assistant automation** template to configure the `nextion_handler.py` service, including an example of an **alias 'dictionary'** (for managing how Nextion variables used in NH commands are associated with HA entity_ids).  You need a separate `automation:` for each Nextion device (but they all use the same Python script.)

The example dictionary matches the irrigation page used in the CUSTOMIZABLE examples above.

Aliases are convenient because _a)_ they save you having to switch back & forth between the Nextion Editor & HA, _b)_ the alias is typically based on the name of the Nextion (global) variable it is associated with, _c)_ they save you having to reflash the Nextion TFT each time you fix a typo in an entity_id, _d)_ you enter the entity_ids in the HA YAML editor (where autocompletion helps avoid typos in the first place), and _e)_ they make the command_strings shorter for more efficient management with the resource contraints of Nextion devices.

```YAML
#  Nextion Handler service automation template (v0.5.002)
# (Replace NSP entity_ids with your own; Build the 'alias:' dictionary to match your own HMI project)
#  - handles everything coming from and going back to a Nextion device.
- alias: "NSPanel 1 Nextion Handler"
  mode: queued
  max: 10
  trigger:
    - platform: state
      entity_id: sensor.nsp1_trigger
  action:
    - service: python_script.nextion_handler
      data:
        trig_val: sensor.nsp1_trigger
        nx_cmd_service: esphome.nsp1_send_command  # << for sending Nextion Instructions back to the NSPanel
        action_cmds:
          - sensor.nsp1_ha_act  # << receives ACTION commands from Nextion (for making HA service calls)
        update_cmds:
          - sensor.nsp1_ha_set1 # << receives SET commands (for updating Nextion variables using nx_cmd_service)
          - sensor.nsp1_ha_set2 # ..ha_set5, as needed
        aliases:
          #...
          #____ example aliases 'dictionary' for IR page example above ______________
          IR.nIR_AL: input_number.irr_pct
          IR.nIR_BG: input_number.irr_bg
          IR.nIR_FG: input_number.irr_fg
          IR.nIR_BL: input_number.irr_bl
          IR.nIR_FL: input_number.irr_fl
          IR.bIR_BG: switch.irrigate_back_garden
          IR.bIR_FG: switch.irrigate_front_garden
          IR.bIR_BL: switch.irrigate_back_lawn
          IR.bIR_FL: switch.irrigate_front_lawn
          IR.nRN_DL: sensor.rain_delay
          IR.tIRR: input_select.irrigate_area
          rain+7: script.rain_delay_incr
          rain-7: script.rain_delay_decr
          #...
```

---
  
</details>


<details>
  <summary>▶️ (OPTIONAL) Home Assistant UI card for monitoring nextion_handler (Home Assistant UI MarkDown card)</summary>
  
---
  
> **Lovelace UI Markdown Card** for monitoring flow of nextion_handler command_strings & TRIGGERs (YAML for this card is included included in the repository.)

Output from Lovelace card matching the irrigation page CUSTOMIZABLE examples above, 
after just having pushed the [+7] 'button' (which has executed a script and initiated fast updates to pass resulting state changes in HA back to the Nextion).

<img src="https://github.com/krizkontrolz/Home-Assistant-nextion_handler/blob/main/current_version/images/Lovelace_MarkDown_Card.png" alt="Lovelace MarkDown Card example output">
 
   
MarkDown card template to generate above NSP monitoring card (for Home Assistant Lovelace).
(Replace `nsp1` in the YAML with the prefix/entity_id of your own Nextion device.)
   
```YAML
cards:
  # Monitor Nextion Handler commands (set DEVICE below)
  - type: markdown
    title: Nextion command_strings
    content: |
      ``` {# Display as code/monospaced font #}
      {%- set DEVICE = 'nsp1' %} {#-<< Set your device short name (prefix part of each entity_id) #}
      TRIGGER: >> {% set n = states('sensor.'+DEVICE+'_trigger')|int -%}
      {%- set ts = (states.sensor.nsp1_trigger.last_updated).timestamp() | timestamp_custom('%Hh%M') %}
      {%- if n > 0 -%}
        {{n}} (ACTION {{ts}})
      {%- elif n == 0 -%}
        {{n}} (SLEEPING {{ts}})
      {%- elif n > -3 -%}
        {{n}} (SLOW UPDATES {{ts}})
      {%- else -%}
        {{n}} (FAST UPDATES {{ts}})
      {%- endif %}
      {%- set ts = (states.sensor.nsp1_ha_act.last_updated).timestamp() | timestamp_custom('%Hh%M') %}
      HA_Act (<- SEND_ACTIONS {{ts}}):
      {%- set s = states('sensor.'+DEVICE+'_ha_act').replace('\r','').replace(',','\n') %}
      {%- for i in s.split('\n') %}
        <{{i}}>
      {%- endfor %}
      {%- set ts = (states.sensor.nsp1_ha_set1.last_updated).timestamp() | timestamp_custom('%Hh%M') %}
      Update settings (<- Page PostInit {{ts}}):
      HA_Set1 ---------------
      {%- set s = states('sensor.'+DEVICE+'_ha_set1').replace('\r','').replace(',','\n') %}
      {%- for i in s.split('\n') %}
        <{{i}}>
      {%- endfor %}
      HA_Set2 ---------------
      {%- set s = states('sensor.'+DEVICE+'_ha_set2').replace('\r','').replace(',','\n') %}
      {%- for i in s.split('\n') %}
        <{{i}}>
      {%- endfor %}
      HA_Set3 ---------------
      {%- set s = states('sensor.'+DEVICE+'_ha_set3').replace('\r','').replace(',','\n') %}
      {%- for i in s.split('\n') %}
        <{{i}}>
      {%- endfor %}
      HA_Set4 ---------------
      {%- set s = states('sensor.'+DEVICE+'_ha_set4').replace('\r','').replace(',','\n') %}
      {%- for i in s.split('\n') %}
        <{{i}}>
      {%- endfor %}
      HA_Set5 ---------------
      {%- set s = states('sensor.'+DEVICE+'_ha_set5').replace('\r','').replace(',','\n') %}
      {%- for i in s.split('\n') %}
        <{{i}}>
      {%- endfor %}
      ```   
```
      
---
  
</details>

   
   
<details>
  <summary>▶️ (OPTIONAL) 'Swipe' and 'Press' GESTUREs (Nextion Editor - timer)</summary>
  
---

> Gestures are not a _requirement_ for Nextion Handler.  But they are helpful for many projects and the one included in the HMI templates is a very robust and generalizable implementation.  It uses a `GESTURES` timer (called by `tc0`) to interpret 'swipe' gestures in real time (to be able to respond to before a release Event is generated), and returns the final gesture as a `gest_type` code (a Global* variable) for 'Touch Release Events' of other UI components to use in their code.
 
The HMI example files have complete implementations with all code, and a Debug template to test out how they work (including components to demonstrate common traps in designing these gestures into your own HMI files.)
 
The swipe gestures work even on a page that is entirely covered in active 'dual state' buttons (triggering those components only on 'press' gestures, not 'swipes'), and the gestures are automatically disabled when a stroke starts on a 'slider' (to avoid UI conflicts).

More details on Nextion gesture approaches are being prepared in a separate document.
  
<img src="https://github.com/krizkontrolz/Home-Assistant-nextion_handler/blob/main/current_version/images/DBG_GESTURE_timer.png" alt="GESTURE timer code">
 

---
  
</details>
   
   


<!---  Template for 
<details>
  <summary>Main line ...</summary>
  
---

> Highlight point ...
  
Details ...

---
  
</details>
--->



  
------------------------------------------------------------------------------
## Credits & Related Resources:

### UI Design
* ▶️  Tips and information for **[designing graphical components of UIs](/UI_Design)** for small displays like the NSPanel, including template vector graphics files (that can easily be adapted to other projects) and example HMI files using these designs.
* ▶️  Tips, tricks and traps related to **[programing the touch interaction functionality](/Tips_and_Tricks)** of UIs, including HMI code and examples for robust gestures, circular sliders, and geometric functions.

### ESPHome: Flashing, Base Configuration, Functionality
* [ESPHome Nextion device](https://www.esphome.io/components/display/nextion.html).
* [ESPHome Nextion class](https://esphome.io/api/classesphome_1_1nextion_1_1_nextion.html).
* Masto [Github config](https://github.com/masto/NSPanel-Demo-Files/blob/main/Dimming%20Update/Screensaver%20Page/nspanel-demo.yaml) and [video](https://www.youtube.com/watch?v=Kdf6W_Ied4o&t=2341s).
* [Fix for Sonoff NSPanel display](https://github.com/esphome/esphome/pull/2956) to escape Protocol Reparse Mode so standard communication protocol will work.

### Nextion
* Nextion 
  [HMI editor](https://nextion.tech/nextion-editor/),
  [Editor Guide](https://nextion.tech/editor_guide/),
  [Nextion Instruction Set](https://nextion.tech/instruction-set/),
  [Blog examples](https://nextion.tech/blogs/).
* Unofficial Nextion [user forum](https://unofficialnextion.com/).
------------------------------------------------------------------------------

