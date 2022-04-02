## CHANGELOG:

## [0.5.0] - 2022-04-02

### Added

- SET & ACT NH commands for Lights: setlt, lt_brt, lt_ct, lt_rgb, lt_hs, lt_cw, lt_wt
- SET & ACT commands for Persistent Notifications: setntf, ntf, ntfx
- SET command for fetching Home Assistant date_time: setdt
- Full GESTURE controls in HMI (with new separate documentation and template HMI).

### Changed

- Added flexibility/efficiency to NH commands by making more arguements optional.
- Added optional argument in some SET NH commands to specify default value (to return when HA doesn't return a valid state for an entity). 
- TRIGGER was 'overworked' in HMI, trying to cover functions of both trigger & counter. Now Separated into TRIGGER (just state toggle and status) & LOOP_CNT (fast & slow refreshes).
- Updated all template files

### Fixed

- Tested and debugged all NH commands.
- Improved UPDATE_LOOP timing.


## [0.4.0] - 2022-02-18
### Added
- First public release of all Python script initial Nextion Handler Instruction Set
- First public release of Nextion Editor HMI template with Customizable & Template code   
### Changed
- Return to a single automation in HA YAML
- Nx UPDATE_LOOP now controls timing of: slow UPDATEs, ACTIONs, fast UPDATEs (with delays & repeats) after user interactions
- Fast update speed & repeat settings can now override the defaults in SEND_ACTIONS (to allow customized updates after actions involving high-lag devices, e.g., garage door, blinds, etc.)
- The 'sub APPLY_VARS' NhCmd (which should be at the end of HA_SET1...) gives the nextion_handler control of timing of Nx UI updates (to immediately follow sending the update data requested in HA_SET1...)
- Key default parameters controlling UPDATE_LOOP move to Global_Settings in Program.s* (so that they can be adjusted/tweaked live from HA by sending Nextion Instructions).
- Started marking '**boilerplate**' parts of HMI code more clearly & consistently.

## [0.3.0 unreleased] - 2022-02-14
### Changed
- Separated lists of ACTION & UPDATE command strings (for easier separation in triggering, processing and delay between them)
- Simplified main program loop to only Actions OR Update (based on trigger)
- Removed delays & repeats from this script (processing them in a Py script is not a good fit with HA multithreaded Py environment)
- Use THREE separate HA YAML components (call this script from separate places):
    * ACTION automation (... -> delayed update script)
    * UPDATE automation
    * DELAYED update script (with repeats) - called at the end of this Py script IF it was an ACTION

## [0.2.0 unreleased] - 2022-02-10
### Changed
- Transferred  control of  looping and sequencing from Nx to this script (with new sub, rpt and noupdt NHCmds)

## [0.1.0 unreleased] - 2022-01-01
- First version where all loop/sequencing control was attempted on the Nextion (double inter-linked timer loops)

------------------------------------------------------------------------------
Based on [juampynr's template](https://gist.github.com/juampynr/4c18214a8eb554084e21d6e288a18a2c)
The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).  
