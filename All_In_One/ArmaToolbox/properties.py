# GPL 3.0

import bpy
from bpy.props import (    
    BoolProperty,
    EnumProperty,
    FloatProperty,
    IntProperty,
    PointerProperty,
    StringProperty,
)



lodPresets=[
    ## Graphical LOD
        ('-1.0', 'Custom', 'Custom Viewing Distance'),
    ## Functional lod
        ('1.000e+3', 'View Gunner', 'View Gunner'),
        ('1.100e+3', 'View Pilot', 'View Pilot'),
        ('1.200e+3', 'View Cargo', 'View Cargo'),
        ('1.000e+4', 'Stencil Shadow', 'Stencil Shadow'),
        ('1.001e+4', 'Stencil Shadow 2', 'Stencil Shadow 2'),
        ('1.100e+4', 'Shadow Volume', 'Shadow Volume'),
        ('1.101e+4', 'Shadow Volume 2', 'Shadow Volume 2'),
        ('1.000e+13', 'Geometry', 'Geometry'),
        ('1.000e+15', 'Memory', 'Memory'),
        ('2.000e+15', 'Land Contact', 'Land Contact'),
        ('3.000e+15', 'Roadway', 'Roadway'),
        ('4.000e+15', 'Paths', 'Paths'),
        ('5.000e+15', 'HitPoints', 'Hit Points'),
        ('6.000e+15', 'View Geometry', 'View Geometry'),
        ('7.000e+15', 'Fire Geometry', 'Fire Geometry'),
        ('8.000e+15', 'View Cargo Geometry', 'View Cargo Geometry'),
        ('9.000e+15', 'View Cargo Fire Geometry', 'View Cargo Fire Geometry'),
        ('1.000e+16', 'View Commander', 'View Commander'),
        ('1.100e+16', 'View Commander Geometry', 'View Commander Geometry'),
        ('1.200e+16', 'View Commander Fire Geometry', 'View Commander Fire Geometry'),
        ('1.300e+16', 'View Pilot Geometry', 'View Pilot Geometry'),
        ('1.400e+16', 'View Pilot Fire Geometry', 'View Pilot Fire Geometry'),
        ('1.500e+16', 'View Gunner Geometry', 'View Gunner Geometry'),
        ('1.600e+16', 'View Gunner Fire Geometry', 'View Gunner Fire Geometry'),
        ('1.700e+16', 'Sub Parts', 'Sub Parts'),
        ('1.800e+16', 'Shadow Volume - View Cargo', 'Cargo View shadow volume'),
        ('1.900e+16', 'Shadow Volume - View Pilot', 'Pilot View shadow volume'),
        ('2.000e+16', 'Shadow Volume - View Gunner', 'Gunner View shadow volume'),
        ('2.100e+16', 'Wreck', 'Wreckage'),
        ('2.000e+13', 'Geometry Buoyancy', 'Geometry Buoyancy'),
        ('4.000e+13', 'Geometry PhysX', 'Geometry PhysX'),
        ('2.000e+4',  'Edit', 'Edit'),
        ]

textureTypes = [
            ("CO", "CO", "Color Value"),
            ("CA", "CA", "Texture with Alpha"),
            ("LCO", "LCO", "Terrain Texture Layer Color"),
            ("SKY", "SKY", "Sky texture"),
            ("NO", "NO", "Normal Map"),
            ("NS", "NS", "Normal map specular with Alpha"),
            ("NOF", "NOF", "Normal map faded"),
            ("NON", "NON", "Normal map noise"),
            ("NOHQ", "NOHQ", "Normal map High Quality"),
            ("NOPX", "NOPX", "Normal Map with paralax"),
            ("NOVHQ", "NOVHQ", "two-part DXT5 compression"),
            ("DT", "DT", "Detail Texture"),
            ("CDT", "CDT", "Colored detail texture"),
            ("MCO", "MCO", "Multiply color"),
            ("DTSMDI", "DTSMDI", "Detail SMDI map"),
            ("MC", "MC", "Macro Texture"),
            ("AS", "AS", "Ambient Shadow texture"),
            ("ADS", "ADS", "Ambient Shadow in Blue"),
            ("PR", "PR", "Ambient shadow from directions"),
            ("SM", "SM", "Specular Map"),
            ("SMDI", "SMDI", "Specular Map, optimized"),
            ("mask", "mask", "Mask for multimaterial"),
            ("TI", "TI", "Thermal imaging map")
]

