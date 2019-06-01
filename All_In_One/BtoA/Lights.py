import imp,os,glob
from arnold import *
from bpy.props import (CollectionProperty,StringProperty, BoolProperty,
                       IntProperty, FloatProperty, FloatVectorProperty,
                       EnumProperty, PointerProperty)
from bl_ui.properties_data_lamp import DataButtonsPanel

if "bpy" in locals():
    imp.reload(PointLight)
    imp.reload(SpotLight)
else:
    import bpy
    from . import PointLight
    from . import SpotLight

def updateBlenderLight(self,context):
    atype = context.lamp.BtoA.lightType
    context.lamp.type = self.arnoldBlenderMap[atype]
    
#################
# Lamp
################
Lamp = bpy.types.Lamp

class BtoA_lamp_ui(DataButtonsPanel, bpy.types.Panel):
    bl_label = "Lamp"
    COMPAT_ENGINES = {'BtoA'}

    def draw(self, context):
        layout = self.layout

        lamp = context.lamp
        bt = lamp.BtoA
        layout.prop(bt,"lightType",text="Type")

        split = layout.split()
        col1 = split.column()
        col2 = split.column()
        col1.prop(lamp, "color", text="Color")
        col1.prop(lamp, "energy")
        col1.prop(bt,"exposure")
        col1.prop(bt,"bounces",text="Bounces")
        col1.prop(bt,"mis",text="Mis")
        col2.label("Affect:")
        col2.prop(lamp, "use_specular")
        col2.prop(lamp, "use_diffuse")
        col2.prop(bt,"normalize",text="Normalize")
        col2.prop(bt,"bounce_factor",text="Bounce Factor")

class BtoALampSettings(bpy.types.PropertyGroup):
    name="BtoALampSettings"
    #################   
    # Import Modules from default folder
    #################
    defaultLightsDir = os.path.join(os.path.dirname(__file__),"lights")
    defaultLights = glob.glob(os.path.join(defaultLightsDir,"*.py"))
    # if the dir is not a "module", lets turn it into one
    if not os.path.exists(os.path.join(defaultLightsDir,"__init__py")):
        fin = open(os.path.join(defaultLightsDir,"__init__.py"),'w')
        fin.close()

    # load all materials from the materials folder
    lights = []
    loadedLights = {}
    arnoldBlenderMap = {}
    for modulePath in defaultLights:
        module = os.path.basename(modulePath)
        moduleName = module[:-3]
        if module == '__init__.py' or module[-3:] != '.py':
            continue
        print("BtoA:: Loading %s" % moduleName) 
        foo = __import__("BtoA.lights."+moduleName, locals(), globals())
        module = eval("foo.lights."+moduleName)
        lights.append(module.enumValue)
        vars()[moduleName] = PointerProperty(type=module.className)
        loadedLights[module.enumValue[0]] = module
        arnoldBlenderMap[module.enumValue[0]]=module.blenderType

    
    lightType = EnumProperty(items=lights,
                             name="Light", description="Light", 
                             default="POINTLIGHT",update=updateBlenderLight)
    # attrubutes that are common to all lights
    normalize = BoolProperty(name="Normalize",default=True)
    bounces = IntProperty(name="Bounces",description="Max bounces for this light",
                          default=999)
    bounce_factor = FloatProperty(name="Bounce Factor",
                            min=0,max=10,default=1)
    exposure = FloatProperty(name="Exposure",
                            description="Light Exposure",
                            min=0,max=100,default=0)
    mis = BoolProperty(name="Mis",default=True)
    shadow_enable = BoolProperty(name="Enable Shadows",
                                description="",default=True)
    shadow_density = FloatProperty(name="Shadow Density",
                                   description="Shadow Density",
                                   min = 0,max=1000,default=1)
bpy.utils.register_class(BtoALampSettings)
bpy.types.Lamp.BtoA = PointerProperty(type=BtoALampSettings,name='BtoA')


class BtoA_shadow_ui(DataButtonsPanel, bpy.types.Panel):
    bl_label = "Shadow"
    COMPAT_ENGINES = {'BtoA'}

    @classmethod
    def poll(cls, context):
        lamp = context.lamp
        if lamp:
            engine = context.scene.render.engine in cls.COMPAT_ENGINES
            ltype = lamp.type in {'POINT', 'SUN', 'SPOT', 'AREA'}
            return lamp and ltype and engine
        else:
            return False

    def draw(self, context):
        layout = self.layout
        lamp = context.lamp
        bt = lamp.BtoA
        layout.prop(bt,"shadow_enable")

        if (bt.shadow_enable):
            split = layout.split()
            col1 = split.column()
            col2 = split.column()
            col1.prop(lamp, "shadow_color")
            col1.prop(bt, "shadow_density", text="Density")
            col2.prop(lamp, "use_shadow_layer", text="This Layer Only")
            split = layout.split()
            col1 = split.column()
            col1.label(text="Sampling:")

            if lamp.type in {'POINT', 'SUN', 'SPOT'}:
                sub = col1.row()
                sub.prop(lamp, "shadow_ray_samples", text="Samples")
                sub.prop(lamp, "shadow_soft_size", text="Soft Size")

            elif lamp.type == 'AREA':
                sub = col.row(align=True)

                if lamp.shape == 'SQUARE':
                    sub.prop(lamp, "shadow_ray_samples_x", text="Samples")
                elif lamp.shape == 'RECTANGLE':
                    sub.prop(lamp, "shadow_ray_samples_x", text="Samples X")
                    sub.prop(lamp, "shadow_ray_samples_y", text="Samples Y")

class Lights:
    '''This class handles the export of all lights'''
    def __init__(self):
        self.lightDict = {}
        
    def writeLights(self):
        for li in bpy.data.lamps:
            self.writeLight(li)

    def writeLight(self,li):
        outli = None
        currentLight = li.BtoA.loadedLights[li.BtoA.lightType]
        outli = currentLight.write(li)

        AiNodeSetStr(outli,b"name",li.name.encode('utf-8'))
        self.lightDict[li.as_pointer()] = outli
        return outli
