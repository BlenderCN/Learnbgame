import bpy, bmesh
from mathutils import *

prop_updates = []
_block_updates = False

def stop_prop_updates():
    global _block_updates
    _block_updates = True

def start_prop_updates():
    global _block_updates
    _block_updates = False
    
def register_prop_update(cb):
    global prop_updates

    #XXX
    #prop_updates.append(cb)
    prop_updates = [cb]
    
def on_prop_update(self, context):
    global prop_updates, _block_updates
    
    if _block_updates: return
    
    for cb in prop_updates:
        cb(self, context)

HerringShapes = [
    ("TRIANGLE", "Triangle", "", 0),
    ("SMOOTHSTEP", "Smoothstep", "", 1),
    ("WIDE", "Wide", "", 2),
    ("PINCHED", "Pinched", "", 3),
]

PropNames = [
    "depth",
    "thickness",
    "modulus",
    "shaft_diameter",
    "zoff",
    "genshaft",
    "spacer_on",
    "spacer_width",
    "spacer_thick",
    "spacer_height",
    "xy_scale",

    "double_helical",
    "helical_angle",
    "subdivisions",
    "taper_on",
    "taper_amount",
    "taper_height",
    "invert_helical",
    "herringchannel_blend",
    "herringchannel_depth",
    "herringchannel_on",
    "herringchannel_width",
    "inner_gear_mode",
    "inner_gear_depth",
    "herring_shape",
    "helical_on",
    "backlash",
    "no_cutouts",
    "pressure_angle",
    "key_shaft",
    "key_depth"
]

PropBits = {}

def makePropEnum():
    global PropBits
    
    #make enum property definition
    enumdef = []
    
    for i, p in enumerate(PropNames):
        record = (p, p, p, 1<<i)
        PropBits[p] = 1 << i
        
        enumdef.append(record);
        
    return enumdef
    
CURRENT_VERSION = 0.5
INHERIT_VALUE = -1

_enumdef = makePropEnum()
print(makePropEnum())

def getprop(object, scene, name):
    if name in object.geargen.local_overrides:
        return getattr(object.geargen, name)
    else:
        return getattr(scene.geargen, name)
        
class GearGenProfile (bpy.types.PropertyGroup):
    local_overrides: bpy.props.EnumProperty(items=_enumdef, name="overrides", options={"ENUM_FLAG"}, update=on_prop_update)
    
    key_shaft : bpy.props.BoolProperty(default=False)
    key_depth : bpy.props.FloatProperty(default=0.45)
    
    version: bpy.props.FloatProperty(default=CURRENT_VERSION)
    
    auto_generate: bpy.props.BoolProperty(default=False)
    
    depth: bpy.props.FloatProperty(default=1.0, update=on_prop_update)
    thickness: bpy.props.FloatProperty(default=4, update=on_prop_update)
    modulus: bpy.props.FloatProperty(default=-1.0, update=on_prop_update)

    init: bpy.props.BoolProperty(update=on_prop_update)

    enabled: bpy.props.BoolProperty(update=on_prop_update)
    genshaft: bpy.props.BoolProperty(update=on_prop_update)
    shaft_diameter: bpy.props.FloatProperty(default=4, update=on_prop_update)
    zoff: bpy.props.FloatProperty(update=on_prop_update)
    
    spacer_on: bpy.props.BoolProperty(default=True, update=on_prop_update)
    spacer_width: bpy.props.FloatProperty(default=1.5, update=on_prop_update)
    spacer_thick: bpy.props.FloatProperty(default=1, update=on_prop_update)
    spacer_height: bpy.props.FloatProperty(default=1.5, update=on_prop_update)
    
    xy_scale: bpy.props.FloatProperty(default=1.0, update=on_prop_update)
 
    double_helical: bpy.props.BoolProperty(update=on_prop_update)
    helical_angle: bpy.props.FloatProperty(default=1.0, update=on_prop_update)
    subdivisions: bpy.props.IntProperty(default=8, update=on_prop_update)

    taper_on: bpy.props.BoolProperty(update=on_prop_update)
    taper_amount: bpy.props.FloatProperty(default=0.75, update=on_prop_update)
    taper_height: bpy.props.FloatProperty(default=1.25, update=on_prop_update)

    invert_helical: bpy.props.BoolProperty(default=False, update=on_prop_update) #local property

    herringchannel_on: bpy.props.BoolProperty(default=False, update=on_prop_update)
    herringchannel_width: bpy.props.FloatProperty(default=0.5, update=on_prop_update)
    herringchannel_blend: bpy.props.FloatProperty(default=0.5, update=on_prop_update)
    herringchannel_depth: bpy.props.FloatProperty(default=1.0, update=on_prop_update)
    
    inner_gear_mode: bpy.props.BoolProperty(default=False, update=on_prop_update) #local property
    inner_gear_depth: bpy.props.FloatProperty(default=4.0, update=on_prop_update)

    herring_shape: bpy.props.EnumProperty(default="TRIANGLE", items=HerringShapes, update=on_prop_update)
    
    helical_on: bpy.props.BoolProperty(default=False, update=on_prop_update);
    
    backlash: bpy.props.FloatProperty(default=0.05, update=on_prop_update)
    pitch_out: bpy.props.FloatProperty(default=-1) #used to tell the user final pitch circle radius
    numteeth: bpy.props.IntProperty(default=9, update=on_prop_update) #tell user what final number of teeth are, unless use_numteeth is true in which case this is the number of teeth
    use_numteeth: bpy.props.BoolProperty(default=False, update=on_prop_update);
    no_cutouts: bpy.props.BoolProperty(default=False, update=on_prop_update);
    
    pressure_angle: bpy.props.FloatProperty(default=20, update=on_prop_update)
    
    def set_defaults(self):
        self.init = True
        self.scale = 1.0
        self.taper = 0.2
        self.genshaft = True
        self.zoff = 0
        self.spacer_on = True
        self.spacer_width = 1.5
        self.spacer_thick = 1
        
        self.round = 0.2
        self.enabled = False
        self.depth = 2.0
        self.width = 1.0
        self.thickness = 2.0
        self.shaft = 4.0

