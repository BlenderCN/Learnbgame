import imp
from arnold import *

from bpy.props import (CollectionProperty,StringProperty, BoolProperty,
IntProperty, FloatProperty, FloatVectorProperty, EnumProperty, PointerProperty)
from bl_ui import properties_material
pm = properties_material

from ..GuiUtils import pollMaterial

if "bpy" not in locals():
    import bpy

# This tuple is used to display the shader in the GUI dropdown. It has the form
# (SHADER_ID,LABEL,Description)
# SHADER_ID must be unique, its better to use the name of the shader
enumValue = ("UTILITY","Utility","")

# There must be one class that inherits from bpy.types.PropertyGroup
# Here we place all the parameters for the Material
class BtoAUtilityMaterialSettings(bpy.types.PropertyGroup):
    colorMode = EnumProperty(items=(("0","color",""),("1","ng",""),("2","n",""),
                                    ("3","bary",""),("4","uv",""),("5","u",""),
                                    ("6","v",""),("7","dpdu",""),("8","dpdv",""),
                                    ("9","p",""),("10","prims",""),("11","wire",""),
                                    ("12","polywire",""),("13","obj",""),("14","edgelength",""),
                                    ("15","floatgrid",""),("16","reflectline",""),("17","bad_uvs","")),
                                    name="Color Mode", description="", 
                                    default="0")
    shadeMode = EnumProperty(items=(("0","ndoteye",""),("1","lambert",""),("2","flat",""),
                                    ("3","ambocc","")),
                                    name="Color Mode", description="", 
                                    default="0")
    color = FloatVectorProperty(name="Color",default=(1,1,1),subtype="COLOR")
    opacity = FloatProperty(name="Opacity",default=1)

# The className variable must contain the class that defines the parameters for the 
# material. It is esential for the auto-load process
className = BtoAUtilityMaterialSettings
# Of course we must register the new class
bpy.utils.register_class(className)

# Define as many GUI pannels as necessary, they must all follow this structure.
# Utility only needs one
class BtoA_material_utility_gui(pm.MaterialButtonsPanel, bpy.types.Panel):
    bl_label = "Utility"
    COMPAT_ENGINES = {'BtoA'}

    @classmethod
    def poll(cls, context):
		# this function from ..Materials handles the polling to display the
		# gui widget
        return pollMaterial(cls,context,enumValue[0] )

    def draw(self, context):
        mat = pm.active_node_mat(context.material)
        if mat:
            layout = self.layout
            # Here we see mat.BtoA.utility . The "utility" part is created by the 
            # auto loader and it is derived from the python module name. In this case
            # utility.py
            layout.prop(mat.BtoA.utility,"colorMode")
            layout.prop(mat.BtoA.utility,"shadeMode")
            layout.prop(mat.BtoA.utility,"color")
            layout.prop(mat.BtoA.utility,"opacity")

# Every material module MUST have a writeMaterial function where the 
# material is actually inserted into the Arnold scene.
def write(mat,textures):
    util = mat.BtoA.utility
    node = AiNode(b"utility")
    AiNodeSetInt(node,b"color_mode",int(util.colorMode))
    AiNodeSetInt(node,b"shade_mode",int(util.shadeMode))
    AiNodeSetRGB(node,b"color",util.color.r,
                               util.color.g,
                               util.color.b)
    AiNodeSetFlt(node,b"opacity",util.opacity)
    return node