textureClass = [
            ("Texture", "Texture", "Texture Map"),
            ("Color", "Color", "Procedural Color"),
            ("Custom", "Custom", "Custom Procedural String")
]

###
##   Custom Property Collections
#
class ArmaToolboxNamedProperty(bpy.types.PropertyGroup):
    name : bpy.props.StringProperty(name="Name", 
        description = "Property Name")
    value : bpy.props.StringProperty(name="Value",
        description="Property Value") 

class ArmaToolboxKeyframeProperty(bpy.types.PropertyGroup):
    timeIndex : bpy.props.IntProperty(name="Frame Index",
        description="Frame Index for keyframe")

class ArmaToolboxComponentProperty(bpy.types.PropertyGroup):
    name   : bpy.props.StringProperty(name="name", description="Component name")
    weight : bpy.props.FloatProperty(name="weight", description="Weight of Component", default = 0.0)

# Would have preferred to have that in ArmaProxy, but apparently that doesn't work.
# Seriously, can I have JAVA plugins for Blender? Please? Python is shit.
class ArmaToolboxProxyProperty(bpy.types.PropertyGroup):
    open   : bpy.props.BoolProperty(name="open", description="Show proxy data in GUI", default=False)
    name   : bpy.props.StringProperty(name="name", description="Proxy name")
    path   : bpy.props.StringProperty(name="path", description="File path", subtype="FILE_PATH")
    index  : bpy.props.IntProperty(name="index", description="Index of Proxy", default=1)

class ArmaToolboxHeightfieldProperties(bpy.types.PropertyGroup):
    isHeightfield : bpy.props.BoolProperty(
        name = "IsArmaHeightfield",
        description = "Is this an ARMA Heightfield object",
        default = False)
    cellSize : bpy.props.FloatProperty(
        name="cell size",
        description = "Size of a single cell in meters",
        default = 4.0)
    northing : bpy.props.FloatProperty(
        name="northing",
        description="Northing",
        default = 200000.0)
    easting : bpy.props.FloatProperty(
        name="easting",
        description = "Easting",
        default = 0)
    undefVal : bpy.props.FloatProperty(
        name="NODATA value",
        description = "Value for Heightfield holes",
        default=-9999)

class ArmaToolboxProperties(bpy.types.PropertyGroup):
    isArmaObject : bpy.props.BoolProperty(
        name = "IsArmaObject",
        description = "Is this an ARMA exportable object",
        default = False)
    
    # Mesh Objects
    lod : bpy.props.EnumProperty(
        name="LOD Type",
        description="Type of LOD",
        items=lodPresets,
        default='-1.0')
    lodDistance : bpy.props.FloatProperty(
        name="Distance",
        description="Distance of Custom LOD",
        default=1.0)
    mass : bpy.props.FloatProperty(
        name="Mass",
        description="Object Mass",
        default=1.0)
    massArray : bpy.props.CollectionProperty(type = ArmaToolboxComponentProperty, description="Masses")

    namedProps : bpy.props.CollectionProperty(type = ArmaToolboxNamedProperty,
          description="Named Properties")
    namedPropIndex : bpy.props.IntProperty("namedPropIndex", default = -1)
    
    proxyArray : bpy.props.CollectionProperty(type = ArmaToolboxProxyProperty, description = "Proxies")
    
    # Armature
    keyFrames : bpy.props.CollectionProperty(type = ArmaToolboxKeyframeProperty,
          description="Keyframes")
    keyFramesIndex : bpy.props.IntProperty("keyFrameIndex", default = -1)
    motionVector : bpy.props.FloatVectorProperty(name = "RTM Motion Vector", 
         description = "Motion Vector written to the RTM Animation",
          subtype='TRANSLATION')
    centerBone : bpy.props.StringProperty(name="Center Of Animation", 
          description="The center of animation for calculating the motion vector")
    
