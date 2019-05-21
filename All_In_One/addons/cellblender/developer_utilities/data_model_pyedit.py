# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

"""
This stand-alone Python program supports
  reading, printing, editing, and saving
  a CellBlender data model. This is all
  done via an interactive Python session.
  All data model manipulation is done via
  python operations on the dictionary.
"""


import pickle
import sys

def pickle_data_model ( dm ):
    """ Return a pickle string containing a data model """
    return ( pickle.dumps(dm,protocol=0).decode('latin1') )

def unpickle_data_model ( dmp ):
    """ Return a data model from a pickle string """
    return ( pickle.loads ( dmp.encode('latin1') ) )

def read_data_model ( file_name ):
    """ Return a data model read from a named file """
    f = open ( file_name, 'r' )
    pickled_model = f.read()
    data_model = unpickle_data_model ( pickled_model )
    return data_model

def write_data_model ( dm, file_name ):
    """ Write a data model to a named file """
    f = open ( file_name, 'w' )
    status = f.write ( pickle_data_model(dm) )
    f.close()
    return status

def help():
    print ( "\n\nhelp():" )
    print ( "\n=======================================" )
    print ( "Available functions:" )
    print ( "  dm = read_data_model ( file_name ) - returns a data model dictionary" )
    print ( "  write_data_model ( dm, file_name ) - writes the data model (dm) to a file" )
    print ( "  dump_data_model ( data_model ) - prints the data_model" )
    print ( "The data model itself is a dictionary of dictionaries, lists, and data items" )
    print ( "Use Control-D to exit the interactive mode" )
    print ( "=======================================\n\n" )
    

data_model_depth = 0
def dump_data_model ( dm ):
    global data_model_depth
    data_model_depth += 1
    if type(dm) == type({'a':1}): # dm is a dictionary
        for k,v in sorted(dm.items()):
            print ( str(data_model_depth*"  ") + "Key = " + str(k) )
            dump_data_model ( v )
    elif type(dm) == type(['a',1]): # dm is a list
        i = 0
        for v in dm:
            print ( str(data_model_depth*"  ") + "Entry["+str(i)+"]" )
            dump_data_model ( v )
            i += 1
    elif (type(dm) == type('a1')) or (type(dm) == type(u'a1')): # dm is a string
        print ( str(data_model_depth*"  ") + "\"" + str(dm) + "\"" )
    else: # dm is anything else
        print ( str(data_model_depth*"  ") + str(dm) )
    data_model_depth += -1



if len(sys.argv) > 1:
    data_model = read_data_model ( sys.argv[1] )

# Print the help information
help()

# Drop into an interactive python session
__import__('code').interact(local={k: v for ns in (globals(), locals()) for k, v in ns.items()})

print ( "Done with \"data_model\"" )

