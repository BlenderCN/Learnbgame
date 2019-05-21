# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 3
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

# Author: Petr Ohlidal (https://github.com/only-a-ptr)
                                    
import bpy
import bmesh

# How to obtain notifications about mesh changes:
#     https://www.blender.org/forum/viewtopic.php?p=104947&sid=6e58712b66a8207481d93e4fc542b042#p104947
# Manual: https://docs.blender.org/api/blender2.8/bpy.app.handlers.html?highlight=handlers#module-bpy.app.handlers

# TODO - RESEARCH HOW TO READ LAYER VALUES W/O BMESH
#    bpy.context.active_object.data.vertex_layers_string['layer-name']
#    

"""
# Very insigthful snippet 
# https://blenderartists.org/t/getting-vertices-of-a-vertex-group-from-within-python/584014/5

ob =  bpy.context.active_object
group_lookup = {g.index: g.name for g in ob.vertex_groups} # creates a dict
verts = {name: [] for name in group_lookup.values()} # creates a dict
for v in ob.data.vertices:
    for g in v.groups:
        verts[group_lookup[g.group]].append(v.index)

for key, val in verts.items():
    print('  {} {} -> {} {}'.format(key, type(key), val, len(val)))
"""

class ROR_OT_node_options(bpy.types.Operator):
    """ {Loads / applies} node options {from/to} selected vertices """
    bl_idname = "mesh.ror_node_options_op"
    bl_label = "Node options manipulation"
    
    action = bpy.props.StringProperty() # {'LOAD', 'APPLY'}
    
    @classmethod
    def poll(cls, context):
        ob = context.active_object
        return ob and ob.type == 'MESH' and ob.mode == 'EDIT' and ob.ror_truck
        
    def execute(self, context):
        ob = bpy.context.active_object  
        ob.update_from_editmode() # must be called to make `Vertex.select` attributes up-to-date      
        bm = bmesh.from_edit_mesh(ob.data)
        bm.verts.ensure_lookup_table()
        options_key = bm.verts.layers.string.get("options")
        if self.action == 'LOAD':
            ob.ror_truck.active_node_options = ''
            num_selected = 0
            result = ''
            for v, bv in zip(ob.data.vertices, bm.verts):              
                if v.select:
                    num_selected += 1
                    val = bv[options_key].decode()               
                    if result != '' and result != val:
                        result = '<different values>'
                    else:
                        result = val
            ob.ror_truck.active_node_options = result
                                    
        elif self.action == 'APPLY':
            for v, bv in zip(ob.data.vertices, bm.verts):
                if v.select:
                    bv[options_key] = ob.ror_truck.active_node_options.encode()
                                        
        return {'FINISHED'}   
                      
class ROR_PT_node_options(bpy.types.Panel):
    """ Node options (section 'nodes' in Truckfile) """
    bl_label = "Node Options"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "physics"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        ob = bpy.context.active_object
        
        # Return: https://docs.blender.org/api/blender2.8/bpy.types.UILayout.html#bpy.types.UILayout
        row = layout.row() 
        
        # NOTE: you can't add operator properties to a panel (https://blender.stackexchange.com/a/17755)
        row.prop(ob.ror_truck, "active_node_options", text='') # object (aka 'data') and property name

        row = layout.row()
        # HOWTO add UI button: https://docs.blender.org/api/blender2.8/bpy.types.UILayout.html#bpy.types.UILayout.operator
        op_props = row.operator("mesh.ror_node_options_op", text="Load")
        op_props.action = 'LOAD'

        op_props = row.operator("mesh.ror_node_options_op", text="Apply")
        op_props.action = 'APPLY'


