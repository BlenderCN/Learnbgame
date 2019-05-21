import bpy

class ToolsPanel444(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_category = "3DSC"
    bl_label = "Shift"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        obj = context.object

        row = layout.row()        
        row.label(text="Shift values:")
        row = layout.row()
        row.prop(context.scene, 'SRID', toggle = True)
        row = layout.row() 
        row.prop(context.scene, 'BL_x_shift', toggle = True)
        row = layout.row()  
        row.prop(context.scene, 'BL_y_shift', toggle = True)
        row = layout.row()  
        row.prop(context.scene, 'BL_z_shift', toggle = True)    
        row = layout.row()
        if scene['crs x'] is not None and scene['crs y'] is not None:
            if scene['crs x'] > 0 or scene['crs y'] > 0:
                self.layout.operator("shift_from.blendergis", icon="PASTEDOWN", text='from Bender GIS')


class OBJECT_OT_IMPORTPOINTS(bpy.types.Operator):
    """Import points as empty objects from a txt file"""
    bl_idname = "shift_from.blendergis"
    bl_label = "Copy from BlenderGis"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        scene = context.scene
        scene['BL_x_shift'] = scene['crs x']
        scene['BL_y_shift'] = scene['crs y']

        return {'FINISHED'}