# * Home Assistant Nextion Handler
# * (v0.7_2022-07-30)
# Handler for NH 'command_strings' sent from Nextion events & update requests.
# see: https://github.com/krizkontrolz/Home-Assistant-nextion_handler
#
# ------------------------------------------------------------------------------
#
# * CHANGELOG: https://github.com/krizkontrolz/Home-Assistant-nextion_handler/blob/main/CHANGELOG.md
#
# ------------------------------------------------------------------------------
#
# TODO:
#    (v0.7 new features complete)
#    ...
# ------------------------------------------------------------------------------
# Reformatted code with Black: https://black.vercel.app/

VERSION = 20220730  # version of this script as YYYYMMDD integer; ('__version__' not allowed in restricted env)

# *------------------------------------------------------------------------------
# * CONFIGURABLE CONSTANTS
# *------------------------------------------------------------------------------

NX_UI_UPDATE = "APPLY_VARS"  # name of Nx 'subroutine' to click to apply the refreshed data to the UI after a data update
NX_CMD_SERVICE = None  # GLOBAL - stores the YAML parameter for ESPH 'send' to pass to output function

# * Valid Nextion data attribute extensions/suffixes (exluding preceding '.')
STANDARD_NX_DATA_EXTs = ["val", "txt"]

# * List of entity states (as strings) to be interpreted as false (return a value of 0 when assigned to a binary Nx variable)
# 'None' (text, title-case, e.g., button inactive state - not invalid)
FALSE_STATES = [
    "off",
    "False",
    "0",
    "None",
    "none",
    "",
]

# * List of entity states (as strings) to be interpreted as missing ("Unavailable", "not available")
INVALID_STATES = [
    "unavailable",
    "unknown",
    "undefined",
]

# * WIDGETCONSTANTS
# widgets_read = False  #not used #do not read 'widgets:' from YAML until needed, then flag when this is done
MAX_ICON_NUM = 167  # limited to this by max image size allowed by Nextion
BLANK_ERR_ICON = 47  # Widget state 0=Blank, 1=Error! versions of icon
UNAVAILABLE_ICON = 46
DEFAULT_ICON = 0  # eye symbol, default for valid sensors in unknown domain

DOMAIN_NUM_MASK = 127  # first 7 bits give unique code for entity domain
TOGGLE_MASK = 384  # sum of individual toggle masks
DIRECT_TOGGLE_MASK = 128  # indicates the domain has an actual 'toggle' service
LOGICAL_TOGGLE_MASK = 256  # NOT directly with 'hass.toggle'
ALL_INTERACTIONS_MASK = 3968  # extracts all interactive capabilities

# Gives the Domain_code & default Icon_num (cropped from image pair) for each domain.
# Domain_code is bit encoded:
#   Unique domain (bits 0..6),
#   (HA actions) Toggleable (bit7), logical toggleable (bit8), other HA action (bit9),
#   (Nx actions) other Nx action (bit10), Nx pop-up (bit11).
DOMAINS_DICT = {
    "blank": (0, BLANK_ERR_ICON),
    "alarm_control_panel": (513, 1),
    "automation": (642, 2),
    "binary_sensor": (3, 3),
    "button": (516, 4),
    "calendar": (5, 5),
    "camera": (134, 6),
    "climate": (2823, 7),
    "cover": (648, 8),
    "device_tracker": (9, 9),
    "fan": (650, 10),
    "geo_location": (11, 11),
    "group": (140, 12),
    "humidifier": (653, 13),
    "input_boolean": (142, 14),
    "input_datetime": (15, 5),
    "input_number": (528, 15),
    "input_select": (529, 16),
    "light": (2706, 17),
    "lock": (531, 18),
    "media_player": (2708, 19),
    "persistent_notification": (2069, 20),
    "person": (22, 9),
    "remote": (151, 21),
    "scene": (536, 22),
    "script": (153, 23),
    "select": (538, 16),
    "sensor": (27, 24),
    "siren": (156, 25),
    "sun": (29, 26),
    "switch": (158, 27),
    "timer": (543, 28),
    "update": (544, 29),
    "vacuum": (801, 30),
    "water_heater": (546, 31),
    "weather": (35, 26),
    "zone": (36, 32),
}

# * Entity Class dictionaries (for icons etc.)

BIN_SENSOR_DICT = {
    "battery": ["normal", "LOW", 96],
    "battery_charging": ["OFF", "charging", 3],
    "carbon_monoxide": ["clear", "CO", 102],
    "cold": ["normal", "COLD", 158],
    "connectivity": ["OFF", "connected", 37],
    "door": ["closed", "OPEN", 97],
    "garage_door": ["closed", "OPEN", 139],
    "gas": ["clear", "GAS", 102],
    "heat": ["normal", "HOT", 159],
    "light": ["off", "LIGHT", 17],
    "lock": ["locked", "UNLOCKED", 98],
    "moisture": ["dry", "WET", 99],
    "motion": ["clear", "MOTION", 100],
    "moving": ["stopped", "MOVING", 100],
    "occupancy": ["clear", "OCCUPIED", 100],
    "opening": ["closed", "OPEN", 97],
    "plug": ["OFF", "plugged", 101],
    "power": ["OFF", "power", 27],
    "presence": ["away", "home", 95],
    "problem": ["OK", "problem", 40],
    "running": ["OFF", "running", 3],
    "safety": ["safe", "UNSAFE", 40],
    "smoke": ["clear", "SMOKE", 102],
    "sound": ["clear", "SOUND", 81],
    "tamper": ["clear", "TAMPER", 40],
    "update": ["none", "UPDATE", 29],
    "vibration": ["clear", "VIBRATION", 40],
    "window": ["closed", "OPEN", 103],
}

SENSOR_ICON_DICT = {
    "apparent_power": 112,
    "aqi": 113,
    "battery": 114,
    "carbon_dioxide": 115,
    "carbon_monoxide": 116,
    "current": 117,
    "date": 118,
    "energy": 126,
    "frequency": 119,
    "gas": 120,
    "humidity": 121,
    "illuminance": 122,
    "monetary": 123,
    "nitrogen_dioxide": 124,
    "nitrogen_monoxide": 124,
    "nitrous_oxide": 124,
    "ozone": 124,
    "pm1": 124,
    "pm25": 124,
    "pm10": 124,
    "power": 112,
    "power_factor": 125,
    "pressure": 24,
    "reactive_power": 127,
    "signal_strength": 128,
    "sulphur_dioxide": 124,
    "temperature": 129,
    "timestamp": 118,
    "volatile_organic_compounds": 124,
    "voltage": 130,
}

COVER_ICON_DICT = {
    "awning": 141,
    "blind": 8,
    "curtain": 137,
    "damper": 142,
    "door": 138,
    "garage": 139,
    "gate": 140,
    "shade": 8,
    "shutter": 141,
    "window": 136,
}


# *------------------------------------------------------------------------------
# * HANDLER FUNCTIONS for each NhCmd instruction
# *------------------------------------------------------------------------------
# Extend funtionality of Hanlder by adding extra custom SET & ACT functions.
# (Then add to FUNC_DICT dictionary below).


# *_________________________
# * GENERAL HELPER FUNCTIONS

#! OLD - replaced with send_nx_cmd(nx_command_str) 2022-07-21
# def nx_cmd(nx_command_str, domain, service):
#     '''Send the Nextion command string to the send cmd service for the Nextion device'''
#     try:
#         service_data = {'cmd': nx_command_str}  #!.encode('iso-8859-1')
#         hass.services.call(domain, service, service_data, False)
#         # #!
#         # dbg_msg = 'Nextion Handler sent Nextion command:\n<{}>.'.format(nx_command_str)
#         # hass.services.call('persistent_notification', 'create', {'title': 'Nextion Handler Debug', 'message': dbg_msg, 'notification_id': 'nx_handler_debug' }, False)
#     except Exception as exptn:
#         err_msg = '{}\nNextion Handler failed sending the Nextion command:\n\
#             <{}>\n to the service _{}.{}_.'.format(exptn, nx_command_str, domain, service)
#         logger.error('nextion_handler.py ' + err_msg)
#         hass.services.call('persistent_notification', 'create', {'title': 'Nextion Handler Error!', 'message': err_msg, 'notification_id': 'nx_handler_error_helper' }, False)
#         raise Exception(err_msg)
#     return True


def send_nx_cmd(nx_command_str):
    """Send the Nextion command string to the send cmd service for the Nextion device"""
    # NOTE: NX_CMD_SERVICE is now a GLOBAL variable, to save repeatedly passing it between functions.
    # Encode all text consistently as UTF-8: Py(HA default), ESPH, Nx.
    try:
        esph_domain, esph_send_service = NX_CMD_SERVICE.split(".")
        service_data = {"cmd": nx_command_str}
        hass.services.call(esph_domain, esph_send_service, service_data, False)
    except Exception as exptn:
        err_msg = "{}\nNextion Handler failed sending the Nextion command:\n\
            <{}>\n to the ESPHome send service _{}_.".format(
            exptn, nx_command_str, NX_CMD_SERVICE
        )
        logger.error("nextion_handler.py " + err_msg)
        hass.services.call(
            "persistent_notification",
            "create",
            {
                "title": "Nextion Handler Error!",
                "message": err_msg,
                "notification_id": "nx_handler_error_helper",
            },
            False,
        )
        raise Exception(err_msg)
    return True


def nx_var_parse(nx_shorthand, data_type=None):
    """Interpret 'shorthand' Nextion variable names by appending their data type
    returns:
        nx_full: the full Nextion variable name (for nx_cmd).
        nx_lookup: the standardized lookup name for that Nextion variable
            (the standard key that would link that Nextion variable to its
            paired Home Assistant entity_id in ENTITY_ALIASES dictionary).
        data_type: 'val' for Nextion ints, or 'txt' for strings.
    """
    nx_full = None
    nx_lookup = None
    nx_parts = nx_shorthand.split(".")
    ext = nx_parts[-1]
    # Set data_type, #*Assume all Nextion variable attributes that don't end in '.txt' are ints(val), including Program*s globals #! check this assumption
    if data_type is None:
        data_type = "txt" if (ext == "txt") else "val"
    # Set full & lookup Nx names
    if ext in STANDARD_NX_DATA_EXTs:
        # The Nextion variable name already included its datatype extension
        nx_lookup = nx_shorthand  # INCLUDE the extension where explicity specified so that unique naming/aliasing of multiple attributes of the same object is preserved
        nx_full = nx_shorthand
    else:
        nx_lookup = nx_shorthand  # EXCLUDE the data extension where shorthand (without ext) was specified
        # * Possible shorthands with ASSUMED interpretation: (nx_shorthand, data_type) -> (nx_full, nx_lookup)
        # - t1 txt: -> t1.txt t1  (local string)
        # - sss val: -> sss sss  (Global* int) #! Cannot use 'nLocal' as shorthand for local page val
        # - PP.aaa __: -> PP.aaa.val PP.aaa (Page local/global)
        # - aaa.val __: -> PP.aaa.val aaa.val (Page local/global)
        if len(nx_parts) == 2:
            # The Nextion variable was 'shorthand', without a datatype extension (val or txt)
            nx_full = nx_shorthand + "." + data_type
        elif len(nx_parts) == 1:
            if data_type != "txt":
                # Assume nx_shorthand is a Program.s* Global variable (int, with no page_name_prefix, or data_ext_suffix)
                #! Cannot use 'nLocal' as shorthand for local page val - must include ext to distinguish from Program.s Global
                nx_full = nx_shorthand
            else:
                # Append 'txt' ext (Prog Globals cannot be text, so this must be a page-local string (e.g. t1.txt))
                nx_full = nx_shorthand + ".txt"
        elif len(nx_parts) >= 3:
            if data_type == "txt" and nx_shorthand[-3:] != "txt":
                # Add 'txt' extension if it is missing from variable that is known to be 'txt' data_type
                nx_full = nx_shorthand + ".txt"
            else:
                # Assume nx_shorthand has an unlisted extension and that it is to be treated as a 'val' (int)
                nx_full = nx_shorthand
    #! dbg msgs
    # msg = 'Nextion Handler HELPER function {}:\n\nnx_full <{}>\nnx_lookup <{}>\next <{}>'.format('nx_var_parse', nx_full, nx_lookup, ext)
    # logger.warning('nextion_handler.py ' + msg)
    # hass.services.call('persistent_notification', 'create', {'title': 'Nextion Handler Debug!', 'message': msg, 'notification_id': 'nx_handler_dbg' }, False)
    return nx_full, nx_lookup, data_type


def get_entity_id_state(e, nx_lookup=None, domain_prefix=None):
    """Translate the (shorthand) HA entity parameter (e) by:
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
    * ACTION NhCmds typically provide the domain_prefix of the entity being acted on.

    Returns:
        entity_id: the (full) HA entity_id
        ent_state: ALL the mapped state data for entity_id (incl. attributes)
        state: the string value for just the 'state' (ent_state.state) of e
    """
    name = ""
    entity_id = ""
    # $ Alias
    if e[0] == "$":
        # Expected/typical use case is 'e' provided as an alias, indicated by a '$' prefix
        if e == "$":
            # e == '$' indicates the the Nextion variable name should be used as the base of the alias
            key = nx_lookup
        else:
            # '$...' indicates an explicitly named alias - remove the $ to get the lookup key
            key = e[1:]
        try:
            entity_id = ENTITY_ALIASES[key]
        except:
            raise ValueError("$Alias not found: <{}>".format(e))
    # @ Widget number
    elif e[0] == "@":
        # '@n' Widget aliases indicates the nth entity in the calling automations YAML 'widgets:' list (indexed from 0)
        # NOTE: WIDGETS_LIST now read with other automation data at start
        # * Get list of Widgets (& their settings) from 'widgets:' YAML section
        try:
            # the rest of the entity alias after @ should be the widget number (0...) and its index position in the YAML list
            n = int(e[1:])
            # entity_id is REQUIRED - no default provided - will trigger exception if missing
            entity_id = WIDGETS_LIST[n]["entity"]
        except:
            raise ValueError(
                '@Alias for Widget not found in "widgets:" list from YAML in calling automation: <{}>'.format(
                    e
                )
            )
    # Append missing domain prefix
    elif domain_prefix and e[: len(domain_prefix)] != domain_prefix:
        entity_id = domain_prefix + e
    # Full HA entity_id (no adjustment needed)
    else:
        entity_id = e
    # Get the state of entity_id - this also ensures that entity_id is valid
    try:
        # full mapped state & attribute data for entity
        ent_state = hass.states.get(entity_id)
        state = ent_state.state  # just the _string_ for the state
    except:
        raise ValueError(
            "Home Assistant could not find specified entity_id: <{}>".format(entity_id)
        )
    return entity_id, ent_state, state


def set_nx_val(nx_shorthand, val, IS_TEXT=False):
    """Set the Nextion variable (Nx in shorthand form) to val.
    By default as a numeric Nx variable and value"""
    try:
        if IS_TEXT:
            nx_full, nx_lookup, data_type = nx_var_parse(nx_shorthand, "txt")
            nx_cmd_str = '{}="{}"'.format(nx_full, val)
            # nx_cmd(nx_cmd_str, domain, service) #! OLD
            send_nx_cmd(nx_cmd_str)
        else:
            nx_full, nx_lookup, data_type = nx_var_parse(nx_shorthand)
            nx_cmd_str = "{}={}".format(nx_full, val)
        send_nx_cmd(nx_cmd_str)
    except:
        return False
    return True


def timedelta_to_str(now, compare_time):
    """Convert the timedelta (now - compare_time) to a nicely readable string"""
    #! Debug - test speed cost
    # return ""

    try:
        if compare_time > now:
            # compare_time is in future
            td = compare_time - now
            pfx = "in "
            sfx = ""
            # return td
        else:
            # compare_time is in past
            td = now - compare_time
            pfx = ""
            sfx = " ago"
        # Parse and simplify td string formatted as 'dd day(s), hh:mm:ss.uuuuuu'
        parts = str(td).split(":")
        dh = parts[0].split(",")
        if len(dh) > 1:
            # days hr
            return "{}{} {} hr{}".format(pfx, dh[-2], dh[-1], sfx)
        elif parts[0] == "0":
            # min only
            if len(parts[1]) == 2 and parts[1][0] == "0":
                parts[1] = parts[1][1:]  # removing leading '0'
            return "{}{} min{}".format(pfx, parts[1], sfx)
        else:
            # hr min
            return "{}{} hr {} min{}".format(pfx, parts[0], parts[1], sfx)
    except:
        return "Never"


def adjust(
    x,
    adj,
    min_val,
    max_val,
    FIT_TO_RANGE=True,
    IS_MOD=None,
    AS_INT=False,
    OPTION_LIST=None,
):
    """Return the new value of a parameter 'x' after applying the
    (abs/pct/delta/delta_pct) 'adjustment' string '(+/-/--)adj(%)' to 'x':
        set x directly ('adj' or '--adj'): NOTE double '-' for a negative value;
        set x to 'adj%' between its possible min and max range;
        apply delta ajustment to x ('+adj' or '-adj');
        apply delta_%_of_range ajustment to x ('+adj%' or '-adj%').
    RETURNS: new_x, new adjusted value of x as:
            None (if check for valid 'adjustment' fails)
            float (default),
            integer (if AS_INT==True),
            a value from a list of options (if OPTION_LIST provided).
        If IS_MOD==True modulo divide out-of-range new_x (by max_val),
        otherwise truncate new_x to range bounds (unless min/max == None).
    If 'adj' is NOT a valid adjustment string, returns None.
    Subsequent exceptions are raised.
    """

    # Check 'adjustment' string is valid
    adj_str = str(adj)
    if OPTION_LIST and adj in OPTION_LIST:
        return adj  # adj is already a valid listed option (no ajustment required)
    else:
        try:
            adj_num = float(
                adj_str.replace("+", "").replace("--", "-").replace(r"%", "")
            )
        except:
            return None
    # Convert and fill in default args (when picking a value from a list / normal numeric adjustment)
    if OPTION_LIST:
        if IS_MOD is None:
            IS_MOD = True
        num_opts = len(OPTION_LIST)
        if min_val is None:
            min_val = 0
        if max_val is None:
            max_val = num_opts - 1
        modulo_val = num_opts  # NOTE: for lists must use list length (NOT max index value) - works for negative index values too
        AS_INT = True
        curr_opt = x
        try:
            x = OPTION_LIST.index(curr_opt)
        except:
            x = 0
    else:
        if IS_MOD is None:
            IS_MOD = False
        if min_val is None:
            FIT_TO_RANGE = False
            min_val = 0  # default
        if max_val is None:
            FIT_TO_RANGE = False
            IS_MOD = False
            max_val = 100  # default
        modulo_val = max_val
    # General init
    IS_PCT = False
    IS_DELTA = False
    new_x = 0  # default
    try:
        # parse what TYPE of adjustment is required (VALUE is from adj_num above)
        if adj_str[-1:] == "%":
            IS_PCT = True
            # adj_str = adj_str[:-1]
        if adj_str[0] == "+":
            IS_DELTA = True
        elif adj_str[0] == "-":
            # double '-' is a way to indicate this is an ACTUAL NEGATIVE VALUE (NOT a delta)
            # if (adj_str[1] == "-"):
            #     adj_str = adj_str[1:]
            # else:
            #     IS_DELTA = True
            if (len(adj_str) >= 2) and (adj_str[1] != "-"):
                IS_DELTA = True
        # calculate the adjustment
        if IS_DELTA:
            if IS_PCT:
                # Adjust original value by the specified PERCENT of the RANGE
                new_x = x + (max_val - min_val) * adj_num / 100
            else:
                # Adjust original value by the specified DELTA VALUE (direclty)
                new_x = x + adj_num
        else:
            if IS_PCT:
                # Set new value PERCENT location WITHIN RANGE
                new_x = min_val + (max_val - min_val) * adj_num / 100
            else:
                # Set new value DIRECTLY TO VALUE
                new_x = adj_num
        # Convert to final value (as set by kwargs options)
        if AS_INT:
            if new_x >= 0:
                new_x = int(new_x + 0.5)
            else:
                # correct int rounding of negative numbers (Note: int(-0.9)=0)
                new_x = int(new_x + 0.5) - 1
        if IS_MOD:
            new_x = new_x % modulo_val
        elif FIT_TO_RANGE:
            new_x = min_val if new_x < min_val else new_x
        if not OPTION_LIST is None:
            new_x = OPTION_LIST[new_x]
        return new_x
    except ValueError as exptn:
        err_msg = "{}\nNextion Handler failed within `adjust(x, adj, min, max, IS_MOD, AS_INT)` function:\n<{}> <{}> <{}> <{}> <{}> <{}>.".format(
            exptn, x, adjustement, min_val, max_val, IS_MOD, AS_INT
        )
        logger.warning("nextion_handler.py " + err_msg)
        # hass.services.call('persistent_notification', 'create', {'title': 'Nextion Handler Error!', 'message': err_msg, 'notification_id': 'nx_handler_error_set' }, False)
        raise ValueError(err_msg)
    # -- adjust() --


# _________________
# * SET FUNCTIONS - set variables in Nx to value of requested HA entity states (don't perform any other actions in HA)
# Nx = name of Nextion (global) variable EXCLUDING '.val' or '.txt' extension
# E = HA entity, preferably as a $alias (but can handle shorthand/full entity_id too)


def sett(args_list):
    """sett Nx chars E  (assign len chars of state of E, as string/text, to Nx)"""
    try:
        if len(args_list) == 3:
            [nx, chars_, e] = args_list
            try:
                chars = int(chars_)
            except:
                # chars = 255
                raise ValueError("Number of chars is not an integer.")
            nx_full, nx_lookup, data_type = nx_var_parse(nx, "txt")
            # state = entity_state(e, nx_lookup)
            state = get_entity_id_state(e, nx_lookup=nx_lookup)[2]
            if state is not None:
                # new_value = '"' + str(state)[:chars] +'"'  # Nextion commands need double quotes for text
                # nx_cmd_str = '{}={}'.format(nx_full, new_value)
                # send_nx_cmd(nx_cmd_str)
                set_nx_val(nx, state, IS_TEXT=True)
        else:
            raise ValueError("Wrong number of items in arguments list.")
    except ValueError as exptn:
        err_msg = "{}\nNextion Handler failed within SET function:\n<{}> <{}>.".format(
            exptn, "sett", "> <".join(args_list)
        )
        logger.warning("nextion_handler.py " + err_msg)
        # hass.services.call('persistent_notification', 'create', {'title': 'Nextion Handler Error!', 'message': err_msg, 'notification_id': 'nx_handler_error_set' }, False)
        raise ValueError(err_msg)
    return True


