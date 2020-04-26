import bpy

class NiftoolsUtilityPanel(bpy.types.Panel):
    bl_label = "Niftools Utilites Panel"
    bl_idname = "OBJECT_PT_niftools_utilities"
    
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "scene"
    
    def draw(self, context):
        layout = self.layout
        
        #options
        box = layout.box()
        row = box.row()
        row.prop(context.scene.vertexcolor, "fileinput")
        row = box.row()
        row.operator("vertexcolor.nifread", "Load")
        row = box.row()
        row.prop(context.scene.vertexcolor, "hexwidget")
        row = box.row()
        row.prop(context.scene.vertexcolor, "fileoutput")
        row = box.row()
        row.operator("vertexcolor.nifwrite", "Save")