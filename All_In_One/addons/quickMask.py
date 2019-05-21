# ##### BEGIN GPL LICENSE BLOCK #####
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


import bpy
import bmesh



bl_info = {
    "name": "Quick Mask",
    "author": "Ray Mairlot",
    "version": (1, 0),
    "blender": (2, 78, 0),
    "location": "Mesh > Vertices > Vertex Groups",
    "description": "Adds tools to create Mask modifiers quickly by selecting vertices in Edit Mode",
    "category": "Object"
    }



def getMaskModifiers(context):
    
    return [modifier for modifier in context.object.modifiers if modifier.type == "MASK"]
        


def getSelectedVertices(context):
        
    #Use bmesh so that 'invoke' function can detect selected vertices in edit mode
    me = context.object.data
    bm = bmesh.from_edit_mesh(me)   # fill it in from a Mesh
        
    return [v.index for v in bm.verts if v.select]



def newMaskFromSelection(self, context):
    
    object = context.object
    selectedVertices = getSelectedVertices(context)  

    bpy.ops.object.mode_set(mode='OBJECT')

    maskName = "Mask"
    vertexGroupName = "Group"
    if self.name != "Mask":
        
        maskName = self.name
        vertexGroupName = self.name       
              
    vertexGroup = object.vertex_groups.new(name=vertexGroupName)
    vertexGroup.add(selectedVertices, 1, "ADD")
    
    modifier = object.modifiers.new(maskName, "MASK")
    modifier.vertex_group = vertexGroup.name
    modifier.show_in_editmode = True
    modifier.show_on_cage = True
    modifier.invert_vertex_group = True
    
    bpy.ops.object.mode_set(mode="EDIT")



def addSelectionToMask(self, context):
    
    object = context.object
    mask = object.modifiers[self.maskName]
    vertexGroup = object.vertex_groups[mask.vertex_group]
    selectedVertices = getSelectedVertices(context)

    bpy.ops.object.mode_set(mode='OBJECT')
    vertexGroup.add(selectedVertices, 1, "ADD")
    bpy.ops.object.mode_set(mode="EDIT")
    


class NewMaskFromSelectionOperator(bpy.types.Operator):
    """Adds a new Mask modifier using the selected vertices as the vertex group"""
    bl_idname = "object.new_mask_from_selection"
    bl_label = "New Mask From Selection"
    bl_options = {"UNDO"}

    name = bpy.props.StringProperty(name="Mask name", default="Mask")

    @classmethod
    def poll(cls, context):
        return bpy.context.mode == "EDIT_MESH"

    
    def execute(self, context):
        newMaskFromSelection(self, context)    
        return {'FINISHED'}


    def invoke(self, context, event):

        if len(getSelectedVertices(context)) == 0:
            
            self.report({'ERROR'}, "No selected vertices")
            return {'CANCELLED'}
        
        else:
            
            return context.window_manager.invoke_props_dialog(self)
    
    

class AddSelectionToMaskMenu(bpy.types.Operator):
    """Adds the selected vertices to an existing Mask modifier's vertex group"""
    bl_idname = "object.add_selection_to_mask_menu"
    bl_label = "Add Selection To Existing Mask Menu"

    @classmethod
    def poll(cls, context):
        return bpy.context.mode == "EDIT_MESH"
    

    def execute(self, context):
        bpy.ops.wm.call_menu(name=MaskModifierMenu.bl_idname)
        return {'FINISHED'}
    
    
    
class AddSelectionToMaskOperator(bpy.types.Operator):
    """Adds the selected vertices to an existing Mask modifier's vertex group"""
    bl_idname = "object.add_selection_to_existing_mask"
    bl_label = "Add Selection To Existing Mask"
    bl_options = {"UNDO", "INTERNAL"}

    maskName = bpy.props.StringProperty(default="", description="Name of the mask to add the selected vertices to")

    @classmethod
    def poll(cls, context):
        return bpy.context.mode == "EDIT_MESH"
    

    def execute(self, context):
        if len(getMaskModifiers(context)) > 0:    
            
            addSelectionToMask(self, context)
            
        else:
            
            self.report({'ERROR'}, "No existing Mask modifiers")
            return {'CANCELLED'}
            
        return {'FINISHED'}    
    
    
    
class MaskModifierMenu(bpy.types.Menu):
    bl_label = "Mask Modifiers"
    bl_idname = "object.mask_modifier_menu"

    def draw(self, context):
        layout = self.layout
        
        maskModifiers = getMaskModifiers(context)
        
        row = layout.row()
        
        if len(maskModifiers) > 0:
                
            for mask in maskModifiers:
            
                operator = row.operator("object.add_selection_to_existing_mask", text=mask.name, icon="MOD_MASK")    
                operator.maskName = mask.name
                
        else:
            
            row.label("No Mask modifiers to add to")



def vertexGroupMenuDraw(self, context):
    
    layout = self.layout
    layout.separator()
    row = layout.row()
    #INVOKE_DEFAULT is needed to ensure invoke_props_dialog appears
    row.operator_context = "INVOKE_DEFAULT"
    row.operator("object.new_mask_from_selection", text="New Mask from Selection")
    row = layout.row()
    row.menu(MaskModifierMenu.bl_idname, text="Add Selection to Existing Mask")


def register():
    bpy.utils.register_module(__name__)
    bpy.types.VIEW3D_MT_vertex_group.append(vertexGroupMenuDraw)  


def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.VIEW3D_MT_vertex_group.remove(vertexGroupMenuDraw)    


if __name__ == "__main__":
    register() 