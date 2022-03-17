# Home Assistant Nextion Handler
(*Last updated: 2022-03-18*)

A framework that allows a Nextion touch screen device (NSPanels in particular) to be programmed to interact with Home Assistant.  This uses a supporting Python script (that handles HA '**command_strings**' sent from Nextion to request updates of HA data and to perform actions on HA) and some boilerplate code (to handle the loop of sending actions and receiving updated data).

* **ESPhome** acts as simple broker tranferring command_strings from Nextion to HA and Nextion Instructions back from HA to Nextion (fixed boilerplate configuration, after entering device details and passwords in a list of ```substitutions:```).

* **Home Assistant** configuration is a single automation calling ```nextion_handler.py``` and includes a dictionary of entity_id aliases (that makes book-keeping much easier in the Nextion Editor).

* All programming logic is coded in one place, the **Nextion Editor**, supported by cut-and-paste boilerplate code to handle the HA interaction loop.

------------------------------------------------------------------------------
## Nextion Handler Framework Overview
There are 2 types of HA commands (**HaCmds**) in the ```nextion_handler.py```:
>'**SET**' commands assign HA entity states to Nextion variable by sending back
  Nextion Instructions (sent with the **nx_cmd_service** configured on the ESP32).
  **HA_Set1..5** **command_strings** are a sequence of HaCmds defined for each
    page in the Nextion Editor.
  The **Postinit of each page** sends the HA_Set1..5 command_strings to HA.
  Updates to page data are applied by nextion_handler when **TRIGGER**ed.

>'**ACTION**' commands perform requested actions in HA (scripts, scenes etc.).
  Events in Nextion Editor need to assign a sequence of Action HaCmds to
  the **command_string HA_Act**, then call the **SEND_ACTIONS** subroutine.

>'**command_string**'s are comma- or linebreak- separated lists of HaCmds
  (255 chars max each) with arguements separated by spaces.

>'**UPDATE_LOOP**' on the Nextion controls the sending of a **TRIGGER** value (INT):
   >> POSITIVE TRIGGER values direct the nextion_handler to apply the HaCmds in
   the most recent **HA_Act** command_string sent to HA.

   >> NEGATIVE TRIGGER values direct the nextion_handler to apply the HaCmds in
   the most recent **HA_Set1..** comand_strings sent to HA.

   >> ZERO TRIGGER value indicates the Nextion is SLEEPing.

>'**APPLY_VARS**' subroutine on Nextion updates UI elements using the refreshed 
  Nextion data.
------------------------------------------------------------------------------

