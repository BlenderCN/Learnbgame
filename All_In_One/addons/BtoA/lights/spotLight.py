import imp
from arnold import *
from ..GuiUtils import pollLight
from bpy.props import (CollectionProperty,StringProperty, BoolProperty,
                       IntProperty, FloatProperty, FloatVectorProperty,
                       EnumProperty, PointerProperty)
from bl_ui import properties_data_lamp
pm = properties_data_lamp


if "bpy" not in locals():
    import bpy

enumValue = ("SPOTLIGHT","Spot","")
blenderType = "SPOT"
def _updatePenumbra(self,context):
    context.lamp.spot_blend = self.penumbra_angle / context.lamp.spot_size

# There must be one class that inherits from bpy.types.PropertyGroup
# Here we place all the parameters for the Material
class BtoASpotLightSettings(bpy.types.PropertyGroup):
    penumbra_angle = FloatProperty(name="Penumbra Angle",
                                   description="Penumbra Angle",
                                   min = 0,max=180,default=1,
                                   subtype="ANGLE",
                                   update=_updatePenumbra)
    aspect_ratio = FloatProperty(name="Aspect Ratio",
                                description="Aspect",
                                min = 0,max=10,default=1)

className = BtoASpotLightSettings
bpy.utils.register_class(className)

# Define as many GUI pannels as necessary, they must all follow this structure.
class BtoA_SpotLight_gui(pm.DataButtonsPanel, bpy.types.Panel):
    bl_label = "Spot Light"
    COMPAT_ENGINES = {'BtoA'}

    @classmethod
    def poll(cls, context):
        return pollLight(cls,context,enumValue[0],blendLights={"SPOT"} )

    def draw(self, context):
        try:
            layout = self.layout
            lamp = context.lamp
            spot = lamp.BtoA.spotLight
            split = layout.split()

            col1 = split.column()
            col2 = split.column()
            col1.prop(lamp, "spot_size", text="Cone Angle")
            col1.prop(spot, "penumbra_angle", text="Penumbra")
            col2.prop(spot, "aspect_ratio", text="Aspect Ratio")
            col2.prop(lamp, "show_cone")
        except:
            pass
