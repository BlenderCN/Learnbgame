"""
Name:    carinfo
Purpose: Reading parameters.txt files

Description:
Used to import entire cars and getting texture paths for models.

"""

if "bpy" in locals():
    import imp
    imp.reload(common)

import os
import bpy
from . import common

# Action name for error reporting
action_name = "reading parameters"


# Structure block name (used for the second "trans" value in the spinner block)
global block
block = None

def read_word(fd):
    """ Reads a word from the file (usually a keyword which is followed by a 
        value or a block) """
    word = ""

    ch = fd.read(1)

    if ch == "":
        common.queue_error(action_name, "End of file reached.")
        return None

    while is_space(ch) and ch != "":
        ch = fd.read(1)

    # Skips comments
    while ch == ";" and ch != "":
        ch = fd.read(1)

        # Checks for backwards compatible words
        if ch not in [")", "\n"]:
            ch = skip_line(fd)
        else:
            ch = fd.read(1)

    while not is_space(ch) and ch != "":
        word += ch
        ch = fd.read(1)

    return word


def read_model(fd):
    """ Reads the model index and path """
    index = read_int(fd)
    path = read_path(fd)

    return {index: path}


def read_int(fd):
    """ Reads a word and interprets it as an integer """
    integer = ""
    ch = fd.read(1)

    while is_space(ch):
        ch = fd.read(1)

    while not is_space(ch):
        integer += ch
        ch = fd.read(1)

    return int(integer)


def read_bool(fd):
    """ Reads a word and interprets it as a boolean """
    bool = ""
    ch = fd.read(1)

    while is_space(ch):
        ch = fd.read(1)

    while not is_space(ch):
        bool += ch
        ch = fd.read(1)

    if bool.lower() in ["true", "1", "yes"]:
        return True
    else:
        return False


def read_float(fd):
    """ Reads a word and interprets it as a float """
    flt = ""
    ch = fd.read(1)

    while is_space(ch):
        ch = fd.read(1)
        
    while not is_space(ch):
        flt += ch
        ch = fd.read(1)

    return float(flt)


def read_vector_float(fd):
    """ Reads three words and interprets them as a float vector """
    return (read_float(fd), read_float(fd), read_float(fd))


def read_quintuple_float(fd):
    """ Reads five words and interprets them as a float vector """
    return (
        read_float(fd), read_float(fd), read_float(fd), 
        read_float(fd), read_float(fd)
    )


def read_3x3_float(fd):
    """ Reads nine words and interprets them as a float vector """
    return (
        read_float(fd), read_float(fd), read_float(fd), 
        read_float(fd), read_float(fd), read_float(fd),
        read_float(fd), read_float(fd), read_float(fd)
    )

def read_vector_int(fd):
    """ Reads three words and interprets them as an int vector """
    return (read_int(fd), read_int(fd), read_int(fd))


def read_string(fd):
    """ Reads a word encased by " """
    string = ""
    ch = fd.read(1)

    # Finds the " and advances the the first letter of the string
    while not ch == "\"":
        ch = fd.read(1)
    ch = fd.read(1)
    
    # Adds characters to the string until " has been reached
    while not ch == "\"":
        string += ch
        ch = fd.read(1)
    ch = fd.read(1)

    return string


def read_path(fd):
    """ Reads a path and replaced the separators with the native one """
    path = read_string(fd)
    path = path.replace("\\", os.sep)
    path = path.replace("/", os.sep)
    path = path.lower()
    if path == "none":
        return None
    else:
        return path


def read_ambivalent(fd):
    """ A hack for the dispatcher: Two keywords are called 'trans' """
    global block

    if block is None:
        return read_int(fd)
    elif block == "spinner":
        return read_vector_float(fd)
    else:
        return None


""" Functions for reading sub-structures """


def read_number_list(fd):
    """ Reads a list of numbers, e.g. 0-3 or 1, 2, 3"""
    nlist = ""
    ch = fd.read(1)

    while ch != "{":
        nlist += ch
        ch = fd.read(1)

    nlist = nlist.strip()


    if "," in nlist:
        nlist = [int(x) for x in nlist.split(",")]
    elif "-" in nlist:
        nlist = [int(x) for x in nlist.split("-")]
        nlist = list(range(nlist[0], nlist[1]))
    else:
        nlist = [int(x) for x in nlist]

    return nlist

def read_struct(fd):
    """ Reads a regular structure block encased by {} """
    struct = {}
    # Skips to the first opening bracket
    ch = fd.read(1)
    while ch != "{":
        ch = fd.read(1)

    struct = process_words(fd)

    return struct


def read_struct_numbered(fd):
    """ Reads a structure block introduced 
        by a numbered list, encased by {} """
    struct = {}

    # Reads a number list, after this the fd is past the {
    nlist = read_number_list(fd)

    # Skips to the first opening bracket
   
    content = process_words(fd)

    for x in nlist:
        struct[x] = content

    return struct