![Nextion handler framework](https://user-images.githubusercontent.com/100061886/154831899-4fbf9ff9-cb42-4a55-88d7-86fd3c81443d.png "Nextion handler framework")

See expandable details and examples for each CUSTOMISABLE and BOILERPLATE component below.

------------------------------------------------------------------------------
## Template Files with Demo
Template files for getting a simple demo up and running are [here](https://github.com/krizkontrolz/Home-Assistant-nextion_handler/tree/main/v0-4), including [instructions on how to use them](https://github.com/krizkontrolz/Home-Assistant-nextion_handler/blob/main/v0-4/Installation.md).

------------------------------------------------------------------------------
## HaCmd Instruction Set
(```Nx``` = Nextion variable name (_excluding_ '.val'/'.txt'); ```E``` = $alias/HA entity_id; as a **shorthand**, ```$``` alone can be used fore ```E``` in set_ commands to indicate the alias should be the same as the associated ```Nx```; and in Action commands, the entity class can be ommited where it is implicit, e.g. you can drop ```script.``` from ```E``` when calling the ```scpt E``` command).
### SET COMMAND LIST
SET commands are entered in the Nextion Editor in strings ```HA_SET1``` .. ```HA_SET5``` on each page.  They configure how you want to pull data from Home Assistant each time that Nextion page is updated by configuring how HA data is assigned to Nextion global variables.

*  ```sett Nx len E```  (assign ```len``` chars of state of ```E```, as string/text, to ```Nx```).
*  ```setn Nx scale E``` (assign ```Nx``` the integer value of ```scale``` * state of ```E```).
*  ```setb Nx E``` (assign ```Nx``` a value of 0 or 1 based the binary interpretation of
        the state of ```E``` (given by str(state of E) in FALSE_STATES)).
*  ```setb Nx E cp x``` (assign ```Nx``` the value of the binary expression from
        comparing the state of ```E``` to ```x``` where ```cp``` in ```[eq, ne, lt, le, gt, ge]```)

<details>
  <summary>Example SET HaCmd (Click to expand)</summary>

---

>```setb ST.bDSH $``` (using shorthand notation).  
(Equivalent to long form of ```setb ST.bDSH.val binary_sensor.dishes_washed```.)

  Set the Nextion variable ```ST.bDSH.val``` to boolean-interpreted state of the HA entity with
  the alias ```ST.bDSH``` (where the enitity_id for each alias is configured under the ```aliases:``` section of the service call to nextion_handler in the HA automation, e.g., ```'ST.bDSH': 'binary_sensor.dishes_washed'``` - see the ALIAS example below for more detail).

--- 
  
</details>

### ACTION COMMAND LIST
ACTION commands are assigned to the ```HA_ACT``` string in Nextion Editor 'events' tabs.  They configure what commands are sent to Home Assistant when events, such as button pushes, are triggered on the Nextion.


*  ```tgl E``` (toggle ```E```)
*  ```ton E``` (turn on ```E```)
*  ```tof E``` (turn off ```E```)
*  ```inps E string``` (set value of input_select ```E``` to ```string```)
*  ```inpb E 0/1``` (set value of input_binary to (state of ```E``` != 0))
*  ```inpn E x``` (set value of input_number ```E``` to ```x```)
*  ```scpt E``` (call script ```E```)
*  ```scn E``` (turn on scene ```E```)
*  ```say E string``` (Play TTS of message ```string``` to media player ```E```)
*  ```ntf string``` (Display a persistent notification with message ```string``` to HA)
*  ```sub Nx``` ('click' the Nextionx (hidden) hotspot ```Nx``` to execute a 'subroutine')
*  TODO: RGBWW light controls with colour wheel UI (I prefer using scenes, but am working on this feature)

<details>
  <summary>Example ACTION HaCmd (Click to expand)</summary>
  
---
  
>```tgl $ST.bDSH``` (using shorthand notation).  
(Equivalent to long form of ```tgl binary_sensor.dishes_washed```.)

  Toggles the binary sensor (on/off) that we set up to fetch HA data updates for above.
  
---
  
</details>

------------------------------------------------------------------------------
## CUSTOMISABLE components (with shorthand notation)

Click to expand sections below for examples of each of the components of the framework that can be customised.

<details>
  <summary>Example NEXTION EVENT to SEND an ACTION command to Home Assistant (Nextion Editor - event tab)</summary>
  
---

>Nextion events assign ACTION HaCmds to  ```HA_Act.txt```, then send with  ```SEND_ACTIONS``` (boilerplate subroutine - see boilerplate section below)

This example shows how to program calling Home Assistant actions from within Nextion Editor Events.
The 'basic' version of the Event in the screenshot duplicates similar logic to the HA Lovelace UI, where pressing a toggle button simply toggles a Home Assistant entity.  This is done in the Nextion Event panel by assigning one or more Nextion Handler commands (separated by commas) to the ```HA_Act.txt``` variable then entering ```click SEND_ACTIONS,1``` (a 'subroutine' attached to a hidden Nextion hotspot component).  When the event is triggered the commands in HA_Act will be sent by boilerplate code in ```SEND_ACTIONS``` (that you never need to edit), which will do all the magic of sending the commands to the nextion_handler in Home Assistant (via ESPHome), getting back the updated data needed for the Nextion page, and applying that data to update the UI components on the Nextion.

The second version of the Event in the screenshot 'Adds some Nextion smarts' to do something a bit more complicated in the code, but to the user would still be intuitively thought of as toggling.  When the switch is toggled to 'on', it will run a script in Home Assistant that will run through a program of all the irrigation stations sequentially; when it is toggled to 'off', it stop *all* possible scripts that control irrigation valves and then turn off all the valves (a very thorough way of making sure everything is *really* off).  This just demonstrates that the Nextion Handler framework doesn't stop you in any way from being as creative as you like.  You can have really complicated Nextion Events that conditionally add progressively additional HA commands to the HA_Act string (each separated by a comma), then use the ```SEND_ACTIONS``` 'subroutine` to take care of all the book-keeping to make your magic happen.  (Or, you can start as simple as the basic example with just 2 lines in your Nextion event code).

<img src="https://github.com/krizkontrolz/Home-Assistant-nextion_handler/blob/main/v0-4/Example_HA_Act_Event.png" alt="drawing" width="656"/>

---
  
</details>



<details>
  <summary>Example HA_SET string for pulling HA data into Nextion on each page update (Nextion Editor - string)</summary>
  
---
  
TO DO! - add screen shot example with explanation

---
  
</details>


<details>
  <summary>Example APPLY_VARS to update Nextion UI with updated data from HA (Nextion Editor - hidden hotspot 'subroutine')</summary>
  
---
  
TO DO! - add screen shot example with explanation

---
  
</details>



<details>
  <summary>Example Nextion Handler service configuration with ALIASES (Home Assistant - automation.yaml)</summary>
  
---
  
>**ALIAS in service automation**: linking ```sensor.rain_delay``` to Nextion ```IR.nRN_DL.val```

Aliases are convenient because they save having to switch back & forth between the Nextion Editor & HA, the alias is typically based on the name of the Nextion (global) variable it is associated with, they save having to reflash the Nextion TFT each time you fix a typo in an entity_id, and you enter the entity_ids in the HA YAML editor (where autocompletion helps avoid typos in the first place).  The YAML automation for the ```nextion_handler``` shows how the example alias is added to the 'dictionary'.
```YAML
#  Nextion Handler service automation (this handles everything coming from and going back to Nextion)
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
        nx_cmd_service: esphome.nsp1_send_command
        action_cmds:
          - sensor.nsp1_ha_act
        update_cmds:
          - sensor.nsp1_ha_set1
        aliases: # << Nextion alias (excl. '$' prefix and '.val'/'.txt' suffix) paired with HA entity_id
          "IR.nRN_DL": "sensor.rain_delay"
          "PAGE.Variable": "sensor.another" # ... etc.
```

---
  
</details>


<details>
  <summary>Example Home Assistant UI card for monitoring nextion_handler</summary>
  
---
  
> **Lovelace UI Markdown Card** for monitoring flow of nextion_handler command_strings & TRIGGERs.

  Example Lovelace card after just having pushed a 'button' (on the Nextion 'ST' page) to clear an alert that the dish washing was done.
```
TRIGGER: >> 1 (ACTION)
HA_Act (<- Last SEND_ACTIONS):
  > tgl $ST.bDSH
HaCmds for Update (<- Page PostInit):
HA_Set1 ---------------
  > setn ST.nGDA 1 $
  > setb ST.bMAIL $
  > setb ST.bRCYC $
  > setn ST.nNTFC 1 $
  > setb ST.bIRR $
  > setb ST.bGUEST $
  > setb ST.bDSH $
  > setb ST.bLNDY $
  > 
HA_Set2 ---------------
  > setb ST.bGRG $
  > setb ST.bPATD $
  > setb ST.bFNTD $
  > setb ST.bPCHM $
  > setn ST.x1SOL 0.01 $
  > setn ST.x1CONS -0.01 $
  > setn ST.x1GRD 0.01 $
  > setn ST.x1EN 0.01 $
  > setb ST.bMLGR $
  > setb ST.bMLLR $
HA_Set3 ---------------
  > 
HA_Set4 ---------------
  > 
HA_Set5 ---------------
  > sub APPLY_VARS
```


---
  
</details>


<details>
  <summary>Example next ...</summary>
  
---
  
TO DO!

---
  
</details>



------------------------------------------------------------------------------
## BOILERPLATE components

Click to expand sections below for boilerplate code (that can be cut and pasted, without editing, to do all the heavy lifting in managing the Nextion interactions with Home Assistant).

<details>
  <summary>UPDATE_LOOP (Nextion Editor - timer)</summary>
  
---

There is no need to edit boilerplate code at all - you can just copy and paste it.
You can modify the behaviour of the ```UPDATE_LOOP``` through Nextion Global Settings (see the ```Program.s``` details below).
The ```UPDATE_LOOP``` is a Nextion ```Timer Event``` attached to a timer on each page to controls all the fetching of data from Home Assistant in a very efficient and scaleable manner to prevent flooding the Nextion, ESP chip or Home Assistant with communications requests.
```
//~~~~~~boilerplate~~~~
// UPDATE LOOP controls:
//  1) Slow passive polling for HA data updates.
//  2) Sleep timer (when TRIGGER value falls below threshold).
//  3) Temporary fast updates after user Actions (incl. page change).
//  4) Manage fast repeated update queue (and stop overstacking).
//  5) Temporary fast update on waking from sleep.
//  6) Progressively dim the display with inaction.
// by controlling values of TRIGGER, *.tim (rate), fast_updates, dim.
// See Program.s* --GlobalSettings-- for variables that control default loop behaviour.
//~~~~~~~~~~~~~~~~~~~~~
// 'TRIGGER' is responded to by HA nextion_handler to send the updates
// specified in the the list of HA_Set(1..5) command_strings that are sent
// to HA in this Page's Preintialize Event.
//
// Enforce a TRIGGER state change with Trigger < 0
// (NEGATIVE TRIGGER vals ==> UPDATE requests; POSITIVE ==> ACTION request to nextion_handler)
if(TRIGGER>-1)
{
  dim=dim_default
  if(fast_updates>0)
  {
    //Need to make sure that a fast_update repeat of 1 does NOT produce two -1 triggers in a row (not state change in HA)
    TRIGGER=-2
  }else
  {
    TRIGGER=-1
  }
}else
{
  TRIGGER-=1
  // Progressively dim display with inaction
  if(fast_updates==0)
  {
    if(dim>=dim_min)
    {
      dim-=1
    }
  }
}
//
// INACTIVITY CHECK (flag1=1 will be used to sleep later, AFTER writing TRIGGER (=0 when sleeping))
flag1=0
// calculate the (negative) threshold for TRIGGER to cross before sleeping
tmp=0
tmp-=sleep_secs
tmp/=upate_secs // -> (negative) number of inactive/polled update loops before sleep
if(TRIGGER<=tmp)
{
  // only set sleep flag when fast_updates are not active
  if(fast_updates<=0)
  {
    TRIGGER=0 //Indicator to HA that Nextion is sleeping
    flag1=1   //Flag to sleep AFTER writing the 0 TRIGGER value
  }
}
//
// SEND TRIGGER Integer value (to HA via ESPhome)
// Nextion Custom Sensor Protocol - see: https://www.esphome.io/components/sensor/nextion.html
printh 91            //Tells the library this is a sensor (int) data
prints "TRIGGER",0   // Sends the name that matches component_name or variable_name
printh 00            //Sends a NULL
prints TRIGGER,0     //The actual value to send. For a variable use the Nextion variable name temperature with out .val
printh FF FF FF      //Nextion command ack
//
// RESTORE POLLING RATE (slow updates) after fast_updates, incl. repeats (set by Page-Preint & SEND_ACTIONS)
tmp=upate_secs
tmp*=1000 // default slow update interval converted to ms
if(fast_updates>1)
{
  // if there is only 1 (or last) repeat, then this loop was it, pass straight through to reset
  fast_updates-=1
}else if(UPDATE_LOOP.tim!=tmp)
{
  // reset after fast update repeats are complete
  UPDATE_LOOP.tim=tmp
  TRIGGER=0 // will be modified to a non-zero (non-sleep) value by the time of the next 'send trigger'
  fast_updates=0
}
//
//SLEEP flag
if(flag1==1)
{
  //prepare for fast update on wake
  UPDATE_LOOP.tim=300
  fast_updates=1
  dim=dim_default
  sleep=1
}
```

---
  
</details>

<details>
  <summary>SEND_ACTIONS (Nextion Editor - hidden hotspot 'subroutine')</summary>
  
---

```SEND_ACTIONS``` is the code attached to a ```Touch Press Event``` for a hidden hotspot on each Nextion page (to serve as a 'subroutine').
Each Nextion Event should first add the sequence of ACTION HaCmds to the ```HA_ACT.txt``` string on that page, followed by ```click SEND_ACTIONS,1``` (which then sends the Action commands to the nextion_handler on Home Assistant to be excecuted).
(See the example Nextion Event above for how this done in the Nextion Editor.)

```
//~~~~~~boilerplate~~~~
// SEND ACTION HaCmds (CSV sequencence set in HA_Act string by calling Event)
//~~~~~~~~~~~~~~~~~~~~~
// This subroutine is called by each Event programmed for Nextion UI elements.
// The HA_Act string_commands are sent to the HA nextion_handler, which performs the
// actions and then conducts fast/repeated data updates (coded in list of HA_Set strings).
// The default number and speed of fast repeat updates follow global settings (see below).
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
// Enforce TRIGGER state change with TRIGGER > 0
// (HA nextion_handler interprets POSITIVE TRIGGER vals as ACTION requests)
if(TRIGGER<0)
{
  TRIGGER=1
}else
{
  TRIGGER+=1
}
// Send TRIGGER Integer value (to HA via ESPhome using Nextion Custom Sensor Protocol)
printh 91
prints "TRIGGER",0
printh 00
prints TRIGGER,0
printh FF FF FF
//
// Set UPDATE_LOOP for fast repeated updates (for HA data changes after sending HA_ACT)
if(override_frpts==0)
{
  // Use default global fast update settings, unless override flag is set
  fast_updates=fastupdate_rpt
  UPDATE_LOOP.tim=fastupdate_tim
}else
{
  //Allow calling Events to set Action-specific follow-up updates (then revert to defaults)
  override_frpts=0
}
```
  
---
  
</details>

<details>
  <summary>Global settings (Nextion Editor - Program.s tab)</summary>
  
---
  
Nextion Global Settings are set in the ```Program.s``` tab in the Nextion Editor.
Some of these settings can be used to fine tune the behaviour of the boilerplate ```UPDATE_LOOP``` code (including adjusting these 'live' while the Nextion is running, see comments in code), while other variables are only for internal use.
  
```
//~~~~~~boilerplate~~~~
// DEVICE CONFIG & GLOBAL SETTINGS (directly controllable from HA)
//~~~~~~~~~~~~~~~~~~~~~
//
// CHANGELOG for Nextion Handler framework:
// v0.4 2022-02-22
//   ....
// ------------------------------------------------------------------------------------------
// Nextion Progra.s* notes:
// The following code is only run once when power on, and is generally used for global variable definition and power on initialization data
// At present, the definition of global variable only supports 4-byte signed integer (int), and other types of global quantity declaration are not supported. If you want to use string type, you can use variable control in the page to implement
// ------------------------------------------------------------------------------------------
//
// ----- Global Settings controlling UPDATE_LOOP behaviour ------
// DESIGNED TO BE ADJUSTED/fined-tuned live from HA (by sending Nextion Intructions)
int upate_secs=15         //Passive polling interval when inactive
int sleep_secs=300        //Inactivity period before sleeping (also see thsp and ussp below)
int fastupdate_rpt=3      //Default number of fast repeats after SEND_ACTIONS
int fastupdate_tim=2000   //Default fast update interval after SEND_ACTIONS
int dim_default=20        //Default screen brightness when there is activity
int dim_min=5             //Minimum screen brightness screen dims to without actvity
//
// ----- Internal Working Variables ------
// DO NOT modify these from HA
//int sys0=0,sys1=0,sys2=0  << default scratch globals
int TRIGGER=0,fast_updates=0,override_frpts=0
int tmp=0,flag1=0,flag2=0
int x=0,y=0,dx=0,dy=0,press_time=0
//
//
// ----- Device Config ------
//ESPHome Nextion config - as stated at https://esphome.io/components/display/nextion.html
baud=115200   // Sets the baud rate to 115200
bkcmd=0       // Tells the Nextion to not send responses on commands. This is the current default but can be set just in case
//
//Sleep settings, see: https://nextion.tech/2021/08/02/the-sunday-blog-energy-efficient-design-with-nextion-hmi-portable-and-wearable-designs/
//Backstop sleep settings (if not set in UPDATE_LOOP)
thsp=7200  //Sleep after this many secs without touch
thup=1     //Enables(1) touch to wake device
ussp=7200  //Sleep after this many secs without serial port activity
usup=0     //Disable(0) wake on serial data - NB*** will still wake if command string "sleep=1ÿÿÿ" is sent over serial
page 255   //Power on start page (255 = last page)
```
---
  
</details>

<details>
  <summary>Page PostInitialise Event (Nextion Editor - Page tab)</summary>
  
---

```
//~~~~~~boilerplate~~~~
// INITIALISE UPDATE settings by sending list of HA_Set command_strings to HA nextion_handler
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
printh 92            //Tells the library this is text sensor
prints "HaSet1",0    //Sends the name that matches component_name or variable_name
printh 00            //Sends a NULL
prints HA_SET1.txt,0  //The actual text to send. For a variable use the Nextion variable name text0 with out .txt
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
// Initialise UPDATE_LOOP and force an initial FAST update (UPDATE_LOOP will reset to slow polling)
dim=dim_default
//TRIGGER=0  //MUST let fast updates take care of FORCING Trigger change
//     simply setting TRIGGER=0 was causing MISSED updates 2+ quick page changes in a row
fast_updates=2  // 2 guarantees at least one state change after rapid page changes
UPDATE_LOOP.tim=100
//
// Call subroutine to Apply (stale) variables to UI elements while waiting for data update
click APPLY_VARS,1
```

---
  
</details>

<details>
  <summary>ESPHome configuration to send commands & data between HA and Nextion (ESPHome YAML file)</summary>
  
---
  
TO DO! - copy required sections of YAML

---
  
</details>

<details>
  <summary>nextion_handler.py (Home Assistant Python script)</summary>
  
---
  
TO DO! - link to script and brief description of how it works

---
  
</details>

  
------------------------------------------------------------------------------
## Credits & Related Resources:
### ESPHome: Flasshing, Base Configuration, Functionality
* [ESPHome Nextion device](https://www.esphome.io/components/display/nextion.html)
* [ESPHome Nextion class](https://esphome.io/api/classesphome_1_1nextion_1_1_nextion.html)
* Masto [Github config](https://github.com/masto/NSPanel-Demo-Files/blob/main/Dimming%20Update/Screensaver%20Page/nspanel-demo.yaml) and [video](https://www.youtube.com/watch?v=Kdf6W_Ied4o&t=2341s)
* [Fix for Sonoff NSPanel display to escape Protocol Reparse Mode so standard communication protocol will work](https://github.com/esphome/esphome/pull/2956)

### UI Design
* Material Design
  [reference](https://material.io/design),
  [icons](https://materialdesignicons.com/),
  [fonts](https://fonts.google.com/specimen/Roboto+Condensed)
* Inkscape
  [software](https://inkscape.org/release/) and 
  [tutorials](https://inkscape.org/learn/tutorials/)

### Nextion
* Nextion 
  [HMI editor](https://nextion.tech/nextion-editor/),
  [Editor Guide](https://nextion.tech/editor_guide/),
  [Nextion Instruction Set](https://nextion.tech/instruction-set/),
  [Blog examples](https://nextion.tech/blogs/)
* Unofficial Nextion [user forum](https://unofficialnextion.com/)
------------------------------------------------------------------------------

## CHANGELOG:
* v0.4 2022-02-18...
   * Return to a single automation in HA YAML
   * Nx UPDATE_LOOP now controls timing of: slow UPDATEs, ACTIONs, fast UPDATEs (with delays & repeats) after user interactions
   * Fast update speed & repeat settings can now override the defaults in SEND_ACTIONS (to allow customised updates after actions involving high-lag devices, e.g., garage door, blinds, etc.)
   * The 'sub APPLY_VARS' HaCmd (which should be at the end of HA_SET1...) gives the nextion_handler control
     of timing of Nx UI updates (to immediately follow sending the update data requested in HA_SET1...)
   * Key default parameters controlling UPDATE_LOOP move to Global_Settings in Program.s* (so that they can be adjusted/tweaked live from HA by sending Nextion Instructions).
   * Started marking ~~~boilerplate ~~~ parts of HMI code more clearly & consistently.
* v0.3 2022-02-14 ...
  * Separated lists of ACTION & UPDATE command strings (for easier separation in triggering, processing and delay between them)
  * Simplified main program loop to only Actions OR Update (based on trigger)
  * Removed delays & repeats from this script (processing them in a Py script is not a good fit with HA multithreaded Py environment)
  * Use THREE separate HA YAML components (call this script from separate places):
    * ACTION automation (... -> delayed update script)
    * UPDATE automation
    * DELAYED update script (with repeats) - called at the end of this Py script IF it was an ACTION
* v0.2 2022-02-10 ...
  * Transferred  control of  looping and sequencing from Nx to this script (with new sub, rpt and noupdt HaCmds)
* v0.1 2022-01 ...
  * First version where all loop/sequencing control was attempted on the Nextion (double inter-linked timer loops)
------------------------------------------------------------------------------

