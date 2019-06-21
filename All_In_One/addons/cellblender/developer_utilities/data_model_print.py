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
This stand-alone Python program reads and prints a CellBlender data model.
This is mostly instructional for anyone writing data model interface code.
"""

file_name = "data_model.txt"

import pickle
import sys

def pickle_data_model ( dm ):
    return ( pickle.dumps(dm,protocol=0).decode('latin1') )

def unpickle_data_model ( dmp ):
    return ( pickle.loads ( dmp.encode('latin1') ) )


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


data_model_keys = set([])
def get_data_model_keys ( dm, key_prefix ):
    global data_model_keys
    if type(dm) == type({'a':1}): # dm is a dictionary
        for k,v in sorted(dm.items()):
            get_data_model_keys ( v, key_prefix + "['" + str(k) + "']" )
    elif type(dm) == type(['a',1]): # dm is a list
        i = 0
        for v in dm:
            #get_data_model_keys ( v, key_prefix + "[" + str(i) + "]" )
            get_data_model_keys ( v, key_prefix + "[" + "#" + "]" )
            i += 1
    #elif (type(dm) == type('a1')) or (type(dm) == type(u'a1')): # dm is a string
    #    print ( str(data_model_depth*"  ") + "\"" + str(dm) + "\"" )
    else: # dm is anything else
        dm_type = str(type(dm)).split("'")[1]
        data_model_keys.update ( [key_prefix + "   (" + dm_type + ")"] )
    return data_model_keys


if len(sys.argv) > 1:
    file_name = sys.argv[1]

f = open ( file_name, 'r' )

pickled_model = f.read()

data_model = unpickle_data_model ( pickled_model )

print ( "===== Data Model Keys =====" )

key_set = get_data_model_keys ( data_model, "" )

key_list = [k for k in key_set]
key_list.sort()

for s in key_list:
    print ( s )


print ( "===== Data Model =====" )
dump_data_model ( data_model )

