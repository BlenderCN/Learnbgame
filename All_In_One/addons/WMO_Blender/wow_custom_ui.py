
import bpy
import bpy.utils
import bpy.types


###############################
## Material
###############################

class WowMaterialPanel(bpy.types.Panel):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "material"
    bl_label = "Wow material"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        layout = self.layout
        self.layout.prop(context.material.WowMaterial, "Enabled")

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        self.layout.prop(context.material.WowMaterial, "Shader")
        self.layout.prop(context.material.WowMaterial, "Transparent")
        self.layout.prop(context.material.WowMaterial, "Texture1")
        self.layout.prop(context.material.WowMaterial, "Color1")
        self.layout.prop(context.material.WowMaterial, "Flags1")
        self.layout.prop(context.material.WowMaterial, "Texture2")
        self.layout.prop(context.material.WowMaterial, "Color2")
        self.layout.prop(context.material.WowMaterial, "Flags2")
        self.layout.prop(context.material.WowMaterial, "Texture3")
        self.layout.prop(context.material.WowMaterial, "Color3")
        self.layout.prop(context.material.WowMaterial, "Flags3")
        layout.enabled = context.material.WowMaterial.Enabled

    @classmethod
    def poll(cls, context):
        return (context.material is not None)

class WowMaterialPropertyGroup(bpy.types.PropertyGroup):
    shaderEnum = [('0', "Diffuse", ""), ('1', "Specular", ""), ('2', "Metal", ""), \
        ('3', "Env", ""), ('4', "Opaque", ""), ('5', "EnvMetal", ""), \
        ('6', "TwoLayerDiffuse", ""), ('7', "TwoLayerEnvMetal", ""), ('8', "TwoLayerTerrain", ""), \
        ('9', "DiffuseEmissive", ""), ('11', "MaskedEnvMetal", ""), ('12', "EnvMetalEmissive", ""), \
        ('13', "TwoLayerDiffuseOpaque", ""), ('14', "TwoLayerDiffuseEmissive", "")]#, ('16', "Diffuse", "")]
    Enabled = bpy.props.BoolProperty(name="", description="Enable wow material properties")
    Shader = bpy.props.EnumProperty(items=shaderEnum, name="Shader", description="Wow shader assigned to this material")
    Transparent = bpy.props.BoolProperty(name="Transparent", description="Enable transparency")
    Texture1 = bpy.props.StringProperty(name="Texture 1", description="Texture assigned to first slot in shader")
    Color1 = bpy.props.FloatVectorProperty(name="Color 1", subtype='COLOR', default=(1,1,1), min=0.0, max=1.0)
    Flags1 = bpy.props.EnumProperty(items=[('0', "Clamp", ""), ('1', "Repeat", "")], name="Extension 1", description="Extension mode for texture 1")
    Texture2 = bpy.props.StringProperty(name="Texture 2", description="Texture assigned to second slot in shader")
    Color2 = bpy.props.FloatVectorProperty(name="Color 2", subtype='COLOR', default=(1,1,1), min=0.0, max=1.0)
    Flags2 = bpy.props.EnumProperty(items=[('0', "Clamp", ""), ('1', "Repeat", "")], name="Extension 2", description="Extension mode for texture 2")
    Texture3 = bpy.props.StringProperty(name="Texture 3", description="Texture assigned to third slot in shader")
    Color3 = bpy.props.FloatVectorProperty(name="Color 3", subtype='COLOR', default=(1,1,1), min=0.0, max=1.0)
    Flags3 = bpy.props.EnumProperty(items=[('0', "Clamp", ""), ('1', "Repeat", "")], name="Extension 3", description="Extension mode for texture 3")


def RegisterWowMaterialProperties():
    bpy.types.Material.WowMaterial = bpy.props.PointerProperty(type=WowMaterialPropertyGroup)

def UnregisterWowMaterialProperties():
    bpy.types.Material.WowMaterial = None

###############################
## Light
###############################