class ArmaToolboxMaterialProperties(bpy.types.PropertyGroup):
    texture : bpy.props.StringProperty(
        name="Face Texture", 
        description="ARMA texture", 
        subtype="FILE_PATH", 
        default="")
    rvMat : bpy.props.StringProperty(
        name="RVMat Material", 
        description="RVMat associated with this materiaL", 
        subtype="FILE_PATH",
        default="")
    texType : bpy.props.EnumProperty(
        name="Color Map Type",
        description="The type/source of the color for this surface",
        items=textureClass)
    colorValue : bpy.props.FloatVectorProperty(
        name= "Color",
        description= "Color for procedural texture",
        subtype= 'COLOR',
        min= 0.0,
        max= 1.0,
        soft_min= 0.0,
        soft_max= 1.0,
        default= (1.0,1.0,1.0))
    colorType : bpy.props.EnumProperty(
        name="Color Type",
        description="The Type of color, corresponding to the suffix of a texture name",
        items = textureTypes)
    colorString : bpy.props.StringProperty (
        name = "Resulting String", 
        description = "Resulting value for the procedural texture")

class ArmaToolboxRenamableProperty(bpy.types.PropertyGroup):
    renamable : bpy.props.StringProperty(name="Texture Path")

class ArmaToolboxGUIProps(bpy.types.PropertyGroup):
    framePanelOpen : bpy.props.BoolProperty(name="Open Frames Settings Panel",
        description="Open or close the settings of the 'Add Frame Range' tool",
        default = False)
    framePanelStart : bpy.props.IntProperty(name="Start of frame range",
        description = "Start of the range of frames to add to the list",
        default = -1, min = 0)
    framePanelEnd : bpy.props.IntProperty(name="ENd of frame range",
        description = "End of the range of frames to add to the list",
        default = -1, min=1)
    framePanelStep : bpy.props.IntProperty(name="Step of frame range",
        description = "Step of the range of frames to add to the list",
        default = 5, min=1)

    bulkRenamePanelOpen : bpy.props.BoolProperty(name="Open Bulk Rename Settings Panel",
        description="Open or close the settings of the 'Bulk Rename' tool",
        default = False) 
    bulkReparentPanelOpen : bpy.props.BoolProperty(name="Open Bulk Reparent Settings Panel",
        description="Open or close the settings of the 'Bulk Reparent' tool",
        default = False) 
    selectionRenamePanelOpen : bpy.props.BoolProperty(name="Open Selection Renaming Settings Panel",
        description="Open or close the settings of the 'Bulk Reparent' tool",
        default = False) 
    rvmatRelocPanelOpen : bpy.props.BoolProperty(name="Open RVMat Relocation Settings Panel",
        description="Open or close the settings of the 'RVMat Relocator' tool",
        default = False) 
    
    hitpointCreatorPanelOpen : bpy.props.BoolProperty(name="Open hitpoint creator settings panel", 
        description="Open or close the 'Hitpoint Creator' tool",
        default = False)
    
    # Bulk Rename features
    renamableList : bpy.props.CollectionProperty(type = ArmaToolboxRenamableProperty,
          description="Renamables")
    renamableListIndex : bpy.props.IntProperty()

    renameFrom : bpy.props.StringProperty("renameFrom", description="Rename From", subtype='FILE_PATH')
    renameTo : bpy.props.StringProperty("renameTo", description="Rename to", subtype='FILE_PATH')
    
    # Bulk Reparent features
    parentFrom : bpy.props.StringProperty("parentFrom", description="Parent From", subtype='DIR_PATH')
    parentTo : bpy.props.StringProperty("parentTo", description="Parent to", subtype='DIR_PATH')
    
    # Selection Rename
    renameSelectionFrom : bpy.props.StringProperty("renameSelectionFrom", description="Rename from")
    renameSelectionTo : bpy.props.StringProperty("renameSelectionTo", description="Rename to")
    
    # RVMat Relocator
    rvmatRelocFile : bpy.props.StringProperty("rvmatRelocFile", description="RVMat to relocate", subtype = 'FILE_PATH')
    rvmatOutputFolder : bpy.props.StringProperty("rvmatOutputFolder", description="RVMat output", subtype = 'DIR_PATH')
      
    
    # Material Relocator
    matOutputFolder : bpy.props.StringProperty("matOutputFolder", description="RVMat output", subtype = 'DIR_PATH')
    matAutoHandleRV : bpy.props.BoolProperty(name="matAutoHandleRV", description="Automatically relocate RVMat", default=True)
    matPrefixFolder : bpy.props.StringProperty("matPrefixFolder", description="Prefix for texture search", subtype = 'DIR_PATH', 
                                               default= "P:\\")
    # Merge as Proxy
    mapProxyObject : bpy.props.StringProperty("mapProxyObject", description="Proxy Object", subtype = 'FILE_PATH')
    mapProxyIndex :  bpy.props.IntProperty("mapProxyIndex", description="Base Index", default=1)
    mapProxyDelete : bpy.props.BoolProperty("mapProxyDelete", description="Delete original", default=True)
    mapProxyEnclose : bpy.props.StringProperty("mapProxyEnclose", description="Enclosed Selection")
    mapOpen : bpy.props.BoolProperty(name="mapOpen", default=False)
    
    # Proxy Path Changer
    proxyPathFrom : bpy.props.StringProperty("proxyPathFrom", description="Proxy Path From", subtype = 'FILE_PATH')
    proxyPathTo : bpy.props.StringProperty("proxyPathTo", description="Proxy path To", subtype = 'FILE_PATH')
    
    # Weight setter
    vertexWeight : bpy.props.FloatProperty("vertexWeight", description="Vertex Weight to set to", default = 0, min=0)
    
    # Selection Tools
    hiddenSelectionName : bpy.props.StringProperty("hiddenSelectionName", description = "Name of the hidden selection to create", default="camo")

    # Hitpoint creator
    hpCreatorSelectionName : bpy.props.StringProperty("hpCreatorSelectionName", description = "Name of the hitpoint selection create", default="_point")
    hpCreatorRadius : bpy.props.FloatProperty("hpCreatorRadius", description = "radius of hitpont sphere", default = 0.3, min = 0.001)

