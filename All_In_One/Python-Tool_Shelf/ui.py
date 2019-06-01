import bpy
from .operators import externalPythonScripts

################
#  Python Tab  #
################

class Python_Tab(bpy.types.Panel):
    bl_idname = "python_tab"
    bl_label = "Python Scripts"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Python"
    
    @classmethod
    def poll(cls, context):
        return True
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        for operator in externalPythonScripts:
            layout.operator(operator.bl_idname)
            layout.separator()