class WowLightPanel(bpy.types.Panel):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"
    bl_label = "Wow light"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        layout = self.layout
        self.layout.prop(context.object.data.WowLight, "Enabled")

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        self.layout.prop(context.object.data.WowLight, "LightType")
        self.layout.prop(context.object.data.WowLight, "UseAttenuation")
        self.layout.prop(context.object.data.WowLight, "Color")
        self.layout.prop(context.object.data.WowLight, "Intensity")
        self.layout.prop(context.object.data.WowLight, "AttenuationStart")
        self.layout.prop(context.object.data.WowLight, "AttenuationEnd")
        layout.enabled = context.object.data.WowLight.Enabled

    @classmethod
    def poll(cls, context):
        return (context.object is not None and context.object.data is not None and isinstance(context.object.data, bpy.types.Lamp))

class WowLightPropertyGroup(bpy.types.PropertyGroup):
    lightTypeEnum = [('0', "Omni", ""), ('1', "Spot", ""), ('2', "Direct", ""), ('3', "Ambient", "")]
    Enabled = bpy.props.BoolProperty(name="", description="Enable wow light properties")
    LightType = bpy.props.EnumProperty(items=lightTypeEnum, name="Type", description="Type of the lamp")
    UseAttenuation = bpy.props.BoolProperty(name="Use attenuation", description="True if lamp use attenuation")
    Color = bpy.props.FloatVectorProperty(name="Color", subtype='COLOR', default=(1,1,1), min=0.0, max=1.0)
    Intensity = bpy.props.FloatProperty(name="Intensity", description="Intensity of the lamp")
    AttenuationStart = bpy.props.FloatProperty(name="Attenuation start", description="Distance at which light intensity start to decrease")
    AttenuationEnd = bpy.props.FloatProperty(name="Attenuation end", description="Distance at which light intensity reach 0")

def RegisterWowLightProperties():
    bpy.types.Lamp.WowLight = bpy.props.PointerProperty(type=WowLightPropertyGroup)

def UnregisterWowLightProperties():
    bpy.types.Lamp.WowLight = None

    
###############################
## Liquid
###############################

#XTextures\river\lake_a.1.blp
#XTextures\river\lake_a.1.blp
#XTextures\river\lake_a.1.blp
#XTextures\ocean\ocean_h.1.blp
#XTextures\lava\lava.1.blp
#XTextures\slime\slime.1.blp
#XTextures\slime\slime.1.blp
#XTextures\river\lake_a.1.blp
#XTextures\procWater\basicReflectionMap.1.blp
#XTextures\river\lake_a.1.blp
#XTextures\river\lake_a.1.blp
#XTextures\river\fast_a.1.blp
#XTextures\ocean\ocean_h.1.blp
#XTextures\ocean\ocean_h.1.blp
#XTextures\lava\lava.1.blp
#XTextures\lava\lava.1.blp
#XTextures\slime\slime.1.blp
#XTextures\slime\slime.1.blp
#XTextures\ocean\ocean_h.1.blp
#XTextures\LavaGreen\lavagreen.1.blp
"""
class WowLiquidPanel(bpy.types.Panel):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"
    bl_label = "Wow liquid"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        layout = self.layout
        self.layout.prop(context.object.WowLiquid, "Enabled")

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        self.layout.prop(context.object.WowLiquid, "LiquidType")
        self.layout.prop_search(context.object.WowLiquid, "VertexGroup", context.object, "vertex_groups", text="Liquid vertex group")
        layout.enabled = context.object.WowLiquid.Enabled

    @classmethod
    def poll(cls, context):
        return (context.object is not None and context.object.data is not None and isinstance(context.object.data,bpy.types.Mesh))

class WowLiquidPropertyGroup(bpy.types.PropertyGroup):
    liquidTypeEnum = [('81', "Lake Wintergrasp - Water", ""), ('41', "Coilfang Raid - Water", ""), ('1', "Water", ""), \
        ('2', "Ocean", ""), ('3', "Magma", ""), ('4', "Slime", ""), \
        ('21', "Naxxramas - Slime", ""), ('61', "Hyjal Past - Water", ""), ('100', "Basic Procedural Water", ""), \
        ('13', "WMO Water", ""), ('5', "Slow Water", ""), ('9', "Fast Water", ""), \
        ('6', "Slow Ocean", ""), ('10', "Fast Ocean", ""), ('7', "Slow Magma", ""), \
        ('11', "Fast Magma", ""), ('8', "Slow Slime", ""), ('12', "Fast Slime", ""), \
        ('14', "WMO Ocean", ""), ('15', "Green Lava", "")]
    Enabled = bpy.props.BoolProperty(name="", description="Enable wow liquid properties")
    LiquidType = bpy.props.EnumProperty(items=liquidTypeEnum, name="Liquid Type", description="Type of the liquid present in this WMO group")
    VertexGroup = bpy.props.StringProperty()

def RegisterWowLiquidProperties():
    bpy.types.Object.WowLiquid = bpy.props.PointerProperty(type=WowLiquidPropertyGroup)
    
def UnregisterWowLiquidProperties():
    bpy.types.Object.WowLiquid = None
"""
###############################
## Collision
###############################

