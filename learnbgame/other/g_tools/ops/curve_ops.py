#importdefs
import bpy
from g_tools.bpy_itfc_funcs import curve_fs
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty, CollectionProperty 
from bpy.types import Operator

#fdef


#opdef
class curve_to_armature_op(bpy.types.Operator):
    """NODESC"""
    bl_idname = "curve.curve_to_armature"
    bl_label = "Curve to armature"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category ="Tools"
    bl_options = {'UNDO','REGISTER'}
    
    def execute(self, context):
        curve_fs.curve_to_armature()
        return {'FINISHED'}
        
        
class GCurvePanel(bpy.types.Panel):
    """Creates a Panel in the 3D View"""
    bl_label = "GCurve"    
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "G Tools"

    def draw(self, context):
        layout = self.layout

        obj = context.object

        #rowdefs
        row = layout.row()
        row.operator("curve.curve_to_armature")
        
        
def register():
    #regdef
    bpy.utils.register_class(curve_to_armature_op)
    bpy.utils.register_class(GCurvePanel)

def unregister():
    #unregdef
    bpy.utils.unregister_class(curve_to_armature_op)
    bpy.utils.unregister_class(GCurvePanel)
    
    