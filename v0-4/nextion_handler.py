#* Handler for HA 'command_strings' sent from Nextion events & update requests.
# A framework that allows a Nextion touch screen device (NSPanels in particular)
# to be programmed to interact with Home Assistant. This uses a supporting
# Python script (that handles HA 'command_strings' sent from Nextion to request
# updates of HA data and to perform actions on HA) and some boilerplate code (to
# handle the loop of sending actions and receiving updated data).
# see: https://github.com/krizkontrolz/Home-Assistant-nextion_handler
# ------------------------------------------------------------------------------
#
#* SET COMMAND LIST
#    (Nx = Nextion variable name (EXCL '.val'/'.txt'); E = $alias/HA entity_id).
#    sett Nx len E  (assign len chars of state of E, as string/text, to Nx).
#    setn Nx scale E (assign Nx the integer value of scale * state of E).
#    setb Nx E (assign Nx a value of 0 or 1 based the binary interpretation of
#         the state of E (given by str(state of E) in FALSE_STATES)).
#    setb Nx E cp x (assign Nx the value of the binary expression from
#         comparing the state of E to x where cp in [eq, ne, lt, le, gt, ge])
#
#* ACTION COMMAND LIST
#    tgl E (toggle E)
#    ton E (turn on E)
#    tof E (turn off E)
#    inps E string (set value of input_select E to string)
#    inpb E 0/1 (set value of input_binary to (state of E != 0))
#    inpn E x (set value of input_number to x)
#    scpt E (call script E)
#    scn E (set scenario E)
#    swt E 0/1 (turn switch E on or off)
#    say E string (Play TTS of message string to media player E)
#    ntf string (Send a persistent notification with message string to HA)
#    sub Nx ('click' the Nextionx (hidden) hotspot Nx to execute a 'subroutine')
# ------------------------------------------------------------------------------
#
#* CHANGELOG:
#* v0.4 2022-02-16...
#  Return to a single automation in HA YAML
#  Nx UPDATE_LOOP now controls timing of: slow UPDATEs, ACTIONs, fast UPDATEs (with delays & repeats) after user interactions
#  Fast update speed & repeat settings can now override the defaults in SEND_ACTIONS (to allow customised updates after actions involving high-lag devices, e.g., garage door, blinds, etc.)
#  The 'sub APPLY_VARS' HaCmd (which should be at the end of HA_SET1...) gives the nextion_handler control of timing of Nx UI updates (to immediately follow sending the update data requested in HA_SET1...)
# Key default parameters controlling UPDATE_LOOP moved to Global_Settings in Program.s* (so that they can be adjusted/tweaked live from HA by sending Nextion Instructions).
# Started marking ~~~boilerplate ~~~ parts of HMI code more clearly & consistently.
#* v0.3 2022-02-14 ...
#   Separated lists of ACTION & UPDATE command strings (for easier separation in triggering, processing and delay between them)
#   Simplified main program loop to only Actions OR Update (based on trigger)
#   Removed delays & repeats from this script (processing them in a Py script is not a good fit with HA multithreaded Py environment)
#   Use THREE separate HA YAML components (call this script from separate places):
#     ACTION automation (... -> delayed update script)
#     UPDATE automation
#     DELAYED update script (with repeats) - called at the end of this Py script IF it was an ACTION
#* v0.2 2022-02-10 ...
#   Transferred  control of  looping and sequencing from Nx to this script (with new sub, rpt and noupdt HaCmds)
#* v0.1 2022-01 ...
#   First version where all loop/sequencing control was attempted on the Nextion (double inter-linked timer loops)
# ------------------------------------------------------------------------------
#
# TODO: Light controls for Brt/CT/RGB/Colour-wheel
#    lt E Brt CT/_ (r g b)/_ (x y r)/_ (set light E attributes (x y r interpret Nextion colour wheel))
#    Need to finish designing and testing Nx control page first (with hiding/showing appropriate elements)




#*------------------------------------------------------------------------------
#* CONFIGURABLE CONSTANTS

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

#* Valid Nextion data attribute extensions
STANDARD_NX_DATA_EXTs = ['.val', '.txt']

#* List of entity states (as strings) to be interpreted as false (return a value of 0 when assigned to a binary Nx variable)
FALSE_STATES = [
    'off',
    'Off',
    'False',
    'None',
    '0',
    '',
    'unavailable',
    'unknown',
    'undefined'
]