def setn(args_list):
    """setn Nx scale E (d) (assign Nx the integer value of scale * state of E)
    The scaling factor can cater for the way Nx uses ints to represent floats
    and for changing of units (e.g for energy, kW fits better on small display than Watts)
    (e.g. HA state in Watts * scalefactor of 0.01 gives Nx 1 dp float in kW)
    Optionally specify a value, d, to return if state of E is not numeric,
    otherwise the setn commands will be skipped on errors.
    """
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
                raise ValueError(
                    "The scaling factor provided is not a valid number: {}.".format(
                        scale_str
                    )
                )
            nx_full, nx_lookup, data_type = nx_var_parse(nx)
            state = get_entity_id_state(e, nx_lookup=nx_lookup)[2]
            try:
                new_value = int(float(state) * scale_factor)
            except:
                if d is not None:
                    if d == "e":
                        # log bad values as errors ONLY if explicity instructed by use of d = 'e'
                        err_msg = "The entity state did not return a valid number (logging of these errors requested by user specifying <e> for agrument d): {}, {} : {}.".format(
                            e, nx_lookup, state
                        )
                        raise ValueError(
                            err_msg
                        )  # move on WITHOUT sending value to Nextion
                    else:
                        # use provided default instead
                        new_value = int(d)
                else:
                    # no default value - SKIP command & leave Nx unchanged WITHOUT logging an error
                    # <<
                    raise ValueError(
                        "SKIP"
                    )  #  exception intended to be skipped (and passed to a higher level)
            # nx_cmd_str = '{}={}'.format(nx_full, new_value)
            # send_nx_cmd(nx_cmd_str)
            set_nx_val(nx, new_value)
        else:
            raise ValueError("Wrong number of items in arguments list.")
    except ValueError as exptn:
        if str(exptn) == "SKIP":
            # <<
            raise ValueError("SKIP")  # not an error - raise again
        else:
            err_msg = (
                "{}\nNextion Handler failed within SET function:\n<{}> <{}>.".format(
                    exptn, "setn", "> <".join(args_list)
                )
            )
            logger.warning("nextion_handler.py " + err_msg)
            # hass.services.call('persistent_notification', 'create', {'title': 'Nextion Handler Error!', 'message': err_msg, 'notification_id': 'nx_handler_error_set' }, False)
            raise ValueError(err_msg)
    return True
    # --- setn() ---


def setb(args_list):
    """(a) setb Nx E (d) (assign Nx the value of the binary interpretation of the state of E)
    (b) setb Nx E cp x (d) (assign Nx the value of the binary expression from comparing
        the state of E to x where cp in [eq, ne, lt, le, gt, ge])
    Optionally specify a value, d, to return if state of E is not numeric,
    otherwise the setb command will be skipped on errors.
    """
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
            state = get_entity_id_state(e, nx_lookup=nx_lookup)[2]
            if str(state) in INVALID_STATES:
                if d is not None:
                    if d == "e":
                        # log bad values as errors ONLY if explicity instructed by use of d = 'e'
                        err_msg = "The entity state did not return a valid number (logging of these errors requested by user specifying <e> for agrument d): {}, {} : {}.".format(
                            e, nx_lookup, state
                        )
                        raise ValueError(
                            err_msg
                        )  # move on WITHOUT sending value to Nextion
                    else:
                        # use provided default instead
                        new_value = d
                else:
                    # no default value - SKIP command & leave Nx unchanged WITHOUT logging an error
                    # <<
                    raise ValueError(
                        "SKIP"
                    )  #  exception intended to be skipped (and passed to a higher level)
            else:
                new_value = 0 if str(state) in FALSE_STATES else 1
            set_nx_val(nx, new_value)
        # (b) Set boolean value based on a specified COMPARISON (E cp x)
        elif len(args_list) in [4, 5]:
            if len(args_list) == 5:
                # default value, d, provided - to be assigned to Nx if entity returns invalid state
                [nx, e, cp, x, d] = args_list
            else:
                [nx, e, cp, x] = args_list
                d = None
            nx_full, nx_lookup, data_type = nx_var_parse(nx)
            state = get_entity_id_state(e, nx_lookup=nx_lookup)[2]
            if str(state) in INVALID_STATES:
                if d is not None:
                    if d == "e":
                        # log bad values as errors ONLY if explicity instructed by use of d = 'e'
                        err_msg = "The entity state did not return a valid number (logging of these errors requested by user specifying <e> for agrument d): {}, {} : {}.".format(
                            e, nx_lookup, state
                        )
                        raise ValueError(
                            err_msg
                        )  # move on WITHOUT sending value to Nextion
                    else:
                        # use provided default instead
                        new_value = d
                else:
                    # no default value - SKIP command & leave Nx unchanged WITHOUT logging an error
                    # <<
                    raise ValueError(
                        "SKIP"
                    )  #  exception intended to be skipped (and passed to a higher level)
            else:
                if data_type == "txt":
                    state = str(state)
                else:
                    try:
                        x = float(x)
                        state = float(state)
                    except:
                        # try treating both the state and comparison value as strings
                        # TODO? use letter comparitors (eq etc.) for TEXT comparisons (vs numeric) - ALREADY DONE (with above exception??)
                        state = str(state)
                if cp in ["eq", "==", "="]:
                    new_value = 1 if state == x else 0
                elif cp in ["ne", "!="]:
                    new_value = 1 if state != x else 0
                elif cp in ["lt", "<"]:
                    new_value = 1 if state < x else 0
                elif cp in ["le", "<="]:
                    new_value = 1 if state <= x else 0
                elif cp in ["gt", ">"]:
                    new_value = 1 if state > x else 0
                elif cp in ["ge", ">="]:
                    new_value = 1 if state >= x else 0
                else:
                    raise ValueError(
                        "Provided boolean comparator _{}_ is invalid.".format(cp)
                    )
            # nx_cmd_str = '{}={}'.format(nx_full, new_value)
            # send_nx_cmd(nx_cmd_str)
            set_nx_val(nx, new_value)
        else:
            raise ValueError("Wrong number of items in arguments list.")
        # #!
        # #DBG
        # if nx == 'ST.bGRG':  #< fixed to ST.bGRGD in HA_Set2 and in automation aliases
        #     err_msg = 'Nextion Handler Debug: SET function:\n<{}> <{}>\n.nx_full: <{}>; nx_lookup: <{}>\n<{}>'.format('setb', '> <'.join(args_list), nx_full, nx_lookup, nx_cmd_str)
        #     logger.warning('nextion_handler.py ' + err_msg)
    except ValueError as exptn:
        if str(exptn) == "SKIP":
            # <<
            raise ValueError("SKIP")  # not an error - raise again
        else:
            err_msg = (
                "{}\nNextion Handler failed within SET function:\n<{}> <{}>.".format(
                    exptn, "setb", "> <".join(args_list)
                )
            )
            logger.warning("nextion_handler.py " + err_msg)
            # hass.services.call('persistent_notification', 'create', {'title': 'Nextion Handler Error!', 'message': err_msg, 'notification_id': 'nx_handler_error_set' }, False)
            raise ValueError(err_msg)
    return True
    # --- setb() ---


def setlt(args_list):
    """setlt Nx_state Nx_tp Nx_brt Nx_ct Nx_rgb565 E (assign Nx variables the state,
    'type, brightness, color temperature and color of light E).
    'type' is a bit-encoded value of the supported modes of light `E`: bits are 1:brightness, 2:color_temp, 3:rgb.
    Use '_' in place of `Nx` variable names to skip assignments for those attributes.
    The light color is converted to Nextion 16-bit RGB565 format (to assign directly to color attributes of Nextion UI components).
    """
    prefix = "light."
    try:
        rgb565 = 0  # 33808  # default (on failure to set properly below): mid grey (128,128,128)
        (r, g, b) = (0, 0, 0)  # (70, 70, 70)
        if len(args_list) == 6:
            [nx_st, nx_tp, nx_brt, nx_ct, nx_rgb565, e] = args_list
            #
            # -- READ light attributes from HA
            # *state & entity_id
            nx_full, nx_lookup, data_type = nx_var_parse(nx_st)
            entity_id, ent_state, state = get_entity_id_state(
                e, nx_lookup=nx_lookup, domain_prefix=prefix
            )
            # ..
            # *supported_color_modes (-> light type capabilities)
            # modes in [None (default), 'onoff', 'brightness', 'color_temp', 'white', 'hs', 'xy', 'rgb', 'rgbw', 'rgbww']
            sm = ent_state.attributes.get("supported_color_modes", "onoff")
            # *light_type (nextion_handler encoding for light control 'pop-up page')
            is_brt = False
            is_ct = False
            is_clr = False
            if any(
                i in sm for i in ["brightness", "white", "rgbw"]
            ):  # bit 1: brightness
                is_brt = True
            if any(i in sm for i in ["color_temp", "rgbww"]):  # bit 2: color_temp
                is_brt = True
                is_ct = True
            if any(
                i in sm for i in ["rgb", "rgbw", "rgbww", "hs", "xy"]
            ):  # bit 3: color
                is_brt = True
                is_clr = True
            # * convert lt capability flags to bit encoding for Nx variable
            light_type = 0
            #! '+=' NOT SUPPORTED in restricted HA Python script env: gives error: '_inplacevar_' is not defined'
            if is_brt:  # bit 1: brightness
                light_type = (
                    light_type + 1
                )  # HA Py Env error for "+=": "'_inplacevar_' is not defined"
            if is_ct:  # bit 2: color_temp
                light_type = light_type + 2
            if is_clr:  # bit 3: color
                light_type = light_type + 4
            # ..
            # Most other light attributes are only reported when the light is ON
            # state (on/off)
            if str(state) == "on":
                on_state = 1
                # *color_mode (to help interpret other/conditional light attributes)
                # modes in [None (default), 'onoff', 'brightness', 'color_temp', 'white', 'hs', 'xy', 'rgb', 'rgbw', 'rgbww']
                cm = ent_state.attributes.get("color_mode", "x")
                # *brightness
                brightness = ent_state.attributes.get("brightness", 200)
                brightness_pct = int(float(brightness) * 100 / 255)
                # *color_temp
                ct = ent_state.attributes.get("color_temp", 370)
                ct = int(ct)
                # *rgb_color
                (r_, g_, b_) = ent_state.attributes.get(
                    "rgb_color", (99, 0, 0)
                )  #! (99,0,0) is dark red (color to indicate and error in NX UI)
                (r, g, b) = (int(r_), int(g_), int(b_))
            else:
                on_state = 0
                cm = "off"
                brightness_pct = 0  # default value
                ct = 370  # warmish white (mireds)
                (r, g, b) = (0, 0, 0)  # (70, 70, 70)
            #
            # -- WRITE light attributes to Nx
            # state
            if nx_st != "_":
                set_nx_val(nx_st, on_state)
            # light type (encoding of supported_color_modes)
            if nx_tp != "_":
                set_nx_val(nx_tp, light_type)
            # brightness percent (0..100)
            if (
                nx_brt != "_" and on_state == 1
            ):  # only update if light is ON (otherwise leave Nx variable unchanged)
                set_nx_val(nx_brt, brightness_pct)
            # color temperature
            if (
                nx_ct != "_" and on_state == 1
            ):  # only update if light is ON (otherwise leave Nx variable unchanged)
                set_nx_val(nx_ct, ct)
            # color - generate rgb based on color_mode (cm), then convert to RGB565 for writing to Nx
            if (
                nx_rgb565 != "_"
            ):  # Even if the light is OFF, return a color to indicate light status in the color bar (beneath the title bar)
                if on_state == 0:
                    (r, g, b) = (0, 0, 0)  # black for OFF
                elif cm == "onoff":
                    (r, g, b) = (
                        0,
                        176,
                        255,
                    )  # default value for light ON (if no RGB below)
                elif cm in ["brightness", "white"]:
                    # rgb settings for rgb565 (1:(50% darkened) ..  100:cyan(0,176,255)) - may be overwritten below
                    pct = (
                        brightness_pct / 100
                    )  # offset percentage towards max brightness
                    r = int(55 * (1 - pct) + 0 * pct)
                    g = int(55 * (1 - pct) + 176 * pct)
                    b = int(55 * (1 - pct) + 255 * pct)
                elif cm == "color_temp":
                    # rgb settings for rgb565 (153:blueish(168,210,255)   320:white(255,255,255)   500:orangeish(255,162,4)) - may be overwritten below
                    if ct < 320:
                        pct = (ct - 153) / (
                            320 - 153
                        )  # percentage ct is towards mid/white from max BLUE
                        r = int(120 + (255 - 120) * pct)
                        g = int(160 + (255 - 160) * pct)
                        b = 255
                    else:
                        pct = (500 - ct) / (
                            500 - 320
                        )  # percentage ct is toward mid/white from max ORANGE
                        r = 255
                        g = int(162 + (255 - 162) * pct)
                        b = int(4 + (255 - 4) * pct)
                else:
                    # The light is in a color mode - use it's rgb as set above
                    pass
                # Convert the 24bit r,g,b values set above to 16bit RGB565
                #   http://www.barth-dev.de/online/rgb565-color-picker/
                #   https://nextion.tech/2020/08/31/the-sunday-blog-understanding-and-customizing-hmi-components-part-3-color-encoding-sliders-subroutines-and-a-hue-control/
                rgb565 = (r & 0b11111000) << 8  # 5 r bits, msb bits 15-11
                rgb565 = rgb565 + ((g & 0b11111100) << 3)  # 6 g bits, mid bits 10-5
                rgb565 = rgb565 + ((b) >> 3)  # 5 b bits, lsb bits 4-0
                # rgb565 = ((int(r / 255 * 31) << 11) | (int(g / 255 * 63) << 5) | (int(b / 255 * 31)))
                set_nx_val(nx_rgb565, rgb565)
        else:
            raise ValueError("Wrong number of items in arguments list.")
    except ValueError as exptn:
        err_msg = "{}\nNextion Handler failed within SET function:\n<{}> <{}>.".format(
            exptn, "setlt", "> <".join(args_list)
        )
        logger.warning("nextion_handler.py " + err_msg)
        # hass.services.call('persistent_notification', 'create', {'title': 'Nextion Handler Error!', 'message': err_msg, 'notification_id': 'nx_handler_error_set' }, False)
        raise ValueError(err_msg)
    return True
    # --- setlt() ---


def setmp(args_list):
    """setmp Nx_state Nx_pos Nx_dur Nx_nm Nx_src Nx_vol Nx_mut Nx_ttl Nx_alb Nx_art E (assign Nx variables the
    state, media_pos, duration, name, source, volume, is_muted, media_title, album_name, artist(media) of media_player E).
    Use '_' in place of `Nx` variable names to skip assignments for those attributes.
    (ALTERNATE SETS of attributes or INDIVIDUAL attributes can be requested from this same function )).
    """
    # state: -1: err, 0: off, 1: on, 2: pause, 3: play
    STATE_DICT = {
        "off": 0,
        "on": 1,
        "idle": 2,
        "paused": 3,
        "playing": 4,
    }  # else -1  #! ? stop ... anything else - 'unavailable' etc.
    NUM_NM_CHARS = 15
    NUM_SRC_CHARS = 20
    NUM_TTL_CHARS = 128
    NUM_ALB_CHARS = 50
    NUM_ART_CHARS = 20
    prefix = "media_player."
    # initialise to skip all attributes
    [nx_st, nx_pos, nx_dur, nx_nm, nx_src, nx_vol, nx_mut, nx_ttl, nx_alb, nx_art] = [
        "_"
    ] * 10  # assign default 'skip' char ('_') to each arg (except Entity, which MUST be specified)
    try:
        # -- PARSE and assign incoming arguments
        num_args = len(args_list)
        if num_args == 11:
            # setmp requesting FULL_standard set of attributes (SET of 10 attributes + e)
            [
                nx_st,
                nx_pos,
                nx_dur,
                nx_nm,
                nx_src,
                nx_vol,
                nx_mut,
                nx_ttl,
                nx_alb,
                nx_art,
                e,
            ] = args_list
            nx = nx_st  # the Nextion variable name to be used to determine the entity alias if E == '$'
        elif num_args == 8:
            # setmp requesting REDUCED_standard set of attributes (SET of 7 attributes + e)
            [nx_st, nx_pos, nx_dur, nx_src, nx_vol, nx_mut, nx_ttl, e] = args_list
            nx = nx_st
        elif num_args == 3:
            # setmp nx attr E (INDIVIDUAL attribute - numeric)
            [nx, attr, e] = args_list
            if attr == "st":  # numeric state code
                nx_st = nx
            elif attr == "pos":
                nx_pos = nx
            elif attr == "dur":
                nx_dur = nx
            elif attr == "vo":
                nx_vol = nx
            elif attr == "mut":
                nx_mut = nx
            else:
                raise ValueError("Invalid ATTRIBUTE requested in setmp.")
        elif num_args == 4:
            # setmp nx attr chars E  (INDIVIDUAL attribute - string)
            [nx, attr, num_chars, e] = args_list
            if attr == "nm":
                nx_nm = nx
                NUM_NM_CHARS = int(num_chars)
            elif attr == "src":
                nx_src = nx
                NUM_SRC_CHARS = int(num_chars)
            elif attr == "ttl":
                nx_ttl = nx
                NUM_TTL_CHARS = int(num_chars)
            elif attr == "alb":
                nx_alb = nx
                NUM_ALB_CHARS = int(num_chars)
            elif attr == "art":
                nx_art = nx
                NUM_ART_CHARS = int(num_chars)
            # TODO: add TEXT status option (instead of numeric coding)
            # elif attr == 'stt':
            #     nx_stt = nx
            #     NUM_STT_CHARS = int(num_chars)
            else:
                raise ValueError("Invalid ATTRIBUTE requested in setmp.")
        else:
            raise ValueError("Wrong number of items in arguments list.")
        #
        # -- READ attributes from HA & SET Nextion variables
        # *ent_state & state
        nx_full, nx_lookup, data_type = nx_var_parse(nx)
        entity_id, ent_state, state = get_entity_id_state(
            e, nx_lookup=nx_lookup, domain_prefix=prefix
        )
        state_code = STATE_DICT.get(state, -1)
        # ..
        # State (string -> code)  #TODO? add option for TEXT state too?
        if nx_st != "_":
            nx_full, nx_lookup, data_type = nx_var_parse(nx_st)
            nx_cmd_str = "{}={}".format(nx_full, state_code)
            send_nx_cmd(nx_cmd_str)
        # * NUMERIC attributes
        # media_position (int secs)
        if nx_pos != "_":
            try:
                val = ent_state.attributes["media_position"]
                val = int(val)
            except:
                val = 0  # pass
            set_nx_val(nx_pos, val)
        # media_duration (int secs)
        if nx_dur != "_":
            val = ent_state.attributes.get("media_duration", 0)
            val = int(val)
            set_nx_val(nx_dur, val)
        # source (int 0..100, from float 0..1)
        if nx_vol != "_":
            val = ent_state.attributes.get("volume_level", 0)
            val = int(val * 100)
            set_nx_val(nx_vol, val)
        # is_volume_muted (0, 1 ; from False, True)
        if nx_mut != "_":
            val = ent_state.attributes.get("is_volume_muted", False)
            val = 1 if val else 0
            set_nx_val(nx_mut, val)
        # * STRING attributes - NB: Nextion Instructions need to use double quotes for text
        # friendly_name (string NUM_NM_CHARS)
        if nx_nm != "_":
            val = ent_state.attributes.get("friendly_name", "")
            val = val[:NUM_NM_CHARS]
            set_nx_val(nx_nm, val, IS_TEXT=True)
        # source (string NUM_SRC_CHARS) (incl source_list number)
        if nx_src != "_":
            val = ent_state.attributes.get("source", "")
            if val:
                try:
                    # try to prefix the option number (1..) of item in list
                    options = ent_state.attributes.get("source_list", "")
                    opt_num = options.index(val) + 1
                    val = "{}: {}".format(opt_num, val)
                except:
                    pass  # just use the base value if adding opt_num doesn't work
            val = val[:NUM_SRC_CHARS]
            set_nx_val(nx_src, val, IS_TEXT=True)
        # media_title (string NUM_TTL_CHARS)
        if nx_ttl != "_":
            val = ent_state.attributes.get("media_title", "-")
            val = val.replace('"', "'")[:NUM_TTL_CHARS]
            set_nx_val(nx_ttl, val, IS_TEXT=True)
        # media_album_name (string NUM_ALB_CHARS)
        if nx_alb != "_":
            val = ent_state.attributes.get("media_album_name", "")
            val = val.replace('"', "'")[:NUM_ALB_CHARS]
            set_nx_val(nx_alb, val, IS_TEXT=True)
        # media_artist (string NUM_ART_CHARS) - less frequently, 'media_album_artist' is also provided
        if nx_art != "_":
            val = ent_state.attributes.get("media_artist", None)
            if val is None:
                val = ent_state.attributes.get("media_album_artist", "")
            val = val[:50]
            set_nx_val(nx_art, val, IS_TEXT=True)
    except ValueError as exptn:
        err_msg = "{}\nNextion Handler failed within SET function:\n<{}> <{}>.".format(
            exptn, "setmp", "> <".join(args_list)
        )
        logger.warning("nextion_handler.py " + err_msg)
        #!dbg
        # hass.services.call('persistent_notification', 'create', {'title': 'Nextion Handler Error!', 'message': err_msg, 'notification_id': 'nx_handler_error_set' }, False)
        raise ValueError(err_msg)
    return True
    # --- setmp() ---


