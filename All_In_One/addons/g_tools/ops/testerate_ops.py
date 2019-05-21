#importdefs
import bpy
from g_tools.bpy_itfc_funcs.font_fs import make_test_font
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty, CollectionProperty 
from bpy.types import Operator

#fdef
def testerate_f():
    make_test_font()
    print("Success")
    

#opdef
class testerate_op(bpy.types.Operator):
    """NODESC"""
    bl_idname = "mesh.testerate"
    bl_label = "Testerate"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category ="Tools"
    bl_options = {'UNDO','REGISTER'}
    
    def execute(self, context):
        testerate_f()
        return {'FINISHED'}
        
        
class TesteratePanel(bpy.types.Panel):
    """Creates a Panel in the 3D View"""
    bl_label = "G Tools"    
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "G Tools"

    def draw(self, context):
        layout = self.layout

        obj = context.object

        #rowdefs
        row = layout.row()
        row.operator("mesh.testerate")
        
        
def register():
    #regdef
    bpy.utils.register_class(testerate_op)
    bpy.utils.register_class(TesteratePanel)

def unregister():
    #unregdef
    bpy.utils.unregister_class(testerate_op)
    bpy.utils.unregister_class(TesteratePanel)
    
    