def process_words(fd):
    """ Checks keywords and looks them up in the 
        dispatcher dict to read them """
    struct = {}
    word = ""
        
    while word not in ["}", None]:

        word = read_word(fd)
        
        if word is None:
            return struct

        word = word.lower()
        
        if word in dispatcher:

            try:
                val = dispatcher[word](fd)
            except Exception as e:
                val = None
                common.queue_error(
                    action_name,
                    "Could not read {}\n{}".format(word, e)
                )
            if isinstance(val, dict):
                global block
                block = word
                
            if isinstance(val, dict) and word in struct:
                struct[word].update(val)
            else:
                struct[word] = val

        else:
            continue
    
    return struct



""" Helper functions for processing files """

def skip_line(fd):
    ch = fd.read(1)
    while ch != "\n" and ch != '':
        ch = fd.read(1)
    ch = fd.read(1)
    return ch


def is_space(ch):
    return ch in [" ", "\t", "\n", ","]


""" Stores keywords and the functions their values have to be read with """

dispatcher = {
    # Car data and info
    "name":            read_string,
    "besttime":        read_bool,
    "selectable":      read_bool,
    "cpuselectable":   read_bool,
    "statistics":      read_bool,
    "class":           read_int,
    "rating":          read_int,
    "obtain":          read_int,
    "topend":          read_float,
    "acc":             read_float,
    "weight":          read_float,
    
    "model":           read_model,
    "tpage":           read_path,
    "tcarbox":         read_path,
    "tshadow":         read_path,
    "coll":            read_path,
    "shadowindex":     read_int,
    "shadowtable":     read_quintuple_float,
    "envrgb":          read_vector_int,

    "steerrate":       read_float,
    "steermod":        read_float,
    "enginerate":      read_float,
    "topspeed":        read_float,
    "maxrevs":         read_float,
    "downforcemod":    read_float,
    "com":             read_vector_float,
    "weapon":          read_vector_float,
    "flippable":       read_bool, 
    "flying":          read_bool,
    "clothfx":         read_bool,

    "body":            read_struct,
    "wheel":           read_struct_numbered,
    "spring":          read_struct_numbered,
    "pin":             read_struct_numbered,
    "axle":            read_struct_numbered,
    "spinner":         read_struct,
    "aerial":          read_struct,
    "ai":              read_struct,
    "camattached":     read_struct,

    # Misc./shared data
    "trans":           read_ambivalent,
    "modelnum":        read_int,
    "offset":          read_vector_float,
    "mass":            read_float,
    "grip":            read_float,
    "staticfriction":  read_float,
    "kineticfriction": read_float,
    
    # Body data
    "inertia":         read_3x3_float,
    "gravity":         read_float,
    "hardness":        read_float,
    "resistance":      read_float,
    "angres":          read_float,
    "resmod":          read_float,

    # Wheel data
    "offset1":         read_vector_float,
    "offset2":         read_vector_float,
    "ispresent":       read_bool,
    "ispowered":       read_bool,
    "isturnable":      read_bool,
    "steerratio":      read_float,
    "engineratio":     read_float,
    "radius":          read_float,
    "maxpos":          read_float,
    "skidwidth":       read_float,
    "toein":           read_float,
    "axlefriction":    read_float,

    # Spring data
    "length":          read_float,
    "stiffness":       read_float,
    "damping":         read_float,
    "restitution":     read_float,

    # Spinner data
    "axis":            read_float,
    "angvel":          read_float,

    # Aerial data
    "secmodelnum":     read_int,
    "topmodelnum":     read_int,
    "direction":       read_vector_float,

    # AI data
    "underthresh":     read_float,
    "underrage":       read_float,
    "underfront":      read_float,
    "underrear":       read_float,
    "undermax":        read_float,
    "overthresh":      read_float,
    "overrange":       read_float,
    "overmax":         read_float,
    "overaccthresh":   read_float,
    "overaccrange":    read_float,
    "pickupbias":      read_float,
    "blockbias":       read_float,
    "overtakebias":    read_float,
    "suspension":      read_float,
    "aggression":      read_float
}




def read_parameters(filepath):
    print("Reading {}...".format(filepath))
    with open(filepath) as fd:
        parameters = read_struct(fd)
        return parameters



# filepath = "/home/marv/.rvgl/online/cars/"
def test():
    for folder in os.listdir(filepath):
        print("Testing", folder)
        for f in os.listdir(os.path.join(filepath, folder)):
            if f == "parameters.txt":
                # with open(os.path.join(filepath, folder, f), "r") as fd:

                with open(os.path.join(filepath, folder, f)) as fd:
                    parameters = read_struct(fd)
                    print(len(parameters))

# test()