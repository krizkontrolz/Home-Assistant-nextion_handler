#
#* Home Assistant Nextion Handler
#* (v0.5.0; Last updated: 2022-04-02)
# Handler for NH 'command_strings' sent from Nextion events & update requests.
# see: https://github.com/krizkontrolz/Home-Assistant-nextion_handler
#
# ------------------------------------------------------------------------------
#
#* Notes to add to next CHANGELOG (https://github.com/krizkontrolz/Home-Assistant-nextion_handler/blob/main/CHANGELOG.md):
# ...
# ------------------------------------------------------------------------------
#
# TODO:
#    Complete support for simpler no-code 'widget'-based configuration option (that use specialize template TFT files.)
# ------------------------------------------------------------------------------




#*------------------------------------------------------------------------------
#* CONFIGURABLE CONSTANTS
#*------------------------------------------------------------------------------


NX_UI_UPDATE = 'APPLY_VARS'  # name of Nx 'subroutine' to click to apply the refreshed data to the UI after a data update

#* Widgets variables
widgets_read = False  # do not read 'widgets:' from YAML until needed, then flag when this is done
WIDGETS_LIST = []

#* Valid Nextion data attribute extensions/suffixes (exluding preceding '.')
STANDARD_NX_DATA_EXTs = ['val', 'txt']

#* List of entity states (as strings) to be interpreted as false (return a value of 0 when assigned to a binary Nx variable)
FALSE_STATES = ['off', 'False', '0', '']

#* List of entity states (as strings) to be interpreted as missing
INVALID_STATES = ['unknown', 'not available', 'None', 'unavailable', 'unknown', 'undefined']


#* Alternative Aliases Dictionary for translating shorthand entitity aliases ($nx -> e)
#! Preferred approach is to specify this dictionary under 'aliases' in service call to this script
# (but, if not provided in YAML, this dictionary will be used instead)
# Do NOT include the leading '$' from the alias in the dictionary keys
# 'Data attribute Extensions' of '.txt' for sett and '.val' for other set_ functions area assumed and appended to Nextion variable names provided in string_commands
ENTITY_ALIASES_ALT = {
    # #Page XX_______________________________________________________________________
    # 'XX.alias1': 'sensor.my_sensor',
    # 'XX.alias2': 'light.my_light'
}


#*------------------------------------------------------------------------------
#* HANDLER FUNCTIONS for each NhCmd instruction
#*------------------------------------------------------------------------------
# Extend funtionality of Hanlder by adding extra custom SET & ACT functions.
# (Then add to FUNC_DICT dictionary below).


#*_________________________
#* GENERAL HELPER FUNCTIONS


def nx_cmd(nx_command_str, domain, service):
    '''Send the Nextion command string to the send cmd service for the Nextion device'''
    try:
        service_data = {'cmd': nx_command_str}
        hass.services.call(domain, service, service_data, False)
        # #!
        # dbg_msg = 'Nextion Handler sent Nextion command:\n<{}>.'.format(nx_command_str)
        # hass.services.call('persistent_notification', 'create', {'title': 'Nextion Handler Debug', 'message': dbg_msg, 'notification_id': 'nx_handler_debug' }, False)
    except Exception as exptn:
        err_msg = '{}\nNextion Handler failed sending the Nextion command:\n\
            <{}>\n to the service _{}.{}_.'.format(exptn, nx_command_str, domain, service)
        logger.error('nextion_handler.py ' + err_msg)
        hass.services.call('persistent_notification', 'create', {'title': 'Nextion Handler Error!', 'message': err_msg, 'notification_id': 'nx_handler_error_helper' }, False)
        raise Exception(err_msg)
    return True


def nx_var_parse (nx_shorthand, data_type = None):
    '''Interpret 'shorthand' Nextion variable names by appending their data type
    return: the full Nextion variable name (for nx_cmd) and 
            the standardized lookup name for that Nextion variable
                (the standard key that would link that Nextion variable to its
                paired Home Assistant entity_id in ENTITY_ALIASES dictionary)
            the data type ('val' for ints, or 'txt' for strings)'''
    nx_full = None
    nx_lookup = None
    nx_parts = nx_shorthand.split('.')
    ext = nx_parts[-1]
    # Set data_type, #*Assume all Nextion variable attributes that don't end in '.txt' are ints(val), including Program*s globals #! check this assumption
    if data_type is None:
        if ext == 'txt':
            data_type = 'txt'
        else:
            data_type = 'val'
    # Set full & lookup Nx names
    if ext in STANDARD_NX_DATA_EXTs:
        # The Nextion variable name already included its datatype extension
        nx_lookup = nx_shorthand  # INCLUDE the extension where explicity specified so that unique naming/aliasing of multiple attributes of the same object is preserved
        nx_full = nx_shorthand
    else:
        nx_lookup = nx_shorthand  # EXCLUDE the data extension where shorthand (without ext) was specified
        #* Possible shorthands with ASSUMED interpretation: (nx_shorthand, data_type) -> (nx_full, nx_lookup)
        # - t1 txt: -> t1.txt t1  (local string)
        # - sss val: -> sss sss  (Global* int) #! Cannot use 'nLocal' as shorthand for local page val
        # - PP.aaa __: -> PP.aaa.val PP.aaa (Page local/global)
        # - aaa.val __: -> PP.aaa.val aaa.val (Page local/global)
        if len(nx_parts) == 2:
            # The Nextion variable was 'shorthand', without a datatype extension (val or txt)
            nx_full = nx_shorthand + '.' + data_type  #'.'.join((nx_shorthand, data_type))
        elif len(nx_parts) == 1:
            if data_type != 'txt':
                # Assume nx_shorthand is a Program.s* Global variable (int, with no page_name_prefix, or data_ext_suffix)
                #! Cannot use 'nLocal' as shorthand for local page val - must include ext to distinguish from Program.s Global
                nx_full = nx_shorthand
            else:
                # Append 'txt' ext (Prog Globals cannot be text, so this must be a page-local string (e.g. t1.txt))
                nx_full = nx_shorthand + '.txt'
        elif len(nx_parts) >= 3:
            if data_type == 'txt' and nx_shorthand[-3:] != 'txt':
                # Add 'txt' extension if it is missing from variable that is known to be 'txt' data_type
                nx_full = nx_shorthand + '.txt'
            else:
                # Assume nx_shorthand has an unlisted extension and that it is to be treated as a 'val' (int)
                nx_full = nx_shorthand
    #! dbg msgs
    # msg = 'Nextion Handler HELPER function {}:\n\nnx_full <{}>\nnx_lookup <{}>\next <{}>'.format('nx_var_parse', nx_full, nx_lookup, ext)
    # logger.warning('nextion_handler.py ' + msg)
    # hass.services.call('persistent_notification', 'create', {'title': 'Nextion Handler Debug!', 'message': msg, 'notification_id': 'nx_handler_dbg' }, False)
    return nx_full, nx_lookup, data_type


#TODO: test WIDGET-based entity lookup (when WIDGETs are fully implemented)
def get_entity_id_state(e, nx_lookup=None, class_prefix=None):
    '''Translate the (shorthand) HA entity parameter by:
        * treating e as a $ alias (leading $ stripped to create lookup key) to
            find its matching entity_id in the ENTITY_ALIASES dictionary, or
        * if e == '$' use nx_lookup (the standardized lookup key for a Nextion
            variable) as the key (no leading $) for ENTITY_ALIASES dictionary,
        * if e is an @n widget alias (@ followed by reference to nth widget in
            widget list provided in the 'widgets:' section of YAML), or
        * assigning e directly (adding the expected class prefix if missing).

    Dictionary ALIASES are the EXPECTED way of specifying 'e' in NhCmds:
        An alias is indicated in the NhCmd if 'e' has a preceding '$'
        The ENTITY_ALIASES lookup key REMOVES the '$' (easier to manage the dictionary that way)
        (Directly specifying the entity_id is not preferred, but supported).
    Checks the entity_id is valid, and raise ValueError if not.

    * SET NhCmds typically provide nx_lookup (from the Nx variable being set).
    * ACTION NhCmds typically provide the class_prefix of the entity being acted on. 
    Return the entity_id and its state.
    '''
    name = ''
    if e[0] == '$':
        # Expected/typical use case is 'e' provided as an alias, indicated by a '$' prefix
        if e == '$':
            # e == '$' indicates the the Nextion variable name should be used as the base of the alias
            key = nx_lookup
        else:
            # '$...' indicates an explicitly named alias - remove the $ to get the lookup key
            key = e[1:]
        try:
            entity_id = ENTITY_ALIASES[key]
        except:
            raise ValueError('$Alias not found: <{}>'.format(e))
    #TODO: Widget alias #@wd - complete, but need to test this **
    elif e[0] == '@':
        # '@n' Widget aliases indicates the nth entity in the calling automations YAML 'widgets:' list (indexed from 0)
        if not widgets_read:
            #* Get list of Widgets (& their settings) from 'widgets:' YAML section
            try:
                WIDGETS_LIST = data.get('widgets')
            except:
                # Log error message
                err_msg = 'Error trying get "widgets:" list from YAML in calling automation.'
                #logger.warning('nextion_handler.py ' + err_msg)
                raise ValueError(err_msg)
            widgets_read = True
        try:
            n = int(e[1:])  # the rest of the entity alias after @ should be the widget number (0...) and its index position in the YAML list
            entity_id = WIDGETS_LIST[n]['entity_id']  # entity_id is REQUIRED - no default provided - will trigger exception if missing
        except:
            raise ValueError('@Alias for Widget not found in "widgets:" list from YAML in calling automation: <{}>'.format(e))
    elif class_prefix and e[:len(class_prefix)] != class_prefix:
        # The expected entity class_prefix is not present, so needs to be prepended to e
        entity_id = class_prefix + e
    else:
        # e is the full entity_id already (no adjustment needed)
        entity_id = e

    # Get the state of entity_id - this also ensures that entity_id is valid
    try:
        state = hass.states.get(entity_id).state
    except:
        raise ValueError('Home Assistant could not find specified entity_id.')

    return entity_id, state