def objectprop(context, layout, prop):
    row = layout.row()
    row2 = row.row()
    
    if prop in context.object.geargen.local_overrides:
        icon = "UNLOCKED"
        row2.enabled = True
    else:
        icon = "LOCKED"
        row2.enabled = False
        
    row2.prop(context.object.geargen, prop)
    row.prop_enum(context.object.geargen, "local_overrides", prop, text="", icon=icon)

def uifunc(self, context, gear):
    row = self.layout
    
    col = self.layout.column()
    col.prop(context.object.geargen, "enabled")
    
    col.label(text="Information")
    col.prop(context.object.geargen, "pitch_out")
    
    col.label(text="Local settings")
    
    row = col.row()
    
    col2 = row.column()
    col2.prop(context.object.geargen, "numteeth")
    col2.prop(context.object.geargen, "inner_gear_mode")
    
    col2 = row.column()
    col2.prop(context.object.geargen, "invert_helical")
    col2.prop(context.object.geargen, "inner_gear_depth")
        
    col.label(text="Overrides")

    row = col.row()

    col2 = row.column()

    objectprop(context, col2, "modulus")
    objectprop(context, col2, "depth")
    objectprop(context, col2, "thickness")

    objectprop(context, col2, "helical_on")
    objectprop(context, col2, "double_helical")
    objectprop(context, col2, "helical_angle")
    objectprop(context, col2, "thickness")
    
    col2 = row.column()
    objectprop(context, col2, "pressure_angle")
    objectprop(context, col2, "backlash")
    objectprop(context, col2, "helical_angle")

    row2 = col2.column()
    objectprop(context, row2, "genshaft")
    objectprop(context, row2, "shaft_diameter")
    
    row2 = col2.column()
    objectprop(context, row2, "key_shaft")
    
    row2 = col2.column()
    row2.enabled = gear.key_shaft
    
    objectprop(context, row2, "key_depth")
    
    row2 = col2.column()
    objectprop(context, row2, "spacer_on")
    objectprop(context, row2, "spacer_width")
    objectprop(context, row2, "spacer_thick")
    objectprop(context, row2, "spacer_height")

    row2 = col2.column()
    objectprop(context, row2, "no_cutouts")
        
    row = col.column()
    row.operator("object.geargen_recalc_all_gears")
    