#*------------------------------------------------------------------------------
#* HANDLER FUNCTIONS for each HaCmd instruction
#*------------------------------------------------------------------------------
# Extend funtionality of Hanlder by adding extra custom functions as needed
# (then add to FUNC_DICT dictionary below).

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


def nx_var_parse (nx_shorthand, data_type = 'val'):
    '''Interpret 'shorthand' Nextion variable names by appending their data type
    return: the full Nextion variable name (for nx_cmd) and 
            the standardised lookup name for that Nextion variable
                (the standard key that would link that Nextion variable to its
                paired Home Assistant entity_id in ENTITY_ALIASES dictionary)
            the data type ('val' for ints, or 'txt' for strings)'''
    ext = nx_shorthand[-4:]
    if ext in STANDARD_NX_DATA_EXTs:
        # The Nextion variable name already included its datatype extension
        data_type = ext[-3:]
        nx_lookup = nx_shorthand  # INCLUDE the extension where explicity specified so that unique naming/aliasing of multiple attributes of the same object is preserved
        nx_full = nx_shorthand
    else:
        nx_parts = nx_shorthand.split('.')
        if len(nx_parts) == 3:
            # Assume there is an unlisted extension and that it is to be treated as a 'val' (int)
            data_type = 'val'
            nx_lookup = nx_shorthand  # INCLUDE the extension where explicity specified so that unique naming/aliasing of multiple attributes of the same object is preserved
            nx_full = nx_shorthand
        elif len(nx_parts) == 1:
            # Assume this is a Program.s* Global variable (int, with no page_name prefix, or data ext)
            data_type = 'val'
            nx_lookup = nx_shorthand
            nx_full = nx_shorthand
        else:
            # The Nextion variable was 'shorthand', without a datatype extension
            ext = '.' + data_type
            nx_full = nx_shorthand + ext
            nx_lookup = nx_shorthand  # EXCLUDE the data extension where shorthand (without ext) was specified
        # err_msg = '{}\nNextion Handler failed parsing the Nextion variable name:\n\
        #     {}.'.format(expt, nx_shorthand)
    return nx_full, nx_lookup, data_type


def get_entity_id_state(e, nx_lookup=None, class_prefix=None):
    '''Translate the (shorthand) HA entity parameter by:
        * treating e as an alias (leading $ stripped to create lookup key) to
            find its matching entity_id in the ENTITY_ALIASES dictionary, or
        * if e == '$' use nx_lookup (the standardised lookup key for a Nextion
            variable) as the key (no leading $) for ENTITY_ALIASES dictionary, or
        * assigning e directly (adding the expected class prefix if missing).
    Dictionary ALIASES are the EXPECTED way of specifying 'e' in HaCmds:
        An alias is indicated in the HaCmd if 'e' has a preceding '$'
        The ENTITY_ALIASES lookup key REMOVES the '$' (easier to manage the dictionary that way)
        (Directly specifying the entity_id is not preferred, but supported).
    Checks the entity_id is valid, and raise ValueError if not.

    * SET HaCmds typically provide nx_lookup (from the Nx variable being set).
    * ACTION HaCmds typically provide the class_prefix of the entity being acted on. 
    Return the entity_id and its state.
    '''
    # Expected/typical use case is 'e' provided an an alias, indicated by a preceding '$'
    if len(e) == 1:
        # e == '$' indicates the standardised lookup key for the Nextion variable should be used
        key = nx_lookup
    else:
        # '$...' indicates an explicitly named alias - remove the $ to get the lookup key
        key = e[1:]
    # empty string/None is not expected - will be handled by exceptions
    try:
        entity_id = ENTITY_ALIASES[key]
    except:
        # no valid alias - test if it is a directly specified entity_id
        if class_prefix and e[:len(class_prefix)] != class_prefix:
            entity_id = class_prefix + e
        else:
            entity_id = e
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
            [nx, chars, e] = args_list
            try:
                int_chars = int(chars)
            except:
                raise ValueError('Number of chars is not an integer.')
            nx_full, nx_lookup, data_type = nx_var_parse(nx, 'txt')
            #state = entity_state(e, nx_lookup)
            entity_id, state = get_entity_id_state(e, nx_lookup=nx_lookup)  # will raise exception if it can't translate e to valid entity_id
            if state is not None:
                new_value = '"' + str(state)[:int_chars] +'"'  # Nextion commands need double quotes for text
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
    '''setn Nx scale E (assign Nx the integer value of scale * state of E)
    The scaling factor can cater for the way Nx uses ints to represent floats
    and for changing of units (e.g W - kW fits better on small display)
    (e.g. HA state in W * scalefactor of 0.01 gives Nx 1 dp float in kW)
    '''
    try:
        if len(args_list) == 3:
            [nx, scale_str, e] = args_list
            try:
                scale_factor = float(scale_str)
            except:
                raise ValueError('The scaling factor provided is not a valid number: {}.'.format(scale_str))
            nx_full, nx_lookup, data_type = nx_var_parse(nx)
            #state = entity_state(e, nx_lookup)
            entity_id, state = get_entity_id_state(e, nx_lookup=nx_lookup)  # will raise exception if it can't translate e to valid entity_id
            try:
                new_value = int(float(state) * scale_factor)
            except:
                #! invalid int: assigning 0 is valid/better option for most of my sensors
                #err_msg = 'The entity state did not return a valid number: {}, {} : {}.'.format(e, nx_lookup, state)
                # raise ValueError(err_msg)  # move on WITHOUT sending value to Nextion
                new_value = 0  # use this instead to FORCE assignment of default value instead (e.g. non-numeric solar power sensor at night)
                #logger.warning('nextion_handler.py ' + err_msg)
            nx_cmd_str = '{}={}'.format(nx_full, new_value)
            nx_cmd(nx_cmd_str, domain, service)
        else:
            raise ValueError('Wrong number of items in arguments list.')
    except ValueError as exptn:
        err_msg = '{}\nNextion Handler failed within SET function:\n<{}> <{}>.'.format(exptn, 'setn', '> <'.join(args_list))
        #logger.warning('nextion_handler.py ' + err_msg)
        #hass.services.call('persistent_notification', 'create', {'title': 'Nextion Handler Error!', 'message': err_msg, 'notification_id': 'nx_handler_error_set' }, False)
        raise ValueError(err_msg)
    return True