#_________________
#* SET FUNCTIONS - set variables in Nx to value of requested HA entity states (don't perform any other actions in HA)
# Nx = name of Nextion (global) variable EXCLUDING '.val' or '.txt' extension
# E = HA entity, preferably as a $alias (but can handle shorthand/full entity_id too)


def sett(args_list, domain, service):
    '''sett Nx chars E  (assign len chars of state of E, as string/text, to Nx)'''
    try:
        # #!
        # dbg_msg = 'Nextion Handler:\n<{}>.'.format('Made it to start of sett')
        # hass.services.call('persistent_notification', 'create', {'title': 'Nextion Handler Debug', 'message': dbg_msg, 'notification_id': 'nx_handler_debug' }, False)
        if len(args_list) == 3:
            [nx, chars_, e] = args_list
            try:
                chars = int(chars_)
            except:
                #chars = 255
                raise ValueError('Number of chars is not an integer.')
            nx_full, nx_lookup, data_type = nx_var_parse(nx, 'txt')
            #state = entity_state(e, nx_lookup)
            entity_id, state = get_entity_id_state(e, nx_lookup=nx_lookup)  # will raise exception if it can't translate e to valid entity_id
            if state is not None:
                new_value = '"' + str(state)[:chars] +'"'  # Nextion commands need double quotes for text
                nx_cmd_str = '{}={}'.format(nx_full, new_value)
                nx_cmd(nx_cmd_str, domain, service)
        else:
            raise ValueError('Wrong number of items in arguments list.')
    except ValueError as exptn:
        err_msg = '{}\nNextion Handler failed within SET function:\n<{}> <{}>.'.format(exptn, 'sett', '> <'.join(args_list))
        logger.warning('nextion_handler.py ' + err_msg)
        #hass.services.call('persistent_notification', 'create', {'title': 'Nextion Handler Error!', 'message': err_msg, 'notification_id': 'nx_handler_error_set' }, False)
        raise ValueError(err_msg)
    return True


def setn (args_list, domain, service):
    '''setn Nx scale E (d) (assign Nx the integer value of scale * state of E)
    The scaling factor can cater for the way Nx uses ints to represent floats
    and for changing of units (e.g for energy, kW fits better on small display than Watts)
    (e.g. HA state in Watts * scalefactor of 0.01 gives Nx 1 dp float in kW)
    Optionally specify a value, d, to return if state of E is not numeric,
    otherwise the setn commands will be skipped on errors.
    '''
    try:
        if len(args_list) in [3, 4]:
            if len(args_list) == 4:
                # Default value, d, provided to use when state of E is not numeric
                [nx, scale_, e, d] = args_list
            else:
                # No default value provided (SKIP non-numeric values and leave Nx unchanged)
                [nx, scale_, e] = args_list
                d = None
            try:
                scale_factor = float(scale_)
            except:
                raise ValueError('The scaling factor provided is not a valid number: {}.'.format(scale_str))
            nx_full, nx_lookup, data_type = nx_var_parse(nx)
            #state = entity_state(e, nx_lookup)
            entity_id, state = get_entity_id_state(e, nx_lookup=nx_lookup)  # will raise exception if it can't translate e to valid entity_id
            try:
                new_value = int(float(state) * scale_factor)
            except:
                if d is not None:
                    if d == 'e':
                        # log bad values as errors ONLY if explicity instructed by use of d = 'e'
                        err_msg = 'The entity state did not return a valid number (logging of these errors requested by user specifying <e> for agrument d): {}, {} : {}.'.format(e, nx_lookup, state)
                        raise ValueError(err_msg)  # move on WITHOUT sending value to Nextion
                    else:
                        # use provided default instead
                        new_value = int(d)
                else:
                    # no default value - SKIP command & leave Nx unchanged WITHOUT logging an error
                    #<<
                    raise ValueError('SKIP')  #  exception intended to be skipped (and passed to a higher level)
            nx_cmd_str = '{}={}'.format(nx_full, new_value)
            nx_cmd(nx_cmd_str, domain, service)
        else:
            raise ValueError('Wrong number of items in arguments list.')
    except ValueError as exptn:
        if str(exptn) == 'SKIP':
            #<<
            raise ValueError('SKIP')  # not an error - raise again
        else:
            err_msg = '{}\nNextion Handler failed within SET function:\n<{}> <{}>.'.format(exptn, 'setn', '> <'.join(args_list))
            logger.warning('nextion_handler.py ' + err_msg)
            #hass.services.call('persistent_notification', 'create', {'title': 'Nextion Handler Error!', 'message': err_msg, 'notification_id': 'nx_handler_error_set' }, False)
            raise ValueError(err_msg)
    return True


def setb (args_list, domain, service):
    '''(a) setb Nx E (d) (assign Nx the value of the binary interpretation of the state of E)
    (b) setb Nx E cp x (d) (assign Nx the value of the binary expression from comparing
        the state of E to x where cp in [eq, ne, lt, le, gt, ge])
    Optionally specify a value, d, to return if state of E is not numeric,
    otherwise the setb command will be skipped on errors.
    '''
    # INVALID_STATES
    try:
        # (a) Directly set boolean value
        if len(args_list) in [2, 3]:
            if len(args_list) == 3:
                # default value, d, provided - to be assigned to Nx if entity returns invalid state
                [nx, e, d] = args_list
            else:
                [nx, e] = args_list
                d = None
            nx_full, nx_lookup, data_type = nx_var_parse(nx)
            entity_id, state = get_entity_id_state(e, nx_lookup=nx_lookup)  # will raise exception if it can't translate e to valid entity_id
            if str(state) in INVALID_STATES:
                if d is not None:
                    if d == 'e':
                        # log bad values as errors ONLY if explicity instructed by use of d = 'e'
                        err_msg = 'The entity state did not return a valid number (logging of these errors requested by user specifying <e> for agrument d): {}, {} : {}.'.format(e, nx_lookup, state)
                        raise ValueError(err_msg)  # move on WITHOUT sending value to Nextion
                    else:
                        # use provided default instead
                        new_value = d
                else:
                    # no default value - SKIP command & leave Nx unchanged WITHOUT logging an error
                    #<<
                    raise ValueError('SKIP')  #  exception intended to be skipped (and passed to a higher level)
            else:
                new_value = 0 if str(state) in FALSE_STATES else 1
            nx_cmd_str = '{}={}'.format(nx_full, new_value)
            nx_cmd(nx_cmd_str, domain, service)
        # (b) Set boolean value based on a specified COMPARISON (E cp x)
        elif len(args_list) in [4, 5]:
            if len(args_list) == 5:
                # default value, d, provided - to be assigned to Nx if entity returns invalid state
                [nx, e, cp, x, d] = args_list
            else:
                [nx, e, cp, x] = args_list
                d = None
            nx_full, nx_lookup, data_type = nx_var_parse(nx)
            entity_id, state = get_entity_id_state(e, nx_lookup=nx_lookup)  # will raise exception if it can't translate e to valid entity_id
            if str(state) in INVALID_STATES:
                if d is not None:
                    if d == 'e':
                        # log bad values as errors ONLY if explicity instructed by use of d = 'e'
                        err_msg = 'The entity state did not return a valid number (logging of these errors requested by user specifying <e> for agrument d): {}, {} : {}.'.format(e, nx_lookup, state)
                        raise ValueError(err_msg)  # move on WITHOUT sending value to Nextion
                    else:
                        # use provided default instead
                        new_value = d
                else:
                    # no default value - SKIP command & leave Nx unchanged WITHOUT logging an error
                    #<<
                    raise ValueError('SKIP')  #  exception intended to be skipped (and passed to a higher level)
            else:
                if data_type == 'txt':
                    state = str(state)
                else:
                    try:
                        x = float(x)
                        state = float(state)
                    except:
                        # try treating both the state and comparison value as strings
                        state = str(state)
                if cp in ['eq', '==']:
                    new_value = 1 if state == x else 0
                elif cp in ['ne', '!=']:
                    new_value = 1 if state != x else 0
                elif cp in ['lt', '<']:
                    new_value = 1 if state <  x else 0
                elif cp in ['le', '<=']:
                    new_value = 1 if state <= x else 0
                elif cp in ['gt', '>']:
                    new_value = 1 if state >  x else 0
                elif cp in ['ge', '>=']:
                    new_value = 1 if state >= x else 0
                else:
                    raise ValueError("Provided boolean comparator _{}_ is invalid.".format(cp))
            nx_cmd_str = '{}={}'.format(nx_full, new_value)
            nx_cmd(nx_cmd_str, domain, service)
        else:
            raise ValueError('Wrong number of items in arguments list.')
        # #!
        # #DBG
        # if nx == 'ST.bGRG':  #< fixed to ST.bGRGD in HA_Set2 and in automation aliases
        #     err_msg = 'Nextion Handler Debug: SET function:\n<{}> <{}>\n.nx_full: <{}>; nx_lookup: <{}>\n<{}>'.format('setb', '> <'.join(args_list), nx_full, nx_lookup, nx_cmd_str)
        #     logger.warning('nextion_handler.py ' + err_msg)
    except ValueError as exptn:
        if str(exptn) == 'SKIP':
            #<<
            raise ValueError('SKIP')  # not an error - raise again
        else:
            err_msg = '{}\nNextion Handler failed within SET function:\n<{}> <{}>.'.format(exptn, 'setb', '> <'.join(args_list))
            logger.warning('nextion_handler.py ' + err_msg)
            #hass.services.call('persistent_notification', 'create', {'title': 'Nextion Handler Error!', 'message': err_msg, 'notification_id': 'nx_handler_error_set' }, False)
            raise ValueError(err_msg)
    return True