def setcl(args_list):
    """setcl attr Nx (args) E : assign the Nextion variable Nx the value of the
    'attr' attribute of climate entity 'E' (using args).
    ALTERNATE usage: setcl (Nx_vars...) E
        Assign list of Nx variables to predefined list of attributes.
        (Mainly used to return all 'popup page' data in one instruction.)
    Valid 'attr' options:
        [nx_supf, nx_tset, nx_tlo, nx_thi, nx_tmin, nx_tmax, nx_aux,
        nx_hum, nx_hmin, nx_hmax,
        nx_nm, nx_st, nx_pre_md, nx_fan_md, nx_swg_md]"""
    NUM_NM_CHARS = 15
    NUM_CHARS_MAX = 20
    nx_t_PAIR = (
        None  # (nx1, nx2) pair (special case used by custom lists for popup page)
    )
    prefix = "climate."
    # nx = None  #NOTE: nx will be assigned to the Nx variable used for translating the '$' alias
    # Initialise all possible attributes with '_' (to SKIP assignemnt)
    [
        nx_st,
        nx_supf,
        nx_tset,
        nx_tlo,
        nx_thi,
        nx_tmin,
        nx_tmax,
        nx_aux,
        nx_hum,
        nx_hmin,
        nx_hmax,
        nx_nm,
        nx_stt,
        nx_pre_md,
        nx_fan_md,
        nx_swg_md,
    ] = ["_"] * 16

    try:
        # -- PARSE and assign incoming arguments
        num_args = len(args_list)
        if num_args == 14:
            # * set MULTIPLE attributes: FULL standard set (support 'popup page')
            [
                nx_st,
                nx_supf,
                nx_aux,
                p1,
                p2,
                nx_tmin,
                nx_tmax,
                nx_hum,
                nx_hmin,
                nx_hmax,
                nx_pre_md,
                nx_fan_md,
                nx_swg_md,
                e,
            ] = args_list
            nx_t_PAIR = (
                p1,
                p2,
            )  # (nx1, nx2) pair (special case for 'adaptable' tempearture target settings)
            nx = nx_st  # the Nextion variable name to be used to determine the entity alias if E == '$'
        elif num_args in [3, 4]:
            # * set INDIVIDUAL attribute
            [nx, attr, e] = args_list
            if num_args == 4:
                # TODO: allow optional extra parameter to set default value to return on errors
                #   or set max num chars?
                arg4 = args_list[3]
            else:
                arg4 = None
            # Use 'attr' value to determine which attribute will be assigned
            if attr == "st":  # Coded state (HVAC mode)
                nx_st = nx
            elif attr == "nm":
                nx_nm = nx
            elif attr == "supf":
                nx_supf = nx
            elif attr == "tlo":
                nx_tlo = nx
            elif attr == "thi":
                nx_thi = nx
            elif attr == "tmin":
                nx_tmin = nx
            elif attr == "tmax":
                nx_tmax = nx
            elif attr == "aux":
                nx_aux = nx
            elif attr == "hum":
                nx_hum = nx
            elif attr == "hmin":
                nx_hmin = nx
            elif attr == "hmax":
                nx_hmax = nx
            elif attr == "stt":  # STRING state (HVAC mode)
                nx_stt = nx
            elif attr == "pre_md":
                nx_pre_md = nx
            elif attr == "fan_md":
                nx_fan_md = nx
            elif attr == "swg_md":
                nx_swg_md = nx
            else:
                raise ValueError("Invalid ATTRIBUTE requested in setcl.")
        else:
            raise ValueError("Wrong number of items in arguments list.")
        #
        # -- READ attributes from HA & SET non-skip("_") Nextion variables
        # *ent_state & state: will raise exception if it can't translate e to valid entity_id
        nx_full, nx_lookup, data_type = nx_var_parse(nx)
        entity_id, ent_state, state = get_entity_id_state(
            e, nx_lookup=nx_lookup, domain_prefix=prefix
        )
        # ..
        # * NUMERIC attributes
        # state (= HVAC mode, coded) see nx_stt below in TEXT variable section.
        # 0 HVACMode.OFF  The device is turned off.
        # 1 HVACMode.HEAT  The device is set to heat to a target temperature.
        # 2 HVACMode.COOL  The device is set to cool to a target temperature.
        # 3 HVACMode.HEAT_COOL  The device is set to heat/cool to a target temperature range.
        # 4 HVACMode.AUTO  The device is set to a schedule, learned behavior, AI.
        # 5 HVACMode.DRY  The device is set to dry/humidity mode.
        # 6 HVACMode.FAN_ONLY  The device only has the fan on. No heating or cooling taking place.
        if nx_st != "_":
            STATE_DICT = {
                "off": 0,
                "heat": 1,
                "cool": 2,
                "heat_cool": 3,
                "auto": 4,
                "dry": 5,
                "fan_only": 6,
            }  # else -1
            val = STATE_DICT.get(state, -1)
            set_nx_val(nx_st, val)
        # supported features - bit encoded: https://developers.home-assistant.io/docs/core/entity/climate#supported-features
        if nx_supf != "_":
            val = ent_state.attributes.get("supported_features", 0)
            val = int(val)
            set_nx_val(nx_supf, val)
        # temperature target (SINGLE set point) - in C/F as configured
        if nx_tset != "_":
            val = ent_state.attributes.get("temperature", -99)  # float
            val = int(val)
            set_nx_val(nx_tset, val)
        # temperature target RANGE - LOW target - in C/F as configured
        if nx_tlo != "_":
            val = ent_state.attributes.get("target_temp_low", -99)
            val = int(val)
            set_nx_val(nx_tlo, val)
        # temperature target RANGE - HIGH target - in C/F as configured
        if nx_thi != "_":
            val = ent_state.attributes.get("target_temp_high", -99)
            val = int(val)
            set_nx_val(nx_thi, val)
        # temperature MIN device can set - in C/F as configured
        if nx_tmin != "_":
            val = ent_state.attributes.get("min_temp", 7)  # 7,35 = HA defaults
            val = int(val)
            set_nx_val(nx_tmin, val)
        # temperature MIN device can set - in C/F as configured
        if nx_tmax != "_":
            val = ent_state.attributes.get("max_temp", 35)
            val = int(val)
            set_nx_val(nx_tmax, val)
        # temperature set point PAIR - in C/F as configured
        # for SINGLE set point, return tartet in 1st variable, -99 in second
        # for RANGE set point, return low, high target pair
        if nx_t_PAIR != None:
            nx1, nx2 = nx_t_PAIR
            val1 = ent_state.attributes.get("temperature", None)
            if val1:
                val2 = -99  # indicates a SINGLE set point
            else:
                val1 = ent_state.attributes.get("target_temp_low", -99)
                val2 = ent_state.attributes.get("target_temp_high", -99)
            # val1
            val = int(val1)
            set_nx_val(nx1, val)
            # val2
            val = int(val2)
            set_nx_val(nx2, val)
        # aux heat (convert to binary 0,1)
        if nx_aux != "_":
            # val = ent_state.attributes.get("is_aux_heat", False)  #! << attribute in HA Dev Docs
            #! ??? << from https://github.com/mcaminiti/homeassistant/blob/master/sensors.yaml
            val = ent_state.attributes.get("aux_heat", False)
            val = 1 if val is True else 0
            set_nx_val(nx_aux, val)
        # humidity target set point (0..100)  #! are humidity attribute names correct?
        if nx_hum != "_":
            val = ent_state.attributes.get("target_humidity", -99)
            val = int(val)
            set_nx_val(nx_hum, val)
        # humidity MIN device can set
        if nx_hmin != "_":
            val = ent_state.attributes.get("min_humidity", 30)  # 30,99 = HA defaults
            val = int(val)
            set_nx_val(nx_hmin, val)
        # temperature MIN device can set - in C/F as configured
        if nx_hmax != "_":
            val = ent_state.attributes.get("max_humidity", 99)
            val = int(val)
            set_nx_val(nx_hmax, val)
        # * STRING attributes - NB: Nextion Instructions need to use double quotes for text
        # friendly_name (string NUM_NM_CHARS)
        if nx_nm != "_":
            val = ent_state.attributes.get("friendly_name", "")
            val = val[:NUM_NM_CHARS]
            set_nx_val(nx_nm, val, IS_TEXT=True)
        # state STRING (= HVAC mode)  #! is HMI currently using a NUMERIC CODE or TEXT???
        if nx_stt != "_":
            val = state
            if val:
                try:
                    # try to prefix the option number (1..) of item in list
                    options = ent_state.attributes.get("hvac_modes", "")
                    opt_num = options.index(val) + 1
                    val = "{}: {}".format(opt_num, val)
                except:
                    pass  # just use the base value if adding opt_num doesn't work
            val = val[:NUM_CHARS_MAX]
            set_nx_val(nx_stt, val, IS_TEXT=True)
        if nx_pre_md != "_":
            val = ent_state.attributes.get("preset_mode", "")
            if val:
                try:
                    # try to prefix the option number (1..) of item in list
                    options = ent_state.attributes.get("preset_modes", "")
                    opt_num = options.index(val) + 1
                    val = "{}: {}".format(opt_num, val)
                except:
                    pass  # just use the base value if adding opt_num doesn't work
            val = val[:NUM_CHARS_MAX]
            set_nx_val(nx_pre_md, val, IS_TEXT=True)
        if nx_fan_md != "_":
            val = ent_state.attributes.get("fan_mode", "")
            if val:
                try:
                    # try to prefix the option number (1..) of item in list
                    options = ent_state.attributes.get("fan_modes", "")
                    opt_num = options.index(val) + 1
                    val = "{}: {}".format(opt_num, val)
                except:
                    pass  # just use the base value if adding opt_num doesn't work
            val = val[:NUM_CHARS_MAX]
            set_nx_val(nx_fan_md, val, IS_TEXT=True)
        if nx_swg_md != "_":
            val = ent_state.attributes.get("swing_mode", "")
            if val:
                try:
                    # try to prefix the option number (1..) of item in list
                    options = ent_state.attributes.get("swing_modes", "")
                    opt_num = options.index(val) + 1
                    val = "{}: {}".format(opt_num, val)
                except:
                    pass  # just use the base value if adding opt_num doesn't work
            val = val[:NUM_CHARS_MAX]
            set_nx_val(nx_swg_md, val, IS_TEXT=True)
    except ValueError as exptn:
        err_msg = "{}\nNextion Handler failed within SET function:\n<{}> <{}>.".format(
            exptn, "setcl", "> <".join(args_list)
        )
        logger.warning("nextion_handler.py " + err_msg)
        #!dbg
        # hass.services.call('persistent_notification', 'create', {'title': 'Nextion Handler Error!', 'message': err_msg, 'notification_id': 'nx_handler_error_set' }, False)
        raise ValueError(err_msg)
    return True
    # --- setcl() ---


# setntf NF.nNTFC t1.txt t2.txt -1 nIdx
# setntf NF.nNTFC NF.tTTL NF.tMSG -1
def setntf(args_list):
    """setntf Nx_count (Nx_title) (Nx_msg) (n) (Nx_idx) (chars_ttl) (chars_msg)
    (assign 3 Nx variables the Count, Title and Message of the nth
    (index 0..len-1) Persistent Notification.)
    Use '_' in place of `Nx` variable names, or omit them, to skip assignments
    for those attributes.
    Nx_idx return the index of the actual notification returned, which may be
    different from the index requrested (n), e.g. where n is '-1' or outofrange.
    Default numeric arguments (if unassigned) are 1, for message num,
    and 255 for string len.)
    """
    # NOTE: v2022-07-21: changed n from item number (1..) to INDEX value (0..): Also changed in HMI
    try:
        num_args = len(args_list)
        if num_args == 4:
            #! deprectated - old version
            [nx_c, nx_t, nx_m, n_] = args_list
            [nx_idx, len_t_, len_m_] = ["_"] * 3
        elif 1 <= num_args <= 7:
            #! new version (2022-07-24) can send back ACTUAL list index of selected notification.
            # extend list with '_'s to indicate potential unassigned/default values
            args_list.extend(["_"] * 7)
            [nx_c, nx_t, nx_m, n_, nx_idx, len_t_, len_m_] = args_list[:7]
        else:
            raise ValueError("Wrong number of items in arguments list.")
        try:
            # Apply defaults to missing values or convert str to int
            len_t = 255 if len_t_ == "_" else int(len_t_)
            len_m = 255 if len_m_ == "_" else int(len_m_)
            n = -1 if n_ == "_" else int(n_)  # selected list INDEX value
        except:
            raise ValueError("Values are not integers.")
        # Get notification list, count & item n
        try:
            ntf_list = hass.states.entity_ids("persistent_notification")
            ntf_cnt = len(ntf_list)
            if ntf_cnt > 0:
                n = n % ntf_cnt  # keep index in list range (-1%5 = 4)
                entity_id = ntf_list[n]
                ent_state = hass.states.get(entity_id)
                title = ent_state.attributes["title"]
                # Fix text that Nextion cannot parse/render properly
                title = title.replace('"', "'")
                message = ent_state.attributes["message"].replace("\n\n", "\n")
                # Convert from HA linebreak (\n) to Nextion (\r)
                message = r"\r".join(message.split("\n"))
                message = message.replace('"', "'")
                message = (
                    message
                    + r"\r"
                    + timedelta_to_str(dt_util.now(), ent_state.last_changed)
                )
            else:
                n = 0
                title = "NONE"
                message = "No Notifications"
        except:
            # raise ValueError('Error reading list of Persistent Notifications.')
            title = "Error"
            message = "Error reading list of Persistent Notifications."
        # Notification title (.txt)
        if nx_t != "_":
            # Convert from HA linebreak (\n) to Nextion (\r)
            title = r"\r".join(title.split("\n"))
            val = title[:len_t]
            set_nx_val(nx_t, val, IS_TEXT=True)
        # Notification message (.txt)
        if nx_m != "_":
            val = message[:len_m]
            set_nx_val(nx_m, val, IS_TEXT=True)
        # Notification count (.val)
        if nx_c != "_":
            set_nx_val(nx_c, ntf_cnt)
        # List Index of returned notification (.val)
        if nx_idx != "_":
            set_nx_val(nx_idx, n)
    except ValueError as exptn:
        err_msg = "{}\nNextion Handler failed within SET function:\n<{}> <{}>.".format(
            exptn, "setntf", "> <".join(args_list)
        )
        logger.warning("nextion_handler.py " + err_msg)
        # hass.services.call('persistent_notification', 'create', {'title': 'Nextion Handler Error!', 'message': err_msg, 'notification_id': 'nx_handler_error_set' }, False)
        raise ValueError(err_msg)
    return True
    # --- setntf() ---


# setdt CFG.tTime $ %a %d/%m %Hh%M
def setdt(args_list):
    """setdt Nx (fmt)  (assign Nx the string of the current data-time, formatted as fmt).
    (Default fmt is r"%a %d/%m %Hh%M", e.g. "Sun 28/02 17h30".)
    """
    #! datetime.datetime.now() with strftime() not working in restricted Python env.
    FMT_DEFAULT = r"%a %d/%m %Hh%M"  # e.g. 'Sun 28/02 17h30'
    try:
        if len(args_list) > 0:
            nx = args_list[0]
            if len(args_list) >= 2:
                fmt = " ".join(args_list[1:])
            else:
                fmt = FMT_DEFAULT
            dt_now = datetime.datetime.now()  #! this works
            # try:
            #     val = dt_now.strftime(fmt)  #! but strftime() fails exception check
            # except:
            #     try:
            #         #val = dt_now.strftime(FMT_DEFAULT)
            #         #val = dt_now.strftime("%d %b %y, %I:%M:%S %p")
            #         val = datetime.datetime.strftime(datetime.datetime.now(), "%d %b %y, %I:%M:%S %p")
            #     except:
            #         try:
            #             #! failsafe date-time string approach that seems reliable
            #             val = '*{:02}/{:02} {:02}h{:02}'.format(dt_now.day, dt_now.month, dt_now.hour, dt_now.minute)
            #         except:
            #             raise ValueError('Formatting date-time string failed.')
            try:
                val = "{:02}/{:02} {:02}h{:02}".format(
                    dt_now.day, dt_now.month, dt_now.hour, dt_now.minute
                )
            except:
                raise ValueError("Formatting date-time string failed.")
            set_nx_val(nx, val, IS_TEXT=True)
        else:
            raise ValueError("Wrong number of items in arguments list.")
    except ValueError as exptn:
        err_msg = "{}\nNextion Handler failed within SET function:\n<{}> <{}>.".format(
            exptn, "setdt", "> <".join(args_list)
        )
        logger.warning("nextion_handler.py " + err_msg)
        # hass.services.call('persistent_notification', 'create', {'title': 'Nextion Handler Error!', 'message': err_msg, 'notification_id': 'nx_handler_error_set' }, False)
        raise ValueError(err_msg)
    return True


def setsys(args_list):
    """setsys nh_ver num_widgets num_aliases
    (Assign system information to the provided list of variables
    (but skip if they are '_'))"""

    try:
        args_list.extend(["_"] * (3))
        [nh_ver, wd_tot, al_tot] = args_list[:3]
        # version
        if nh_ver != "_":
            val = VERSION
            set_nx_val(nh_ver, val)
        # Num Widgets
        if wd_tot != "_":
            val = len(WIDGETS_LIST)
            set_nx_val(wd_tot, val)
        # Num Aliases
        if al_tot != "_":
            val = len(ENTITY_ALIASES)
            set_nx_val(al_tot, val)
    except ValueError as exptn:
        err_msg = "{}\nNextion Handler failed within SET function:\n<{}> <{}>.".format(
            exptn, "setsys", "> <".join(args_list)
        )
        logger.warning("nextion_handler.py " + err_msg)
        # hass.services.call('persistent_notification', 'create', {'title': 'Nextion Handler Error!', 'message': err_msg, 'notification_id': 'nx_handler_error_set' }, False)
        raise ValueError(err_msg)
    return True