def setb (args_list, domain, service):
    '''setb Nx E (assign Nx the value of the binary interpretation of the state of E)
    setb Nx E cp x (assign Nx the value of the binary expression from comparing
        the state of E to x where cp in [eq, ne, lt, le, gt, ge])'''
    try:        
        if len(args_list) == 2:
            [nx, e] = args_list
            nx_full, nx_lookup, data_type = nx_var_parse(nx)
            #state = entity_state(e, nx_lookup)
            entity_id, state = get_entity_id_state(e, nx_lookup=nx_lookup)  # will raise exception if it can't translate e to valid entity_id
            new_value = 0 if str(state) in FALSE_STATES else 1
            nx_cmd_str = '{}={}'.format(nx_full, new_value)
            nx_cmd(nx_cmd_str, domain, service)
        elif len(args_list) == 4:
            [nx, e, cp, x] = args_list
            nx_full, nx_lookup, data_type = nx_var_parse(nx)
            #state = entity_state(e, nx_lookup)
            entity_id, state = get_entity_id_state(e, nx_lookup=nx_lookup)  # will raise exception if it can't translate e to valid entity_id
            if data_type == 'txt':
                state = str(state)
            else:
                try:
                    x = float(x)
                    state = float(state)
                except:
                    raise ValueError('Either the state or comparison value are not valid numbers: state: <{}>; comparison: <{}>.'.format(state, x))
            #if type(state) in [int, float]:
            #    x = float(x)
            if cp == 'eq':
                new_value = 1 if state == x else 0
            elif cp == 'ne':
                new_value = 1 if state != x else 0
            elif cp == 'lt':
                new_value = 1 if state <  x else 0
            elif cp == 'le':
                new_value = 1 if state <= x else 0
            elif cp == 'gt':
                new_value = 1 if state >  x else 0
            elif cp == 'ge':
                new_value = 1 if state >= x else 0
            else:
                raise ValueError("Provided boolean comparator '{}' is invalid.".format(cp))
            nx_cmd_str = '{}={}'.format(nx_full, new_value)
            nx_cmd(nx_cmd_str, domain, service)
        else:
            raise ValueError('Wrong number of items in arguments list.')
    except ValueError as exptn:
        err_msg = '{}\nNextion Handler failed within SET function:\n<{}> <{}>.'.format(exptn, 'setb', '> <'.join(args_list))
        logger.warning('nextion_handler.py ' + err_msg)
        #hass.services.call('persistent_notification', 'create', {'title': 'Nextion Handler Error!', 'message': err_msg, 'notification_id': 'nx_handler_error_set' }, False)
        raise ValueError(err_msg)
    return True



