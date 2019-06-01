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


bl_info = {
    "name": "Global Subsurf Level",
    "description": "Allows you to modify the subsurf level for all objects that already have the modifier",
    "author": "David Velasquez",
    "version": (0, 1),
    "blender": (2, 65, 0),
    "location": "3D View -> Properties Panel -> Global Subsurf Level",
    "warning": "",
    "category": "Learnbgame",
}

import bpy

class GlobalSubsurfLevel(bpy.types.Operator):
    """Modify subsuf level to objects that already have the modifier"""
    bl_idname = "object.subsurflevel"
    bl_label = "Modify Subsurf Level"
    bl_options = {'REGISTER', 'UNDO'}
        
    def execute(self, context):
        scene = context.scene
        i = 0
        
        for obj in scene.objects:
            if obj.type == 'MESH':
                obj_modifiers = obj.modifiers
                #apply to all objects
                if scene.apply_to == "ALL":
                    #loop in object modifiers
                    for mod in obj_modifiers:
                        #look if has subsurf modifier and apply if True
                        if mod.type == 'SUBSURF':
                            mod.levels = scene.subdivisions_view
                            mod.render_levels = scene.subdivisions_render
                            i += 1
                            #shade_smooth
                            if scene.shade_smooth:
                                apply_shade_smooth(obj)                                
                            
                #apply to selected objects
                elif scene.apply_to == 'SEL':
                    if not context.selected_objects:
                        self.report({'ERROR'}, "No objects selected")
                        return {'CANCELLED'}
                    #check object selected
                    if obj.select:
                        #loop in object modifiers                          
                        for mod in obj_modifiers:
                           #look if has subsurf modifier and apply if True
                           if mod.type == 'SUBSURF':
                               mod.levels = scene.subdivisions_view
                               mod.render_levels = scene.subdivisions_render       
                               i += 1
                               #shade_smooth
                               if scene.shade_smooth:
                                    apply_shade_smooth(obj)
        
        if i == 0:
            self.report({'INFO'}, "No objects with Subsurf modifier")
        else:
            self.report({'INFO'}, "Subsurf level modified for " + str(i) + " objects")            
        return {'FINISHED'}

def apply_shade_smooth(obj):
    """ apply shade smooth to the objects """
    obj.select = True
    bpy.ops.object.shade_smooth()
    #obj.select = False

def init_properties():
    scene = bpy.types.Scene
    
    scene.subdivisions_view = bpy.props.IntProperty(
        name="View",
        description="Subsurf level to appy to the view",
        default=1,
        min=0,
        max=7)
    scene.subdivisions_render = bpy.props.IntProperty(
        name="Render",
        description="Subsurf level to appy to the render",
        default=3,
        min=0,
        max=7)
    scene.apply_to = bpy.props.EnumProperty(
        items=[
            ("ALL", "All Objects", "Apply subsurf level to all objects that already have the modifier"),
            ("SEL", "Selected Objects", "Apply subsurf level to selected objects that already have the modifier")
        ],
        name="Objects",
        description="Apply subsurf level to"
        )
    scene.shade_smooth = bpy.props.BoolProperty(
        name="ShadeSmooth",
        description="Apply shade smooth to the objects"
        )
        
def clear_properties():
    scene = bpy.types.Scene
    
    del scene.subdivisions_view
    del scene.subdivisions_render
    del scene.apply_to
    del scene.shade_smooth

class OBJECT_PT_modify_subsurf(bpy.types.Panel):
    """draw panel in propierties panel"""
    bl_label = "Modify Subsurf Level"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = "objectomode"
    
    def draw(self, context):
        sc = context.scene
        layout =  self.layout
                
        split = layout.split()
        
        col = split.column()
        sub = col.column(align=True)
        sub.label(text="Subdivisions:")
        sub.prop(sc, "subdivisions_view", text="View")
        sub.prop(sc, "subdivisions_render", text="Render")
        
        sub = col.column(align=True)
        sub.label(text="Modify Subsurf Level To:")
        sub.prop(sc, "apply_to", text="")
        
        sub = col.column(align=True)
        sub.label(text="Shade Smooth:")
        sub.prop(sc, "shade_smooth", text="Apply shade smooth")
        
        layout.separator()
        
        layout.operator("object.subsurflevel", text="Apply")
    
def register():
    init_properties()
    bpy.utils.register_class(GlobalSubsurfLevel)
    bpy.utils.register_class(OBJECT_PT_modify_subsurf)
    
def unregister():
    clear_properties()
    bpy.utils.unregister_class(GlobalSubsurfLevel)
    bpy.utils.unregister_class(OBJECT_PT_modify_subsurf)
    
if __name__ == "__main__":
    register()