#! NEW: setlt bLtOn.val LT.nLtType.val nLtBrt.val nLtCt.val nLtClr.val $SW.bLG_LP
def setlt (args_list, domain, service):
    '''setlt Nx_state Nx_tp Nx_brt Nx_ct Nx_rgb565 E (assign Nx variables the state,
    'type, brightness, color temperature and color of light E).
    'type' is a bit-encoded value of the supported modes of light `E`: bits are 1:brightness, 2:color_temp, 3:rgb.
    Use '_' in place of `Nx` variable names to skip assignments for those attributes.
    The light color is converted to Nextion 16-bit RGB565 format (to assign directly to color attributes of Nextion UI components).
    '''
    try:
        rgb565 = 0  # 33808  # default (on failure to set properly below): mid grey (128,128,128)
        (r, g, b) = (0, 0, 0) # (70, 70, 70) 
        if len(args_list) == 6:
            [nx_st, nx_tp, nx_brt, nx_ct, nx_rgb565, e] = args_list
            #
            #-- READ light attributes from HA
            #*state & entity_id
            entity_id, state = get_entity_id_state(e, class_prefix='light.')  # will raise exception if it can't translate e to valid entity_id
            #..
            #*supported_color_modes (-> light type capabilities)
            # modes in [None (default), 'onoff', 'brightness', 'color_temp', 'white', 'hs', 'xy', 'rgb', 'rgbw', 'rgbww']
            try:
                sm = hass.states.get(entity_id).attributes['supported_color_modes']
            except:
                sm = ['onoff']
            #*light_type (nextion_handler encoding for light control 'pop-up page')
            #TODO? (option c is now working?): find a set intersection test that works in HA py scripts (these 2 methods DO NOT!) #!
            is_brt = False
            is_ct = False
            is_clr = False
            if any(i in sm for i in ['brightness', 'white', 'rgbw']):       # bit 1: brightness
                is_brt = True
            if any(i in sm for i in ['color_temp', 'rgbww']):               # bit 2: color_temp
                is_brt = True
                is_ct = True
            if any(i in sm for i in ['rgb', 'rgbw', 'rgbww', 'hs', 'xy']):  # bit 3: color
                is_brt = True
                is_clr = True
            #* convert lt capability flags to bit encoding for Nx variable
            light_type = 0
            #! '+=' "NOT SUPPORTED in restricted HA Python script env: gives error: "'_inplacevar_' is not defined"
            if is_brt:              # bit 1: brightness
                light_type = light_type + 1  # HA Py Env error for "+=": "'_inplacevar_' is not defined"
            if is_ct:               # bit 2: color_temp
                light_type = light_type + 2
            if is_clr:              # bit 3: color
                light_type = light_type + 4
            #..
            # Most other light attributes are only reported when the light is ON
            # state (on/off)
            if str(state) == 'on':
                on_state = 1
                #*color_mode (to help interpret other/conditional light attributes)
                # modes in [None (default), 'onoff', 'brightness', 'color_temp', 'white', 'hs', 'xy', 'rgb', 'rgbw', 'rgbww']
                try:
                    cm = hass.states.get(entity_id).attributes['color_mode']
                except:
                    cm = 'x'  #pass
                #*brightness
                try:
                    brightness = hass.states.get(entity_id).attributes['brightness']
                    brightness_pct = int(float(brightness)*100/255)
                except:
                    brightness_pct = 80  # default value
                    #err_msg = 'Could not get brightness for <{}>.'.format(e)
                    #raise ValueError(err_msg)
                #*color_temp
                try:
                    ct = hass.states.get(entity_id).attributes['color_temp']
                    ct = int(ct)
                except:
                    ct = 370  # warmish white (mireds)
                    #err_msg = 'Could not get color_temp for <{}>.'.format(e)
                    #raise ValueError(err_msg)
                #*rgb_color
                try:
                    (r_, g_, b_) = hass.states.get(entity_id).attributes['rgb_color']
                    (r, g, b) = (int(r_), int(g_), int(b_))
                except:
                    # this color will only make it through to the NX UI if there has been an error.
                    (r,g,b)=(99,0,0) #! << dark red (color to indicate and error in NX UI)
                    #err_msg = 'Could not get valid rgb_color for <{}>.'.format(e)
                    #raise ValueError(err_msg)
            else:
                on_state = 0
                cm = 'off'
                brightness_pct = 0  # default value
                ct = 370  # warmish white (mireds)
                (r, g, b) = (0, 0, 0) # (70, 70, 70) 
            #
            #-- WRITE light attributes to Nx
            # state
            if nx_st != '_':
                nx_full, nx_lookup, data_type = nx_var_parse(nx_st)
                nx_cmd_str = '{}={}'.format(nx_full, on_state)
                nx_cmd(nx_cmd_str, domain, service)
            # light type (encoding of supported_color_modes)
            if nx_tp != '_':
                nx_full, nx_lookup, data_type = nx_var_parse(nx_tp)
                nx_cmd_str = '{}={}'.format(nx_full, light_type)
                nx_cmd(nx_cmd_str, domain, service)
            # brightness percent (0..100)
            if nx_brt != '_' and on_state == 1:  # only update if light is ON (otherwise leave Nx variable unchanged)
                nx_full, nx_lookup, data_type = nx_var_parse(nx_brt)
                nx_cmd_str = '{}={}'.format(nx_full, brightness_pct)
                #nx_cmd_str = '{}={}'.format(nx_full, light_type) #!dbg - test sending light_type code to brightness slider
                nx_cmd(nx_cmd_str, domain, service)
            # color temperature
            if nx_ct != '_' and on_state == 1:  # only update if light is ON (otherwise leave Nx variable unchanged)
                nx_full, nx_lookup, data_type = nx_var_parse(nx_ct)
                nx_cmd_str = '{}={}'.format(nx_full, ct)
                nx_cmd(nx_cmd_str, domain, service)
            # color - generate rgb based on color_mode (cm), then convert to RGB565 for writing to Nx
            if nx_rgb565 != '_':  # Even if the light is OFF, return a color to indicate light status in the color bar (beneath the title bar)
                if on_state == 0:
                    (r, g, b) = (0, 0, 0)  # black for OFF
                elif cm == 'onoff':
                    (r, g, b) = (0, 176, 255) # default value for light ON (if no RGB below)
                elif cm in ['brightness', 'white']:
                    # rgb settings for rgb565 (1:(50% darkened) ..  100:cyan(0,176,255)) - may be overwritten below
                    pct = brightness_pct/100  # offset percentage towards max brightness
                    r = int(55 * (1-pct) + 0 * pct)
                    g = int(55 * (1-pct) + 176 * pct)
                    b = int(55 * (1-pct) + 255 * pct)
                elif cm == 'color_temp':
                    # rgb settings for rgb565 (153:blueish(168,210,255)   320:white(255,255,255)   500:orangeish(255,162,4)) - may be overwritten below
                    if ct < 320:
                        pct = (ct - 153)/(320 - 153)  # percentage ct is towards mid/white from max BLUE
                        r = int(120 + (255 - 120) * pct)
                        g = int(160 + (255 - 160) * pct)
                        b = 255
                    else:
                        pct = (500 - ct)/(500 - 320)  # percentage ct is toward mid/white from max ORANGE
                        r = 255
                        g = int(162 + (255 - 162) * pct)
                        b = int(4 + (255 - 4) * pct)
                else:
                    # The light is in a color mode - use it's rgb as set above
                    pass
                # Convert the 24bit r,g,b values set above to 16bit RGB565
                #   http://www.barth-dev.de/online/rgb565-color-picker/
                #   https://nextion.tech/2020/08/31/the-sunday-blog-understanding-and-customizing-hmi-components-part-3-color-encoding-sliders-subroutines-and-a-hue-control/
                rgb565 = (r & 0b11111000) <<8              # 5 r bits, msb bits 15-11
                rgb565 = rgb565 + ((g & 0b11111100 ) <<3)  # 6 g bits, mid bits 10-5
                rgb565 = rgb565 + ((b) >> 3)               # 5 b bits, lsb bits 4-0
                #rgb565 = ((int(r / 255 * 31) << 11) | (int(g / 255 * 63) << 5) | (int(b / 255 * 31)))
                nx_full, nx_lookup, data_type = nx_var_parse(nx_rgb565)
                nx_cmd_str = '{}={}'.format(nx_full, rgb565)
                nx_cmd(nx_cmd_str, domain, service)
        else:
            raise ValueError('Wrong number of items in arguments list.')
    except ValueError as exptn:
        err_msg = '{}\nNextion Handler failed within SET function:\n<{}> <{}>.'.format(exptn, 'setlt', '> <'.join(args_list))
        logger.warning('nextion_handler.py ' + err_msg)
        #hass.services.call('persistent_notification', 'create', {'title': 'Nextion Handler Error!', 'message': err_msg, 'notification_id': 'nx_handler_error_set' }, False)
        raise ValueError(err_msg)
    return True


#setntf NF.nNTFC t1.txt t2.txt 1
def setntf(args_list, domain, service):
    '''setntf Nx_count (Nx_title) (Nx_msg) (n) (chars_title) (chars_msg)
    (assign 3 Nx variables the Count, Title and Message of the nth Persistent Notification.)
    Use '_' in place of `Nx` variable names, or omit them, to skip assignments for those attributes.
    Default numeric arguments (if unassigned) are 1, for message num, and 255 for string len.)
    '''
    try:
        if 1 <= len(args_list) <= 6:
            args_list.extend(['_']*6)  # extend list with '_'s to indicate potential unassigned/default values
            [nx_c, nx_t, nx_m, n_, len_t_, len_m_] = args_list[:6]
            try:
                # Apply defaults to missing values or convert str to int
                len_t = 255 if len_t_ == '_' else int(len_t_)
                len_m = 255 if len_m_ == '_' else int(len_m_)
                n     =   1 if n_     == '_' else int(n_)
            except:
                raise ValueError('Values are not integers.')
            # Get notification list, count & item n
            try:
                ntf_list = hass.states.entity_ids('persistent_notification')
                ntf_cnt = len(ntf_list)
                if ntf_cnt > 0:
                    if n > ntf_cnt:
                        n = ntf_cnt
                    elif n < 1:
                        n = 1
                    entity_id = ntf_list[n - 1]
                    title = hass.states.get(entity_id).attributes['title']
                    message = hass.states.get(entity_id).attributes['message']
                else:
                    title = 'NONE'
                    message = 'No Notifications'
            except:
                #raise ValueError('Error reading list of Persistent Notifications.')
                title = 'Error'
                message = "Error reading list of Persistent Notifications."
            # Notification title (.txt)
            if nx_t != '_':
                nx_full, nx_lookup, data_type = nx_var_parse(nx_t, 'txt')
                title = '\r\n'.join(title.split('\n'))  # Convert from HA linebreak (\n) to Nextion (\r\n)
                new_value = title[:len_t]
                nx_cmd_str = '{}="{}"'.format(nx_full, new_value) # Nextion commands need double quotes for text
                nx_cmd(nx_cmd_str, domain, service)
            # Notification message (.txt)
            if nx_m != '_':
                nx_full, nx_lookup, data_type = nx_var_parse(nx_m, 'txt')
                message = '\r\n'.join(message.split('\n'))  # Convert from HA linebreak (\n) to Nextion (\r\n)
                new_value = message[:len_m]
                nx_cmd_str = '{}="{}"'.format(nx_full, new_value) # Nextion commands need double quotes for text
                nx_cmd(nx_cmd_str, domain, service)
            # Notification count (.val)
            if nx_c != '_':
                nx_full, nx_lookup, data_type = nx_var_parse(nx_c, 'val')
                nx_cmd_str = '{}={}'.format(nx_full, ntf_cnt)
                nx_cmd(nx_cmd_str, domain, service)
        else:
            raise ValueError('Wrong number of items in arguments list.')
    except ValueError as exptn:
        err_msg = '{}\nNextion Handler failed within SET function:\n<{}> <{}>.'.format(exptn, 'sett', '> <'.join(args_list))
        logger.warning('nextion_handler.py ' + err_msg)
        #hass.services.call('persistent_notification', 'create', {'title': 'Nextion Handler Error!', 'message': err_msg, 'notification_id': 'nx_handler_error_set' }, False)
        raise ValueError(err_msg)
    return True


