#    NeuroMorph_Naming.py (C) 2017,  Anne Jorstad
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/

bl_info = {  
    "name": "NeuroMorph Object Naming",
    "author": "Anne Jorstad",
    "version": (1, 0, 0),
    "blender": (2, 7, 8),
    "location": "View3D > Lengths",
    "description": "Interface for NeuroMorph naming convention",
    "warning": "",  
    "wiki_url": "",  
    "tracker_url": "",  
    "category": "Learnbgame"
}  
  
import bpy
from bpy.props import *
from mathutils import Vector
import mathutils
import math
import os
import sys


global global_name
global_name = "submesh"
#global_axon_index = 0

# set the global variable object name
# This is assigned via a global variable in order to handle multiple methods of input.
def get_name(self):
    global global_name
    return global_name

# this gets called, but doesn't do anything
def set_name(self, value):
    return

class NamingPanel(bpy.types.Panel):
    bl_label = "Object Naming Convention"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "NeuroMorph"

    def draw(self, context):
        global global_name  #, global_axon_index
        layout = self.layout
        scn = context.scene
        obj = context.object

        # name the object
        ### todo:  would like to have default index be ind+1
        layout.prop(scn, 'obj_type')  #, expand=True)
        if obj is not None:
            if scn.obj_type == "other":
                    layout.prop(obj, 'string_name_in')
                    this_name = obj.string_name_in
            elif scn.obj_type == "axon":
                #global_axon_index = get_highest_index("dendrite")
                # make global_axon_index+1 the default for axon_index: not yet implemented
                layout.prop(scn, 'axon_index')
                layout.prop(scn, 'axon_type')
                #this_name = "axon" + str(scn.axon_index)
                this_name = "axon{:0>3d}".format(scn.axon_index)
                if scn.axon_type != "other":
                    this_name = this_name + scn.axon_type
            elif scn.obj_type == "dendrite":
                layout.prop(scn, 'dendrite_index')
                #this_name = "dendrite" + str(scn.dendrite_index)
                this_name = "dendrite{:0>3d}".format(scn.dendrite_index)
            elif scn.obj_type == "synapse":
                layout.prop(scn, 'synapse_d_ind')
                layout.prop(scn, 'synapse_s_ind')
                layout.prop(scn, 'synapse_a_ind')
                layout.prop(scn, 'synapse_b_ind')
                layout.prop(scn, 'synapse_type')
                #this_name = 'd'+str(scn.synapse_d_ind) + 's'+str(scn.synapse_s_ind) + \
                #            'a'+str(scn.synapse_a_ind) + 'b'+str(scn.synapse_b_ind)
                this_name = 'syn_''d{:0>3d}'.format(scn.synapse_d_ind) + 's{:0>2d}'.format(scn.synapse_s_ind) + \
                            'a{:0>3d}'.format(scn.synapse_a_ind) + 'b{:0>2d}'.format(scn.synapse_b_ind)
                if scn.synapse_type != "other":
                    this_name = this_name + scn.synapse_type
            elif scn.obj_type == "bouton":
                layout.prop(scn, 'bouton_index')
                #this_name = "bouton" + str(scn.bouton_index)
                layout.prop(scn, 'Completeness_types')
                this_name = "bouton{:0>2d}".format(scn.bouton_index) + str(scn.Completeness_types)
            elif scn.obj_type == "spine":
                layout.prop(scn, 'spine_index')
                #this_name = "spine" + str(scn.spine_index)
                layout.prop(scn, 'Completeness_types')
                this_name = "spine{:0>2d}".format(scn.spine_index) + str(scn.Completeness_types)
            layout.operator("mesh.update_name", text = "Update Object Name")
            global_name = this_name


# update name of already existing object
class Update_Name(bpy.types.Operator):
    """Change name of object"""
    bl_idname = "mesh.update_name"
    bl_label = "update object name"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        if bpy.ops.object.mode_set.poll():
            bpy.ops.object.mode_set(mode='OBJECT')
        obj = context.object
        obj.name = bpy.context.object.string_name
        return{'FINISHED'}


# # return the current highest index of a particular object name:  not used
# def get_highest_index(typename):
#     n = 0
#     nname = len(typename)
#     for obj in bpy.context.scene.objects[:]:
#         obj_name = obj.name
#         if obj_name[0:nname] == typename:
#             all_ints = re.findall(r'\d+', obj_name)
#             this_ind = int(all_ints[0])
#             n = max(n, this_ind)
#     return n




def register():
    bpy.utils.register_module(__name__)

    bpy.types.Object.string_name = StringProperty(name = "obj name", default="submesh", get=get_name, set=set_name)
    bpy.types.Object.string_name_in = StringProperty(name = "obj name", default="submesh")

    obj_types_enum = [("other","other","",1),("axon","axon","",2),("dendrite","dendrite","",3),\
                      ("synapse","synapse","",4),("bouton","bouton","",5),("spine","spine","",6)]
    axon_types_enum = [("other","other","",1),("_E","excitatory","",2),("_I", "inhibitory","",3),("_U", "unknown","",4)]
    synapse_types_enum = [("other","other","",1),("_E","excitatory","",2),("_I", "inhibitory","",3),("_U", "unknown","",4)]
    Completeness_types_enum = [(" ","complete","",1), ("_in","incomplete","",2)]
    bpy.types.Scene.obj_type = EnumProperty(name = 'Obj Type', default = "other", items = obj_types_enum)
    bpy.types.Scene.axon_type = EnumProperty(name = 'axon type', default = "other", items = axon_types_enum)
    bpy.types.Scene.axon_index = IntProperty(name = 'axon index', default=0, min=0)
    bpy.types.Scene.dendrite_index = IntProperty(name = 'dendrite index', default=0, min=0)
    bpy.types.Scene.synapse_d_ind = IntProperty(name = 'dendrite index', default=0, min=0)
    bpy.types.Scene.synapse_s_ind = IntProperty(name = 'spine index', default=0, min=0)
    bpy.types.Scene.synapse_a_ind = IntProperty(name = 'axon index', default=0, min=0)
    bpy.types.Scene.synapse_b_ind = IntProperty(name = 'bouton index', default=0, min=0)
    bpy.types.Scene.synapse_type = EnumProperty(name = 'synapse type', default = "other", items = synapse_types_enum)
    bpy.types.Scene.bouton_index = IntProperty(name = 'bouton index', default=0, min=0)
    bpy.types.Scene.spine_index = IntProperty(name = 'spine index', default=0, min=0)
    bpy.types.Scene.Completeness_types = EnumProperty(name = 'Complete?', items = Completeness_types_enum, \
                                                      description="Mark object as not completely contained in the scene (optional)")

def unregister():
    bpy.utils.unregister_module(__name__)

    del bpy.types.Scene.Completeness_types
    del bpy.types.Scene.spine_index
    del bpy.types.Scene.bouton_index
    del bpy.types.Scene.synapse_type
    del bpy.types.Scene.synapse_b_ind
    del bpy.types.Scene.synapse_a_ind
    del bpy.types.Scene.synapse_s_ind
    del bpy.types.Scene.synapse_d_ind
    del bpy.types.Scene.dendrite_index
    del bpy.types.Scene.axon_index
    del bpy.types.Scene.axon_type
    del bpy.types.Scene.obj_type
    del bpy.types.Object.string_name_in
    del bpy.types.Object.string_name


if __name__ == "__main__":
    register()
    