#_________________
#* ACTION FUNCTIONS - perform an action in HA (don't do anything to Nx)


#* ---- Actions for GENERIC Entities, NO PREFIX/CLASS can be assumed ------
#  $Aliases are preferred for all entity arguements entered in Nx HaCmds.
#  (If HA entitiy_ids are used instead, the full entity_id, including class,
#  is required for the functions immediately below.  Class can be deduced for the next block of HaCmds.)

def tgl(args_list, domain, service):
    '''tgl E (toggle E)'''
    prefix = None # multiple entity classes - user needs to be explicit
    domain = 'homeassistant'
    service = 'toggle'
    try:
        # FULL entity required - a generic function across multiple types of entities
        if len(args_list) == 1:
            [e] = args_list  # Quaint notation is for consistency with Actions that have 2+ args
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
            [e] = args_list
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
            [e] = args_list
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
# be deduced and added (but $ aliases are still the expected norm in HaCmds)

def inps(args_list, domain, service):
    '''inps E string (set value of input_select E to string)'''
    prefix = 'input_select.'
    domain = 'input_select'
    service = 'set_value'
    try:
        if len(args_list) == 2:
            [e, string] = args_list
            entity_id, unused = get_entity_id_state(e, class_prefix=prefix)  # will raise exception if it can't translate e to valid entity_id
            service_data = {'entity_id': entity_id, 'value': string }
            try:
                hass.services.call('input_select', 'set_value', service_data, False)
            except:  # need HASS API docs to be explicit about the exception to catch here
                raise ValueError('Failed HASS input_number service call.')
        else:
            raise ValueError('Wrong number of items in arguments list.')
    except ValueError as exptn:
        err_msg = '{}\nNextion Handler failed within ACTION function:\n<{}> <{}>.'.format(exptn, 'inps', '> <'.join(args_list))
        logger.warning('nextion_handler.py ' + err_msg)
        #hass.services.call('persistent_notification', 'create', {'title': 'Nextion Handler Error!', 'message': err_msg, 'notification_id': 'nx_handler_error_set' }, False)
        raise ValueError(err_msg)
    return True


def inpb(args_list, domain, service):
    '''inpb E b(0/1) (set value of input_binary to state of b != 0)'''
    prefix = 'input_boolean.'
    domain = 'input_boolean'
    service = 'set_value'
    try:
        if len(args_list) == 2:
            [e, b] = args_list
            entity_id, unused = get_entity_id_state(e, class_prefix=prefix)  # will raise exception if it can't translate e to valid entity_id
            service_data = {'entity_id': entity_id, 'value': b != '0' }
            try:
                hass.services.call('input_boolean', 'set_value', service_data, False)
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
    '''inpn E x (set value of input_number to x)'''
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


def scn(args_list, domain, service):
    '''scn E (set scenario E)'''
    prefix = 'scene.'
    domain = 'scene'
    service = 'turn_on'
    try:
        if len(args_list) == 1:
            [e] = args_list
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
    '''scpt E (call script E)'''
    prefix = 'script.'
    domain = 'script'
    service = 'turn_on'
    try:
        if len(args_list) == 1:
            [e] = args_list
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


#! RGB/WW/Dimmer Colour wheel support functions still needed for lights
def lt(args_list, domain, service):
    '''lt e Brt CT/_ (r_ g_ b_) (x y r/_) (set light attributes (x y r interpret Nextion colour wheel))
    Need to add this functionality including:
        if loop for valid attributes to apply
        x y r handling for Nextion colour wheel
        return Nextion color value to Nextion & set it to a provided variable (?) to update colour wheel?
    '''
    prefix = 'light.'
    domain = 'light'
    service = 'turn_on'
    color_wheel_used = False
    try:
        if len(args_list) >= 1 and len(args_list) <= 9:
            args_list.extend(['_'] * 8)  #! update once final max possible num args is known for sure
            [e, br, ct, r, g, b, x, y, r] = args_list[:9]
            entity_id, unused = get_entity_id_state(e, class_prefix=prefix)  # will raise exception if it can't translate e to valid entity_id
            if entity_id[:len(prefix)] != prefix:
                entity_id = prefix + entity_id
            if br != '_':
                pass
                # set brightness
            if ct != '_':
                pass
                # set colour temperature
            if (x != '_') and (y != '_') and (r != '_'):
                pass
                # cacl r,g,b from colorwheel coordinates
                color_wheel_used = True
            if (r != '_') and (b != '_') and (b != '_'):
                pass
                # set r,g,b
                # calc nextion rgb
            if color_wheel_used:
                pass
                # update Nextion color wheel?
        else:
            raise ValueError('Wrong number of items in arguments list.')
    except ValueError as exptn:
        err_msg = '{}\nNextion Handler failed within ACTION function:\n<{}> <{}>.'.format(exptn, 'lt', '> <'.join(args_list))
        logger.warning('nextion_handler.py ' + err_msg)
        #hass.services.call('persistent_notification', 'create', {'title': 'Nextion Handler Error!', 'message': err_msg, 'notification_id': 'nx_handler_error_set' }, False)
        raise ValueError(err_msg)
    return True