#! remove all '+=' etc. in_place_vars NOT supported in restricted ENV
# * Widget setwd helper function
def get_widget_info(entity_id):
    """Get info required by widgets for entity e, with domain_code wd_dmn.
    Returns:
        wd_name: name/title for widget card
        wd_info: a descriptive string for the state/attributes
        wd_alt: addition descriptive text
        wd_icon: icon index number (for precompiled Widget icon pairs)
        wd_bst: boolean state of entity (as 0/1)
        wd_dmn: (modified to -1 if entity_id is not valid)
    """

    # Uses GLOBAL constants for lookup dicts and bit masks

    ERROR = False
    # no_errors = True
    wd_name = ""
    wd_info = ""
    wd_alt = ""
    wd_icon = 0
    wd_bst = 0
    wd_dmn = 0

    # Domain part of entity_id -> domain codes (full & num) & icon
    ent_domain = entity_id.split(".")[0]
    # defaults to generic sensor
    (wd_dmn, wd_icon) = DOMAINS_DICT.get(ent_domain, (2, DEFAULT_ICON))
    domain_num = wd_dmn & DOMAIN_NUM_MASK

    # TODO: add meaningful info for each domain (e.g. Notifications) - this is a simple placeholder for now
    # 1	alarm_control_panel
    # 2	automation
    # 3	binary_sensor
    # 4	button
    # 5	calendar
    # 6	camera
    # 7	climate
    # 8	cover
    # 9	device_tracker
    # 10	fan
    # 11	geo_location
    # 12	group
    # 13	humidifier
    # 14	input_boolean
    # 15	input_datetime
    # 16	input_number
    # 17	input_select
    # 18	light
    # 19	lock
    # 20	media_player
    # 21	persistent_notification
    # 22	person
    # 23	remote
    # 24	scene
    # 25	script
    # 26	select
    # 27	sensor
    # 28	siren
    # 29	sun
    # 30	switch
    # 31	timer
    # 32	update
    # 33	vacuum
    # 34	water_heater
    # 35	weather
    # 36	zone

    # * persistent_notifications - SPECIAL CASE - DOES NOT SEND A VALID ENTITY
    # (need to process the list for the entire domain instead).
    if domain_num == 21:
        wd_name = "Notificatn"
        try:
            ntf_list = hass.states.entity_ids("persistent_notification")
            ntf_cnt = len(ntf_list)
            if ntf_cnt > 0:
                entity_id = ntf_list[ntf_cnt - 1]  # newest
                wd_info = hass.states.get(entity_id).attributes["title"]
                # message = hass.states.get(entity_id).attributes['message']
                wd_alt = str(ntf_cnt)
                wd_bst = 1
            else:
                wd_info = "No Notifications"
                wd_alt = "-"
                wd_bst = 0
        except:
            ERROR = True
            wd_info = "Err reading Notifications"
            wd_alt = "?"
        return wd_name, wd_info, wd_alt, wd_icon, wd_bst, wd_dmn, ERROR  #!
    else:
        # Get the state of entity_id and make sure it exists
        try:
            ent_state = hass.states.get(entity_id)
            state = ent_state.state
            # * Defaults (if not overwritten by domain matches below)
            wd_name = ent_state.attributes["friendly_name"]
            wd_info = state.title()
            wd_bst = (
                0 if (state in FALSE_STATES) or (state in INVALID_STATES) else 1
            )  # default binary (0/1) state conversion
        except:
            ERROR = True
            wd_name = "Bad entity"
            wd_dmn = -1
            wd_info = "<{}>".format(entity_id)
            wd_alt = "Fix Ent!"
            wd_icon = BLANK_ERR_ICON
            wd_bst = 1
            # no_errors = False #!
            return wd_name, wd_info, wd_alt, wd_icon, wd_bst, wd_dmn, ERROR  #!
        # * ---- Process Matches for Each Domain ---

        # * lights
        if domain_num == 18:
            try:
                if wd_bst == 0:
                    wd_alt = "Off"
                    wd_info = timedelta_to_str(dt_util.now(), ent_state.last_changed)
                else:
                    cm = ent_state.attributes["color_mode"]
                    if cm == "onoff":
                        wd_info = "On (on/off light)"
                    else:
                        try:
                            brightness = ent_state.attributes["brightness"]
                            brightness_str = "{}%".format(int(brightness * 100 / 255))
                        except:
                            brightness_str = "?%"
                        if cm in ["brightness", "white"]:
                            wd_info = "({} mode)".format(cm.title())
                            wd_alt = "{}".format(brightness_str)
                        elif cm == "color_temp":
                            ct_ = ent_state.attributes["color_temp"]
                            ct = int(float(ct_))
                            if ct < 240:
                                wd_info = "Very cool white"
                            elif ct < 290:
                                wd_info = "Cool white"
                            elif ct < 350:
                                wd_info = "Neutral white"
                            elif ct < 420:
                                wd_info = "Warm white"
                            else:
                                wd_info = "Very warm white"
                            # wd_info = '{}, {}'.format(wd_info, ct)
                            wd_alt = "{}".format(brightness_str)
                        else:
                            try:  # should be a color mode
                                hue_, sat_ = ent_state.attributes["hs_color"]
                                hue = int(float(hue_))
                                sat = int(float(sat_))
                                if hue < 10:
                                    wd_info = "Red"
                                elif hue < 45:
                                    wd_info = "Orange"
                                elif hue < 80:
                                    wd_info = "Yellow"
                                elif hue < 145:
                                    wd_info = "Green"
                                elif hue < 200:
                                    wd_info = "Aqua"
                                elif hue < 250:
                                    wd_info = "Blue"
                                elif hue < 300:
                                    wd_info = "Purple"
                                elif hue < 340:
                                    wd_info = "Pink"
                                else:
                                    wd_info = "Red"
                                if sat > 70:
                                    wd_info = "Bright " + wd_info
                                elif sat < 30:
                                    wd_info = "Slightly " + wd_info
                                # wd_info = '{}, {}'.format(wd_info, hue)
                                wd_alt = "{}".format(brightness_str)
                            except:
                                wd_info = "*On"
                                wd_alt = hue_
            except:
                wd_info = "Err light attributes"
        # * media_players
        elif domain_num == 20:
            wd_alt = state.title()
            wd_bst = 1 if state in ["on", "idle", "paused", "playing"] else 0
            ttl = ent_state.attributes.get("media_title", "")
            src = ent_state.attributes.get("source", None)
            vol = ent_state.attributes.get("volume_level", None)
            muted = ent_state.attributes.get("is_volume_muted", "")
            vol_str = int(vol * 100) if vol else "."
            if state == "off":
                wd_info = timedelta_to_str(dt_util.now(), ent_state.last_changed)
            if ttl:
                wd_info = ttl
                if muted:
                    vol_str = "mt"
                wd_alt = "{}:{}".format(wd_alt[:5], vol_str)
            else:
                if src:
                    if muted:
                        wd_info = "{}, Muted:{}".format(src, vol_str)
                    else:
                        wd_info = "{}, Vol:{}".format(src, vol_str)
                elif vol:
                    if muted:
                        wd_info = "Muted {}".format(vol_str)
                    else:
                        wd_info = "Volume {}".format(vol_str)
        # * alarm control panels
        #! needs testing
        elif domain_num == 1:
            wd_bst = 0 if state == "disarmed" else 1
            wd_alt = state.title()
            wd_info = timedelta_to_str(
                dt_util.now(), ent_state.attributes.get("last_triggered", dt_util.now())
            )
        # * automations
        elif domain_num == 2:
            if wd_bst:
                wd_alt = "Active"
            else:
                wd_alt = "DISABLED"
            curr = ent_state.attributes.get("current", 0)
            if curr > 0:
                wd_info = "{} Running".format(curr)
            else:
                wd_info = timedelta_to_str(
                    dt_util.now(),
                    ent_state.attributes.get("last_triggered", dt_util.now()),
                )
                # wd_info = '({}) {}'.format(curr, wd_info)
        # * binary sensors
        elif domain_num == 3:
            dev_class = ent_state.attributes.get("device_class", "")
            dev_info = BIN_SENSOR_DICT.get(dev_class, ("off", "on", wd_icon))
            wd_alt = dev_info[wd_bst].title()
            wd_icon = dev_info[2]
            # wd_info = '  {} ({})'.format(state.title(), dev_class.title())
            wd_info = timedelta_to_str(dt_util.now(), ent_state.last_changed)
        # * button
        elif domain_num == 4:
            wd_alt = "(Button)"
            wd_info = timedelta_to_str(dt_util.now(), ent_state.last_changed)
            # highlight icon for 30 sec after press
            td = dt_util.now() - ent_state.last_changed
            wd_bst = 1 if (td.total_seconds() < 30) else 0
        # * climate (incl. themostats)
        #! needs testing
        elif domain_num == 7:
            wd_bst = 0 if state in ["off", "unknown"] else 1
            if wd_bst == 1:
                CLIMATE_ICON_DICT = {
                    "heat": 159,
                    "cool": 158,
                    "heat_cool": 157,
                    "auto": 153,
                    "dry": 156,
                    "fan_only": 101,
                }
                wd_icon = CLIMATE_ICON_DICT.get(state, wd_icon)
            sup_ft = ent_state.attributes.get("supported_features", 0)
            # Supported Features:
            #   1 TARGET_TEMPERATURE	The device supports a target temperature.
            #   2 TARGET_TEMPERATURE_RANGE	The device supports a ranged target temperature. Used for HVAC modes heat_cool and auto
            #   4 TARGET_HUMIDITY	The device supports a target humidity.
            #   8 FAN_MODE	The device supports fan modes.
            #  16 PRESET_MODE	The device supports presets.
            #  32 SWING_MODE	The device supports swing modes.
            #  64 AUX_HEAT	The device supports auxiliary heaters.
            wd_alt = ""
            if sup_ft & 2:  # temperature range
                # ? *** check attr names for temperature range match HA DevDocs
                set_tlo = ent_state.attributes.get("target_temp_low", None)
                set_thi = ent_state.attributes.get("target_temp_high", None)
                if set_tlo and set_thi:
                    wd_alt = "{:.0f}-{:.0f}°".format(set_tlo, set_thi)
            elif sup_ft & 1:  # single set point
                set_t = ent_state.attributes.get("temperature", None)
                if set_t:
                    wd_alt = "{:.0f}°".format(set_t)
            wd_info = state.replace("_", " ").title()
            if sup_ft & 64:  # aux heat
                aux = ent_state.attributes.get("aux_heat", False)
                if aux is True:
                    wd_info = wd_info + "*"
            # Additional mode info
            if sup_ft & 16:  # preset mode
                mode = ent_state.attributes.get("preset_mode", "")
            elif sup_ft & 8:  # fan mode
                mode = ent_state.attributes.get("fan_mode", "")
            if mode:
                wd_info = wd_info + " " + mode.replace("_", " ").title()
            if wd_info == "":
                wd_info = timedelta_to_str(dt_util.now(), ent_state.last_changed)
        # * cover
        #! Tested by zigomatic - docs seem incorrect: https://developers.home-assistant.io/docs/core/entity/cover/
        elif domain_num == 8:
            wd_bst = (
                1 if state in ["open", "opening"] else 0
            )  # A cover entity can be in states (open, closing and (opening, closing) or 'stopped').
            # wd_alt = state.title()
            #! Are docs incorrect or are do different devices return different attributes?
            pos = ent_state.attributes.get("current_position", None)  #! zigomatic test
            if pos is None:
                pos = ent_state.attributes.get(
                    "current_cover_position", None
                )  #! fallback (HA Dev Docs)
            pos_t = ent_state.attributes.get("cover_tilt_position", None)
            if pos_t is None:
                pos_t = ent_state.attributes.get("current_cover_tilt_position", None)
            if pos is None and pos_t is None:
                wd_info = state.title()
            elif pos_t is None:
                wd_info = "Position: {}%".format(pos)
                wd_alt = state.title()
            elif pos is None:
                wd_info = "Tilt: {}%".format(pos_t)
                wd_alt = state.title()
            else:
                wd_info = "Pos: {}%, Tilt: {}%".format(pos, pos_t)
                wd_alt = state.title()
            dev_class = ent_state.attributes.get("device_class", None)
            wd_icon = COVER_ICON_DICT.get(dev_class, wd_icon)
        # * device_trackers AND person
        elif domain_num in [9, 22]:
            # TODO: distance from Home would be nice (but need to access Home lat, long)
            # lat = ent_state.attributes.get('latitude', '')
            # lon = ent_state.attributes.get('longitude', '')
            # wd_info = '({:.3f}, {:.3f})'.format(lat, lon)
            # td = dt_util.utcnow() - ent_state.last_changed #! returns UTC time, not local time
            # wd_info = timedelta_to_str(td)
            wd_info = timedelta_to_str(
                dt_util.utcnow(), ent_state.last_changed
            )  #! returns UTC time
            wd_alt = state.title()
            wd_bst = 1 if state in ["home", "Home", "HOME"] else 0
        # * fans
        #! needs testing
        elif domain_num == 10:
            if wd_bst == 0:
                wd_alt = state.title()
                wd_info = timedelta_to_str(dt_util.now(), ent_state.last_changed)
            else:
                wd_alt = ent_state.attributes.get("speed", "On")
                pct = ent_state.attributes.get("percentage", None)
                dirn = ent_state.attributes.get("direction", "Speed")
                if pct:
                    wd_info = "{}: {}%".format(dirn, pct)
                else:
                    wd_info = timedelta_to_str(dt_util.now(), ent_state.last_changed)
        # * groups
        elif domain_num == 12:
            #! CLUNKY! Get count of entity_id list (len() won't work!)
            lent = ent_state.attributes.get("entity_id", "")
            n = 0
            for i in lent:
                n = n + 1
            wd_alt = "{} (x{})".format(state.title(), n + 1)
            wd_info = timedelta_to_str(dt_util.now(), ent_state.last_changed)
        # * humidifiers (2 device_classes: humdifier, dehumidifier)
        elif domain_num == 13:
            set_hum = ent_state.attributes.get("target_humidity", "0")
            curr_hum = ent_state.attributes.get("humidity", None)
            speed = ent_state.attributes.get("speed", None)
            if wd_bst == 0 or speed is None:
                wd_alt = state.title()
            else:
                wd_alt = speed
            if curr_hum is None:
                wd_info = "Set {}%H".format(set_hum)
            else:
                wd_info = "Set {}%H ({}%)".format(set_hum, curr_hum)
        # * input_booleans
        elif domain_num == 14:
            if state in ["on", "off"]:
                wd_alt = "{}(Inp)".format(state.title())
            else:
                wd_alt = state.title()
                # wd_bst = 0  #INVALID_STATES
            wd_info = timedelta_to_str(dt_util.now(), ent_state.last_changed)
        # * input_datetimes
        elif domain_num == 15:
            ts = ent_state.attributes.get("timestamp", "")
            #! need timestamp formatting (also for last changed)
            # wd_info = '{}'.format(ts.strftime('%Y-%m-%dT')) #%H:%M:%S
            # wd_info = '{}'.format(state)
            wd_info = "{}".format(state[:16])
            wd_alt = "(Inp DT)"
            wd_bst = 0  # users set threshold rules with YAML templates
        # * input_numbers
        elif domain_num == 16:
            unit = ent_state.attributes.get("unit_of_measurement", "")
            mn = ent_state.attributes.get("min", "")
            mx = ent_state.attributes.get("max", "")
            # wd_info = 'Range: {} - {}'.format(mn, mx)
            wd_info = "{} to {}".format(mn, mx)
            wd_alt = "{} {}".format(state, unit)
            wd_bst = 0  # users set threshold rules with YAML templates
        # * input_select AND select
        elif domain_num in [17, 26]:
            options = ent_state.attributes.get("options", [])
            try:
                pos = options.index(state) + 1
            except:
                pos = "?"
            wd_alt = "{} of {}".format(pos, len(options))
            wd_info = state  # .title()
            wd_bst = 0  # users set threshold rules with YAML templates
        # * locks
        #! needs testing
        elif domain_num == 19:
            wd_bst = 0 if state == "locked" else 1
            wd_alt = state.title()
            wd_info = ent_state.attributes.get("lock_status", None)
            if wd_info is None:
                wd_info = timedelta_to_str(dt_util.now(), ent_state.last_changed)
        # * person (22) - included with device_trackers (9)

        # * scenes
        elif domain_num == 24:
            # lent = ent_state.attributes.get('entity_id', '')
            # wd_alt = list(lent).length_hint()  #! cannot get count of entity_id list to work
            wd_info = timedelta_to_str(dt_util.now(), ent_state.last_changed)
            wd_alt = "(Scene)"
            td = dt_util.now() - ent_state.last_changed
            wd_bst = (
                1 if (td.total_seconds() < 3600) else 0
            )  # 3600 = 1hr   #! Change based on timestamp relative to other Scenes?
        # * scripts
        elif domain_num == 25:
            # if wd_bst:
            #     wd_info = 'Running Script'
            # else:
            #     wd_info = 'Inactive Script'
            # if wd_bst:
            #     wd_alt = 'Running'
            # else:
            #     wd_alt = 'zzz'
            curr = ent_state.attributes.get("current", 0)
            wd_alt = "{} Running".format(curr)
            wd_info = timedelta_to_str(
                dt_util.now(), ent_state.attributes.get("last_triggered")
            )
            # wd_info = '({}) {}'.format(curr, wd_info)
        # * select (26) - included with input_select (17)

        # * sensors
        elif domain_num == 27:
            unit = ent_state.attributes.get("unit_of_measurement", "")
            # dev_class = ent_state.attributes.get('device_class', '')
            # wd_info = '  {} {} ({})'.format(state, unit, dev_class.title())
            wd_info = "  {} {}".format(state, unit)
            wd_bst = 0
            dev_class = ent_state.attributes.get("device_class", "")
            wd_alt = dev_class.title()
            wd_icon = SENSOR_ICON_DICT.get(dev_class, wd_icon)
        # * sun
        elif domain_num == 29:
            elevation = ent_state.attributes.get("elevation", 0)
            wd_alt = "{:.0f}°".format(elevation)
            wd_bst = 1 if elevation > 0 else 0
            # sets = dt_util.parse_datetime(set_str)
            # test = datetime.datetime.now()
            if wd_bst:
                set_str = ent_state.attributes.get("next_setting")
                sets = timedelta_to_str(
                    dt_util.utcnow(), dt_util.parse_datetime(set_str)
                )
                wd_info = "Sets {}".format(sets)
            else:
                set_str = ent_state.attributes.get("next_rising")
                sets = timedelta_to_str(
                    dt_util.utcnow(), dt_util.parse_datetime(set_str)
                )
                wd_info = "Rises {}".format(sets)
            # rise = dt_util.as_local(dt_util.parse_datetime(set_str)) #, '%H:%M') #.as_local()
            #!wd_info =  datetime.strptime(set_str, '%H:%M')#rise.strftime('%H:%M')
            #!wd_info = datetime.datetime.now().strftime("%Y") #! HA Err: "'__import__'" see: https://community.home-assistant.io/t/got-a-minute-to-test-a-python-script/309727/8
            # wd_info = datetime.datetime.now() # This works, but strftime does not
            #!wd_info =  datetime.datetime.strptime(set_str, '%H:%M')
        # * switches
        elif domain_num == 30:
            temp = ent_state.attributes.get("temperature", "")
            pwr = ent_state.attributes.get("power", "")
            td_str = timedelta_to_str(dt_util.now(), ent_state.last_changed)
            if wd_bst:
                if temp:
                    wd_info = "{}°C, {}".format(temp, td_str)
                else:
                    wd_info = "{}".format(td_str)
                if pwr:
                    wd_alt = "{:.1f} W".format(pwr)
                else:
                    wd_alt = "On (Sw)"
            else:
                wd_info = timedelta_to_str(dt_util.now(), ent_state.last_changed)
                wd_alt = "OFF (Sw)"
        # * timers
        elif domain_num == 31:
            wd_bst = 1 if state == "active" else 0  # 0 for idle & paused
            dur = ent_state.attributes.get("duration", "0")
            dur_str = "{}".format(dur)  # string(dur)
            if dur_str[:3] == "0:0":
                dur_str = dur_str[3:]
            elif dur_str[:2] == "0:":
                dur_str = dur_str[2:]
            if state == "active":
                wd_alt = dur_str
                now = dt_util.now()
                fin = ent_state.attributes.get("finishes_at", None)
                if fin:
                    wd_info = "Ends " + timedelta_to_str(
                        now, dt_util.parse_datetime(fin)
                    )
            elif state == "paused":
                wd_alt = "Paused"
                rem = ent_state.attributes.get("remaining", "0")
                rem_str = "{}".format(rem)
                if rem_str[:3] == "0:0":
                    rem_str = rem_str[3:]
                elif rem_str[:2] == "0:":
                    rem_str = rem_str[2:]
                wd_info = "{} Remains".format(rem_str)
            else:
                wd_alt = state.title()
                wd_info = "Duration {}".format(dur_str)
        # * updates
        elif domain_num == 32:
            installed = ent_state.attributes.get("installed_version", "")
            latest = ent_state.attributes.get("latest_version", "")
            skipped = ent_state.attributes.get("skipped_version", None)
            updating = ent_state.attributes.get("in_progress", None)
            if updating:
                wd_info = "Updating {}".format(installed, latest)
                wd_alt = "Busy"
            elif wd_bst:
                wd_info = "{}»{}".format(installed, latest)  # →->
                wd_alt = "Skip?"
            else:
                if skipped:
                    wd_alt = skipped
                    wd_info = "{}(installed)".format(installed)
                else:
                    wd_alt = "Latest"
                    wd_info = "{}(installed)".format(installed)
                    # wd_info = timedelta_to_str(dt_util.now(), ent_state.last_changed)
        # * vacuums
        elif domain_num == 33:
            status = ent_state.attributes.get("status", "")
            bat = ent_state.attributes.get("battery_level", "")
            wd_info = "{},  {}".format(state.title(), status)
            wd_alt = "{} %".format(bat)
            wd_bst = 0 if state == ["docked"] else 1
        # * water heaters
        elif domain_num == 34:
            set_t = ent_state.attributes.get("temperature", None)
            if set_t is None:
                set_t = ent_state.attributes.get("target_temp_low", "?")
            temp = ent_state.attributes.get("current_temperature", None)
            away_mode = ent_state.attributes.get("away_mode", False)
            wd_alt = state.title()  # the current mode
            wd_bst = 0 if state in ["off", "unknown"] else 1
            away_str = "Away" if away_mode else "Set"
            if temp is None:
                wd_info = "{} {}°".format(away_str, set_t)
            else:
                wd_info = "{} {}° ({}°)".format(away_str, set_t, temp)
        # * weather
        # TODO: better handling of weather icons (add popup page eventually?)
        elif domain_num == 35:
            temp = ent_state.attributes.get("temperature", "")
            hum = ent_state.attributes.get("humidity", "")
            press = ent_state.attributes.get("pressure", "")
            wd_alt = "{}°C".format(
                temp
            )  # NOTE need to set Nx HMI to use utf8 ENCODING, then add uft8 FONTs (subsets)
            # wd_info = '{} ({}%, {}hPa)'.format(state, hum, press)
            wd_info = "{} {}%H".format(state.replace("-", " ").title(), hum)
            wd_bst = 0  # can set threshold rules in YAML
        # * zone
        elif domain_num == 36:
            wd_alt = "{} Persons".format(state)
            # wd_bst = 0 if state == '0' else 1
            if state == "0":
                wd_bst = 0
                wd_info = timedelta_to_str(dt_util.now(), ent_state.last_changed)
            else:
                wd_bst = 1
                persons = ent_state.attributes.get("persons", [])
                wd_info = ",".join([p.replace("person.", "").title() for p in persons])
        #! debug only
        # else:
        #     wd_bst = 1
        #     wd_info = "XX"
        #     domain_num = wd_dmn & DOMAIN_NUM_MASK
        #     wd_alt = '*{}'.format(domain_num)

        # * Unavailable - change icon & disable actions
        if state == "unavailable":
            wd_icon = UNAVAILABLE_ICON
            # wd_dmn = domain_num  # remove action capabilities from domain code
            wd_dmn = 0  # disable interactions & gesture action descriptions
            wd_alt = "Unavailable"
            wd_bst = 0  # Use unhighlighted version of icon
        # * Unknown - change icon (without disabling actions)
        # elif state == 'unknown':
        #     wd_icon = UNAVAILABLE_ICON
    # return wd_bst, str(wd_info), str(wd_alt), wd_dmn, wd_icon
    return wd_name, str(wd_info), str(wd_alt), wd_icon, wd_bst, wd_dmn, ERROR
    # --- get_widget_info() ---


