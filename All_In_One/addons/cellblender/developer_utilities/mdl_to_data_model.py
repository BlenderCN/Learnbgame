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
This stand-alone Python program reads from an MCell MDL file and
attempts to generate a CellBlender Data Model. This functionality
is being developed on an as-needed basis, so beware that full MDL
conversion may not be supported. Additionally, much of this code
may take advantage of certain MDL conventions to make the job a
bit easier. For example, some sections might assume that each MDL
statement is on a separate line.
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
    print ( "Requires 2 parameters: mdl_file_name data_model_file_name" )
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

def create_minimal_cube_data_model():
    dm = {}
    mcell = {}
    dm['mcell'] = mcell
    mcell['api_version'] = 0
    g = {}
    mcell['geometrical_objects'] = g
    obj_list = []
    g['object_list'] = obj_list
    obj = {}
    obj_list.append(obj)
    obj['name'] = "Cube"
    vl = []
    obj['vertex_list'] = vl
    vl.append ( [ 1.0,  1.0, -1.0]  )
    vl.append ( [ 1.0, -1.0, -1.0]  )
    vl.append ( [-1.0, -1.0, -1.0]  )
    vl.append ( [-1.0,  1.0, -1.0]  )
    vl.append ( [ 1.0,  1.0,  1.0]  )
    vl.append ( [ 1.0, -1.0,  1.0]  )
    vl.append ( [-1.0, -1.0,  1.0]  )
    vl.append ( [-1.0,  1.0,  1.0]  )
    ec = []
    obj['element_connections'] = ec
    ec.append ( [1,2,3] )
    ec.append ( [7,6,5] )
    ec.append ( [0,4,5] )
    ec.append ( [1,5,6] )
    ec.append ( [6,7,3] )
    ec.append ( [0,3,7] )
    ec.append ( [0,1,3] )
    ec.append ( [4,7,5] )
    ec.append ( [1,0,5] )
    ec.append ( [2,1,6] )
    ec.append ( [2,6,3] )
    ec.append ( [4,0,7] )
    sr = []
    obj['define_surface_regions'] = sr
    return dm

def create_new_data_model_template():
    dm = {}
    mcell = {}
    dm['mcell'] = mcell
    mcell['api_version'] = 0
    g = {}
    mcell['geometrical_objects'] = g
    obj_list = []
    g['object_list'] = obj_list
    return dm

def read_objects_from_mdl_file ( mdl_file_name, dm ):
    # Warning: This code may make some assumptions about the formatting of the MDL to simplify its work
    mcell = dm['mcell']
    g = mcell['geometrical_objects']
    obj_list = []
    g['object_list'] = obj_list

    f = open ( mdl_file_name, 'r' )
    bracket_depth = 0
    in_object = False
    in_object_bracket = False
    in_vertex_list = False
    in_vertex_list_bracket = False
    in_element_list = False
    in_element_list_bracket = False
    
    obj = None
    vl = None
    ec = None
    sr = None
    
    # Read each line of the file
    for line in f:
        # Keep track of bracket nesting depth
        if ('{' in line) and not ('}' in line):
            # We've gotten an opening bracket (and not an open/close pair) on this line
            bracket_depth += 1
            if in_object and (not in_object_bracket):
              in_object_bracket = True
            elif in_vertex_list and (not in_vertex_list_bracket):
              in_vertex_list_bracket = True
            elif in_element_list and (not in_element_list_bracket):
              in_element_list_bracket = True
        elif ('}' in line) and not ('{' in line):
            # We've gotten a closing bracket (and not an open/close pair) on this line
            bracket_depth += -1
            if in_element_list_bracket:
              in_element_list_bracket = False
              in_element_list = False
            elif in_vertex_list_bracket:
              in_vertex_list_bracket = False
              in_vertex_list = False
            elif in_object_bracket:
              in_object_bracket = False
              in_object = False
        elif 'POLYGON_LIST' in line:
            print ( "Object Definition: " + line.strip() )
            obj = {}
            vl = []
            ec = []
            sr = []
            obj['name'] = line.strip().split()[0]
            obj['vertex_list'] = vl
            obj['element_connections'] = ec
            obj['define_surface_regions'] = sr
            obj_list.append ( obj )
            in_object = True
        elif in_object_bracket and 'VERTEX_LIST' in line:
            in_vertex_list = True
        elif in_object_bracket and 'ELEMENT_CONNECTIONS' in line:
            in_element_list = True
        elif ('[' in line) and (']' in line):
            if (in_vertex_list):
                # print ( "Vertex: " + line.strip() )
                vl.append(eval(line))
            if (in_element_list):
                # print ( "Face: " + line.strip() )
                ec.append(eval(line))
    return dm


if len(sys.argv) > 2:
    print ( "Got parameters: " + sys.argv[1] + " " + sys.argv[2] )
    dm = create_new_data_model_template()
    read_objects_from_mdl_file ( sys.argv[1], dm )
    write_data_model ( dm, sys.argv[2] )
    print ( "Wrote Data Model found in \"" + sys.argv[1] + " to " + sys.argv[2] )
    # Drop into an interactive python session
    #__import__('code').interact(local={k: v for ns in (globals(), locals()) for k, v in ns.items()})

else:
    # Print the help information
    help()