#*_________________
#*  Info Actions

def say(args_list, domain, service):
    '''say E msg (Play TTS of message string msg to media player E)'''
    prefix = 'media_player.'
    domain = 'tts'
    service = 'google_translate_say'
    try:
        if len(args_list) == 2:
            [e, msg] = args_list
            entity_id, unused = get_entity_id_state(e, class_prefix=prefix)  # will raise exception if it can't translate e to valid entity_id
            service_data = {'entity_id': e, 'message': msg }
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
    '''ntf msg (Send a persistent notification with message string to HA)'''
    # no entity or prefix
    domain = 'persistent_notification'
    service = 'create'
    try:
        if len(args_list) == 1:
            [msg] = args_list
            hass.services.call('persistent_notification', 'create', {'title': 'Nextion forwareded Notification', 'message': msg, 'notification_id': 'nx_notify' }, False)
        else:
            raise ValueError('Wrong number of items in arguments list.')
    except ValueError as exptn:
        err_msg = '{}\nNextion Handler failed within ACTION function:\n<{}> <{}>.'.format(exptn, 'ntf', '> <'.join(args_list))
        logger.warning('nextion_handler.py ' + err_msg)
        #hass.services.call('persistent_notification', 'create', {'title': 'Nextion Handler Error!', 'message': err_msg, 'notification_id': 'nx_handler_error_set' }, False)
        raise ValueError(err_msg)
    return True



#*******************
#* CONTROL FUNCTIONS - controlling looping and sequencing in this script (and the combined interactions with Nx)
#*******************

def sub(args_list, domain, service):
    '''sub Nx ('click' the Nx hotspot t to execute a Nx 'subroutine')'''
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
#             xn = min(1, xn)  #! <<<< Don't let anything excessive get through
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
#* DICTIONARY OF FUNCTIONS (translates HaCmd text to associated function above)
#*------------------------------------------------------------------------------
#! Add any new custom functions to this dictionary
# HA won't allow locals() in script to automtically build dictionary of our functions - have to do it manually instead
FUNC_DICT ={
    #* SET functions
    'sett': sett,
    'setn': setn,
    'setb': setb,
#    'setlt': setlt,
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
    'lt': lt,
    # Info Actions
    'say': say,
    'ntf': ntf,
    #* CONTROL functions (unusual behaviour to break out of, control, or modify nested loops)
    'sub': sub
}


#*------------------------------------------------------------------------------
#* MAIN SCRIPT
#*------------------------------------------------------------------------------

#*_________________________________
#* Initialse loop/control variables
continue_script = True
is_ha_act_string = True  # first string in list is HA_Action (special case, following user interaction, indicated by positive trig_val)
unparsed_strings = []
bad_cmds = []
rpt_cmds = []
good_cmds = []
repeat_num = 0 # this value (& delay below) can be modified during the loop by HaCmds rpt() and noupd()
repeat_delay = -99 # (secs) If HA_Act includes a rst command, its settings will take precedence over defaults in HA_Set1..
command_strings = []
unparsed_strings = []
args_list = []

#* variables used in Exception messages
trig_str = None
trig_ent = None
nx_cmd_service = None
trig_val = None
s = None
ha_cmd_str = None
func = None
esphome_domain = None
nx_service = None