def setwd(args_list):
    """setwd page_num_, start_wd, num_cards
    (Updates the data on widget page page_num (numbered from 'W0') starting
    with widget start_wd in card 0 and then the next num_cards widgets
    for the remaining widget cards on the Nextion page.)

    The list of WIDGETs specified in the 'widgets:' YAML of the calling automation.
    Also updates wd_tot (the total number of widgets in the list), which the
    Nextion needs to know which Widget pages it has enough data for to display.
    """

    MAX_NAME_CHARS = 10
    MAX_ALT_CHARS = 8
    MAX_INFO_CHARS = 20
    # also uses GLOBAL variables/constants

    # * Parse calling arguments
    try:
        # defaults for optional parameters
        page_type = 0  # TODO: not used yet: placeholder for allowing future different 'types' of widget pages that support different features (e.g. bit encoded feature support)
        len_name = MAX_NAME_CHARS
        len_alt = MAX_ALT_CHARS
        len_info = MAX_INFO_CHARS
        num_args = len(args_list)
        if num_args == 0:
            # If called without arguments, just write the Global Widget settings to Nextion and SKIP Widget Page update
            # assigned directly as integers: set to skip Page update (& only update Global vars)
            [page_num, start_wd, num_cards] = [
                0,
                0,
                0,
            ]
        elif 3 <= num_args <= 7:
            [page_num_, start_wd_, num_cards_] = args_list[:3]
            try:
                page_num = int(page_num_)
                start_wd = int(start_wd_)
                num_cards = int(num_cards_)
                if num_args > 3:
                    page_type = int(args_list[3])
                if num_args > 4:
                    len_name = int(args_list[4])
                if num_args > 5:
                    len_alt = int(args_list[5])
                if num_args > 6:
                    len_info = int(args_list[6])
            except:
                # chars = 255
                raise ValueError("Some arguements are not integers.")
        else:
            raise ValueError("Wrong number of items in arguments list.")
    except ValueError as exptn:
        err_msg = "{}\nNextion Handler failed within SET function:\n<{}> <{}>.".format(
            exptn, "setwd", "> <".join(args_list)
        )
        logger.warning("nextion_handler.py " + err_msg)
        raise ValueError(err_msg)
    # * Get & Send data for each Widget card on page: Name, Icon, Domain_code, Boolean_status, Info status, Alt_text
    card = 0
    pg_pfx = "W{}.".format(page_num)  # page prefix for Nextion page variable names
    num_widgets = len(
        WIDGETS_LIST
    )  # This is written to Nextion as part of Global variables at the end
    page_widgets = WIDGETS_LIST[start_wd : start_wd + num_cards]
    # If there is at least 1 Widget for page, fill any shortfall cards with blanks
    num_page_widgets = len(page_widgets)
    # Set extra unused cards to None (to be blanked out)
    if 0 < num_page_widgets < num_cards:
        page_widgets.extend([None] * (num_cards - num_page_widgets))
    for card, wd in enumerate(page_widgets):
        # Handle exception INSIDE 'for' loop (so that 1 problem card doesn't stop others from updating)
        try:
            ERR_INFO = False
            # Defaults for 'blank' (including 'None') Widget cards
            card_sfx = "{:02}".format(card)
            entity_id = None
            wd_dmn = 0  # domain code - byte encoded
            wd_icon = BLANK_ERR_ICON
            wd_bst = 0  # icon state: inactive (0) / highlighted (0)
            wd_name = ""  # Line 1: Card title/entity name
            wd_alt = ""  # Line 2: optional alternate/short info on entity
            wd_info = ""  # Line 3: descriptive info on state/attributes of entity

            if not wd is None:
                # * Get widget details from YAML automation config
                # YAML name, info, alt, icon, bst (Optional)
                wd_name_yaml = wd.get("name", None)
                wd_info_yaml = wd.get("info", None)
                wd_alt_yaml = wd.get("alt", None)
                wd_icon_yaml = wd.get("icon", None)  # index number
                wd_bst_yaml = wd.get("icon_state", None)  # boolean icon state (0/1)
                entity_id = wd.get("entity", None)
                # "template" is alternate name for "blank" - more logical in some use cases
                if entity_id in ["template", "blank"]:
                    entity_id = None
                # Get entity data (may modify defalut icon)
                if entity_id:
                    (
                        wd_name,
                        wd_info,
                        wd_alt,
                        wd_icon,
                        wd_bst,
                        wd_dmn,
                        err,
                    ) = get_widget_info(entity_id)
                    if err:
                        ERR_INFO = True
                # final icon
                if wd_icon_yaml and not ERR_INFO and not wd_icon == UNAVAILABLE_ICON:
                    try:
                        if wd_icon_yaml:
                            wd_icon = int(wd_icon_yaml)
                            if wd_icon < 0 or wd_icon > MAX_ICON_NUM:
                                ERR_INFO = True
                                wd_icon = BLANK_ERR_ICON
                                wd_bst = 1  # Use highlighted (Error) version of icon
                                wd_alt = "Fix icon"
                                wd_info = "Bad range <{}>".format(wd_icon_yaml)
                    except:
                        ERR_INFO = True
                        wd_alt = "Fix icon"
                        wd_info = "Bad num <{}>".format(wd_icon_yaml)
                        wd_icon = BLANK_ERR_ICON
                        wd_bst = 1
                # final icon state (unless overridden by error below)
                if not wd_bst_yaml is None:
                    if wd_icon == BLANK_ERR_ICON and wd_bst == 1:
                        pass  # do not overwrite an error icon
                    elif wd_bst_yaml in [0, 1, "0", "1"]:
                        wd_bst = int(wd_bst_yaml)
                    elif wd_bst_yaml in [True, False]:
                        wd_bst = 1 if wd_bst_yaml else 0
                    else:
                        # Invalid icon state
                        wd_alt_yaml = "Fix YAML"
                        wd_info_yaml = "Bad icon_state: <{}>".format(wd_icon_state_yaml)
                        wd_icon = BLANK_ERR_ICON
                        wd_bst = 1
                # final name/title text (allow empty strings for blanking defaults)
                if not wd_name_yaml is None:
                    wd_name = wd_name_yaml
                # final info & alt text outputs (UNLESS these already contain error info)
                if not ERR_INFO:
                    if not wd_info_yaml is None:
                        wd_info = wd_info_yaml
                    if not wd_alt_yaml is None:
                        wd_alt = wd_alt_yaml
            #! Update speed test:
            # wd_alt = ".."
            # wd_info = ".."

            # * Send Widget data to its Card on Nextion page
            # NOTE: Set UTF encoding _everywhere_ (Nextion HMI settings, fonts, ESPHome comms etc.)
            # --- directly written to LOCAL Text UI attribute ---
            # Optional extra short 'alt' text
            nx_cmd_str = '{}{}{}.txt="{}"'.format(
                pg_pfx, "tALT", card_sfx, wd_alt[:len_alt]
            )
            send_nx_cmd(nx_cmd_str)
            # Info status (descriptive string)
            nx_cmd_str = '{}{}{}.txt="{}"'.format(
                pg_pfx, "tINF", card_sfx, wd_info[:len_info]
            )
            send_nx_cmd(nx_cmd_str)
            # --- written to GLOBAL variables used by APPLY_VARS to update UI ---
            # Domain code
            nx_cmd_str = "{}{}{}.val={}".format(pg_pfx, "nDMN", card_sfx, wd_dmn)
            send_nx_cmd(nx_cmd_str)
            # Icon
            nx_cmd_str = "{}{}{}.val={}".format(pg_pfx, "nICN", card_sfx, wd_icon)
            send_nx_cmd(nx_cmd_str)
            # Name
            nx_cmd_str = '{}{}{}.txt="{}"'.format(
                pg_pfx, "tNM", card_sfx, wd_name[:len_name]
            )
            send_nx_cmd(nx_cmd_str)
            # Boolean status
            nx_cmd_str = "{}{}{}.val={}".format(pg_pfx, "bST", card_sfx, wd_bst)
            send_nx_cmd(nx_cmd_str)
        except ValueError as exptn:
            # Handle exceptions INSIDE for loop (for each card individually), so that an error in 1 card doesn't stop others rendering.
            # Log error message
            err_msg = "{}\nError reading settings for Widget Card index *{}* (0 is top-left on page) from YAML list.".format(
                exptn, card
            )
            logger.warning("nextion_handler.py " + err_msg)
            # raise ValueError(err_msg)
            try:
                # Display a highlighted error icon for the Widget as feedback
                # Icon
                nx_cmd_str = "{}{}{}.val={}".format(
                    pg_pfx, "nICN", card_sfx, BLANK_ERR_ICON
                )
                send_nx_cmd(nx_cmd_str)
                # Boolean status
                nx_cmd_str = "{}{}{}.val={}".format(pg_pfx, "bST", card_sfx, 1)
                send_nx_cmd(nx_cmd_str)
            except:
                pass
    # --- end Widget card for loop ---

    # * Write Global Nextion settings
    nx_cmd_str = "wd_tot={}".format(num_widgets)
    send_nx_cmd(nx_cmd_str)

    return True
    # --- setwd() ---


# _________________
# * ACTION FUNCTIONS - perform an action in HA (don't do anything to Nx)


# * ---- Actions for GENERIC Entities, NO PREFIX/CLASS can be assumed ------
#  $Aliases are preferred for all entity arguements entered in Nx NhCmds.
#  (If HA entitiy_ids are used instead, the full entity_id, including class,
#  is required for the functions immediately below.  Class can be deduced for the next block of NhCmds.)


def tgl(args_list):
    """tgl E (toggle E)"""
    prefix = None  # multiple entity classes - user needs to be explicit
    domain = "homeassistant"
    service = "toggle"
    try:
        # FULL entity required - a generic function across multiple types of entities
        if len(args_list) == 1:
            e = args_list[0]
            entity_id = get_entity_id_state(e, domain_prefix=prefix)[0]
            service_data = {"entity_id": entity_id}
            try:
                hass.services.call(domain, service, service_data, False)
            except:  # need HASS API docs to be explicit about the exception to catch here
                raise ValueError(
                    "Failed HASS service call {}.{}.".format(domain, service)
                )
        else:
            raise ValueError("Wrong number of items in arguments list.")
    except ValueError as exptn:
        err_msg = (
            "{}\nNextion Handler failed within ACTION function:\n<{}> <{}>.".format(
                exptn, "tgl", "> <".join(args_list)
            )
        )
        logger.warning("nextion_handler.py " + err_msg)
        raise ValueError(err_msg)
    return True


def ton(args_list):
    """ton E (turn on E)"""
    prefix = None  # multiple entity classes - user needs to be explicit
    domain = "homeassistant"
    service = "turn_on"
    try:
        # FULL entity required - a generic function across multiple types of entities
        if len(args_list) == 1:
            e = args_list[0]
            entity_id = get_entity_id_state(e, domain_prefix=prefix)[0]
            service_data = {"entity_id": entity_id}
            try:
                hass.services.call(domain, service, service_data, False)
            except:  # need HASS API docs to be explicit about the exception to catch here
                raise ValueError(
                    "Failed HASS service call {}.{}.".format(domain, service)
                )
        else:
            raise ValueError("Wrong number of items in arguments list.")
    except ValueError as exptn:
        err_msg = (
            "{}\nNextion Handler failed within ACTION function:\n<{}> <{}>.".format(
                exptn, "ton", "> <".join(args_list)
            )
        )
        logger.warning("nextion_handler.py " + err_msg)
        raise ValueError(err_msg)
    return True


def tof(args_list):
    """tof E (turn off E)"""
    prefix = None  # multiple entity classes - user needs to be explicit
    domain = "homeassistant"
    service = "turn_off"
    try:
        # FULL entity required - a generic function across multiple types of entities
        if len(args_list) == 1:
            e = args_list[0]
            entity_id = get_entity_id_state(e, domain_prefix=prefix)[0]
            service_data = {"entity_id": entity_id}
            try:
                hass.services.call(domain, service, service_data, False)
            except:  # need HASS API docs to be explicit about the exception to catch here
                raise ValueError(
                    "Failed HASS service call {}.{}.".format(domain, service)
                )
        else:
            raise ValueError("Wrong number of items in arguments list.")
    except ValueError as exptn:
        err_msg = (
            "{}\nNextion Handler failed within ACTION function:\n<{}> <{}>.".format(
                exptn, "tof", "> <".join(args_list)
            )
        )
        logger.warning("nextion_handler.py " + err_msg)
        raise ValueError(err_msg)
    return True


# * ---- Actions where entity class can be assumed/deduced ------
# No need to specify entity device class in Nx entity_id arguements - they can
# be deduced and added (but $ aliases are still the expected norm in NhCmds)


def inps(args_list):
    """inps E string (set value of input_select E to string)
    inps E (+/-)n (set value of input_select E to nth option)
    Allow spaces in 'string' by rejoining excess args_list items
    """
    prefix = "input_select."
    domain = "input_select"
    service = "select_option"  #! service 'set_value' with service data 'option'  deprecated ~Mar 2022?
    transfer_err_msg = ""
    try:
        if len(args_list) > 1:
            e = args_list[0]
            # reconstruct string if it was split by on spaces before
            x_ = " ".join(args_list[1:])
            entity_id, ent_state, state = get_entity_id_state(e, domain_prefix=prefix)
            opt_list = ent_state.attributes.get("options", None)
            if opt_list:
                num_opts = len(opt_list)
                # try:
                #     curr_idx = opt_list.index(state)
                #     new_idx = adjust(
                #         curr_idx, x_, 0, num_opts, IS_MOD=True, AS_INT=True
                #     )
                # except:
                #     new_idx = 0
                # if new_idx is None:
                #     # if x_ is a string, select this option directly
                #     opt_str = x_
                # else:
                #     opt_str = opt_list[new_idx]
                try:
                    curr_opt = state
                    new_opt = adjust(curr_opt, x_, None, None, OPTION_LIST=opt_list)
                    if new_opt is None:
                        # TODO: more informative messages for other errors (mode list, current mode)
                        transfer_err_msg = "Bad input_select adjustment: <{}>".format(
                            x_
                        )
                except ValueError:
                    transfer_err_msg = "Bad input_select option: <{}>".format(x_)
            else:
                transfer_err_msg = "No option list for: <{}>".format(e)
        else:
            raise ValueError("Wrong number of items in arguments list.")
        if transfer_err_msg:
            raise ValueError(transfer_err_msg)
        else:
            service_data = {"entity_id": entity_id, "option": new_opt}
            try:
                hass.services.call(domain, service, service_data, False)
            except:  # need HASS API docs to be explicit about the exception to catch here
                raise ValueError("Failed HASS input_number service call.")
    except ValueError as exptn:
        err_msg = (
            "{}\nNextion Handler failed within ACTION function:\n<{}> <{}>.".format(
                exptn, "inps", "> <".join(args_list)
            )
        )
        logger.warning("nextion_handler.py " + err_msg)
        # hass.services.call('persistent_notification', 'create', {'title': 'Nextion Handler Error!', 'message': err_msg, 'notification_id': 'nx_handler_error_set' }, False)
        raise ValueError(err_msg)
    #! dbg
    # msg = 'Nextion Handler Debug:\n<{}> <{}>.'.format('inps', '> <'.join(args_list))
    # hass.services.call('persistent_notification', 'create', {'title': 'Nextion Handler Debug!', 'message': msg, 'notification_id': 'nx_handler_debug_inps' }, False)
    return True
    # --- inps() ---


def sel(args_list):
    """sel E string (set value of select E to string)
    sel E (+/-)n (set value of select E to nth option)
    Allow spaces in 'string' by rejoining excess args_list items
    """
    prefix = "select."
    domain = "select"
    service = "select_option"  #! service 'set_value' with service data 'option'  deprecated ~Mar 2022?
    transfer_err_msg = ""
    try:
        if len(args_list) > 1:
            e = args_list[0]
            # reconstruct string if it was split by on spaces before
            x_ = " ".join(args_list[1:])
            entity_id, ent_state, state = get_entity_id_state(e, domain_prefix=prefix)
            opt_list = ent_state.attributes.get("options", None)
            if opt_list:
                num_opts = len(opt_list)
                try:
                    curr_opt = state
                    new_opt = adjust(curr_opt, x_, None, None, OPTION_LIST=opt_list)
                    if new_opt is None:
                        # TODO: more informative messages for other errors (mode list, current mode)
                        transfer_err_msg = "Bad select adjustment: <{}>".format(x_)
                except ValueError:
                    transfer_err_msg = "Bad select option: <{}>".format(x_)
            else:
                transfer_err_msg = "No option list for: <{}>".format(e)
        else:
            raise ValueError("Wrong number of items in arguments list.")
        if transfer_err_msg:
            raise ValueError(transfer_err_msg)
        else:
            service_data = {"entity_id": entity_id, "option": new_opt}
            try:
                hass.services.call(domain, service, service_data, False)
            except:  # need HASS API docs to be explicit about the exception to catch here
                raise ValueError("Failed HASS select service call.")
    except ValueError as exptn:
        err_msg = (
            "{}\nNextion Handler failed within ACTION function:\n<{}> <{}>.".format(
                exptn, "sel", "> <".join(args_list)
            )
        )
        logger.warning("nextion_handler.py " + err_msg)
        raise ValueError(err_msg)
    return True
    # --- sel() ---


def inpb(args_list):
    """inpb E b (turn input_binary `E` `on` if b!=0 otherwise turn `off`)"""
    prefix = "input_boolean."
    domain = "input_boolean"
    service = None  # set to 'turn_on' or 'turn_off'
    try:
        if len(args_list) == 2:
            [e, b] = args_list
            entity_id = get_entity_id_state(e, domain_prefix=prefix)[0]
            if b != "0":  # treat any non-zero (string) value as True
                service = "turn_on"
            else:
                service = "turn_off"
            service_data = {"entity_id": entity_id}
            try:
                hass.services.call(domain, service, service_data, False)
            except:  # need HASS API docs to be explicit about the exception to catch here
                raise ValueError("Failed HASS input_boolean service call.")
        else:
            raise ValueError("Wrong number of items in arguments list.")
    except ValueError as exptn:
        err_msg = (
            "{}\nNextion Handler failed within ACTION function:\n<{}> <{}>.".format(
                exptn, "inpb", "> <".join(args_list)
            )
        )
        logger.warning("nextion_handler.py " + err_msg)
        raise ValueError(err_msg)
    return True


def inpn(args_list):
    """inpn E (+/-)x(%) (set value of input_number E to x)"""
    prefix = "input_number."
    domain = "input_number"
    service = "set_value"
    mult = 1
    try:
        if len(args_list) == 2:
            [e, adj_] = args_list
            entity_id, ent_state, state = get_entity_id_state(e, domain_prefix=prefix)
            try:
                x1 = float(state)
            except ValueError:
                raise ValueError("Value entity state is not a valid float.")
            mn = ent_state.attributes.get("min", None)
            mx = ent_state.attributes.get("max", None)
            x2 = adjust(x1, adj_, mn, mx)
            service_data = {"entity_id": entity_id, "value": x2}
            try:
                hass.services.call(domain, service, service_data, False)
            except:  # need HASS API docs to be explicit about the exception to catch here
                raise ValueError(
                    "Failed HASS service call {}.{}.".format(domain, service)
                )
        else:
            raise ValueError("Wrong number of items in arguments list.")
    except ValueError as exptn:
        err_msg = (
            "{}\nNextion Handler failed within ACTION function:\n<{}> <{}>.".format(
                exptn, "inpn", "> <".join(args_list)
            )
        )
        logger.warning("nextion_handler.py " + err_msg)
        raise ValueError(err_msg)
    return True