# setdt CFG.tTime $ %a %d/%m %Hh%M
def setdt(args_list, domain, service):
    '''setdt Nx (fmt)  (assign Nx the string of the current data-time, formatted as fmt).
    (Default fmt is r"%a %d/%m %Hh%M", e.g. "Sun 28/02 17h30".)
    '''
    #! datetime.datetime.now() with strftime() not working
    FMT_DEFAULT = r"%a %d/%m %Hh%M"  # e.g. 'Sun 28/02 17h30'
    try:
        if len(args_list) > 0:
            nx = args_list[0]
            if len(args_list) >= 2:
                fmt = ' '.join(args_list[1:])
            else:
                fmt = FMT_DEFAULT
            nx_full, nx_lookup, data_type = nx_var_parse(nx, 'txt')
            dt_now = datetime.datetime.now()  #! this works
            try:
                dt_str = dt_now.strftime(fmt)  #! but strftime() fails exception check
            except:
                try:
                    #dt_str = dt_now.strftime(FMT_DEFAULT)
                    #dt_str = dt_now.strftime("%d %b %y, %I:%M:%S %p")
                    dt_str = datetime.datetime.strftime(datetime.datetime.now(), "%d %b %y, %I:%M:%S %p")
                except:
                    try:
                        #! failsafe date-time string approach that seems reliable
                        dt_str = '*{:02}/{:02} {:02}h{:02}'.format(dt_now.day, dt_now.month, dt_now.hour, dt_now.minute)
                    except:
                        raise ValueError('Formatting date-time string failed.')
            nx_cmd_str = '{}="{}"'.format(nx_full, dt_str)  # Nx strings need double quotes
            nx_cmd(nx_cmd_str, domain, service)
        else:
            raise ValueError('Wrong number of items in arguments list.')
    except ValueError as exptn:
        err_msg = '{}\nNextion Handler failed within SET function:\n<{}> <{}>.'.format(exptn, 'setdt', '> <'.join(args_list))
        logger.warning('nextion_handler.py ' + err_msg)
        #hass.services.call('persistent_notification', 'create', {'title': 'Nextion Handler Error!', 'message': err_msg, 'notification_id': 'nx_handler_error_set' }, False)
        raise ValueError(err_msg)
    return True



#_________________
#* ACTION FUNCTIONS - perform an action in HA (don't do anything to Nx)


#* ---- Actions for GENERIC Entities, NO PREFIX/CLASS can be assumed ------
#  $Aliases are preferred for all entity arguements entered in Nx NhCmds.
#  (If HA entitiy_ids are used instead, the full entity_id, including class,
#  is required for the functions immediately below.  Class can be deduced for the next block of NhCmds.)

def tgl(args_list, domain, service):
    '''tgl E (toggle E)'''
    prefix = None # multiple entity classes - user needs to be explicit
    domain = 'homeassistant'
    service = 'toggle'
    try:
        # FULL entity required - a generic function across multiple types of entities
        if len(args_list) == 1:
            e = args_list[0]
            entity_id, unused = get_entity_id_state(e, class_prefix=prefix)  # will raise exception if it can't translate e to valid entity_id
            service_data = {'entity_id': entity_id}
            try:
                hass.services.call(domain, service, service_data, False)
            except:  # need HASS API docs to be explicit about the exception to catch here
                raise ValueError('Failed HASS service call {}.{}.'.format(domain, service))
        else:
            raise ValueError('Wrong number of items in arguments list.')
    except ValueError as exptn:
        err_msg = '{}\nNextion Handler failed within ACTION function:\n<{}> <{}>.'.format(exptn, 'tgl', '> <'.join(args_list))
        logger.warning('nextion_handler.py ' + err_msg)
        #hass.services.call('persistent_notification', 'create', {'title': 'Nextion Handler Error!', 'message': err_msg, 'notification_id': 'nx_handler_error_set' }, False)
        raise ValueError(err_msg)
    return True

def ton(args_list, domain, service):
    '''ton E (turn on E)'''
    prefix = None # multiple entity classes - user needs to be explicit
    domain = 'homeassistant'
    service = 'turn_on'
    try:
        # FULL entity required - a generic function across multiple types of entities
        if len(args_list) == 1:
            e = args_list[0]
            entity_id, unused = get_entity_id_state(e, class_prefix=prefix)  # will raise exception if it can't translate e to valid entity_id
            service_data = {'entity_id': entity_id}
            try:
                hass.services.call(domain, service, service_data, False)
            except:  # need HASS API docs to be explicit about the exception to catch here
                raise ValueError('Failed HASS service call {}.{}.'.format(domain, service))
        else:
            raise ValueError('Wrong number of items in arguments list.')
    except ValueError as exptn:
        err_msg = '{}\nNextion Handler failed within ACTION function:\n<{}> <{}>.'.format(exptn, 'ton', '> <'.join(args_list))
        logger.warning('nextion_handler.py ' + err_msg)
        #hass.services.call('persistent_notification', 'create', {'title': 'Nextion Handler Error!', 'message': err_msg, 'notification_id': 'nx_handler_error_set' }, False)
        raise ValueError(err_msg)
    return True

def tof(args_list, domain, service):
    '''tof E (turn off E)'''
    prefix = None # multiple entity classes - user needs to be explicit
    domain = 'homeassistant'
    service = 'turn_off'
    try:
        # FULL entity required - a generic function across multiple types of entities
        if len(args_list) == 1:
            e = args_list[0]
            entity_id, unused = get_entity_id_state(e, class_prefix=prefix)  # will raise exception if it can't translate e to valid entity_id
            service_data = {'entity_id': entity_id}
            try:
                hass.services.call(domain, service, service_data, False)
            except:  # need HASS API docs to be explicit about the exception to catch here
                raise ValueError('Failed HASS service call {}.{}.'.format(domain, service))
        else:
            raise ValueError('Wrong number of items in arguments list.')
    except ValueError as exptn:
        err_msg = '{}\nNextion Handler failed within ACTION function:\n<{}> <{}>.'.format(exptn, 'tof', '> <'.join(args_list))
        logger.warning('nextion_handler.py ' + err_msg)
        #hass.services.call('persistent_notification', 'create', {'title': 'Nextion Handler Error!', 'message': err_msg, 'notification_id': 'nx_handler_error_set' }, False)
        raise ValueError(err_msg)
    return True



#* ---- Actions where entity class can be assumed/deduced ------
# No need to specify entity device class in Nx entity_id arguements - they can 
# be deduced and added (but $ aliases are still the expected norm in NhCmds)

def inps(args_list, domain, service):
    '''inps E string (set value of input_select E to string)
    Allow spaces in 'string' by rejoining excess args_list items
    '''
    prefix = 'input_select.'
    domain = 'input_select'
    service = 'set_value'
    try:
        if len(args_list) > 1:
            e = args_list[0]
            string = ' '.join(args_list[1:])  # reconstruct string if it was split by on spaces before
            entity_id, unused = get_entity_id_state(e, class_prefix=prefix)  # will raise exception if it can't translate e to valid entity_id
            #service_data = {'entity_id': entity_id, 'value': string }
            service_data = {'entity_id': entity_id, 'option': string }
            try:
                #hass.services.call('input_select', 'set_value', service_data, False) #! deprecated ~Mar 2022?
                hass.services.call('input_select', 'select_option', service_data, False)
            except:  # need HASS API docs to be explicit about the exception to catch here
                raise ValueError('Failed HASS input_number service call.')
        else:
            raise ValueError('Wrong number of items in arguments list.')
    except ValueError as exptn:
        err_msg = '{}\nNextion Handler failed within ACTION function:\n<{}> <{}>.'.format(exptn, 'inps', '> <'.join(args_list))
        logger.warning('nextion_handler.py ' + err_msg)
        #hass.services.call('persistent_notification', 'create', {'title': 'Nextion Handler Error!', 'message': err_msg, 'notification_id': 'nx_handler_error_set' }, False)
        raise ValueError(err_msg)
    #! dbg
    #msg = 'Nextion Handler Debug:\n<{}> <{}>.'.format('inps', '> <'.join(args_list))
    #hass.services.call('persistent_notification', 'create', {'title': 'Nextion Handler Debug!', 'message': msg, 'notification_id': 'nx_handler_debug_inps' }, False)
    return True


