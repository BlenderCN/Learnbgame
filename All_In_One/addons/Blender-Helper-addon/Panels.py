import bpy
from bpy.types import Menu

class Array(bpy.types.Panel):
    bl_idname = "panel.array"
    bl_label = "Array"
    bl_category = "Helper"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        col = layout.column()
        ob = context.object
        
        # Circle Array Button
        col.operator('object.circle_array_operator', text = 'Circle Array')
        
        # Array Count
        for mod in ob.modifiers:
            if mod.type == "ARRAY" and mod.fit_type == 'FIXED_COUNT':
                col.label(text= mod.name +' Count:')
                col.prop(ob.modifiers[mod.name], 'count')

        col.operator('object.array_path_operator', text= 'Path Array')
        
        # Array relative Offset
        for mod in ob.modifiers:
            if mod.type == "ARRAY" and mod.fit_type == 'FIT_CURVE' and mod.use_relative_offset == True:
                col.prop(ob.modifiers[mod.name], 'relative_offset_displace', text='Array Offset:')
        
        # Instance Collection on faces
        col.label(text='Collection:')
        col.operator('object.instance_collection', text='instance collection')

class Mirror(bpy.types.Panel):
    bl_idname = "panel.mirror"
    bl_label = "Mirror"
    bl_category = "Helper"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):
        layout = self.layout

        ob = context.object
        col = layout.column()

        col.operator('object.object_mirror', text='Mirror over object')

        col = layout.column()
        row = layout.row()
        for mod in ob.modifiers:
            if mod.type == "MIRROR":
                col.label(text='Mirror Axis:')
                row.prop(ob.modifiers[mod.name], 'use_axis', text='X', index=0)
                row.prop(ob.modifiers[mod.name], 'use_axis', text='Y', index=1)
                row.prop(ob.modifiers[mod.name], 'use_axis', text='Z', index=2)

class Others(bpy.types.Panel):
    bl_idname = "panel.others"
    bl_label = "Others"
    bl_category = "Helper"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        col = layout.column()
        col.operator('object.update_scene', text='Update Scene')

        
class PIE_Menu(Menu):
    bl_idname = "mesh.pie"
    bl_label = "Workspaces"

    def draw(self, context):
        layout = self.layout

        pie = layout.menu_pie()

        pie.operator('object.object_mirror', text = 'Mirror over object')           #8
        pie.operator('object.array_path_operator', text = 'Path Array')             #2
        pie.operator('view3d.cursor_center', text = 'Center 3D Cursors')            #4
        pie.operator('object.circle_array_operator', text = 'Circle Array')         #6