# 'lt act E ..' commond Consolidates and replaces depracted 'lt_act' NHcmds
def lt(args_list):
    """lt act E (arg1) (arg2) (arg3) (call action with code 'act' for lt E)
    action/service options:
        (turn_on, turn_off, toggle: use generic ton, tof, tgl instead)
        lt brt E x (set brightness percent of light E to x (0..100))
        lt brt E +/-x (increase/decrease brightness percent of light E by x (0..100))
        lt brtv E x (set brightness value of light E to x(0..255))
        lt ct E x (set colour temperature of light E to x mireds)
        lt rgb E r g b (set colour of light E to RGB = r, g, b)
        lt hs E h s (set colour of light E to Hue = h, Saturation = s)
        lt hct E +/-x (adjust the hue or ct of light E by x%, based on current light mode)
        lt cw E dx dy r (set color of light E to Color-Wheel location dx, dy from centre of circle radius r)
            Assumes a Home-Assistant-style color-wheel with red (hue 0) at 3 o'clock, increasing CLOCKWISE to 360.
            (CLOCKWISE accounts for screen y increasing downwards, which reverses angle of Cartesian ArcTan.)
        lt wt E (set light E to a supported white/color_temp mode).
            (Otherwise just try to turn the light on.)
    """
    MAX_R_MULT = 999  # 130  # ignore co-ordinates outside the radius of color wheel by this % factor

    prefix = "light."
    domain = "light"
    service = None  # assigned based on 'act' code
    # wrong_num_args = False
    transfer_err_msg = ""  # Allows exception messages to be raised & passed upwards without being overwritten by a higher level exception
    skip_service_call = False  # give 'act' processing below a way to skip if required

    # set the service & service_data for the hass.service call
    try:
        num_args = len(args_list)
        if num_args == 2:
            # Action that reqquire no other args (e.g., call HA services with NO service_data (just entity_id))
            # e = args_list[0]
            # act = args_list[1]
            [act, e] = args_list  # [:2]
            entity_id, ent_state, state = get_entity_id_state(e, domain_prefix=prefix)
            service_data = {
                "entity_id": entity_id
            }  # the same for all services below (that have no other arguements)
            if act == "wt":
                service = "turn_on"
                sm = ent_state.attributes.get("supported_color_modes", "onoff")
                if "color_temp" in sm:
                    ct = ent_state.attributes.get("color_temperature", 370)
                    service_data = {"entity_id": entity_id, "color_temp": int(ct)}
                elif "white" in sm:
                    brt = ent_state.attributes.get("brightness", 150)
                    service_data = {"entity_id": entity_id, "white": int(brt)}
                else:
                    service_data = {"entity_id": entity_id}
            # End of  valid act codes
            else:
                transfer_err_msg = "The specified ACTION CODE is not valid."
        elif 3 <= num_args <= 5:
            # services with 1 to 5 args (together with e and act)
            args_list.extend(
                ["_"] * 3
            )  # extend list with '_'s to indicate potential unassigned/default values
            (act, e, x_, y_, z_) = args_list[:5]
            # (e, act, x_) = args_list[:3]
            entity_id, ent_state, state = get_entity_id_state(e, domain_prefix=prefix)
            try:
                # brighness (pct & val)
                if act == "brt":
                    service = "turn_on"
                    if state == "off":
                        if x_[0] == "+":
                            x_ = "100"  # turn on at max brightness
                        elif x_[0] == "-":
                            x_ = "1"  # 15  # turn on at min brightness
                    curr_val = ent_state.attributes.get("brightness", 0) / 2.55
                    new_val = adjust(curr_val, x_, 1, 100, AS_INT=True)
                    if new_val is None:
                        # TODO: add error handling
                        new_val = 33
                    service_data = {"entity_id": entity_id, "brightness_pct": new_val}
                elif act == "brtv":
                    service = "turn_on"
                    if state == "off":
                        if x_[0] == "+":
                            x_ = "255"  # turn on at max brightness
                        elif x_[0] == "-":
                            x_ = "5"  # 5  # turn on at min brightness
                    curr_val = ent_state.attributes.get("brightness", 0)
                    new_val = adjust(curr_val, x_, 1, 255, AS_INT=True)
                    if new_val is None:
                        # TODO: add error handling
                        new_val = 80
                    service_data = {"entity_id": entity_id, "brightness": new_val}
                # color_temp
                elif act == "ct":
                    service = "turn_on"
                    curr_val = ent_state.attributes.get("color_temp", 370)
                    min_val = ent_state.attributes.get("min_mireds", 153)
                    max_val = ent_state.attributes.get("max_mireds", 500)
                    new_val = adjust(curr_val, x_, min_val, max_val, AS_INT=True)
                    if new_val is None:
                        # TODO: add error handling
                        new_val = 370
                    service_data = {"entity_id": entity_id, "color_temp": new_val}
                # color (rgb, hs, cw)
                elif act == "rgb":
                    service = "turn_on"
                    service_data = {
                        "entity_id": entity_id,
                        "rgb_color": [int(x_), int(y_), int(z_)],
                    }
                elif act == "hs":
                    service = "turn_on"
                    x = float(x_)
                    y = float(y_)
                    h, s = ent_state.attributes.get("hs_color", (0, 50))
                    if x_[0] in ["+", "-"]:
                        h = h + x
                    else:
                        h = x
                    h = h % 360
                    if y_[0] in ["+", "-"]:
                        s = s + y
                    else:
                        s = y
                    if s > 100:
                        s = 100
                    elif s < 0:
                        s = 0
                    service_data = {"entity_id": entity_id, "hs_color": [h, s]}
                elif act == "hct":
                    # Percent adjustment to hue OR ct, depending on current (& supported) light mode.
                    service = "turn_on"
                    x = float(x_)
                    cm = ent_state.attributes.get("color_mode", None)
                    if cm == "color_temp":
                        ct = ent_state.attributes.get("color_temp", 370)
                        ct2 = int(ct + x * 3.47)  # x% of 347 mired span (153 .. 500)
                        if ct2 > ent_state.attributes.get("max_mireds", 500):
                            ct2 = ent_state.attributes.get("max_mireds", 500)
                        if ct2 < ent_state.attributes.get("min_mireds", 153):
                            ct2 = ent_state.attributes.get("min_mireds", 153)
                        service_data = {"entity_id": entity_id, "color_temp": ct2}
                    else:
                        h, s = ent_state.attributes.get("hs_color", (None, None))
                        if h:
                            h2 = h + x * 3.6  # x% of 360 hue span
                            #!
                            # h2 = h + 180
                            h2 = h2 % 360
                            service_data = {"entity_id": entity_id, "hs_color": [h2, s]}
                        else:
                            skip_service_call = True
                elif act == "cw":
                    service = "turn_on"
                    # Sign of dy is implictly changed (Screen vs Cartesian y co-ordinate) which reverses the Cartesian arctan angle from ANTICLOCKWISE to CLOCKWISE (relative to 3 o'clock)
                    [dx, dy, r] = [float(x_), float(y_), float(z_)]
                    sat = int(100 * math.sqrt(dx * dx + dy * dy) / r)
                    if sat <= MAX_R_MULT:
                        if sat > 100:
                            sat = 100
                        hue = int(math.atan2(dy, dx) * 180 / math.pi)
                        if hue < 0:
                            hue = hue + 360
                        service_data = {"entity_id": entity_id, "hs_color": [hue, sat]}
                    else:
                        skip_service_call = True
                # End of  valid act codes
                else:
                    transfer_err_msg = "The specified ACTION CODE is not valid."
            except:
                transfer_err_msg = (
                    "The specified argumentss are not of the valid TYPE(S)."
                )
        else:
            transfer_err_msg = "Wrong NUMBER of argumentss."
        if transfer_err_msg:
            raise ValueError(transfer_err_msg)
        # make the requested service call (with the service & service_data set above)
        if not skip_service_call:
            try:
                hass.services.call(domain, service, service_data, False)
            except:  # need HASS API docs to be explicit about the exception to catch here
                raise ValueError(
                    "Failed HASS service call {}.{}.".format(domain, service)
                )
    except ValueError as exptn:
        err_msg = (
            "{}\nNextion Handler failed within ACTION function:\n<{}> <{}>.".format(
                exptn, "lt", "> <".join(args_list)
            )
        )
        logger.warning("nextion_handler.py " + err_msg)
        # hass.services.call('persistent_notification', 'create', {'title': 'Nextion Handler Error!', 'message': err_msg, 'notification_id': 'nx_handler_error_set' }, False)
        raise ValueError(err_msg)
    return True
    # --- lt() ---


def scn(args_list):
    """scn E (set scenario E)"""
    prefix = "scene."
    domain = "scene"
    service = "turn_on"
    try:
        if len(args_list) == 1:
            e = args_list[0]
            entity_id = get_entity_id_state(e, domain_prefix=prefix)[0]
            try:
                hass.services.call("scene", "turn_on", {"entity_id": entity_id}, False)
            except:  # need HASS API docs to be explicit about the exception to catch here
                raise ValueError("Failed HASS scene.turn_on service call.")
        else:
            raise ValueError("Wrong number of items in arguments list.")
    except ValueError as exptn:
        err_msg = (
            "{}\nNextion Handler failed within ACTION function:\n<{}> <{}>.".format(
                exptn, "scn", "> <".join(args_list)
            )
        )
        logger.warning("nextion_handler.py " + err_msg)
        raise ValueError(err_msg)
    return True


def scpt(args_list):
    """scpt E (t) (call script E: if t==off, turn_off instead)"""
    prefix = "script."
    domain = "script"
    service = "turn_on"  # << default: if t=='off', 'turn_off' instead
    try:
        if len(args_list) in [1, 2]:
            if len(args_list) == 1:
                e = args_list[0]
            else:
                [e, t] = args_list
                if t == "off":
                    service = "turn_off"
            entity_id = get_entity_id_state(e, domain_prefix=prefix)[0]
            service_data = {"entity_id": entity_id}
            try:
                hass.services.call(domain, service, service_data, False)
            except:  # need HASS API docs to be explicit about the exception to catch here
                raise ValueError(
                    "Failed HASS service call {}.{}.".format(domain, service)
                )
        else:
            raise ValueError("Wrong number of items in arguments list.")
    except ValueError as exptn:
        err_msg = (
            "{}\nNextion Handler failed within ACTION function:\n<{}> <{}>.".format(
                exptn, "scpt", "> <".join(args_list)
            )
        )
        logger.warning("nextion_handler.py " + err_msg)
        raise ValueError(err_msg)
    return True


def mp(args_list):
    """mp act E (arg1) (arg2) (call action/'service' with code 'act' for media_player E)
    action/service options:
        (turn_on, turn_off, toggle: use generic ton, tof, tgl instead)
        mp pp E (media_play_pause media_player E)
        mp ply E (media_play media_player E)
        mp ps E (media_pause media_player E)
        mp stp E (media_stop media_player E)
        mp nxt E (media_next_track media_player E)
        mp prv E (media_previous_track media_player E)
        mp v+ E (volume_up media_player E - increments are player-dependent?)
        mp v- E (volume_down media_player E)

        mp vol E x (volume_set media_player E to x (0..100))
        mp mut E x (volume_mute media_player E to x (0/1), or toggle i x<0 )
        mp sk E x (media_seek media_player E to position x (seconds, player dependent))
        mp pm E x y (play_media x y on media_player E)
            x = media_content_id: id is player-dependent;
            y = media_content_type: in [music, tvshow, video, episode, channel, playlist]
        mp src E x (select_source x (player dependent) for media_player E)   #! DONE - need to handle spaces
        mp src E n (select_source for media_player E n (+/-)steps forward/back in source_list from current source)
    """
    # Service options deemed unsuitable to include in a Nextion UI:
    # clear_playlist, shuffle_set, repeat_set, play_media, select_sound_mode, join, unjoin

    prefix = "media_player."
    domain = "media_player"
    service = None  # assigned based on 'act' code
    transfer_err_msg = ""
    skip_service_call = False  # give 'act' processing below a way to skip if required

    try:
        # set the service & service_data for the hass.service call
        if len(args_list) == 2:
            # services with NO arguements (just entity_id)
            # (turn_on, turn_off, toggle)
            # pp, ply, ps, stp: media_play_pause, media_play, media_pause, media_stop,
            # nxt, prv: media_next_track, media_previous_track, clear_playlist
            # v+, v-: volume_up, volume_down  (fixed vol increments - player-dependent?)
            act, e = args_list
            # entity_id = get_entity_id_state(e, domain_prefix=prefix)[0]  # will raise exception if it can't translate e to valid entity_id
            entity_id, ent_state, state = get_entity_id_state(e, domain_prefix=prefix)
            service_data = {
                "entity_id": entity_id
            }  # the same for all services below (that have no other arguements)
            if act == "pp":
                service = "media_play_pause"  # not supported on all devices
            elif act == "pp2":
                # TODO: if state=='playing' sent stop AND pause, else send play
                if state == "playing":
                    service = "media_stop"  # also send pause
                else:
                    service = "media_play"
            elif act == "ply":
                service = "media_play"
            elif act == "ps":
                service = "media_pause"
            elif act == "stp":
                service = "media_stop"
            elif act == "nxt":
                service = "media_next_track"
            elif act == "prv":
                service = "media_previous_track"
            elif act == "v+":
                service = "volume_up"
            elif act == "v-":
                service = "volume_down"
            # End of  valid act codes
            else:
                transfer_err_msg = "The specified ACTION CODE is not valid."
        elif len(args_list) > 2:
            # services with 1+ arguements (in addition to entity_id):
            # vol: volume_set(volume_level: 0..1 float)
            # mut: volume_mute(is_volume_muted: True/False), media_play_pause,
            # sk: media_player.media_seek(seek_position: position - player-dependent)
            # pm: media_player.play_media(media_content_id: id - player-dependent; media_content_type: [music, tvshow, video, episode, channel or playlist])
            # src: media_player.select_source(source: source - p-d)
            args_list_ext = (
                args_list + ["_"] * 3
            )  # extend COPY of list with '_'s to indicate potential unassigned/default values
            act, e, x_, y_, z_ = args_list_ext[:5]
            entity_id, ent_state, state = get_entity_id_state(e, domain_prefix=prefix)
            try:
                if act == "vol":
                    service = "volume_set"
                    curr_vol = ent_state.attributes.get("volume_level", 0)
                    new_vol = adjust(curr_vol, x_, 0.0, 1.0)  # float
                    service_data = {"entity_id": entity_id, "volume_level": new_vol}
                elif act == "mut":
                    service = "volume_mute"
                    muted = ent_state.attributes.get("is_volume_muted", None)
                    if muted is None:
                        # entity cannot be muted (in its current state)
                        skip_service_call = True
                    else:
                        if int(x_) < 0:
                            set_mute = not muted  # toggle
                        else:
                            set_mute = False if x_[0] in ["0", "F"] else True
                        service_data = {
                            "entity_id": entity_id,
                            "is_volume_muted": set_mute,
                        }
                elif act == "sk":
                    service = "media_seek"
                    curr_pos = ent_state.attributes.get("media_position", 0)
                    duration = ent_state.attributes.get("media_duration", 1)
                    new_pos = adjust(curr_pos, x_, 0, duration, AS_INT=True)
                    service_data = {"entity_id": entity_id, "seek_position": new_pos}
                elif act == "pm":
                    service = "play_media"
                    service_data = {
                        "entity_id": entity_id,
                        "media_content_id": x_,
                        "media_content_type": y_,
                    }
                elif act == "src":
                    # NEW 'src' version - uses new list handling of adjust() helper
                    # Rejoin args BUT without extra '_' added above
                    src_adj = " ".join(args_list[2:])
                    service = "select_source"
                    try:
                        src_list = ent_state.attributes.get("source_list", None)
                        curr_src = ent_state.attributes.get("source", None)
                        new_src = adjust(
                            curr_src, src_adj, None, None, OPTION_LIST=src_list
                        )  # option
                        if new_src is None:
                            # TODO: more informative messages for other errors (mode list, current mode)
                            transfer_err_msg = (
                                "Bad media source adjustment: <{}>".format(src_adj)
                            )
                        else:
                            service_data = {"entity_id": entity_id, "source": new_src}
                    except ValueError:
                        transfer_err_msg = "Bad media source: <{}>".format(src_adj)
                # End of  valid act codes
                else:
                    transfer_err_msg = "The specified ACTION CODE is not valid."
            except:
                transfer_err_msg = "The specified ARGs are not of the valid type(s)."
        else:
            transfer_err_msg = "Wrong NUMBER of items in arguments list."
        if transfer_err_msg:
            raise ValueError(transfer_err_msg)
        if not skip_service_call:
            # make the requested service call (with the service & service_data set above)
            try:
                hass.services.call(domain, service, service_data, False)
            except:  # need HASS API docs to be explicit about the exception to catch here
                raise ValueError(
                    "Failed HASS service call {}.{}.".format(domain, service)
                )
    except ValueError as exptn:
        err_msg = (
            "{}\nNextion Handler failed within ACTION function:\n<{}> <{}>.".format(
                exptn, "mp", "> <".join(args_list)
            )
        )
        logger.warning("nextion_handler.py " + err_msg)
        # hass.services.call('persistent_notification', 'create', {'title': 'Nextion Handler Error!', 'message': err_msg, 'notification_id': 'nx_handler_error_set' }, False)
        raise ValueError(err_msg)
    return True
    # --- mp() ---


def cl(args_list):
    """cl act E (arg1) (arg2...) (call action/'service' with code 'act' for
    climate entity E)
    action/service options:
        (turn_on, turn_off: use generic ton, tof)
        cl tgl E (climate-specific toggle) (Generic toggle does not work!)
        cl hm E m (set_hvac_mode to mode m)
        cl pm E m (set_preset_mode to mode m)
        cl fm E m (set_fan_mode to mode m)
        cl sm E m (set_swing_mode to mode m)
        cl aux E x (set_aux_heat on(1), off(0), toggle(-1))
        cl tmp E adj (set_temperature (single set point) based on adjustment)
        cl tlo E adj (set_temperature (bottom of range) based on adjustment)
        cl thi E adj (set_temperature (top of range) based on adjustment)
        cl tauto E adj (set_temperature (dedudce tmp, tlo or thi above) based on adjustment)
        cl hum E adj (set_humidity based on adjustment)
    """

    prefix = "climate."
    domain = "climate"
    service = None  # assigned based on 'act' code
    transfer_err_msg = ""
    skip_service_call = False  # give 'act' processing below a way to skip if required

    try:
        # set the service & service_data for the hass.service call
        if len(args_list) == 2:
            act, e = args_list
            entity_id, ent_state, state = get_entity_id_state(e, domain_prefix=prefix)
            # toggle (climate entities don't work with normal toggle)
            if act == "tgl":
                service = "turn_on" if state == "off" else "turn_off"
                service_data = {"entity_id": entity_id}
            # End of  valid act codes (for 2 args)
            else:
                transfer_err_msg = "The specified ACTION CODE is not valid."
        elif len(args_list) >= 3:
            act, e, x_ = args_list[:3]
            if act in ["hm", "pm", "fm", "sm"]:
                # join 'mode' values that contain spaces
                mode_adj = " ".join(args_list[2:])
            entity_id, ent_state, state = get_entity_id_state(e, domain_prefix=prefix)
            try:
                # HVAC mode
                if act == "hm":
                    service = "set_hvac_mode"
                    try:
                        modes = ent_state.attributes.get("hvac_modes", None)
                        curr_mode = state
                        new_mode = adjust(
                            curr_mode, mode_adj, None, None, OPTION_LIST=modes
                        )  # option
                        if new_mode is None:
                            # TODO: more informative messages for other errors (mode list, current mode)
                            transfer_err_msg = "Bad hvac_mode adjustment: <{}>".format(
                                mode_adj
                            )
                        else:
                            service_data = {
                                "entity_id": entity_id,
                                "hvac_mode": new_mode,
                            }
                    except ValueError:
                        # skip_service_call = True  # not required, error message below will trigger exception
                        transfer_err_msg = "Bad hvac_mode: <{}>".format(mode_adj)
                # PRESET mode
                elif act == "pm":
                    service = "set_preset_mode"
                    try:
                        modes = ent_state.attributes.get("preset_modes", None)
                        curr_mode = ent_state.attributes.get("preset_mode", None)
                        new_mode = adjust(
                            curr_mode, mode_adj, None, None, OPTION_LIST=modes
                        )  # option
                        if new_mode is None:
                            # TODO: more informative messages for other errors (mode list, current mode)
                            transfer_err_msg = (
                                "Bad preset_mode adjustment: <{}>".format(mode_adj)
                            )
                        else:
                            service_data = {
                                "entity_id": entity_id,
                                "preset_mode": new_mode,
                            }
                    except ValueError:
                        transfer_err_msg = "Bad preset_mode: <{}>".format(mode_adj)
                # FAN mode
                elif act == "fm":
                    service = "set_fan_mode"
                    try:
                        modes = ent_state.attributes.get("fan_modes", None)
                        curr_mode = ent_state.attributes.get("fan_mode", None)
                        new_mode = adjust(
                            curr_mode, mode_adj, None, None, OPTION_LIST=modes
                        )  # option
                        if new_mode is None:
                            # TODO: more informative messages for other errors (mode list, current mode)
                            transfer_err_msg = "Bad fan_mode adjustment: <{}>".format(
                                mode_adj
                            )
                        else:
                            service_data = {
                                "entity_id": entity_id,
                                "fan_mode": new_mode,
                            }
                    except ValueError:
                        transfer_err_msg = "Bad fan_mode: <{}>".format(mode_adj)
                # SWING mode
                elif act == "sm":
                    service = "set_swing_mode"
                    try:
                        modes = ent_state.attributes.get("swing_modes", None)
                        curr_mode = ent_state.attributes.get("swing_mode", None)
                        new_mode = adjust(
                            curr_mode, mode_adj, None, None, OPTION_LIST=modes
                        )  # option
                        if new_mode is None:
                            # TODO: more informative messages for other errors (mode list, current mode)
                            transfer_err_msg = "Bad swing_mode adjustment: <{}>".format(
                                mode_adj
                            )
                        else:
                            service_data = {
                                "entity_id": entity_id,
                                "swing_mode": new_mode,
                            }
                    except ValueError:
                        transfer_err_msg = "Bad swing_mode: <{}>".format(mode_adj)
                # AUXillary heat
                # Refer to this screenshot link: https://community.home-assistant.io/t/heater-automation/150176/10
                elif act == "aux":
                    service = "set_aux_heat"
                    if x_ == "1":
                        new_val = "true"
                    elif x_ == "0":
                        new_val = "false"
                    else:
                        # toggle (if x_ is "-1" or other)
                        curr_val = ent_state.attributes.get("aux_heat", "off")
                        new_val = "false" if curr_val == "on" else "true"
                    service_data = {"entity_id": entity_id, "aux_heat": new_val}
                # TEMPERATURE (4 options for single set points or range bounds)
                # TODO: Detect oF vs oC for all temperatures and adapt default ranges to match (e.g., t > 40 => oF)
                elif act in ["tmp", "tlo", "thi", "tauto"]:
                    service = "set_temperature"
                    try:
                        t_set = ent_state.attributes.get("temperature", None)
                        t_range_lo = ent_state.attributes.get(
                            "target_temperature_low", None
                        )
                        t_range_hi = ent_state.attributes.get(
                            "target_temperature_high", None
                        )
                        if act == "tauto":
                            # Simple rules to figure out which is the most likely adjustment required
                            action = ent_state.attributes.get("hvac_action", None)
                            if t_range_lo is None:
                                t_type = "tmp"
                            elif state == "heat" or action == "heating":
                                t_type = "tlo"  # to adjust heating, alter the bottom point in the range
                            else:
                                t_type = "thi"
                        else:
                            t_type = act
                        # Apply the required type of temperature adjustment
                        if t_type == "tmp":
                            curr_val = t_set
                            attr = "temperature"
                        elif t_type == "tlo":
                            curr_val = t_range_lo
                            attr = "target_temperature_low"
                        elif t_type == "thi":
                            curr_val = t_range_hi
                            attr = "target_temperature_high"
                        # 7 & 35 are documented HA defaults
                        min_val = ent_state.attributes.get("min_temp", 7)
                        max_val = ent_state.attributes.get("max_temp", 35)
                        new_val = adjust(
                            curr_val, x_, min_val, max_val, AS_INT=True
                        )  # int
                        if new_val is None:
                            transfer_err_msg = (
                                "Bad temperature adjustment: <{}>".format(x_)
                            )
                        else:
                            service_data = {"entity_id": entity_id, attr: new_val}
                    except:
                        transfer_err_msg = (
                            "Error with temperature adjustment: <{}>".format(x_)
                        )
                # HUMIDITY
                elif act == "hum":
                    service = "set_humidity"
                    try:
                        curr_val = ent_state.attributes.get("humidity", None)
                        min_val = ent_state.attributes.get(
                            "min_humidity", 30
                        )  # 30 & 99 are documented HA defaults
                        max_val = ent_state.attributes.get("max_humidity", 99)
                        new_val = adjust(
                            curr_val, x_, min_val, max_val, AS_INT=True
                        )  # int
                        if new_val is None:
                            # TODO: more accurate err_msgs for other types of errors
                            transfer_err_msg = "Bad humidity adjustment: <{}>".format(
                                x_
                            )
                        else:
                            service_data = {"entity_id": entity_id, "humidity": new_val}
                    except:
                        transfer_err_msg = (
                            "Error with humidity adjustment: <{}>".format(x_)
                        )
                # End of  valid act codes
                else:
                    transfer_err_msg = "The specified ACTION CODE is not valid."
            except:
                transfer_err_msg = "The specified ARGs are not of the valid type(s)."
        else:
            transfer_err_msg = "Wrong NUMBER of items in arguments list."
        if transfer_err_msg:
            raise ValueError(transfer_err_msg)
        if not skip_service_call:
            # make the requested service call (with the service & service_data set above)
            try:
                hass.services.call(domain, service, service_data, False)
            except:  # need HASS API docs to be explicit about the exception to catch here
                raise ValueError(
                    "Failed HASS service call {}.{}.".format(domain, service)
                )
    except ValueError as exptn:
        err_msg = (
            "{}\nNextion Handler failed within ACTION function:\n<{}> <{}>.".format(
                exptn, "cl", "> <".join(args_list)
            )
        )
        logger.warning("nextion_handler.py " + err_msg)
        raise ValueError(err_msg)
    return True
    # --- cl() ---