def inpb(args_list, domain, service):
    '''inpb E b (turn input_binary `E` `on` if b!=0 otherwise turn `off`)'''
    prefix = 'input_boolean.'
    domain = 'input_boolean'
    service = None  # set to 'turn_on' or 'turn_off'
    try:
        if len(args_list) == 2:
            [e, b] = args_list
            entity_id, unused = get_entity_id_state(e, class_prefix=prefix)  # will raise exception if it can't translate e to valid entity_id
            #service_data = {'entity_id': entity_id, 'value': b != '0' }
            if b != '0':  # treat any non-zero (string) value as True
                service = 'turn_on'
            else:
                service = 'turn_off'
            service_data = {'entity_id': entity_id}
            try:
                #hass.services.call('input_boolean', 'set_value', service_data, False)
                hass.services.call(domain, service, service_data, False)
            except:  # need HASS API docs to be explicit about the exception to catch here
                raise ValueError('Failed HASS input_boolean service call.')
        else:
            raise ValueError('Wrong number of items in arguments list.')
    except ValueError as exptn:
        err_msg = '{}\nNextion Handler failed within ACTION function:\n<{}> <{}>.'.format(exptn, 'inpb', '> <'.join(args_list))
        logger.warning('nextion_handler.py ' + err_msg)
        #hass.services.call('persistent_notification', 'create', {'title': 'Nextion Handler Error!', 'message': err_msg, 'notification_id': 'nx_handler_error_set' }, False)
        raise ValueError(err_msg)
    return True


def inpn(args_list, domain, service):
    '''inpn E x (set value of input_number E to x)'''
    prefix = 'input_number.'
    domain = 'input_number'
    service = 'set_value'
    try:
        if len(args_list) == 2:
            [e, x] = args_list
            entity_id, unused = get_entity_id_state(e, class_prefix=prefix)  # will raise exception if it can't translate e to valid entity_id
            try:
                service_data = {'entity_id': entity_id, 'value': float(x) }
            except ValueError:
                raise ValueError('Value provided is not a valid float.')
            try:
                hass.services.call(domain, service, service_data, False)
            except:  # need HASS API docs to be explicit about the exception to catch here
                raise ValueError('Failed HASS service call {}.{}.'.format(domain, service))
        else:
            raise ValueError('Wrong number of items in arguments list.')
    except ValueError as exptn:
        err_msg = '{}\nNextion Handler failed within ACTION function:\n<{}> <{}>.'.format(exptn, 'inpn', '> <'.join(args_list))
        logger.warning('nextion_handler.py ' + err_msg)
        #hass.services.call('persistent_notification', 'create', {'title': 'Nextion Handler Error!', 'message': err_msg, 'notification_id': 'nx_handler_error_set' }, False)
        raise ValueError(err_msg)
    return True


def lt_brt(args_list, domain, service):
    '''lt_brt E x (set brightness percent of light E to x (0..100))'''
    prefix = 'light.'
    domain = 'light'
    service = 'turn_on'
    try:
        if len(args_list) == 2:
            [e, x] = args_list
            entity_id, unused = get_entity_id_state(e, class_prefix=prefix)  # will raise exception if it can't translate e to valid entity_id
            try:
                service_data = {'entity_id': entity_id, 'brightness_pct': int(x) }
            except ValueError:
                raise ValueError('Value provided is not a valid integer.')
            try:
                hass.services.call(domain, service, service_data, False)
            except:  # need HASS API docs to be explicit about the exception to catch here
                raise ValueError('Failed HASS service call {}.{}.'.format(domain, service))
        else:
            raise ValueError('Wrong number of items in arguments list.')
    except ValueError as exptn:
        err_msg = '{}\nNextion Handler failed within ACTION function:\n<{}> <{}>.'.format(exptn, 'lt_pct', '> <'.join(args_list))
        logger.warning('nextion_handler.py ' + err_msg)
        #hass.services.call('persistent_notification', 'create', {'title': 'Nextion Handler Error!', 'message': err_msg, 'notification_id': 'nx_handler_error_set' }, False)
        raise ValueError(err_msg)
    return True


def lt_brtv(args_list, domain, service):
    '''lt_brtv E x (set brightness value of light E to x(0..255))'''
    prefix = 'light.'
    domain = 'light'
    service = 'turn_on'
    try:
        if len(args_list) == 2:
            [e, x] = args_list
            entity_id, unused = get_entity_id_state(e, class_prefix=prefix)  # will raise exception if it can't translate e to valid entity_id
            try:
                service_data = {'entity_id': entity_id, 'brightness': int(x) }  #! brightness
            except ValueError:
                raise ValueError('Value provided is not a valid integer.')
            try:
                hass.services.call(domain, service, service_data, False)
            except:  # need HASS API docs to be explicit about the exception to catch here
                raise ValueError('Failed HASS service call {}.{}.'.format(domain, service))
        else:
            raise ValueError('Wrong number of items in arguments list.')
    except ValueError as exptn:
        err_msg = '{}\nNextion Handler failed within ACTION function:\n<{}> <{}>.'.format(exptn, 'lt_brt', '> <'.join(args_list))
        logger.warning('nextion_handler.py ' + err_msg)
        #hass.services.call('persistent_notification', 'create', {'title': 'Nextion Handler Error!', 'message': err_msg, 'notification_id': 'nx_handler_error_set' }, False)
        raise ValueError(err_msg)
    return True


def lt_ct(args_list, domain, service):
    '''lt_ct E x (set colour temperature of light E to x mireds)'''
    prefix = 'light.'
    domain = 'light'
    service = 'turn_on'
    #TODO? Maybe for RGBW bulbs (without CT, but with WHITE) consider switch to WHITE mode instead?
    #NOTE: some RGW bulbs wil interpret CT commands themselves (and try to mix the RGB to match requrested CT)
    #So can't really assume that an RGBW bulb should use 'white' (W channel) instead of a CT call. 
    try:
        if len(args_list) == 2:
            [e, x] = args_list
            entity_id, unused = get_entity_id_state(e, class_prefix=prefix)  # will raise exception if it can't translate e to valid entity_id
            try:
                service_data = {'entity_id': entity_id, 'color_temp': int(x) }
            except ValueError:
                raise ValueError('Value provided is not a valid integer.')
            try:
                hass.services.call(domain, service, service_data, False)
            except:  # need HASS API docs to be explicit about the exception to catch here
                raise ValueError('Failed HASS service call {}.{}.'.format(domain, service))
        else:
            raise ValueError('Wrong number of items in arguments list.')
    except ValueError as exptn:
        err_msg = '{}\nNextion Handler failed within ACTION function:\n<{}> <{}>.'.format(exptn, 'lt_ct', '> <'.join(args_list))
        logger.warning('nextion_handler.py ' + err_msg)
        #hass.services.call('persistent_notification', 'create', {'title': 'Nextion Handler Error!', 'message': err_msg, 'notification_id': 'nx_handler_error_set' }, False)
        raise ValueError(err_msg)
    return True


def lt_rgb(args_list, domain, service):
    '''lt_rgb E r g b (set colour of light E to RGB = r, g, b)'''
    prefix = 'light.'
    domain = 'light'
    service = 'turn_on'
    try:
        if len(args_list) == 4:
            [e, r, g, b] = args_list
            entity_id, unused = get_entity_id_state(e, class_prefix=prefix)  # will raise exception if it can't translate e to valid entity_id
            try:
                service_data = {'entity_id': entity_id, 'rgb_color': [int(r), int(g), int(b)] }
            except ValueError:
                raise ValueError('Values provided are not valid integers.')
            try:
                hass.services.call(domain, service, service_data, False)
            except:  # need HASS API docs to be explicit about the exception to catch here
                raise ValueError('Failed HASS service call {}.{}.'.format(domain, service))
        else:
            raise ValueError('Wrong number of items in arguments list.')
    except ValueError as exptn:
        err_msg = '{}\nNextion Handler failed within ACTION function:\n<{}> <{}>.'.format(exptn, 'lt_rgb', '> <'.join(args_list))
        logger.warning('nextion_handler.py ' + err_msg)
        #hass.services.call('persistent_notification', 'create', {'title': 'Nextion Handler Error!', 'message': err_msg, 'notification_id': 'nx_handler_error_set' }, False)
        raise ValueError(err_msg)
    return True


def lt_hs(args_list, domain, service):
    '''lt_hs E h s (set colour of light E to Hue = h, Saturation = s)'''
    prefix = 'light.'
    domain = 'light'
    service = 'turn_on'
    try:
        if len(args_list) == 3:
            [e, h, s] = args_list
            entity_id, unused = get_entity_id_state(e, class_prefix=prefix)  # will raise exception if it can't translate e to valid entity_id
            try:
                service_data = {'entity_id': entity_id, 'hs_color': [float(h), float(s)] }
            except ValueError:
                raise ValueError('Values provided are not valid floats.')
            try:
                hass.services.call(domain, service, service_data, False)
            except:  # need HASS API docs to be explicit about the exception to catch here
                raise ValueError('Failed HASS service call {}.{}.'.format(domain, service))
        else:
            raise ValueError('Wrong number of items in arguments list.')
    except ValueError as exptn:
        err_msg = '{}\nNextion Handler failed within ACTION function:\n<{}> <{}>.'.format(exptn, 'lt_hs', '> <'.join(args_list))
        logger.warning('nextion_handler.py ' + err_msg)
        #hass.services.call('persistent_notification', 'create', {'title': 'Nextion Handler Error!', 'message': err_msg, 'notification_id': 'nx_handler_error_set' }, False)
        raise ValueError(err_msg)
    return True


