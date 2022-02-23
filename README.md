# Home Assistant Nextion Handler
(*Last updated: 2022-02-23*)

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

------------------------------------------------------------------------------
## Template Files with Demo
Template files for getting a simple demo up and running are [here](https://github.com/krizkontrolz/Home-Assistant-nextion_handler/tree/main/v0-4), including [instructions on how to use them](https://github.com/krizkontrolz/Home-Assistant-nextion_handler/blob/main/v0-4/Installation.md).

------------------------------------------------------------------------------
## HaCmd Instruction Set
(```Nx``` = Nextion variable name (_excluding_ '.val'/'.txt'); ```E``` = $alias/HA entity_id; as a **shorthand**, ```$``` alone can be used fore ```E``` in set_ commands to indicate the alias should be the same as the associated ```Nx```; and in Action commands, the entity class can be ommited where it is implicit, e.g. you can drop ```script.``` from ```E``` when calling the ```scpt E``` command).
### SET COMMAND LIST

*  ```sett Nx len E```  (assign ```len``` chars of state of ```E```, as string/text, to ```Nx```).
*  ```setn Nx scale E``` (assign ```Nx``` the integer value of ```scale``` * state of ```E```).
*  ```setb Nx E``` (assign ```Nx``` a value of 0 or 1 based the binary interpretation of
        the state of ```E``` (given by str(state of E) in FALSE_STATES)).
*  ```setb Nx E cp x``` (assign ```Nx``` the value of the binary expression from
        comparing the state of ```E``` to ```x``` where ```cp``` in ```[eq, ne, lt, le, gt, ge]```)


### ACTION COMMAND LIST

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

------------------------------------------------------------------------------
## EXAMPLES (with shorthand notation)
>**SEND HaCmd**:  ```setb ST.bDSH $```

  (Equivalent to long form of ```setb ST.bDSH.val binary_sensor.dishes_washed```.)

  Set the Nextion variable ```ST.bDSH.val``` to boolean-interpreted state of the HA entity with
  the alias ```ST.bDSH``` (where the enitity_id for each alias is configured under the ```alias``` section of the service call to nextion_handler in the HA automation, e.g., ```'ST.bDSH': 'binary_sensor.dishes_washed'```).

>**ACTION HaCmd**:  ```tgl $ST.bDSH```

  (Equivalent to long form of ```tgl binary_sensor.dishes_washed```.)

  Toggles the binary sensor (on/off) that we set up to fetch HA data updates for above.

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