KNOWN_BAD_STATES = ['unknown', 'unavailable', 'None']  # entity states returned HA that often trigger trivial errors

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
    # command_strings should be a list of entities whose states are strings of comma- or \n- delimited HaCmds
    #   action_cmds: (POSITIVE trig_val, triggered by USER INTERACTION) is list of HA_Act entity_ids containg strings (a sequence of ACTION HaCmds)
    #   update_cmds: (NEGATIVE trig_val, Nx POLLING to refresh its data from HA) is a list of Ha_Set1.. entity_ids containing strings (a sequence of SET HaCmds)

    if trig_val > 0:
        # Positive TRIGGER Indicates new HA_Act needs to be processed (USER INTERACTIONS should be prioritised over polling in script flow)
        try:
            command_strings = data.get('action_cmds')
        except:
            continue_script = False
            raise ValueError('Provided list of action_cmds is not valid: {}.'.format(command_strings))
    elif trig_val < 0:
        # Negative TRIGGER Indicates a data update for page (non-interactive POLLING from Nx) - only process the HA_Set strings (skip the HA_Act that is first in the list)
        try:
            command_strings = data.get('update_cmds')
        except:
            continue_script = False
            raise ValueError('Provided list of update_cmds is not valid: {}.'.format(command_strings))
    else:  # trig_val == 0:
        # 0 indicates Nx has turned off interaction with HA (e.g. sleeping) - skip the intial state change to 0
        #<< catch INTENTIONAL exception (NOT an error) and exit script
        continue_script = False
        raise ValueError('EXIT') 


    #* Create a list of strings to be parsed into HaCmds (Action or Set) to be executed
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
    try:
        for s in unparsed_strings:
            # pre processing to clean up strings was already done in building the list (now clean CSV strings)
            ha_cmd_str = ''
            for ha_cmd_str in s.split(','):
                    ha_cmd_str = ha_cmd_str.strip() # need this BEFORE splitting ' ' (to avoid empty strings in list)
                    try:
                        func_args = [i.strip() for i in ha_cmd_str.split(' ')]
                        func, args_list = func_args[0], func_args[1:]  # func_args[] may be empty, which is OK for some HaCmds
                        # if len(func_args) > 1:
                        #     func, args_list = func_args[0], func_args[1:]  # func_args[] may be empty, which is OK for some HaCmds
                        # else:
                        #     func, args_list = func_args[0], None
                    except:
                        # ha_cmd_str is empty (after stripping)
                        continue
                    # NB arguements will be passed to all functions AS A LIST OF STRINGS - with no guarantee they contain the correct data (or even num args) - error handling is required in each function (can raise back to here)
                    try:
                        HaCmd = FUNC_DICT[func]
                    except:
                        if not str(ha_cmd_str) in KNOWN_BAD_STATES:  # frequent trivial errors
                            bad_cmds.extend([ha_cmd_str])
                            err_msg = 'Provided HaCmd does not start with a function registered in FUNC_DICT: <{}>.'.format(ha_cmd_str)
                            logger.warning('nextion_handler.py ' + err_msg)
                            #raise ValueError(err_msg)
                        continue
                    try:
                        HaCmd(args_list, esphome_domain, nx_service)
                        #good_cmds.extend([ha_cmd_str])
                    except ValueError as exptn:
                        if not str(ha_cmd_str) in KNOWN_BAD_STATES:
                            logger.warning('nextion_handler.py ' + 'Skipped HaCmd (gave errors): <{}>.'.format(ha_cmd_str))
                            bad_cmds.extend([ha_cmd_str])
                        continue  # skip bad command and continue to next in list
    except Exception as exptn:    # <<< These exceptions are not expected (either corner cases or BUG in script)
        if str(command_strings) == 'None' or not unparsed_strings:
            # skip logging errors for trivial anticipated issues (more efficient to catch these in exceptions than waste time testing for them)
            pass
        else:
            err_msg = '{}\nNextion Handler EXCEPTION - failed trying to call command:\n<{}>.'.format(exptn, ha_cmd_str)
            logger.error('nextion_handler.py ' + err_msg)
            #hass.services.call('persistent_notification', 'create', {'title': 'Nextion Handler BUG!?', 'message': err_msg, 'notification_id': 'nx_handler_error_main' }, False)
        continue_script = False
        repeat_num = 0



#*__________________________________________________________
#* Provide notification with list of HaCmds that gave errors for user to fix/debug in their Nextion HMI strings
if bad_cmds:
    err_msg = 'Nextion Handler had problems with the following HaCmds:\n<{}>'.format('\n'.join(bad_cmds))
    hass.services.call('persistent_notification', 'create', {'title': 'Nextion Handler completed with Errors!', 'message': err_msg, 'notification_id': 'nx_handler_error_done' }, False)