def lt_cw(args_list, domain, service):
    '''lt_cw E dx dy r (set color of light E to Color-Wheel location dx, dy from centre of circle radius r)
    Assumes a Home-Assistant-style color-wheel with red (hue 0) at 3 o'clock, increasing CLOCKWISE to 360.
    (CLOCKWISE accounts for screen y increasing downwards, which reverses angle of Cartesian ArcTan.)
    '''
    MAX_R_MULT = 120  # ignore co-ordinates outside the radius of color wheel by this % factor
    prefix = 'light.'
    domain = 'light'
    service = 'turn_on'
    try:
        if len(args_list) == 4:
            [e, dx_, dy_, r_] = args_list
            entity_id, unused = get_entity_id_state(e, class_prefix=prefix)  # will raise exception if it can't translate e to valid entity_id
            try:
                # Sign of dy is implictly changed (Screen vs Cartesian y co-ordinate) which reverses the Cartesian arctan angle from ANTICLOCKWISE to CLOCKWISE (relative to 3 o'clock)
                [dx, dy, r] = [float(dx_), float(dy_), float(r_)]
            except ValueError:
                raise ValueError('Values provided are not valid floats.')
            sat = int(100 * math.sqrt(dx*dx + dy*dy)/r)
            if sat <= MAX_R_MULT:
                if sat > 100:
                    sat = 100
                hue = int(math.atan2(dy, dx)*180/math.pi)
                if hue < 0:
                    hue = hue + 360
                service_data = {'entity_id': entity_id, 'hs_color': [hue, sat] }
                try:
                    hass.services.call(domain, service, service_data, False)
                except:  # need HASS API docs to be explicit about the exception to catch here
                    raise ValueError('Failed HASS service call {}.{}.'.format(domain, service))
        else:
            raise ValueError('Wrong number of items in arguments list.')
    except ValueError as exptn:
        err_msg = '{}\nNextion Handler failed within ACTION function:\n<{}> <{}>.'.format(exptn, 'lt_cw', '> <'.join(args_list))
        logger.warning('nextion_handler.py ' + err_msg)
        #hass.services.call('persistent_notification', 'create', {'title': 'Nextion Handler Error!', 'message': err_msg, 'notification_id': 'nx_handler_error_set' }, False)
        raise ValueError(err_msg)
    return True


def lt_wt(args_list, domain, service):
    '''lt_wt E (set light E to a supported white/color_temp mode).
    (Otherwise just try to turn the light on.)'''
    prefix = 'light.'
    domain = 'light'
    service = 'turn_on'
    try:
        if len(args_list) == 1:
            #args_list.extend(['_'] * 8)  # fill in for missing optional parameters
            e = args_list[0]
            entity_id, unused = get_entity_id_state(e, class_prefix=prefix)  # will raise exception if it can't translate e to valid entity_id
            try:
                # get list of light's supported modes
                sm = hass.states.get(entity_id).attributes['supported_color_modes']
            except:
                sm = ['onoff']
            if 'color_temp' in sm:
                try:
                    # get light's current ct
                    ct = hass.states.get(entity_id).attributes['color_temperature']
                except:
                    ct = 370
                service_data = {'entity_id': entity_id, 'color_temp': int(ct) }
            elif 'white' in sm:
                try:
                    # get light's current brightness (0..255)
                    brt = hass.states.get(entity_id).attributes['brightness']
                except:
                    brt = 150
                service_data = {'entity_id': entity_id, 'white': int(brt) }
            else:
                service_data = {'entity_id': entity_id}
            try:
                hass.services.call(domain, service, service_data, False)
            except:  # need HASS API docs to be explicit about the exception to catch here
                raise ValueError('Failed HASS service call {}.{}.'.format(domain, service))
        else:
            raise ValueError('Wrong number of items in arguments list.')
    except ValueError as exptn:
        err_msg = '{}\nNextion Handler failed within ACTION function:\n<{}> <{}>.'.format(exptn, 'lt_wt', '> <'.join(args_list))
        logger.warning('nextion_handler.py ' + err_msg)
        #hass.services.call('persistent_notification', 'create', {'title': 'Nextion Handler Error!', 'message': err_msg, 'notification_id': 'nx_handler_error_set' }, False)
        raise ValueError(err_msg)
    return True



def scn(args_list, domain, service):
    '''scn E (set scenario E)'''
    prefix = 'scene.'
    domain = 'scene'
    service = 'turn_on'
    try:
        if len(args_list) == 1:
            e = args_list[0]
            entity_id, state = get_entity_id_state(e, class_prefix=prefix)  # will raise exception if it can't translate e to valid entity_id
            try:
                hass.services.call('scene', 'turn_on', {'entity_id': entity_id}, False)
            except:  # need HASS API docs to be explicit about the exception to catch here
                raise ValueError('Failed HASS scene.turn_on service call.')
        else:
            raise ValueError('Wrong number of items in arguments list.')
    except ValueError as exptn:
        err_msg = '{}\nNextion Handler failed within ACTION function:\n<{}> <{}>.'.format(exptn, 'scn', '> <'.join(args_list))
        logger.warning('nextion_handler.py ' + err_msg)
        #hass.services.call('persistent_notification', 'create', {'title': 'Nextion Handler Error!', 'message': err_msg, 'notification_id': 'nx_handler_error_set' }, False)
        raise ValueError(err_msg)
    return True


def scpt(args_list, domain, service):
    '''scpt E (t) (call script E: if t==off, turn_off instead)'''
    prefix = 'script.'
    domain = 'script'
    service = 'turn_on'  # default: if t=='off', changed to 'turn_off'
    try:
        if len(args_list) in [1, 2]:
            if len(args_list) == 1:
                e = args_list[0]
            else:
                [e, t] = args_list
                if t == 'off':
                    service = 'turn_off'
            entity_id, unused = get_entity_id_state(e, class_prefix=prefix)  # will raise exception if it can't translate e to valid entity_id
            service_data = {'entity_id': entity_id}
            try:
                hass.services.call(domain, service, service_data, False)
            except:  # need HASS API docs to be explicit about the exception to catch here
                raise ValueError('Failed HASS service call {}.{}.'.format(domain, service))
        else:
            raise ValueError('Wrong number of items in arguments list.')
    except ValueError as exptn:
        err_msg = '{}\nNextion Handler failed within ACTION function:\n<{}> <{}>.'.format(exptn, 'scpt', '> <'.join(args_list))
        logger.warning('nextion_handler.py ' + err_msg)
        #hass.services.call('persistent_notification', 'create', {'title': 'Nextion Handler Error!', 'message': err_msg, 'notification_id': 'nx_handler_error_set' }, False)
        raise ValueError(err_msg)
    return True



#*_________________
#*  Info Actions


def say(args_list, domain, service):
    '''say E string (Play TTS of message string msg to media player E)
    Allow spaces in 'string' by reconstructing args_list items that were split on spaces before'''
    prefix = 'media_player.'
    domain = 'tts'
    service = 'google_translate_say'
    try:
        if len(args_list) > 1:
            e = args_list[0]
            string = ' '.join(args_list[1:])  # reconstruct string if it was split by on spaces before
            entity_id, unused = get_entity_id_state(e, class_prefix=prefix)  # will raise exception if it can't translate e to valid entity_id
            service_data = {'entity_id': entity_id, 'message': string }
            try:
                hass.services.call(domain, service, service_data, False)
            except:  # need HASS API docs to be explicit about the exception to catch here
                raise ValueError('Failed HASS service call {}.{}.'.format(domain, service))
        else:
            raise ValueError('Wrong number of items in arguments list.')
    except ValueError as exptn:
        err_msg = '{}\nNextion Handler failed within ACTION function:\n<{}> <{}>.'.format(exptn, 'say', '> <'.join(args_list))
        logger.warning('nextion_handler.py ' + err_msg)
        #hass.services.call('persistent_notification', 'create', {'title': 'Nextion Handler Error!', 'message': err_msg, 'notification_id': 'nx_handler_error_set' }, False)
        raise ValueError(err_msg)
    return True


def ntf(args_list, domain, service):
    '''ntf title|message (Create a Persistent Notification with title & message strings in HA).
    Allow spaces in 'string' by reconstructing args_list items that were split on spaces before.'''
    #prefix = 'persistent_notification.'
    domain = 'persistent_notification'
    service = 'create'
    try:
        if args_list:
            string = ' '.join(args_list)  # reconstruct string if it was split on spaces before
            tmp = string.split('|')  # split title from message on '|'
            if len(tmp)<2:
                # No title provided
                title = 'Nextion Alert'
                message = string
            else:
                title = tmp[0]
                message = '|'.join(tmp[1:])
            hass.services.call('persistent_notification', 'create', {'title': title, 'message': message, 'notification_id': 'nx_notify' }, False)
        else:
            raise ValueError('Wrong number of items in arguments list.')
    except ValueError as exptn:
        err_msg = '{}\nNextion Handler failed within ACTION function:\n<{}> <{}>.'.format(exptn, 'ntf', '> <'.join(args_list))
        logger.warning('nextion_handler.py ' + err_msg)
        #hass.services.call('persistent_notification', 'create', {'title': 'Nextion Handler Error!', 'message': err_msg, 'notification_id': 'nx_handler_error_set' }, False)
        raise ValueError(err_msg)
    return True


def ntfx(args_list, domain, service):
    '''ntfx n (Dismiss the nth Persistent Notification in HA).'''
    #prefix = 'persistent_notification.'
    domain = 'persistent_notification'
    service = 'dismiss'
    try:
        if len(args_list) == 1:
            try:
                n = int(args_list[0])
            except:
                raise ValueError('Value is not an integer.')
            # Get notification list, count & item n
            try:
                ntf_list = hass.states.entity_ids('persistent_notification')
                ntf_count = len(ntf_list)
                if n > ntf_count:
                    n = ntf_count
                entity_id = ntf_list[n - 1]
                ntf_id = entity_id.split('.', 1)[-1]
            except:  # need HASS API docs to be explicit about the exception to catch here
                raise ValueError('Failed HASS service call {}.{}.'.format(domain, service))

            service_data = {'notification_id': ntf_id}
            try:
                hass.services.call(domain, service, service_data, False)
            except:  # need HASS API docs to be explicit about the exception to catch here
                raise ValueError('Failed HASS service call {}.{}.'.format(domain, service))

        else:
            raise ValueError('Wrong number of items in arguments list.')
    except ValueError as exptn:
        err_msg = '{}\nNextion Handler failed within SET function:\n<{}> <{}>.'.format(exptn, 'ntfx', '> <'.join(args_list))
        logger.warning('nextion_handler.py ' + err_msg)
        #hass.services.call('persistent_notification', 'create', {'title': 'Nextion Handler Error!', 'message': err_msg, 'notification_id': 'nx_handler_error_set' }, False)
        raise ValueError(err_msg)
    return True



#*******************
#* CONTROL FUNCTIONS - controlling looping and sequencing in this script (and the combined interactions with Nx)
#*******************