def cv(args_list):
    """mp act E (arg1) (call action/'service' with code 'act' for cover E).
    Action/Service options:
        (turn_on, turn_off, toggle: use generic ton, tof, tgl instead)
        cv open E (open cover E)
        cv close E (close cover E)
        cv stop E (stop cover E)
        cv tgl_t E (toggle tilt for cover E)
        cv open_t E (open tilt for cover E)
        cv close_t E (close tilt for cover E)
        cv stop_t E (stop tilt for cover E)
        cv pos E x (set cover E to postion x (0..100))
        cv pos_t E x (set cover E titl position to x (0..100))
    """
    # use generic tgl() to toggle position
    prefix = "cover."
    domain = "cover"
    service = None  # assigned based on 'act' code
    transfer_err_msg = ""
    skip_service_call = False  # give 'act' processing below a way to skip if required

    try:
        # set the service & service_data for the hass.service call
        if len(args_list) == 2:
            # services with NO arguements (other than entity_id)
            act, e = args_list
            entity_id = get_entity_id_state(e, domain_prefix=prefix)[0]
            service_data = {
                "entity_id": entity_id
            }  # the same for all services below (that have no other arguements)
            if act == "open":
                service = "open_cover"
            elif act == "close":
                service = "close_cover"
            elif act == "stop":
                service = "stop_cover"
            elif act == "tgl_t":
                service = "toggle_tilt"
            elif act == "open_t":
                service = "open_cover_tilt"
            elif act == "close_t":
                service = "close_cover_tilt"
            elif act == "stop_t":
                service = "stop_cover_tilt"
            # End of  valid act codes
            else:
                transfer_err_msg = "The specified ACTION CODE is not valid."
        elif len(args_list) == 3:
            act, e, x_ = args_list
            entity_id, ent_state, state = get_entity_id_state(e, domain_prefix=prefix)
            try:
                if act == "pos":
                    service = "set_cover_position"
                    #! Are docs incorrect or are do different devices return different attributes?
                    curr_pos = ent_state.attributes.get(
                        "current_position", None
                    )  #! zigomatic test
                    if curr_pos is None:
                        curr_pos = ent_state.attributes.get(
                            "current_cover_position", 0
                        )  #! fallback (HA Dev Docs)
                    new_pos = adjust(curr_pos, x_, 0, 100, AS_INT=True)
                    service_data = {"entity_id": entity_id, "position": new_pos}
                elif act == "pos_t":
                    service = "set_cover_tilt_position"
                    #! Are docs incorrect or are do different devices return different attributes?
                    curr_pos = ent_state.attributes.get("cover_tilt_position", None)
                    if curr_pos is None:
                        curr_pos = ent_state.attributes.get(
                            "current_cover_tilt_position", None
                        )
                    new_pos = adjust(curr_pos, x_, 0, 100, AS_INT=True)
                    service_data = {"entity_id": entity_id, "tilt_position": new_pos}
                # End of  valid act codes
                else:
                    transfer_err_msg = "The specified ACTION CODE is not valid."
            except:
                transfer_err_msg = "The specified ARGs are not of the valid type(s)."
        else:
            transfer_err_msg = "Wrong NUMBER of items in arguments list."
        if transfer_err_msg:
            raise ValueError(transfer_err_msg)
        if not skip_service_call:
            # make the requested service call (with the service & service_data set above)
            try:
                hass.services.call(domain, service, service_data, False)
            except:  # need HASS API docs to be explicit about the exception to catch here
                raise ValueError(
                    "Failed HASS service call {}.{}.".format(domain, service)
                )
    except ValueError as exptn:
        err_msg = (
            "{}\nNextion Handler failed within ACTION function:\n<{}> <{}>.".format(
                exptn, "cv", "> <".join(args_list)
            )
        )
        logger.warning("nextion_handler.py " + err_msg)
        raise ValueError(err_msg)
    return True
    # --- cv() ---


# *_________________
# *  Info Actions


def say(args_list):
    """say E string (Play TTS of message string msg to media player E)
    Allow spaces in 'string' by reconstructing args_list items that were split on spaces before"""
    prefix = "media_player."
    domain = "tts"
    service = "google_translate_say"
    try:
        if len(args_list) > 1:
            e = args_list[0]
            # reconstruct string if it was split by on spaces before
            string = " ".join(args_list[1:])
            entity_id = get_entity_id_state(e, domain_prefix=prefix)[0]
            service_data = {"entity_id": entity_id, "message": string}
            try:
                hass.services.call(domain, service, service_data, False)
            except:  # need HASS API docs to be explicit about the exception to catch here
                raise ValueError(
                    "Failed HASS service call {}.{}.".format(domain, service)
                )
        else:
            raise ValueError("Wrong number of items in arguments list.")
    except ValueError as exptn:
        err_msg = (
            "{}\nNextion Handler failed within ACTION function:\n<{}> <{}>.".format(
                exptn, "say", "> <".join(args_list)
            )
        )
        logger.warning("nextion_handler.py " + err_msg)
        raise ValueError(err_msg)
    return True


def ntf(args_list):
    """ntf title|message (Create a Persistent Notification with title & message strings in HA).
    Allow spaces in 'string' by reconstructing args_list items that were split on spaces before."""
    # prefix = 'persistent_notification.'
    domain = "persistent_notification"
    service = "create"
    try:
        if args_list:
            # reconstruct string if it was split on spaces before
            string = " ".join(args_list)
            tmp = string.split("|")  # split title from message on '|'
            if len(tmp) < 2:
                # No title provided
                title = "Nextion Alert"
                message = string
            else:
                title = tmp[0]
                message = "|".join(tmp[1:])
            hass.services.call(
                "persistent_notification",
                "create",
                {"title": title, "message": message, "notification_id": "nx_notify"},
                False,
            )
        else:
            raise ValueError("Wrong number of items in arguments list.")
    except ValueError as exptn:
        err_msg = (
            "{}\nNextion Handler failed within ACTION function:\n<{}> <{}>.".format(
                exptn, "ntf", "> <".join(args_list)
            )
        )
        logger.warning("nextion_handler.py " + err_msg)
        raise ValueError(err_msg)
    return True


def ntfx(args_list):
    """ntfx n (Dismiss the nth (index 0..) Persistent Notification in HA)."""
    # prefix = 'persistent_notification.'
    domain = "persistent_notification"
    service = "dismiss"
    try:
        if len(args_list) == 1:
            try:
                n = int(args_list[0])
            except:
                raise ValueError("Value is not an integer.")
            # Get notification list, count & item n
            try:
                ntf_list = hass.states.entity_ids("persistent_notification")
                ntf_count = len(ntf_list)
                n = n % ntf_count  # keep index in valid range for list
                entity_id = ntf_list[n]
                ntf_id = entity_id.split(".", 1)[-1]
            except:  # need HASS API docs to be explicit about the exception to catch here
                raise ValueError(
                    "Failed HASS service call {}.{}.".format(domain, service)
                )
            service_data = {"notification_id": ntf_id}
            try:
                hass.services.call(domain, service, service_data, False)
            except:  # need HASS API docs to be explicit about the exception to catch here
                raise ValueError(
                    "Failed HASS service call {}.{}.".format(domain, service)
                )
        else:
            raise ValueError("Wrong number of items in arguments list.")
    except ValueError as exptn:
        err_msg = "{}\nNextion Handler failed within SET function:\n<{}> <{}>.".format(
            exptn, "ntfx", "> <".join(args_list)
        )
        logger.warning("nextion_handler.py " + err_msg)
        raise ValueError(err_msg)
    return True


# *******************
# * CONTROL FUNCTIONS - controlling looping and sequencing in this script (and the combined interactions with Nx)
# *******************


def sub(args_list):
    """sub Nx (x) (`click Nx,x` the Nextion (hidden) hotspot)
    Executes a Nx 'subroutine'.
    Default x is 1 (click press); x = 0 triggers click release event.
    """
    # no entity or prefix
    try:
        num_args = len(args_list)
        if num_args == 1:
            # click (set to 1) a subroutine hotspot: click SEND_ACTIONS,1
            nx_sub = args_list[0]
            click_str = ",1"  # default (click press event)
        elif num_args == 2:
            # click (set to 1) a subroutine hotspot: click SEND_ACTIONS,1
            nx_sub, x_ = args_list
            if x_ == "0":
                click_str = ",0"  # click release event
            else:
                click_str = ",1"
        else:
            raise ValueError("Wrong number of items in arguments list.")
        nx_cmd_str = "click " + nx_sub + click_str
        send_nx_cmd(nx_cmd_str)
    except ValueError as exptn:
        err_msg = (
            "{}\nNextion Handler failed within CONTROL function:\n<{}> <{}>.".format(
                exptn, "sub", "> <".join(args_list)
            )
        )
        logger.warning("nextion_handler.py " + err_msg)
        raise ValueError(err_msg)
    return True


def gact(args_list):
    """gact e gest_type gest_cnt
    (Perform gesture action, based on gest_type and gest_cnt, on entity 'e'.)
    Wrapper for wdact(), making Widget actions callable from custom HMI code.
    """
    # Gesture types: ◐◑◉◎ ▶◀▼▲
    # ◐91, ◑95: short press (LHS, RHS)
    # ◉92, ◉96: long press
    # ◎93, ◎97: very long press
    # ▶81, ◀82: horizontal swipes
    # ▼83, ▲84: vertical swipes
    # Parse incoming agruments
    if len(args_list) == 3:
        try:
            e, gest_type_, gest_cnt_ = args_list
            entity_id, ent_state, state = get_entity_id_state(e)
            ent_domain = entity_id.split(".")[0]
            (wd_dmn, wd_icon) = DOMAINS_DICT.get(ent_domain, (2, DEFAULT_ICON))
            wdact([e, wd_dmn, gest_type_, gest_cnt_])
        except:
            err_msg = "{}\nNextion Handler, problem parsing arguments in ACTION function:\n<{}> <{}>.".format(
                exptn, "gact", "> <".join(args_list)
            )
            logger.warning("nextion_handler.py " + err_msg)
            raise ValueError(err_msg)
    else:
        err_msg = "Nextion Handler, wrong number of arguments in ACTION function:\n<{}> <{}>.".format(
            "gdact", "> <".join(args_list)
        )
        logger.warning("nextion_handler.py " + err_msg)
        raise ValueError(err_msg)
    return True


def wdact(args_list):
    """wdact e wd_dmn gest_type gest_cnt
    (Assign an action to entity 'e' based on its domain code 'wd_dmn', and the
    type (gest_type) and duration (gest_cnt) of the Nextion gesture.)
    """
    # Parse incoming agruments
    if len(args_list) == 4:
        try:
            e = args_list[0]
            wd_dmn, gest_type, gest_cnt = [int(i) for i in args_list[1:4]]
            # e = '@{}'.format(wd_num)  # widget '@' index for entity_id
            # * Entities with NO interaction  #! These ~should~ be caught & excluded in the Nextion HMI
            if (wd_dmn & ALL_INTERACTIONS_MASK) == 0:
                # Entity has no (supported) Widget actions
                return False  #! Exit WITHOUT performing any action (service call)
            entity_id, ent_state, state = get_entity_id_state(e)
            e = entity_id  # replace any alias/shorthand 'e' with actual entity_id
            domain_num = wd_dmn & DOMAIN_NUM_MASK
        except ValueError as exptn:
            err_msg = "{}\nNextion Handler, problem parsing arguments in WIDGET function:\n<{}> <{}>.".format(
                exptn, "wdact", "> <".join(args_list)
            )
            logger.warning("nextion_handler.py " + err_msg)
            # hass.services.call('persistent_notification', 'create', {'title': 'Nextion Handler Error!', 'message': err_msg, 'notification_id': 'nx_handler_error_set' }, False)
            raise ValueError(err_msg)
    else:
        err_msg = "Nextion Handler, wrong number of arguments in WIDGET function:\n<{}> <{}>.".format(
            "wdact", "> <".join(args_list)
        )
        logger.warning("nextion_handler.py " + err_msg)
        # hass.services.call('persistent_notification', 'create', {'title': 'Nextion Handler Error!', 'message': err_msg, 'notification_id': 'nx_handler_error_set' }, False)
        raise ValueError(err_msg)
    # * toggles (ALL entities capable of toggling - they may support additional interactions, handled below)
    if gest_type == 91 and (wd_dmn & DIRECT_TOGGLE_MASK):  # Top Left 'Icon' quadrant
        tgl([e])
    # * toggle ONLY cards: Both sides: toggle/tof/ton
    # The ONLY interaction these entities are capable of is TOGGLING (incl. separate ON & OFF)
    elif (wd_dmn & ALL_INTERACTIONS_MASK) == DIRECT_TOGGLE_MASK:
        # 91 ◐ already toggles with DIRECT_TOGGLE_MASK
        if gest_type == 95:  # ◑ short press RHS
            tgl([e])
        elif gest_type in [92, 96]:  # ◉ long press
            tof([e])
        elif gest_type in [93, 97]:  # ◎ vlong press
            ton([e])
    # * light
    elif domain_num == 18:
        # 91 ◐ already toggles with DIRECT_TOGGLE_MASK
        if gest_type == 92:  # ◉ long press LHS
            tof([e])
        elif gest_type == 93:  # ◎ vlong press LHS
            ton([e])
        # gest_type == 95 ◑ Nextion Popup page
        elif gest_type == 96:  # ◉ long press RHS
            lt(["wt", e])
        elif gest_type == 81:  # -> ▶ brightness gsetp=20
            adjustment = "+{}".format(20 * gest_cnt)
            lt(["brt", e, adjustment])
        elif gest_type == 82:  # <- ◀
            adjustment = "-{}".format(20 * gest_cnt)
            lt(["brt", e, adjustment])
        elif gest_type == 83:  # v ▼ colortemp/hue gstepv=20
            adjustment = "-{}".format(20 * gest_cnt)
            lt(["hct", e, adjustment])
        elif gest_type == 84:  # ^ ▲
            adjustment = "+{}".format(20 * gest_cnt)
            lt(["hct", e, adjustment])
    # * media_player
    elif domain_num == 20:
        # 91 ◐ already toggles with DIRECT_TOGGLE_MASK
        if gest_type == 92:  # ◉ toggle play-pause
            mp(["pp", e])
        elif gest_type == 93:  # ◎ source back 1 step
            mp(["src", e, "-1"])
        # gest_type == 95 ◑ Nextion Popup page
        elif gest_type == 96:  # ◉ toggle mute
            mp(["mut", e, "-1"])
        elif gest_type == 97:  # ◎ source forward 1 step
            mp(["src", e, "1"])
        elif gest_type == 81:  # -> ▶ track (x repeats)
            for i in range(gest_cnt):
                mp(["nxt", e])  # next track
        elif gest_type == 82:  # <- ◀
            for i in range(gest_cnt):
                mp(["prv", e])  # previous track
        elif gest_type == 83:  # v ▼ volume gsetepv=5%
            adjustment = "-{}".format(0.05 * gest_cnt)
            mp(["vol", e, adjustment])  # step volume up
            # for i in range(gest_cnt):
            #     mp(['v-', e]) # step volume up
        elif gest_type == 84:  # ^ ▲
            adjustment = "+{}".format(0.05 * gest_cnt)
            mp(["vol", e, adjustment])  # step volume down
            # for i in range(gest_cnt):
            #     mp(['v+', e]) # step volume down
    # * alarm_control_panel
    #! needs testing on physical device
    # TODO: possible future pop-up card will use short tap TR (gest_type == 95)
    # TODO: Does not support alarm codes (Can secrets be passed to Py scripts?)
    # TODO: Possibly add a 'setting:' dictionary in future for specifying additional info.
    elif domain_num == 1:
        service = None
        if gest_type == 91:  # ◐ short press LHS
            service = "alarm_arm_night"
        elif gest_type == 92:  # ◉ long press LHS
            service = "alarm_arm_home"
        elif gest_type == 93:  # ◎ vlong press LHS
            service = "alarm_disarm"
        elif gest_type == 95:  # ◑ short press RHS
            service = "alarm_arm_away"
        elif gest_type == 96:  # ◉ long press RHS
            service = "alarm_arm_vacation"
        elif gest_type == 97:  # ◎ vlong press RHS
            service = "alarm_disarm"
        if service:
            hass.services.call(
                "alarm_control_panel", service, {"entity_id": entity_id}, False
            )
    # * automation
    elif domain_num == 2:
        service = None
        if gest_type in [91, 95]:  # ◐◑ short press LHS & RHS
            service = "toggle"
        elif gest_type in [92, 96]:  # ◉◎ long press LHS & RHS
            service = "trigger"
        if service:
            hass.services.call("automation", service, {"entity_id": entity_id}, False)
    # * button
    elif domain_num == 4:
        if gest_type in [91, 95]:
            hass.services.call("button", "press", {"entity_id": entity_id}, False)
    # * climate
    # G.tACT_LIST.txt="Toggle|Cool|Auto|Popup Control|Heat|Heat-Cool|Humidity% +|Humidity% -|Temp° -|Temp° +"
    elif domain_num == 7:
        if gest_type == 91:  # ◐ require special toggle
            cl(["tgl", e])
        elif gest_type == 92:  # ◉ long press LHS
            cl(["hm", e, "cool"])
        elif gest_type == 93:  # ◎ vlong press RHS
            cl(["hm", e, "auto"])
        # gest_type == 95 ◑ Nextion Popup page
        elif gest_type == 96:  # ◉ long press RHS
            cl(["hm", e, "heat"])
        elif gest_type == 97:  # ◎ vlong press RHS
            cl(["hm", e, "heat_cool"])
        elif gest_type == 81:  # -> ▶ humidity gstep=5
            adjustment = "+{}".format(5 * gest_cnt)
            cl(["hum", e, adjustment])
        elif gest_type == 82:  # <- ◀
            adjustment = "-{}".format(5 * gest_cnt)
            cl(["hum", e, adjustment])
        elif gest_type == 83:  # v ▼ temperature gsetpv=1
            adjustment = "-{}".format(gest_cnt)
            cl(
                ["tauto", e, adjustment]
            )  # auto guestimate which temp set point to adjust
        elif gest_type == 84:  # ^ ▲
            adjustment = "+{}".format(gest_cnt)
            cl(["tauto", e, adjustment])
    # * cover
    #  position of cover: 0 means closed and 100 is fully open.
    elif domain_num == 8:
        adjustment = None
        service = None
        attr = None
        # 91 ◐ already toggles with DIRECT_TOGGLE_MASK
        if gest_type == 92:  # ◉ long press LHS
            # service = 'stop_cover'
            cv(["stop", e])
        elif gest_type == 93:  # ◎ vlong press RHS
            # service = 'open_cover'
            cv(["open", e])
        elif gest_type == 95:  # ◑ short press RHS
            # service = 'toggle_tilt'
            cv(["tgl_t", e])
        elif gest_type == 96:  # ◉ long press RHS
            # service = 'stop_cover_tilt'
            cv(["stop_t", e])
        elif gest_type == 97:  # ◎ vlong press RHS
            # service = 'open_cover_tilt'
            cv(["open_t", e])
        elif gest_type == 81:  # -> ▶ tilt gstep=20
            adjustment = "+{}".format(20 * gest_cnt)
            # service = 'set_cover_tilt_position'
            cv(["pos_t", e, adjustment])
        elif gest_type == 82:  # <- ◀
            adjustment = "-{}".format(20 * gest_cnt)
            # service = 'set_cover_tilt_position'
            cv(["pos_t", e, adjustment])
        elif gest_type == 83:  # v ▼ position gstepv=10
            # CHANGED so that Dragging down CLOSES cover (i.e. DECREASE 'current_positon' %)
            adjustment = "-{}".format(10 * gest_cnt)  # close by reducing the %open
            # service = 'set_cover_position'
            cv(["pos", e, adjustment])
        elif gest_type == 84:  # ^ ▲
            adjustment = "+{}".format(10 * gest_cnt)  # open by increasing the %open
            # service = 'set_cover_position'
            cv(["pos", e, adjustment])
    # * fan
    #! needs testing
    elif domain_num == 10:
        service = None
        data = None
        # 91 ◐ already toggles with DIRECT_TOGGLE_MASK
        if gest_type == 92:  # ◉ long press LHS
            service = "oscillate"
            data = True  #! check actual True/False or as text?? (True at: https://www.home-assistant.io/integrations/fan/)
            hass.services.call(
                "fan", service, {"entity_id": entity_id, "oscillating": data}, False
            )
        elif gest_type == 93:  # ◎ vlong press LHS
            service = "oscillate"
            data = False
            hass.services.call(
                "fan", service, {"entity_id": entity_id, "oscillating": data}, False
            )
        # gest_type == 95 ◑ Nextion Popup page (placeholder for future)
        elif gest_type == 96:  # ◉ long press RHS
            service = "set_direction"
            data = "forward"
            hass.services.call(
                "fan", service, {"entity_id": entity_id, "direction": data}, False
            )
        elif gest_type == 97:  # ◎ vlong press RHS
            service = "set_direction"
            data = "reverse"
            hass.services.call(
                "fan", service, {"entity_id": entity_id, "direction": data}, False
            )
        elif gest_type == 81:  # -> ▶ (x repeats)
            service = "increase_speed"
            for i in gest_cnt:
                hass.services.call("fan", service, {"entity_id": entity_id}, False)
        elif gest_type == 82:  # <- ◀
            service = "decrease_speed"
            for i in gest_cnt:
                hass.services.call("fan", service, {"entity_id": entity_id}, False)
        # TODO: V (add precentage step controls - redundant?)
        elif gest_type == 83:  # v ▼  duplicate <--> for now
            service = "decrease_speed"
            for i in gest_cnt:
                hass.services.call("fan", service, {"entity_id": entity_id}, False)
        elif gest_type == 84:  # ^ ▲
            service = "increase_speed"
            for i in gest_cnt:
                hass.services.call("fan", service, {"entity_id": entity_id}, False)
    # * humidifier
    #! needs testing
    elif domain_num == 13:
        # 91 ◐ already toggles with DIRECT_TOGGLE_MASK
        if gest_type in [91, 95]:  # ◐◑ short press (LHS & RHS)
            tgl([e])
        elif gest_type in [92, 96]:  # ◉ long press
            tof([e])
        elif gest_type in [93, 97]:  # ◎ vlong press
            ton([e])
        elif gest_type == 81:  # -> ▶ humidity gstep=5
            adj = "+{}".format(5 * gest_cnt)
            service = "set_humidity"
            curr_h = ent_state.attributes.get("target_humidity", 0)
            hmin = ent_state.attributes.get("min_humidity", 0)
            hmax = ent_state.attributes.get("max_humidity", 100)
            new_h = adjust(curr_h, adj, int(hmin), int(hmax), AS_INT=True)
            service_data = {"entity_id": entity_id, "humidity": new_h}
            hass.services.call("humidifier", service, service_data, False)
        elif gest_type == 82:  # <- ◀
            adj = "-{}".format(5 * gest_cnt)
            service = "set_humidity"
            curr_h = ent_state.attributes.get("target_humidity", 0)
            hmin = ent_state.attributes.get("min_humidity", 0)
            hmax = ent_state.attributes.get("max_humidity", 100)
            new_h = adjust(curr_h, adj, int(hmin), int(hmax), AS_INT=True)
            service_data = {"entity_id": entity_id, "humidity": new_h}
            hass.services.call("humidifier", service, service_data, False)
        # elif gest_type == 83: #TODO v ▼ (add mode cycling?)
        #     adjustment = "+{}".format(gest_cnt)
        #     service = 'set_mode'
        # elif gest_type == 84:  # ^ ▲
        #     adjustment = "-{}".format(gest_cnt)
    # * input number
    elif domain_num == 16:
        adjustment = None
        # 91 ◐ already toggles with DIRECT_TOGGLE_MASK
        # gest_type == 95 ◑ Nextion Popup page (placeholder for future)
        if gest_type == 92:
            adjustment = "0%"  # ◉ long press LHS set to min
        elif gest_type == 96:
            adjustment = "100%"  # ◉ long press RHS set to max
        elif gest_type == 93:
            adjustment = "25%"  # ◎ vlong press LHS set to 25% (of range)
        elif gest_type == 97:
            adjustment = "75%"  # ◎ vlong press RHS set to 75% (of range)
        elif gest_type == 81:  # -> ▶ gsetp=10 (% of range)
            adjustment = "+{}%".format(10 * gest_cnt)
        elif gest_type == 82:  # <- ◀
            adjustment = "-{}%".format(10 * gest_cnt)
        elif gest_type == 83:  # v ▼ gestep=1 (% of range)
            adjustment = "-{}%".format(gest_cnt)
        elif gest_type == 84:  # ^ ▲
            adjustment = "+{}%".format(gest_cnt)
        if adjustment:
            inpn([entity_id, adjustment])
    # * input_select (17) AND select (26)
    elif domain_num in [17, 26]:
        adjustment = None
        # 91 ◐ already toggles with DIRECT_TOGGLE_MASK
        # gest_type == 95 ◑ Nextion Popup page (placeholder for future)
        if gest_type == 92:
            adjustment = "0"  # ◉ long press LHS set to first option
        elif gest_type == 96:
            adjustment = "--1"  # ◉ long press RHS set to last
        elif gest_type == 81:  # -> ▶ cycle gstep=1
            adjustment = "+{}".format(gest_cnt)  # cycle list
        elif gest_type == 82:  # <- ◀
            adjustment = "-{}".format(gest_cnt)  # cycle list
        elif gest_type == 83:  # v ▼ direct pick gstepv=1
            adjustment = "{}".format(gest_cnt)  # direct pick
        elif gest_type == 84:  # ^ ▲
            adjustment = "--{}".format(gest_cnt - 1)  # direct pick (from bottom)
        if adjustment:
            if domain_num == 17:  # input_select
                inps([entity_id, adjustment])
            else:  # select
                sel([entity_id, adjustment])
    # * lock
    #! needs testing
    elif domain_num == 19:
        service = None
        data = None
        if gest_type in [91, 95]:  # ◐◑ short press (LHS & RHS)
            service = "lock"
        elif gest_type in [92, 96]:  # ◉ long press
            service = "unlock"
        elif gest_type in [93, 97]:  # ◎ vlong press
            service = "open"
        if service:
            hass.services.call("lock", service, {"entity_id": entity_id}, False)
    # * select (26) - included with input_select (17)
    # * scene
    elif domain_num == 24:
        # both taps
        if gest_type in [91, 95]:  # ◐◑ short press (LHS & RHS)
            hass.services.call("scene", "turn_on", {"entity_id": entity_id}, False)
    # #* script (25) - ALREADY part of 'ONLY TOGGLES' group above
    # #* switch (30) - ALREADY part of 'ONLY TOGGLES' group above
    # * timer
    elif domain_num == 31:
        service = None
        if gest_type in [91, 95]:  # ◐◑ short press (LHS & RHS)
            service = "start"
        elif gest_type in [92, 96]:  # ◉ long press
            service = "pause"
        elif gest_type == 93:  # ◎ LHS vlong press
            service = "cancel"
        elif gest_type == 97:  # ◎ RHS vlong press
            service = "finish"
        if service:
            hass.services.call("timer", service, {"entity_id": entity_id}, False)
    # * update
    elif domain_num == 32:
        service = None
        if gest_type == 91:  # ◐ short press LHS
            service = "install"
        elif gest_type == 95:  # ◑ short press RHS
            service = "skip"
        elif gest_type == 96:  # ◉ long press RHS
            service = "clear_skipped"
        if service:
            hass.services.call("update", service, {"entity_id": entity_id}, False)
    # * vacuum - too many brand-specific services & sensor values to do much more generically
    elif domain_num == 33:
        l_service = None
        if gest_type == 91:  # ◐ short press LHS
            if state == "cleaning":
                # '.turn_on' For the Xiaomi Vacuum, Roomba, and Neato use '.start' instead.
                l_service = ["stop", "turn_off"]
            else:
                l_service = ["start", "turn_on"]
        elif gest_type == 92:  # ◉ long press LHS
            l_service = ["return_to_base"]
        elif gest_type == 95:  # ◑ short press RHS
            l_service = ["locate"]
            # l_service = ['stop']
        elif gest_type == 96:  # ◉ long press RHS
            l_service = ["clean_spot"]
        for service in l_service:
            hass.services.call("vacuum", service, {"entity_id": entity_id}, False)
    # * water heater
    #! needs testing
    elif domain_num == 34:
        service = ""
        service_data = ""
        # DOES NOT support on/off/toggle - toggle/on/off AWAY MODE instead
        if gest_type in [91, 95]:  # ◐◑ short press (LHS & RHS)  - away mode TOGGLE
            service = "set_away_mode"
            curr_m = ent_state.attributes.get("away_mode", False)
            new_val = not curr_m
            service_data = {"entity_id": entity_id, "away_mode": new_val}
        elif gest_type in [92, 96]:  # ◉ long press - away mode ON
            service = "set_away_mode"
            service_data = {"entity_id": entity_id, "away_mode": True}
        elif gest_type in [93, 97]:  # ◎ vlong press - away mode OFF
            service = "set_away_mode"
            service_data = {"entity_id": entity_id, "away_mode": False}
        elif gest_type in [83, 84]:  # v^ ▼▲ temperature gstepv=1
            # TODO: find a way of detecting farenheit, then change defaults for oF/oC
            # HA docs default range is 110F (40C) - 140F (60C)
            if gest_type == 83:  # v ▼
                adj = "-{}".format(gest_cnt)
            else:  # ^ ▲
                adj = "+{}".format(gest_cnt)
            service = "set_temperature"
            curr_t = ent_state.attributes.get("temperature", None)
            if curr_t is None:
                curr_t = ent_state.attributes.get("target_temp_low", 50)
            tmin = ent_state.attributes.get("min_temp", 40)
            tmax = ent_state.attributes.get("max_temp", 140)
            new_t = adjust(
                float(curr_t), adj, float(tmin), float(tmax), AS_INT=True
            )  # int
            service_data = {"entity_id": entity_id, "temperature": new_t}
        if service_data:
            hass.services.call("water_heater", service, service_data, False)
    # * end of entity types/domains
    # --- wdact() ---
    return True


