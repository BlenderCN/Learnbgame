import bpy

class DogePanel(bpy.types.Panel) :
    bl_idname = "TOOL_PT_Doge"
    bl_label = "Auto Model"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context = 'objectmode'
    bl_category = 'Tools'

    def draw(self, context) :
        layout = self.layout
        layout.label(text="WoW Such Panel")
        layout.column(align=True).operator("object.auto_modeler_avatar")
        layout.column(align=True).operator("import.jason_file")
        layout.label(text="Wow Such Label")
    


def register() :
    bpy.utils.register_class(DogePanel)

def unregister() :
    bpy.utils.unregister_class(DogePanel)