def sub(args_list, domain, service):
    '''sub Nx (`click Nx,1` the Nextion (hidden) hotspot to execute a Nx 'subroutine')'''
    # could add other options, e.g., for 'Nextion timer subroutines'
    # no entity or prefix
    try:
        if len(args_list) == 1:
            # click (set to 1) a subroutine hotspot: click SEND_ACTIONS,1
            nx_sub = args_list[0]
            nx_cmd_str = 'click ' + nx_sub + ',1'
            nx_cmd(nx_cmd_str, domain, service)
        # if len(args_list) == 1:
        #     # start/click (set to 1) timer/button the stop/release (set to 0)
        #     nx_sub = args_list[0]
        #     nx_cmd_str = nx_sub + '=0'
        #     nx_cmd(nx_cmd_str, domain, service)
        #     nx_cmd_str = nx_sub + '=1'
        #     nx_cmd(nx_cmd_str, domain, service)
        # elif len(args_list) == 2:
        #     # reverse order (to 0(off) then 1(on) if any 2nd parameter is given)
        #     [nx_sub] = args_list[0]
        #     nx_cmd_str = nx_sub + '=1'
        #     nx_cmd(nx_cmd_str, domain, service)
        #     nx_cmd_str = nx_sub + '=0'
        #     nx_cmd(nx_cmd_str, domain, service)
        else:
            raise ValueError('Wrong number of items in arguments list.')
    except ValueError as exptn:
        err_msg = '{}\nNextion Handler failed within CONTROL function:\n<{}> <{}>.'.format(exptn, 'sub', '> <'.join(args_list))
        logger.warning('nextion_handler.py ' + err_msg)
        #hass.services.call('persistent_notification', 'create', {'title': 'Nextion Handler Error!', 'message': err_msg, 'notification_id': 'nx_handler_error_set' }, False)
        raise ValueError(err_msg)
    return True



#TODO: for WIDGET (incomplete) @wd
def configure_widgets(args_list, domain, service):
    '''Configures Nextion to use the list of WIDGETs specified in the 'widgets:'
    YAML of the calling automation.
    This will write to a set of Nextion variables (widget, page & global) that
    will configure special 'Widget-Template HMIs' to use the selected entities. 
    '''
    #* Function CONSTANTS
    WIDGETS_PER_PAGE = 6
    MAX_PAGES = 3
    # Dict to map HA entity classes to NX widget types
    # NX grouped types (for entity classes that do not have their own separate type):
    #  TG: TOGGLE (switch, input_boolean, automation)
    #  ST: STATE (only shows the HA state of the entity - no actions)
    CLASS_TO_TYPE_DICT = {
        'light': 'LT',
        'switch': 'TG',
        'input_boolean': 'TG',
        'automation': 'TG',
        'scene':  'SC',
        'script': 'SP',
        #---- not supported yet --- (NX will treat as ST)
        'input_number': 'IN',
        'media_player': 'MP',
        'weather': 'WT',
        'input_select': 'IS',
        #--- status ---
        'sensor': 'ST',
        'binary_sensor': 'ST',
        'DEFAULT': 'ST'  # NX scripts should always default to treating unresolved entities as simple 'STATE' providers
    }
    #TODO Dict to map NX widget types (defined above) to icons (NX picc numbers? Paired? Where ENABLED icon = DISABLE icon num +1?)
    TYPE_TO_ICON_DICT = {'LT': 0, 'TG': 0}

    #* Get list of Widgets (& their settings) from 'widgets:' YAML section
    try:
        WIDGETS_LIST = data.get('widgets')
    except:
        # Log error message
        err_msg = 'Error trying get "widgets:" list from YAML for calling automation.'
        logger.warning('nextion_handler.py ' + err_msg)
    num_widets = min(len(WIDGETS_LIST), MAX_PAGES * WIDGETS_PER_PAGE)
    num_pages = math.ceil(num_widgets / WIDGETS_PER_PAGE)
    n = 0
    try:
        set_cmds = []
        for w, n in enumerate(WIDGETS_LIST):
            current_page_num = math.ceil(n/WIDGETS_PER_PAGE) - 1  # pages numbered from 0 .. (num_pages - 1)
            current_page_name = 'M{}'.format(current_page_num)  # NX template widget pages labelled 'M0'...
            entity_id, wd_type, wd_name, icon = None, None, None
            #TODO:
            # Read YAML for entity_id, short_name, icon
            wd_ent = WIDGETS_LIST[0]['entity_id']  # entity_id is REQUIRED - no default provided - will trigger exception if missing
            wd_name = WIDGETS_LIST[0].get('short_name', None)
            wd_icon = WIDGETS_LIST[0].get('icon', None)
            # Get name from entity friendly_name if not provided in YAML
            if wd_name is None:
                #TODO get friendly_name from HA instead - TEST
                try:
                    wd_name = hass.states.get(entity_id).attributes['friendly_name']
                except:
                    # Placeholder name on error
                    wd_name = 'Widget {}'.format(n+1)
            # HA Entity class, NX Widget Type, and NX icon
            ent_class = entity_id.split[0]
            wd_type = CLASS_TO_TYPE_DICT.get(ent_class, 'ST')
            if wd_icon is None:
                wd_icon = TYPE_TO_ICON_DICT['wd_type']
            #TODO: write widget settings to NX PAGE.Variable.val/txt
            #...
            #TODO: create SET NhCmd for current widget - add to list for current page (write variables here or later)
            set_cmd = ''  #TODO set cmd for current widget
            set_cmds_list += setcmd  # build list of SET cmds for later processing  #! '+=' not supported?
    except:
        pass
        # Log error message
        err_msg = 'Error reading settings for Widget number *{}* in YAML list.'.format(n+1)
        logger.warning('nextion_handler.py ' + err_msg)
        # raise ValueError(err_msg)  #! may need to debug before trapping such a large block

    #TODO: Write NX settings for each page
    for p in num_pages:
        # Need to create and write list of HA_SET commands (for NX to be able to fetch all the data it needs)
        pass

    #TODO: Write Global NX settings
    # page 0 # Change to starting 'main' UI page (which should trigger a page update & refresh with the provided HA_SET 1..5 commands)
    # set 'config_done=1' 

    return True





#! Use at own risks - Python scripts are NOT a good place to put delays/control timing in HA multi-threaded environment
# def delay(args_list, domain, service):
#     '''delay x (delay x seconds between commands - while executing on HA)
#     #!Best NOT to use time.sleep()! >> balloob: This exposes util.dt and the time module in Python Scripts. This does allow people to use time.sleep(), but they should do so at their own risk.
#     https://github.com/home-assistant/core/pull/9736
#     '''
#     # no entity or prefix
#     try:
#         if len(args_list) == 1:
#             [xs] = args_list
#             try:
#                 xn = float(xs)
#             except:
#                 raise ValueError('Delay value was not a valid integer.')
#             xn = min(1, xn)  #! <<<< Don't allow any long delays
#             time.sleep(xn)
#         else:
#             raise ValueError('Wrong number of items in arguments list.')
#     except ValueError as exptn:
#         err_msg = '{}\nNextion Handler failed within ACTION function:\n<{}> <{}>.'.format(exptn, 'delay', '> <'.join(args_list))
#         logger.warning('nextion_handler.py ' + err_msg)
#         #hass.services.call('persistent_notification', 'create', {'title': 'Nextion Handler Error!', 'message': err_msg, 'notification_id': 'nx_handler_error_set' }, False)
#         raise ValueError(err_msg)
#     return True


#*------------------------------------------------------------------------------
#* DICTIONARY OF FUNCTIONS (translates NhCmd text to associated function above)
#*------------------------------------------------------------------------------
#! Add any new custom functions to this dictionary
# HA won't allow locals() in script to automtically build dictionary of our functions - have to do it manually instead
FUNC_DICT ={
    #* SET functions
    'sett': sett,
    'setn': setn,
    'setb': setb,
    'setlt': setlt,
    'setntf': setntf,
    'setdt': setdt,
    #* ACTION functions
    # Actions where entity_id class needs to be provided (but $alias preferred)
    'tgl': tgl,
    'ton': ton,
    'tof': tof,
    # Actions where entity class can be assumed (but $alias preferred)
    'inps': inps,
    'inpb': inpb,
    'inpn': inpn,
    'scn': scn,
    'scpt': scpt,  
    'lt_brt': lt_brt,
    'lt_ct': lt_ct,
    'lt_rgb': lt_rgb,
    'lt_hs': lt_hs,
    'lt_cw': lt_cw,
    'lt_wt': lt_wt,
    # Info Actions
    'say': say,
    'ntf': ntf,
    'ntfx': ntfx,
    #* CONTROL functions (unusual behaviour to break out of, control, or modify nested loops)
    'sub': sub,
    'configure_widgets': configure_widgets  #TODO: incomplete
}


#*------------------------------------------------------------------------------
#* MAIN SCRIPT
#*------------------------------------------------------------------------------

#*_________________________________
#* Initialse loop/control variables
nxh_call_type = None  # in [ACT, SET, SLEEP] - categorise the type of call to this script (to be expanded in future) 
continue_script = True
is_ha_act_string = True  # first string in list is HA_Action (special case, following user interaction, indicated by positive trig_val)
unparsed_strings = []
bad_cmds = []
rpt_cmds = []
good_cmds = []
repeat_num = 0 # this value (& delay below) can be modified during the loop by NhCmds rpt() and noupd()
repeat_delay = -99 # (secs) If HA_Act includes a rst command, its settings will take precedence over defaults in HA_Set1..
command_strings = []
unparsed_strings = []

#* variables used in Exception messages
trig_str = None
trig_ent = None
nx_cmd_service = None
trig_val = None
s = None
nh_cmd_str = None
nh_cmd_func = None
args_list = []
esphome_domain = None
nx_service = None

KNOWN_BAD_STATES = INVALID_STATES  #['unknown', 'unavailable', 'None']  # entity states returned by HA that often trigger trivial errors