#! Use at own risks - Python scripts are NOT a good place to put delays/control timing in HA multi-threaded environment
# def delay(args_list):
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


# *------------------------------------------------------------------------------
# * DICTIONARY OF FUNCTIONS (translates NhCmd text to associated function above)
# *------------------------------------------------------------------------------
#! Add any new custom functions to this dictionary
# HA won't allow locals() in script to automtically build dictionary of our functions - have to do it manually instead
FUNC_DICT = {
    # * SET functions
    "sett": sett,
    "setn": setn,
    "setb": setb,
    "setlt": setlt,
    "setntf": setntf,
    "setdt": setdt,
    "setmp": setmp,
    "setcl": setcl,
    "setwd": setwd,
    "setsys": setsys,
    # * ACTION functions
    # Actions where entity_id class needs to be provided (but $alias preferred)
    "tgl": tgl,
    "ton": ton,
    "tof": tof,
    # Actions where entity class can be assumed (but $alias preferred)
    "inps": inps,
    "inpb": inpb,
    "inpn": inpn,
    "scn": scn,
    "scpt": scpt,
    "lt": lt,
    "mp": mp,
    "cl": cl,
    # Info Actions
    "say": say,
    "ntf": ntf,
    "ntfx": ntfx,
    # Widget UI
    "wdact": wdact,
    # * CONTROL functions
    "sub": sub,
}


# *------------------------------------------------------------------------------
# * MAIN SCRIPT
# *------------------------------------------------------------------------------

# *_________________________________
# * Initialse loop/control variables
WIDGETS_LIST = []
ENTITY_ALIASES = {}

nxh_call_type = None  # in [ACT, SET, SLEEP] - categorise the type of call to this script (to be expanded in future)
continue_script = True
is_ha_act_string = True  # first string in list is HA_Action (special case, following user interaction, indicated by positive trig_val)
unparsed_strings = []
bad_cmds = []
rpt_cmds = []
good_cmds = []
repeat_num = 0  # this value (& delay below) can be modified during the loop by NhCmds rpt() and noupd()
repeat_delay = (
    -99
)  # (secs) If HA_Act includes a rst command, its settings will take precedence over defaults in HA_Set1..
command_strings = []
unparsed_strings = []

# * variables used in Exception messages
trig_str = None
trig_ent = None
trig_val = None
s = None
nh_cmd_str = "unassigned"
nh_cmd_func = None
args_list = []

KNOWN_BAD_STATES = INVALID_STATES  # ['unknown', 'unavailable', 'None']  # entity states returned by HA that often trigger trivial errors


# *________________________
# * Parse Script Arguements passed to this py script by calling HA automation/service
try:

    # * Get and parse the Nextion Instruction sender service
    try:
        NX_CMD_SERVICE = data.get("nx_cmd_service")
        # esphome_domain, nx_service = NX_CMD_SERVICE.split('.')
    except:
        continue_script = False
        raise ValueError(
            "Provided nx_cmd_service is not valid: <{}>".format(NX_CMD_SERVICE)
        )
    # * Get the value of the TRIGGER (that triggered this script and indicates the type of response required)
    try:
        trig_ent = data.get("trig_val")
        # trig_val = int(float(hass.states.get(trig_ent).state))  #! Python cannot convert the state of ESPhome's integer _default_ sensor format (string '-1.00') directly to int (Testing reducing ESPHome dp to 0 for this sensor?)
        trig_str = hass.states.get(trig_ent).state
        trig_val = int(
            trig_str
        )  # ESPHome now configured to return 0 decimal place formatted number
    except:
        if trig_str in ["unavailable", None, ""]:
            trig_val = 0  # Deal with common Nextion startup issue
        else:
            # TODO: either test or remove this option
            # If it is not an entity, see if it is a directly specified int (to allow 'forced' automation overrides)
            try:
                trig_val = int(trig_ent)
            except:
                continue_script = False
                raise ValueError(
                    "Provided trig_val is neither a valid entity_id nor an integer: ent: <{}>, value: <{}>.".format(
                        trig_ent, trig_str
                    )
                )
    # * Get dictionary of aliases - key: value pairs of Nx $alias (WITHOUT $ prefix): Home Assistant entinty_id
    try:
        ENTITY_ALIASES = data.get("aliases", {})  # An empty alias dictionary is valid
    except:
        #! Exception is redundant - Widget configs need to be able to run WITHOUT any alias: list *********************************** (check)
        err_msg = "Aliases dictionary in automaltion YAML not valid."
        logger.warning("nextion_handler.py " + err_msg)
        continue_script = False
    # * Get list of PAGE Widgets (& their settings) from 'widgets:' YAML section
    try:
        WIDGETS_LIST = data.get("widgets", [])  # An empyt widget list is valid
    except:
        err_msg = 'Error trying to read "widgets:" list from YAML.'
        logger.warning("nextion_handler.py " + err_msg)
        raise ValueError(err_msg)
        continue_script = False
    # * Determine the type of triggered Nextion request (Action vs Update) and get the appropriate command_strings to process
    # command_strings should be a list of entities whose states are strings of comma- or \n- delimited NhCmds
    #   action_cmds: (POSITIVE trig_val, triggered by USER INTERACTION) is list of HA_Act entity_ids containg strings (a sequence of ACTION NhCmds)
    #   update_cmds: (NEGATIVE trig_val, Nx POLLING to refresh its data from HA) is a list of Ha_Set1.. entity_ids containing strings (a sequence of SET NhCmds)

    if trig_val > 0:
        # Positive TRIGGER Indicates new HA_Act needs to be processed (USER INTERACTIONS should be prioritised over polling in script flow)
        nxh_call_type = "ACT"
        try:
            command_strings = data.get("action_cmds")
        except:
            continue_script = False
            raise ValueError(
                "Provided list of action_cmds is not valid: {}.".format(command_strings)
            )
    elif trig_val < 0:
        # Negative TRIGGER Indicates a data update for page (non-interactive POLLING from Nx) - only process the HA_Set strings (skip the HA_Act that is first in the list)
        nxh_call_type = "SET"
        try:
            command_strings = data.get("update_cmds")
        except:
            continue_script = False
            raise ValueError(
                "Provided list of update_cmds is not valid: {}.".format(command_strings)
            )
    else:  # trig_val == 0:
        nxh_call_type = "SLEEP"
        # 0 indicates Nx has turned off interaction with HA (e.g. sleeping) - skip the intial state change to 0
        # << catch INTENTIONAL exception (NOT an error) and exit script
        continue_script = False
        raise ValueError("EXIT")
    # * Create a list of strings to be parsed into NhCmds (Action or Set) to be executed
    for string_ent in command_strings:
        s = ""
        try:
            s = hass.states.get(string_ent).state
        except:  # need HASS API docs to be explicit about the exception to catch here
            # Log error message, then continue with remaining 'good' cmd strings
            err_msg = (
                "An entity in the command_strings list is not valid:\n{}\n<{}>".format(
                    string_ent, s
                )
            )
            logger.warning("nextion_handler.py " + err_msg)
            hass.services.call(
                "persistent_notification",
                "create",
                {
                    "title": "Nextion Handler Error!",
                    "message": err_msg,
                    "notification_id": "nx_handler_error_main",
                },
                False,
            )
            # <<
            continue
        #
        # Clean up flotsam from ESPHome Nextion Custom output writing
        s = s.replace(
            "\x00", ""
        )  # remove the non-whitespace string terminaton character(\x00) that Nextion/ESPhome writes to the end of each string & causes parsing issues
        s = s.strip()  # strip BEFORE converting line-breaks to commas
        s = s.replace(
            "\r\n", ","
        )  # handle both commas and line-breaks (NextionEditor/Windows uses CR/LF) as delimeters (line breaks are more readable in Nextion (multi-line) text variables)
        # s = s.replace('\n', ',')  # handle both commas and \n as delimeters (\n is more readable in Nextion text variables)
        if s:
            unparsed_strings.extend([s])
except ValueError as exptn:  # <<< Mainly User errors requiring feedback for them to fix their YAML or command strings
    if str(exptn) == "EXIT":
        # << Exit script, don't continue with other stages
        continue_script = False
    else:
        err_msg = "{}\nNextion Handler failed trying to parse:\nnx_cmd_service: <{}>\ntrig_val: <{}>\ncommand_strings: <{}>\nunparsed_strings: <{}>.".format(
            exptn, NX_CMD_SERVICE, trig_val, command_strings, unparsed_strings
        )
        logger.warning("nextion_handler.py " + err_msg)
        # hass.services.call('persistent_notification', 'create', {'title': 'Nextion Handler Error!', 'message': err_msg, 'notification_id': 'nx_handler_error_main' }, False)
        continue_script = False
except Exception as exptn:  # <<< Unexpected errors, possible BUG
    err_msg = "{}\nNextion Handler EXCEPTION trying to parse:\nnx_cmd_service: <{}>\ntrig_val: <{}>\ncommand_strings: <{}>\nunparsed_strings: <{}>.".format(
        exptn, NX_CMD_SERVICE, trig_val, command_strings, unparsed_strings
    )
    logger.warning("nextion_handler.py " + err_msg)
    # hass.services.call('persistent_notification', 'create', {'title': 'Nextion Handler Error!', 'message': err_msg, 'notification_id': 'nx_handler_error_main' }, False)
    continue_script = False
# *_________________________
# * Process the command_list passing each in turn to specified function
# actions_still_to_process set above = True (CmdCnt > 0) False (CmdCnt < 0) (then apply below in building rpt_cmd[] list)
if continue_script and unparsed_strings:
    #! debug
    # if nxh_call_type == 'ACT':
    #         msg = 'Nextion Handler: ACTION Command Strings:\n{}'.format('\n--\n'.join(unparsed_strings))
    #         hass.services.call('persistent_notification', 'create', {'title': 'Nextion Handler Debug Info', 'message': msg, 'notification_id': 'nx_handler_cmdstr' }, False)
    try:
        for s in unparsed_strings:
            # pre processing to clean up strings was already done in building the list (now clean CSV strings)
            nh_cmd_str = ""
            for nh_cmd_str in s.split(","):
                nh_cmd_str = (
                    nh_cmd_str.strip()
                )  # need this BEFORE splitting ' ' (to avoid empty strings in list)
                try:
                    func_args = [i.strip() for i in nh_cmd_str.split(" ")]
                    func, args_list = (
                        func_args[0],
                        func_args[1:],
                    )  # func_args[] may be empty, which is OK for some NhCmds
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
                    if (
                        not str(nh_cmd_str) in KNOWN_BAD_STATES
                    ):  # frequent trivial errors
                        bad_cmds.extend([nh_cmd_str])
                        err_msg = "Provided NhCmd does not start with a function registered in FUNC_DICT: <{}>.".format(
                            nh_cmd_str
                        )
                        logger.warning("nextion_handler.py " + err_msg)
                        # raise ValueError(err_msg)
                    continue
                try:
                    nh_cmd_func(args_list)
                    # good_cmds.extend([nh_cmd_str])
                except ValueError as exptn:
                    if str(exptn) == "SKIP":
                        # Intentional exception to indicate NhCmd should be skipped and processing of next NhCmd should continue
                        continue
                    elif not str(nh_cmd_str) in KNOWN_BAD_STATES:
                        logger.warning(
                            "nextion_handler.py "
                            + "Skipped NhCmd (gave errors): <{}>.".format(nh_cmd_str)
                        )
                        bad_cmds.extend([nh_cmd_str])
                    continue  # skip bad command and continue to next in list
                #!dbg
                # good_cmds.extend([nh_cmd_str]) #! for debug - COMMENT OUT when done
        # Send subroutine to update Nextion display with refreshed data after a 'SET' update
        if nxh_call_type == "SET":
            if nh_cmd_func != "sub":  # skip if the last NhCmd was a Nx subroutine call
                sub([NX_UI_UPDATE])
    except Exception as exptn:  # <<< These exceptions are not expected (either corner cases or BUG in script)
        if str(command_strings) == "None" or not unparsed_strings:
            # skip logging errors for trivial anticipated issues (more efficient to catch these in exceptions than waste time testing for them)
            pass
        else:
            err_msg = "{}\nNextion Handler EXCEPTION - failed trying to call command:\n<{}>.".format(
                exptn, nh_cmd_str
            )
            logger.error("nextion_handler.py " + err_msg)
            # hass.services.call('persistent_notification', 'create', {'title': 'Nextion Handler BUG!?', 'message': err_msg, 'notification_id': 'nx_handler_error_main' }, False)
        continue_script = False
        repeat_num = 0
# *__________________________________________________________
# * Provide notification with list of NhCmds that gave errors for user to fix/debug in their Nextion HMI strings
if bad_cmds:
    err_msg = "Nextion Handler had problems with the following NhCmds:\n<{}>".format(
        ">\n<".join(bad_cmds)
    )
    hass.services.call(
        "persistent_notification",
        "create",
        {
            "title": "Nextion Handler completed with Errors!",
            "message": err_msg,
            "notification_id": "nx_handler_error_done",
        },
        False,
    )
if nxh_call_type == "ACT":
    if good_cmds:
        msg = "Nextion Handler successfully completed the following ACTIONS:\n<{}>\nTRIGGER:{}".format(
            ">\n<".join(good_cmds), trig_val
        )
        # logger.debug(msg)
        hass.services.call(
            "persistent_notification",
            "create",
            {
                "title": "Nextion Handler completed",
                "message": msg,
                "notification_id": "nx_handler_info_done",
            },
            False,
        )