class WowCollisionPanel(bpy.types.Panel):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"
    bl_label = "Wow collision"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        layout = self.layout
        self.layout.prop(context.object.WowCollision, "Enabled")

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        self.layout.prop_search(context.object.WowCollision, "VertexGroup", context.object, "vertex_groups", text="Collision vertex group")
        self.layout.prop(context.object.WowCollision, "NodeSize", slider=True)
        layout.enabled = context.object.WowCollision.Enabled

    @classmethod
    def poll(cls, context):
        return (context.object is not None and context.object.data is not None and isinstance(context.object.data,bpy.types.Mesh))

class WowCollisionPropertyGroup(bpy.types.PropertyGroup):
    Enabled = bpy.props.BoolProperty(name="", description="Enable wow collision properties")
    VertexGroup = bpy.props.StringProperty()
    NodeSize = bpy.props.IntProperty(name="Node max size", description="Max count of faces for a node in bsp tree", default=150, min=1, soft_max=500)

def RegisterWowCollisionProperties():
    bpy.types.Object.WowCollision = bpy.props.PointerProperty(type=WowCollisionPropertyGroup)

def UnregisterWowCollisionProperties():
    bpy.types.Object.WowCollision = None


###############################
## WMO Group
###############################
class WowWMOGroupPanel(bpy.types.Panel):
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "object"
    bl_label = "Wow WMO group"
    bl_options = {'DEFAULT_CLOSED'}

    def draw_header(self, context):
        layout = self.layout
        self.layout.prop(context.object.WowWMOGroup, "Enabled")

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        self.layout.prop(context.object.WowWMOGroup, "GroupName")
        self.layout.prop(context.object.WowWMOGroup, "GroupDesc")
        self.layout.prop(context.object.WowWMOGroup, "PlaceType")
        layout.enabled = context.object.WowWMOGroup.Enabled

    @classmethod
    def poll(cls, context):
        return (context.object is not None and context.object.data is not None and isinstance(context.object.data,bpy.types.Mesh))

class WowWMOGroupPropertyGroup(bpy.types.PropertyGroup):
    Enabled = bpy.props.BoolProperty(name="", description="Enable wow WMO group properties")
    GroupName = bpy.props.StringProperty()
    GroupDesc = bpy.props.StringProperty()
    placeTypeEnum = [('8', "Outdoor", ""), ('8192', "Indoor", "")]
    PlaceType = bpy.props.EnumProperty(items=placeTypeEnum, name="Place Type", description="Group is indoor or outdoor")

def RegisterWowWMOGroupProperties():
    bpy.types.Object.WowWMOGroup = bpy.props.PointerProperty(type=WowWMOGroupPropertyGroup)

def UnregisterWowWMOGroupProperties():
    bpy.types.Object.WowWMOGroup = None


def register():
    RegisterWowMaterialProperties()
    #RegisterWowLiquidProperties()
    RegisterWowLightProperties()
    RegisterWowCollisionProperties()
    RegisterWowWMOGroupProperties()
    # registered in __init__
    #bpy.utils.register_class(WowMaterialPanel)

def unregister():
    UnregisterWowMaterialProperties()
    #UnregisterWowLiquidProperties()
    UnregisterWowLightProperties()
    UnregisterWowCollisionProperties()
    UnregisterWowWMOGroupProperties()
    # unregistered in __init__
    #bpy.utils.unregister_class(WowMaterialPanel)
