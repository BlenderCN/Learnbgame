# ##### BEGIN GPL LICENSE BLOCK #####
#
#  node_location_panel.py
#  Add a panel in the Node Editor with sliders for the location of the active node
#  Copyright (C) 2015 Quentin Wenger
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
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



bl_info = {"name": "Node Location Panel",
           "description": "Add a panel in the Node Editor with sliders for the location of the active node",
           "author": "Quentin Wenger (Matpi)",
           "version": (1, 1),
           "blender": (2, 73, 0),
           "location": "Node Editor > Properties > Node Location",
           "warning": "",
           "wiki_url": "",
           "tracker_url": "",
           "category": "Node"
           }




import bpy


act = None


    
def getLocation(self):

    if act is None:
        # should not happen
        return 0.0

    return act.location


def setLocation(self, value):

    if act is not None:
        act.location = value




class NodeLocationPanel(bpy.types.Panel):
    bl_label = "Node Location"
    bl_idname = "NODE_PT_node_location"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'


    def draw(self, context):
        global act
        
        layout = self.layout
        
        sce = context.scene
         
        act = context.active_node
        
        if act is not None:
            layout.prop(sce, "node_location")




def register():
    bpy.utils.register_module(__name__)
    
    bpy.types.Scene.node_location = bpy.props.FloatVectorProperty(name="Location",
                                                                  description="The location of active node in the Node Editor",
                                                                  size=2,
                                                                  set=setLocation,
                                                                  get=getLocation
                                                                  )


def unregister():
    bpy.utils.unregister_module(__name__)

    del bpy.types.Scene.node_location



if __name__ == "__main__":
    register()