class GearPanel(bpy.types.Panel):    
    bl_label = "Gear Generation"
    bl_idname = "OBJECT_PT_geargen_settings"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    def draw(self, context):
        layout = self.layout
        gear = context.scene.geargen
        
        uifunc(self, context, context.object.geargen)

class SceneGearPanel(bpy.types.Panel):    
    bl_label = "Default Gear Settings"
    bl_idname = "SCENE_PT_geargen_settings"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        row = self.layout.row()
        col = row.column()
        
        gear = context.scene.geargen
        
        col.prop(context.scene.geargen, "auto_generate")
        
        col.prop(context.scene.geargen, "depth")
        col.prop(context.scene.geargen, "modulus")
        col.prop(context.scene.geargen, "backlash")
        col.prop(context.scene.geargen, "thickness")
        col.prop(context.scene.geargen, "pressure_angle")
        col.prop(context.scene.geargen, "spacer_on");
        
        col.label(text="Cutouts")
        col.prop(context.scene.geargen, "no_cutouts");
        
        col.label(text="Shaft")
        col.prop(context.scene.geargen, "genshaft");
        
        col2 = col.column()
        col2.enabled = context.scene.geargen.genshaft;
        col2.prop(context.scene.geargen, "shaft_diameter");
        col2.prop(context.scene.geargen, "key_shaft");
        col2.prop(context.scene.geargen, "key_depth");
        
        col.label(text="Herringbone Mode")
        col.prop(context.scene.geargen, "double_helical")
        col.prop(context.scene.geargen, "helical_angle")
        col.prop(context.scene.geargen, "subdivisions")
        col.prop(context.scene.geargen, "herring_shape")
        
        col.prop(context.scene.geargen, "herringchannel_on")
        col.prop(context.scene.geargen, "herringchannel_width")
        col.prop(context.scene.geargen, "herringchannel_blend")
        col.prop(context.scene.geargen, "herringchannel_depth")
        
        col.prop(context.scene.geargen, "taper_on")
        if context.scene.geargen.taper_on:
            col.prop(context.scene.geargen, "taper_amount")
            col.prop(context.scene.geargen, "taper_height")

        col.prop(context.scene.geargen, "helical_on")
        col.operator("object.geargen_recalc_all_gears")

registered = False

print("=============")

def register():
    global registered
    if registered: return

    registered = True
    
    bpy.utils.register_class(GearGenProfile)
    bpy.utils.register_class(GearPanel)
    bpy.utils.register_class(SceneGearPanel)
        
    bpy.types.Object.geargen = bpy.props.PointerProperty(
        type=GearGenProfile,
        update=on_prop_update)
    bpy.types.Scene.geargen = bpy.props.PointerProperty(
        type=GearGenProfile,
        update=on_prop_update)

    #bpy.types.OBJECT_PT_context_object.append(uifunc)
    
def unregister():
    global registered
    if not registered: return
    registered = False

    bpy.utils.unregister_class(GearPanel)    
    bpy.utils.unregister_class(GearGenProfile)
    bpy.utils.unregister_class(SceneGearPanel)    

    #bpy.types.OBJECT_PT_context_object.remove(uifunc)

def handleVersioningOb(scene, ob):
    if ob.geargen.version < 0.2:
        ob.geargen.thickness = INHERIT_VALUE
    
    if ob.geargen.version < 0.5:
        ob.geargen.modulus = -1
    
    ob.geargen.version = CURRENT_VERSION
    
def handleVersioningScene(scene, ob):
    gear = scene.geargen
    
    #can happen because of default initialization
    if gear.thickness < 0:
        gear.thickness = -gear.thickness
    if gear.modulus < 0:
        gear.modulus = -gear.modulus
        
    if gear.version < 0.4:
        gear.depth *= 1.5
        
    gear.version = CURRENT_VERSION
    
def handleVersioning(scene, ob):
    stop_prop_updates()
    
    handleVersioningScene(scene, ob)
    handleVersioningOb(scene, ob)
    
    start_prop_updates()
    
if __name__ == "__main__":
    register()