class ArmaToolboxCopyHelper(bpy.types.PropertyGroup):
    name : bpy.props.StringProperty(name="name", 
        description = "Object Name")
    doCopy : bpy.props.BoolProperty(name="doCopy",
        description="Do copy Value") 

def addCustomProperties():
    try:
        if bpy.types.Material.armaMatProps:
            pass
    except:
        bpy.types.Material.armaMatProps = bpy.props.PointerProperty(
            type=ArmaToolboxMaterialProperties,
            description = "Arma Toolbox Properties")  

    try:
        if bpy.types.Object.armaObjProps:
            pass
    except:
        bpy.types.Object.armaObjProps = bpy.props.PointerProperty(
            type = ArmaToolboxProperties,
            description = "Arma Toolbox Properties")

    try:
        if bpy.types.Object.armaHFProps:
            pass
    except:
        bpy.types.Object.armaHFProps = bpy.props.PointerProperty(
            type = ArmaToolboxHeightfieldProperties,
            description = "Arma Toolbox Heightfield Properties")

    try:
        if bpy.types.WindowManager.armaGUIProps:
            pass
    except:
        bpy.types.WindowManager.armaGUIProps = bpy.props.PointerProperty(
            type = ArmaToolboxGUIProps,
            description="Arma Toolbox GUI settings")

class ArmaToolboxFixShadowsHelper(bpy.types.PropertyGroup):
    name : bpy.props.StringProperty(name="name", 
        description = "Object Name")
    fixThis : bpy.props.BoolProperty(name="fixThis",
        description="Fix") 


prpclasses = (
    ArmaToolboxCopyHelper,
    ArmaToolboxNamedProperty,
    ArmaToolboxKeyframeProperty,
    ArmaToolboxComponentProperty,
    ArmaToolboxProxyProperty,
    ArmaToolboxHeightfieldProperties,
    ArmaToolboxProperties,
    ArmaToolboxMaterialProperties,
    ArmaToolboxRenamableProperty,
    ArmaToolboxGUIProps,
    ArmaToolboxFixShadowsHelper,
    
)

def register():
    print ("registering properties")
    from bpy.utils import register_class
    for cls in prpclasses:
        register_class(cls)

def unregister():
    from bpy.utils import unregister_class
    for cls in prpclasses:
        unregister_class(cls)