#*________________________
#* Parse Script Arguements passed to this py script by calling HA automation/service
try:

    #* Get and parse the Nextion Instruction sender service
    try:
        nx_cmd_service = data.get('nx_cmd_service')
        esphome_domain, nx_service = nx_cmd_service.split('.')
    except:
        continue_script = False
        raise ValueError('Provided nx_cmd_service is not valid: {}.'.format(nx_cmd_service))


    #* Get dictionary of aliases - key: value pairs of Nx $alias (WITHOUT $ prefix): Home Assistant entinty_id
    try:
        ENTITY_ALIASES = data.get('aliases')
    except:
        # Log error message, then use alternate dictionary directly set in the body of this script
        ENTITY_ALIASES = ENTITY_ALIASES_ALT
        err_msg = 'Aliases dictionary in automaltion YAMAL not valid, using ALTERNATE dictionary from within the script instead.'
        logger.warning('nextion_handler.py ' + err_msg)


    #* Get the value of the TRIGGER (that triggered this script and indicates the type of response required)
    try:
        trig_ent = data.get('trig_val')
        trig_val = int(float(hass.states.get(trig_ent).state))  #! Python cannot convert the state of ESPhome's integer sensor format (string '-1.00') directly to int
    except:
        # If it is not an entity, see if it is a directly specified int (to allow 'forced' automation overrides)
        try:
            trig_val = int(trig_ent)
        except:
            continue_script = False
            raise ValueError('Provided trig_val is neither a valid entity_id nor an integer: ent: <{}>, value: <{}>.'.format(trig_ent, trig_str))
        if trig_val is None:
            continue_script = False
            raise ValueError('Provided trig_val is neither a valid entity_id nor an integer: ent: <{}>, value: <{}>.'.format(trig_ent, trig_str))


    #* Determine the type of triggered Nextion request (Action vs Update) and get the appropriate command_strings to process
    # command_strings should be a list of entities whose states are strings of comma- or \n- delimited NhCmds
    #   action_cmds: (POSITIVE trig_val, triggered by USER INTERACTION) is list of HA_Act entity_ids containg strings (a sequence of ACTION NhCmds)
    #   update_cmds: (NEGATIVE trig_val, Nx POLLING to refresh its data from HA) is a list of Ha_Set1.. entity_ids containing strings (a sequence of SET NhCmds)

    if trig_val > 0:
        # Positive TRIGGER Indicates new HA_Act needs to be processed (USER INTERACTIONS should be prioritised over polling in script flow)
        nxh_call_type = 'ACT'
        try:
            command_strings = data.get('action_cmds')
        except:
            continue_script = False
            raise ValueError('Provided list of action_cmds is not valid: {}.'.format(command_strings))
    elif trig_val < 0:
        # Negative TRIGGER Indicates a data update for page (non-interactive POLLING from Nx) - only process the HA_Set strings (skip the HA_Act that is first in the list)
        nxh_call_type = 'SET'
        try:
            command_strings = data.get('update_cmds')
        except:
            continue_script = False
            raise ValueError('Provided list of update_cmds is not valid: {}.'.format(command_strings))
    else:  # trig_val == 0:
        nxh_call_type = 'SLEEP'
        # 0 indicates Nx has turned off interaction with HA (e.g. sleeping) - skip the intial state change to 0
        #<< catch INTENTIONAL exception (NOT an error) and exit script
        continue_script = False
        raise ValueError('EXIT') 


    #* Create a list of strings to be parsed into NhCmds (Action or Set) to be executed
    for string_ent in command_strings:
        s  = ''
        try:
            s = hass.states.get(string_ent).state
        except:  # need HASS API docs to be explicit about the exception to catch here
            # Log error message, then continue with remaining 'good' cmd strings
            err_msg = 'An entity in the command_strings list is not valid:\n{}\n<{}>'.format(string_ent,s)
            logger.warning('nextion_handler.py ' + err_msg)
            hass.services.call('persistent_notification', 'create', {'title': 'Nextion Handler Error!', 'message': err_msg, 'notification_id': 'nx_handler_error_main' }, False)
            #<<
            continue
        #
        # Clean up flotsam from ESPHome Nextion Custom output writing
        s = s.replace('\x00', '')  # remove the non-whitespace string terminaton character(\x00) that Nextion/ESPhome writes to the end of each string & causes parsing issues
        s = s.strip()  # strip BEFORE converting line-breaks to commas
        s = s.replace('\r\n', ',')  # handle both commas and line-breaks (NextionEditor/Windows uses CR/LF) as delimeters (line breaks are more readable in Nextion (multi-line) text variables)
        #s = s.replace('\n', ',')  # handle both commas and \n as delimeters (\n is more readable in Nextion text variables)
        if s:
            unparsed_strings.extend([s])


except ValueError as exptn: # <<< Mainly User errors requiring feedback for them to fix their YAML or command strings
    if str(exptn) == 'EXIT':
        #<< Exit script, don't continue with other stages
        continue_script = False
    else:
        err_msg = '{}\nNextion Handler failed trying to parse:\nnx_cmd_service: <{}>\ntrig_val: <{}>\ncommand_strings: <{}>\nunparsed_strings: <{}>.'\
            .format(exptn, nx_cmd_service, trig_val, command_strings, unparsed_strings)
        logger.warning('nextion_handler.py ' + err_msg)
        #hass.services.call('persistent_notification', 'create', {'title': 'Nextion Handler Error!', 'message': err_msg, 'notification_id': 'nx_handler_error_main' }, False)
        continue_script = False
except Exception as exptn:  # <<< Unexpected errors, possible BUG
    err_msg = '{}\nNextion Handler EXCEPTION trying to parse:\nnx_cmd_service: <{}>\ntrig_val: <{}>\ncommand_strings: <{}>\nunparsed_strings: <{}>.'\
        .format(exptn, nx_cmd_service, trig_val, command_strings, unparsed_strings)
    logger.warning('nextion_handler.py ' + err_msg)
    #hass.services.call('persistent_notification', 'create', {'title': 'Nextion Handler Error!', 'message': err_msg, 'notification_id': 'nx_handler_error_main' }, False)
    continue_script = False


#*_________________________
#* Process the command_list passing each in turn to specified function
# actions_still_to_process set above = True (CmdCnt > 0) False (CmdCnt < 0) (then apply below in building rpt_cmd[] list)
if continue_script and unparsed_strings:
    #! debug
    # if nxh_call_type == 'ACT':
    #         msg = 'Nextion Handler: ACTION Command Strings:\n{}'.format('\n--\n'.join(unparsed_strings))
    #         hass.services.call('persistent_notification', 'create', {'title': 'Nextion Handler Debug Info', 'message': msg, 'notification_id': 'nx_handler_cmdstr' }, False)
    try:
        for s in unparsed_strings:
            # pre processing to clean up strings was already done in building the list (now clean CSV strings)
            nh_cmd_str = ''
            for nh_cmd_str in s.split(','):
                    nh_cmd_str = nh_cmd_str.strip() # need this BEFORE splitting ' ' (to avoid empty strings in list)
                    try:
                        func_args = [i.strip() for i in nh_cmd_str.split(' ')]
                        func, args_list = func_args[0], func_args[1:]  # func_args[] may be empty, which is OK for some NhCmds
                        # if len(func_args) > 1:
                        #     func, args_list = func_args[0], func_args[1:]  # func_args[] may be empty, which is OK for some NhCmds
                        # else:
                        #     func, args_list = func_args[0], None
                    except:
                        # nh_cmd_str is empty (after stripping)
                        continue
                    # NB arguements will be passed to all functions AS A LIST OF STRINGS - with no guarantee they contain the correct data (or even num args) - error handling is required in each function (can raise back to here)
                    try:
                        nh_cmd_func = FUNC_DICT[func]
                    except:
                        if not str(nh_cmd_str) in KNOWN_BAD_STATES:  # frequent trivial errors
                            bad_cmds.extend([nh_cmd_str])
                            err_msg = 'Provided NhCmd does not start with a function registered in FUNC_DICT: <{}>.'.format(nh_cmd_str)
                            logger.warning('nextion_handler.py ' + err_msg)
                            #raise ValueError(err_msg)
                        continue
                    try:
                        nh_cmd_func(args_list, esphome_domain, nx_service)
                        #good_cmds.extend([nh_cmd_str])
                    except ValueError as exptn:
                        if str(exptn) == 'SKIP':
                            # Intentional exception to indicate NhCmd should be skipped and processing of next NhCmd should continue
                            continue
                        elif not str(nh_cmd_str) in KNOWN_BAD_STATES:
                            logger.warning('nextion_handler.py ' + 'Skipped NhCmd (gave errors): <{}>.'.format(nh_cmd_str))
                            bad_cmds.extend([nh_cmd_str])
                        continue  # skip bad command and continue to next in list
                    #!good_cmds.extend([nh_cmd_str]) #! for debug - COMMENT OUT when done
        # Send subroutine to update Nextion display with refreshed data after a 'SET' update
        if nxh_call_type == 'SET':
            if nh_cmd_func != 'sub':  # skip if the last NhCmd was a Nx subroutine call
                sub([NX_UI_UPDATE], esphome_domain, nx_service)
    except Exception as exptn:    # <<< These exceptions are not expected (either corner cases or BUG in script)
        if str(command_strings) == 'None' or not unparsed_strings:
            # skip logging errors for trivial anticipated issues (more efficient to catch these in exceptions than waste time testing for them)
            pass
        else:
            err_msg = '{}\nNextion Handler EXCEPTION - failed trying to call command:\n<{}>.'.format(exptn, nh_cmd_str)
            logger.error('nextion_handler.py ' + err_msg)
            #hass.services.call('persistent_notification', 'create', {'title': 'Nextion Handler BUG!?', 'message': err_msg, 'notification_id': 'nx_handler_error_main' }, False)
        continue_script = False
        repeat_num = 0



#*__________________________________________________________
#* Provide notification with list of NhCmds that gave errors for user to fix/debug in their Nextion HMI strings
if bad_cmds:
    err_msg = 'Nextion Handler had problems with the following NhCmds:\n<{}>'.format('>\n<'.join(bad_cmds))
    hass.services.call('persistent_notification', 'create', {'title': 'Nextion Handler completed with Errors!', 'message': err_msg, 'notification_id': 'nx_handler_error_done' }, False)
if nxh_call_type == 'ACT':
    if good_cmds:
        msg = 'Nextion Handler successfully completed the following ACTIONS:\n<{}>'.format('>\n<'.join(good_cmds))
        hass.services.call('persistent_notification', 'create', {'title': 'Nextion Handler completed', 'message': msg, 'notification_id': 'nx_handler_info_done' }, False)
