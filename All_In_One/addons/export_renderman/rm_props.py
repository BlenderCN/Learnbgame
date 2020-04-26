
#Blender 2.5 or later to Renderman Exporter
# Copyright (C) 2011 Sascha Fricke



#############################################################################################
#                                                                                           #
#       Begin GPL Block                                                                     #
#                                                                                           #
#############################################################################################
#                                                                                           #
#This program is free software;                                                             #
#you can redistribute it and/or modify it under the terms of the                            #
#GNU General Public License as published by the Free Software Foundation;                   #
#either version 3 of the LicensGe, or (at your option) any later version.                   #
#                                                                                           #
#This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;  #
#without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  #
#See the GNU General Public License for more details.                                       #
#                                                                                           #
#You should have received a copy of the GNU General Public License along with this program; #
#if not, see <http://www.gnu.org/licenses/>.                                                #
#                                                                                           #
#############################################################################################
#                                                                                           #
#       End GPL Block                                                                       #
#                                                                                           #
############################################################################################

#Thanks to: Campbell Barton, Eric Back, Nathan Vegdahl

import bpy
from math import *

import export_renderman
import export_renderman.rm_maintain
from export_renderman.rm_maintain import *

RM_FILTER =(("box", "Box", "Box Filter"),
            ("gaussian", "Gaussian", "Gaussian Filter"),
            ("sinc", "Sinc", "Cube Filter"),
            ("triangle", "Triangle", "Triangle Filter"),
            ("catmull-rom", "Catmull-Rom", ""),
            ("blackman-harris", "Blackman-Harris", ""),
            ("mitchell", "Mitchell", ""),
            ("bessel", "Bessel", ""),
            ("other", "Other", "Custom Filter"))

##################################################################################################################################
#Define classes for Collection and Pointer properties

def float_callback(self, context):
    if repr(type(self.id_data)).find("Lamp") != -1:
        lamp = self.id_data
        rm = self.id_data.renderman[self.id_data.renderman_index]
        try:
            if "intensity" in rm.light_shader_parameter:
                lamp.energy = rm.light_shader_parameter['intensity'].float_one[0] 
            if "coneangle" in rm.light_shader_parameter:
                lamp.spot_size = rm.light_shader_parameter['coneangle'].float_one[0] 
            if "conedeltaangle" in rm.light_shader_parameter:
                lamp.spot_blend = rm.light_shader_parameter['conedeltaangle'].float_one[0]
            if "lightcolor" in rm.light_shader_parameter:
                lamp.color = rm.light_shader_parameter['lightcolor'].colorparameter
        except AttributeError:
            pass
    

class Collection(bpy.types.PropertyGroup):            #All Variable Properties: Shader Parameters, Options, Attributes

    use_var = bpy.props.BoolProperty(default=False, name = "Use Var", description="use name of output variable as value")

    expand = bpy.props.BoolProperty(default = False, name = "Expand")

    parametertype = bpy.props.EnumProperty(items=(
                                ("string", "String", "String Parameter"),
                                ("float", "Float", "Float Parameter"),
                                ("int", "Integer", "Integer Parameter"),
                                ("color", "Color", "Color Parameter"),
                                ),
                                default="string",
                                name = "Parameter Type",
                                description = "Type of Parameter")


    textparameter = bpy.props.StringProperty()

    input_type = bpy.props.EnumProperty(name = "Input Type",
                                                   description = "Where to look for input",
                                                   items = (("display", "Display", ""),
                                                            ("texture", "Texture", ""),
                                                            ("string", "String", "")),
                                                   default = "string")
                                
    export = bpy.props.BoolProperty(default=True, description="export object attribute", options={'ANIMATABLE'})

    preset_include = bpy.props.BoolProperty(default = True, description = "include Attribute in preset", options={'ANIMATABLE'})

    rib_name = bpy.props.StringProperty()                          

    float_one = bpy.props.FloatVectorProperty( precision = 4,
                                        size = 1,
                                        update=float_callback,
                                        options={'ANIMATABLE'})

    float_two = bpy.props.FloatVectorProperty( default=(0.0, 0.0),
                                        precision = 4,
                                        size = 2,
                                        options={'ANIMATABLE'})
                                    
    float_three = bpy.props.FloatVectorProperty(   default=(0.0, 0.0, 0.0),
                                            precision = 4,
                                            size = 3,
                                            options={'ANIMATABLE'})
                                    
    int_one = bpy.props.IntVectorProperty(     step=100,
                                        size=1,
                                        options={'ANIMATABLE'})
                                    
    int_two = bpy.props.IntVectorProperty( step=100,
                                    size=2,
                                    options={'ANIMATABLE'})
                                    
    int_three = bpy.props.IntVectorProperty(   step=100,
                                        size=3,
                                        options={'ANIMATABLE'})                                                                                                                                                                

    colorparameter = bpy.props.FloatVectorProperty(name="Color Parameter",
                                            description="Color Parameter",
                                            subtype='COLOR',
                                            precision = 4,
                                            step = 0.01,
                                            min=0,
                                            max = 1,
                                            default = (0, 0, 0),
                                            options={'ANIMATABLE'})

    parameterindex = bpy.props.IntProperty(default=-1,
                                    min=-1,
                                    max=1000,
                                    options={'ANIMATABLE'})
                            
    vector_size = bpy.props.IntProperty(   default = 1,
                                    min = 1,
                                    max = 3,
                                    options={'ANIMATABLE'})                        

    free = bpy.props.BoolProperty(default = False)

    type = bpy.props.StringProperty()

    rman_type = bpy.props.StringProperty()

class ImageProcessing(bpy.types.PropertyGroup):
    
    process = bpy.props.BoolProperty(    name="Process",
                                        default=True,
                                        description="run Texture processing tool to convert into rendermans intern texture format")
                                        
    overwrite = bpy.props.BoolProperty(name="Overwrite", description="Overwrite existing", default=False)
    
    output = bpy.props.StringProperty(name="Output",
                                  description="name of Image Output")
    
    default_output = bpy.props.BoolProperty(name="Default",
                                            description="Use Default Output",
                                            default=True)
    
    filter = bpy.props.EnumProperty(   name="Filter",
                                        default="box",
                                        items=RM_FILTER,
                                        description="Filter to use when converting the image")
    
    custom_filter = bpy.props.StringProperty(name = "Custom Filter")
    
    width = bpy.props.FloatProperty(     name ="Width",
                                        min = 0,
                                        max = 100,
                                        default = 1,
                                        description = "Filter Width")
    
    swidth = bpy.props.FloatProperty(    name = "s Width",
                                        min = 0,
                                        max = 100,
                                        default = 1,
                                        description = "Filter Width in s direction")
    
    twidth = bpy.props.FloatProperty(    name = "t Width",
                                        min = 0,
                                        max = 100,
                                        default = 1,
                                        description = "Filter Width in t direction")
    
    stwidth = bpy.props.BoolProperty(    name = "st Width",
                                        default = False,
                                        description = "Specify Filter Width in s and t direction separately")
            
    envcube = bpy.props.BoolProperty(name="EnvCube", description="make cubeface environment", default=False)
    
    fov = bpy.props.FloatProperty(name="FOV", description="Field of View for Cube Face Environment", min=0.01, max=360, default=radians(90), subtype="ANGLE")
    
    shadow = bpy.props.BoolProperty(name="Shadow", description="Make Shadwo", default=False)
    
    custom_parameter = bpy.props.StringProperty(name="Custom Parameter")

class DisplayCollection(bpy.types.PropertyGroup):         #Display Drivers
    send = bpy.props.BoolProperty(default = False)

    export = bpy.props.BoolProperty(default=True, name="Export", description="Export this display")

    custom_options = bpy.props.CollectionProperty(type = Collection)

    default_name = bpy.props.BoolProperty(default = True, 
                                            name = "Default", 
                                            description="Default Filename",
                                            update=CB_maintain_display_drivers)
    
    var = bpy.props.StringProperty(default="rgba")                               
                                
    displaydriver = bpy.props.StringProperty()                                

    file = bpy.props.StringProperty()

    filename = bpy.props.StringProperty()

    raw_name = bpy.props.StringProperty()

    quantize_min = bpy.props.IntProperty(min=0, max=100000, default=0, description = "min")

    quantize_max = bpy.props.IntProperty(min=0, max=100000, default=0, description = "max")

    quantize_black = bpy.props.IntProperty(min=0, max=100000, default=0, description = "black")

    quantize_white = bpy.props.IntProperty(min=0, max=100000, default=0, description = "white")

    quantize_presets = bpy.props.EnumProperty(items=    (
                                                                            ("8bit", "8 bit", ""),
                                                                            ("16bit", "16 bit", ""),
                                                                            ("32bit", "32 bit", ""),
                                                                            ("other", "other", "")
                                                                        ),
                                                                        default = "16bit",
                                                                        name = "Quantization")

    processing = bpy.props.PointerProperty(type=ImageProcessing)

    expand = bpy.props.BoolProperty(default=False)

    quantize_expand = bpy.props.BoolProperty(default=False)

    exposure_expand = bpy.props.BoolProperty(default=False)

    processing_expand = bpy.props.BoolProperty(default=False)

    custom_expand = bpy.props.BoolProperty(default=False)
                                        
    gain = bpy.props.FloatProperty(min=0,
                            max=100,
                            default=1,
                            name="Gain")

    gamma = bpy.props.FloatProperty(min=0,
                            max=100,
                            default=1,
                            name="Gamma")

class OutputImages(bpy.types.PropertyGroup):
    render_pass = bpy.props.StringProperty()

class EmptyCollections(bpy.types.PropertyGroup):
    pass

class AttributeOptionGroup(bpy.types.PropertyGroup):
    expand = bpy.props.BoolProperty(default =False)

    export = bpy.props.BoolProperty(default =True)

    preset_include = bpy.props.BoolProperty(default = True, description="include Attribute Group in preset")

    options = bpy.props.CollectionProperty(type=Collection ,
                                name="Renderman Options",
                                description="Renderman Options")

    attributes = bpy.props.CollectionProperty(type=Collection)

class Shader(bpy.types.PropertyGroup):            #Shader Settings Passes
    links = bpy.props.CollectionProperty(type = EmptyCollections)

    attribute_groups = bpy.props.CollectionProperty(type = AttributeOptionGroup)

    shaderpath = bpy.props.StringProperty(name="Shader Path",
                                    description="Path to custom shader",
                                    default="",
                                    options={'HIDDEN'},
                                    subtype='NONE')

    light_shader_parameter = bpy.props.CollectionProperty(type=Collection ,
                                name="LightParam",
                                description="Light Shader Parameter")     
                        
    use_as_light = bpy.props.BoolProperty(name="AreaLight", description="use the object this material is assigned to as an AreaLight")

    preview_scene = bpy.props.StringProperty()

    preview = bpy.props.BoolProperty(name="Preview", description="activate Preview", default=False)
                            
    arealight_shader = bpy.props.StringProperty(name="AreaLight", description="Area Light Shader")                        

    opacity = bpy.props.FloatVectorProperty(name="Opacity",
                                subtype="COLOR",
                                default=(1, 1, 1),
                                precision = 4,
                                step = 0.01,
                                min=0,
                                max=1)
                                
    color = bpy.props.FloatVectorProperty(name="Color",
                                subtype="COLOR",
                                default=(1, 1, 1),
                                precision = 4,
                                step = 0.01,
                                min=0,
                                max=1)                            
                                
                                
    motion_samples = bpy.props.IntProperty(    default=2,
                                    min=2,
                                    max=1000,
                                    name="Motion Samples",
                                    description="number samples to put into motion block")
                                    
    color_blur = bpy.props.BoolProperty(   default=False,
                                name="Color Blur",
                                description="Motion Blur for surface color")
                                
    opacity_blur = bpy.props.BoolProperty(   default=False,
                                name="Opacity Blur",
                                description="Motion Blur for surface opacity") 
                                
    shader_blur = bpy.props.BoolProperty(  default=False,
                                name = "Shader Blur",
                                description = "Motion Blur for parameters of assigned shader")                                                                                                                                             

    matte = bpy.props.BoolProperty(name="Matte",
                                default=False)                            

    #############################################
    #                                           #
    #   Surface Shader Properties               #
    #                                           #
    #############################################


    surface_shader = bpy.props.StringProperty(name="Surface Shader",
                                        description="Name of Surface Shader",
                                        default="matte",
                                        options={'HIDDEN'},
                                        subtype='NONE')

    surface_shader_parameter = bpy.props.CollectionProperty(type=Collection ,
                                name="SurfaceParam",
                                description="Surface Shader Parameter")

    #############################################
    #                                           #
    #   Displacement Shader Properties          #
    #                                           #
    #############################################


    displacement_shader = bpy.props.StringProperty(name="Displacement Shader",
                                        description="Name of Displacement Shader",
                                        default="",
                                        options={'HIDDEN'},
                                        subtype='NONE')

    disp_shader_parameter = bpy.props.CollectionProperty(type=Collection ,
                                name="DisplacementParam",
                                description="Displacement Shader Parameter")

    #############################################
    #                                           #
    #   Interior Shader Properties              #
    #                                           #
    #############################################


    interior_shader = bpy.props.StringProperty(name="Interior Shader",
                                        description="Interior Volume Shader",
                                        default="",
                                        options={'HIDDEN'},
                                        subtype='NONE')

    interior_shader_parameter = bpy.props.CollectionProperty(type=Collection ,
                                name="VolumeParam",
                                description="Volume Shader Parameter")

    #############################################
    #                                           #
    #   Exterior Shader Properties              #
    #                                           #
    #############################################


    exterior_shader = bpy.props.StringProperty(name="Exterior Shader",
                                        description="Exterior Volume Shader",
                                        default="",
                                        options={'HIDDEN'},
                                        subtype='NONE')

    exterior_shader_parameter = bpy.props.CollectionProperty(type=Collection ,
                                name="VolumeParam",
                                description="Volume Shader Parameter")
                        
    #############################################
    #                                           #
    #   Atmosphere Shader Properties            #
    #                                           #
    #############################################


    atmosphere_shader = bpy.props.StringProperty(name="Atmosphere Shader",
                                        description="Atmosphere Volume Shader",
                                        default="",
                                        options={'HIDDEN'},
                                        subtype='NONE')

    atmosphere_shader_parameter = bpy.props.CollectionProperty(type=Collection ,
                                name="VolumeParam",
                                description="Volume Shader Parameter")

    atmosphere_parameter_index = bpy.props.IntProperty(name="Volume Shader Parameter Index",
                        description="",
                        default=-1,
                        min=-1,
                        max=1000)

class CustomCodeCollection(bpy.types.PropertyGroup):
    foreach = bpy.props.BoolProperty(name="For Each Environment Direction",
                                     description="Export Code for each environment direction or only for the last",
                                     default=False)
    
    position = bpy.props.EnumProperty(name="Position", items=(("begin", "Begin", ""),
                                                              ("end", "End", "")))
    
    world_position = bpy.props.EnumProperty(name="Position", items=(("begin", "Begin", ""),
                                                                    ("end_inside", "End (Inside World Block)", ""),
                                                                    ("end_outside", "End (Outside World Block)", "")))
    
    particle_position = bpy.props.EnumProperty(name="Position", items=(("begin", "Begin", ""),
                                                                        ("end", "End", ""),
                                                                        ("begin_data", "Begin (Data)", ""),
                                                                        ("end_data", "End (Data)", "")))
    
    parameter = bpy.props.PointerProperty(type=Collection)
        
    image_prcessing = bpy.props.PointerProperty(type=ImageProcessing)
    
    all_dirs = bpy.props.BoolProperty(name="All Directions",
                                      description="Convert file name input into 6 files"
                                                   + "replacing [dir] with the direction",
                                      default=True)
    
    makeshadow = bpy.props.BoolProperty(name="MakeShadow (RIB)",
                                        default=False,
                                        description="Convert Image into Shadowmap")
    
    makecubefaceenv = bpy.props.BoolProperty(name="MakeCubeFaceEnvironment (RIB)",
                                    default=False,
                                    description="Convert Images into Cubic Environment")
    
    output = bpy.props.StringProperty(name="Output",
                                  description="name of Image Output")
    
    default_output = bpy.props.BoolProperty(name="Default",
                                            description="Use Default Output",
                                            default=True)
    
    filter = bpy.props.EnumProperty(   name="Filter",
                                        default="box",
                                        items=RM_FILTER,
                                        description="Filter to use when converting the image")
    
    custom_filter = bpy.props.StringProperty(name = "Custom Filter")
    
    width = bpy.props.FloatProperty(     name ="Width",
                                        min = 0,
                                        max = 100,
                                        default = 1,
                                        description = "Filter Width")
    
    swidth = bpy.props.FloatProperty(    name = "s Width",
                                        min = 0,
                                        max = 100,
                                        default = 1,
                                        description = "Filter Width in s direction")
    
    twidth = bpy.props.FloatProperty(    name = "t Width",
                                        min = 0,
                                        max = 100,
                                        default = 1,
                                        description = "Filter Width in t direction")
    
    stwidth = bpy.props.BoolProperty(    name = "st Width",
                                        default = False,
                                        description = "Specify Filter Width in s and t direction separately")
    
    blur = bpy.props.FloatProperty(name="Blur", min=0, max=1000, default=1.0)
        
    fov = bpy.props.FloatProperty(name="FOV", description="Field of View for Cube Face Environment", min=0.01, max=360, default=radians(90), subtype="ANGLE")

class LightCollection(bpy.types.PropertyGroup):           #
    illuminate = bpy.props.BoolProperty(name="Illuminate",
                                default=True)

class ObjectParameters(bpy.types.PropertyGroup):            #Object Attributes
    links = bpy.props.CollectionProperty(type = EmptyCollections)

    custom_code = bpy.props.CollectionProperty(type = CustomCodeCollection)

    custom_code_index = bpy.props.IntProperty(min = -1, max = 100, default = -1)

    attribute_groups = bpy.props.CollectionProperty(type=AttributeOptionGroup)

    lightlist = bpy.props.CollectionProperty(type=EmptyCollections)

    shadingrate = bpy.props.FloatProperty(name="Shading Rate",
                                    min = 0,
                                    max = 100,
                                    default = 1)
                                    
    transformation_blur = bpy.props.BoolProperty(name="transformation Blur",
                                                default=False,
                                                description="apply motion blur to the transformation of this object")
                                        
    deformation_blur = bpy.props.BoolProperty(   name="deformation Blur",
                                                default = False,
                                                description = "apply motion blur to the deformation of this object")
                                                
                                                
                                                
    motion_samples = bpy.props.IntProperty(  name="motion samples",
                                            min = 2,
                                            max = 10,
                                            default = 2,
                                            description="number of motion samples(must be no smaller than motion length")                                           

class ClientParameters(bpy.types.PropertyGroup):
        
    client = bpy.props.StringProperty()

    output = bpy.props.StringProperty()

    preset = bpy.props.StringProperty()

    render_pass = bpy.props.StringProperty()

    pass_name = bpy.props.StringProperty()

    request_pass = bpy.props.StringProperty()

    index = bpy.props.IntProperty(min = 0, max = 100, default = 0)

class PathProperties(bpy.types.PropertyGroup):            #
    lamp_type = bpy.props.EnumProperty(items=(
                                            ("spot", "Spot", "Spot Light"),
                                            ("point", "Point", "Point Light"),
                                            ("directional", "Directional", "Directional Light"),
                                            ),
                                    default="point",
                                    name="Light Type",
                                    description="How to draw this light in Blenders Viewport")

    fullpath = bpy.props.StringProperty(default = "")

    mod_time = bpy.props.IntProperty()

    tmp_mod_time = bpy.props.IntProperty()

class Paths(bpy.types.PropertyGroup):             #Shader Paths
    shaderpaths = bpy.props.CollectionProperty(type = PathProperties)

    shadercollection = bpy.props.CollectionProperty(type = PathProperties)

    surface_collection = bpy.props.CollectionProperty(type = PathProperties)

    displacement_collection = bpy.props.CollectionProperty(type = PathProperties)

    volume_collection = bpy.props.CollectionProperty(type = PathProperties)

    light_collection = bpy.props.CollectionProperty(type = PathProperties)

    imager_collection = bpy.props.CollectionProperty(type = PathProperties)

    shaderpathsindex = bpy.props.IntProperty(min = -1,
                        max = 1000,
                        default = -1)

class RendermanLightSettings(bpy.types.PropertyGroup):            #
    pass

class RendermanPixelFilter(bpy.types.PropertyGroup):          #Filter Settings
    filterlist = bpy.props.EnumProperty(items=RM_FILTER,
                                    default="box",
                                    name = "PixelFilter")

    customfilter = bpy.props.StringProperty(name="Custom Filter",
                                        default = "")

    filterwidth = bpy.props.FloatProperty(min = 0,
                                        max = 100,
                                        default = 1)

    filterheight = bpy.props.FloatProperty(min = 0,
                                        max = 100,
                                        default = 1)

class DisplayDrivers(bpy.types.PropertyGroup):
    custom_parameter = bpy.props.CollectionProperty(type = Collection)

class Hider(bpy.types.PropertyGroup):
    options = bpy.props.CollectionProperty(type=Collection)

class RendermanTexture(bpy.types.PropertyGroup):
    type = bpy.props.EnumProperty(name="Type", 
                                    default="none", 
                                    update=maintain_texture_type,
                                    items=(
                                                                    ("none", "None", ""),
                                                                    ("file", "Image File", ""),
                                                                    ("bake", "Bake File", "")))

    processing = bpy.props.PointerProperty(type = ImageProcessing)                                                       

class ParticleExportVars(bpy.types.PropertyGroup):
    path = bpy.props.StringProperty(name="Path", description="relative python path to particle attribute")

class ParticlePasses(bpy.types.PropertyGroup):
    custom_code = bpy.props.CollectionProperty(type = CustomCodeCollection)

    custom_code_index = bpy.props.IntProperty(min = -1, max = 100, default = -1)

    links = bpy.props.CollectionProperty(type = EmptyCollections)

    motion_blur = bpy.props.BoolProperty(name = "Motion Blur", default=False, description = "Activate Motion Blur for Particles")

    motion_samples = bpy.props.IntProperty(name = "motion samples", description="Number samples to export in this motion block", min=2, max = 100, default = 2)

    render_type = bpy.props.EnumProperty(  name = "Render Type",
                                        description = "Choose how to render the particles",
                                        items = (   ("Points", "Points", "Points"),
                                                    ("Object", "Object", "Object"),
                                                    ("Group", "Group", "Group"),
                                                    ("Archive", "Archive", "Archive")))

    size_factor = bpy.props.FloatProperty(min=0, max=10000, default=1, name="Size Multiplier", description="multiply size of particles")

    constant_size = bpy.props.BoolProperty(default=False, name="Constand Width", description="Export size for each particle individually")
                                                    
    object = bpy.props.StringProperty(name = "Object", description ="Object to use for Rendering Particles")

    archive = bpy.props.StringProperty(name ="Archive", description  = "Archive to load for Rendering Particles", subtype = "FILE_PATH") 

    group = bpy.props.StringProperty(name = "Group", description ="Objects of group to use for Rendering Particles")                                              

    attribute_groups = bpy.props.CollectionProperty(type=AttributeOptionGroup)

    material_slot = bpy.props.IntProperty(name = "Material Slot",
                                                         description = "Material Slot to use",
                                                         min = -1,
                                                         max = 100,
                                                         default = 1)

    export_vars = bpy.props.CollectionProperty(type=ParticleExportVars)

class RibStructure(bpy.types.PropertyGroup):
    ### Rib Structure Settings
    own_file = bpy.props.BoolProperty(default = True, name = "Own File", description="write into own RIB Archive")

    filename = bpy.props.StringProperty(name="File", default="", subtype = 'FILE_PATH')

    default_name = bpy.props.BoolProperty(default = True, 
                                            name = "Default Name", 
                                            description = "Default RIB Archive Name",
                                            update=maintain_rib_structure)

    overwrite = bpy.props.BoolProperty(default = True, name = "Overwrite", description="overwrite existing files")

    expand = bpy.props.BoolProperty(default=False, name="Expand", description="Expand Properties")

    folder = bpy.props.StringProperty(default = "")

class RibStructureBase(bpy.types.PropertyGroup):
    frame = bpy.props.PointerProperty(type=RibStructure)

    render_pass = bpy.props.PointerProperty(type = RibStructure)

    settings = bpy.props.PointerProperty(type = RibStructure)

    world = bpy.props.PointerProperty(type = RibStructure)

    object_blocks = bpy.props.PointerProperty(type = RibStructure)

    objects = bpy.props.PointerProperty(type = RibStructure)

    lights = bpy.props.PointerProperty(type = RibStructure)

    particles = bpy.props.PointerProperty(type = RibStructure)

    particle_data = bpy.props.PointerProperty(type = RibStructure)

    meshes = bpy.props.PointerProperty(type = RibStructure)

    materials = bpy.props.PointerProperty(type = RibStructure)

class RendermanCamera(bpy.types.PropertyGroup):
    respercentage = bpy.props.IntProperty(min=1, max=100, default=100, subtype='PERCENTAGE', name="Resolution Percentage")

    res = bpy.props.IntProperty(min = 1, max = 100000, default = 512, name = "Resolution")

    fov = bpy.props.FloatProperty(default = 90, min=0.001, max= 360, name="FOV")

    depthoffield = bpy.props.BoolProperty(default = False,
                            name = "DOF")
                            
    dof_distance = bpy.props.FloatProperty(default = 1, name = "DOF Distance")

    focal_length = bpy.props.FloatProperty(min=0,
                            default=0,
                            name="Focal Length")

    fstop = bpy.props.FloatProperty(min=0,
                            default=2.8,
                            name="F-Stop")

    use_lens_length = bpy.props.BoolProperty(default=True,
                            name="Use Camera Lens")
                            
    perspective_blur = bpy.props.BoolProperty(   name="perspective_blur",
                                                default = False,
                                                description = "apply motion blur to the viewing angle of this camera")
                                                
    transformation_blur = bpy.props.BoolProperty(name="transformation Blur",
                                                default=False,
                                                description="apply motion blur to the transformation of this object")                     

    near_clipping = bpy.props.FloatProperty(min = 0,
                                        max = 1000000,
                                        default = 1)

    far_clipping = bpy.props.FloatProperty(min = 0,
                                        max = 1000000,
                                        default = 30)

class VarCollections(bpy.types.PropertyGroup):
    type_ = bpy.props.StringProperty()

class passes(bpy.types.PropertyGroup):            #passes
    linkToMe = bpy.props.BoolProperty(default=False)
    export = bpy.props.BoolProperty(name="Export", description="Export this Render Pass", default=True)

    client = bpy.props.StringProperty()

    requested = bpy.props.BoolProperty(default = False)

    displaydrivers = bpy.props.CollectionProperty(type=DisplayCollection)

    displayindex = bpy.props.IntProperty(  default = -1,
                                min=-1,
                                max=1000)

    output_images = bpy.props.CollectionProperty(type = OutputImages)

    hider_list = bpy.props.CollectionProperty(type=Hider)
    
    hider = bpy.props.StringProperty()
    
    pixelsamples_x = bpy.props.IntProperty(name="PixelSamples",
                    default = 2,
                    min = 1,
                    max = 100)

    pixelsamples_y = bpy.props.IntProperty(name="PixelSamples",
                        default = 2,
                        min = 1,
                        max = 100)


    pixelfilter = bpy.props.PointerProperty(type=RendermanPixelFilter)

    imagedir = bpy.props.StringProperty(name="Image Folder",
                            description="Name of Image Output Folder",
                            default="images",
                            options={'HIDDEN'})


    exportobjects = bpy.props.BoolProperty(name="Export All Objects",
                        description="Export All Objects to .rib files",
                        default=True)

    exportlights = bpy.props.BoolProperty(name="Export All Lights",
                        description="Export All Lights to Scene .rib file",
                        default=True)

    exportanimation = bpy.props.BoolProperty(name="Export Animation",
                        default=True)

    shadow = bpy.props.BoolProperty(name="Export Animation",
                        default=False)

    sceneindex = bpy.props.IntProperty(name="Object Index",
                        description = "",
                        default = -1,
                        min = -1,
                        max = 10000)

    objectgroup = bpy.props.StringProperty(name="Object Group",
                            description="export only objects in this group")

    lightgroup = bpy.props.StringProperty(name="Light Group",
                            description="export only lights in this group")

    filename = bpy.props.StringProperty(default = "")

    environment = bpy.props.BoolProperty(default = False)

    camera_object = bpy.props.StringProperty()

    motionblur = bpy.props.BoolProperty(default=False,
                                name="Motion Blur",
                                description = "render motion blur for this pass")

    shutter_type = bpy.props.EnumProperty(name = "Shutter Type",
                                                 items = (  ("angle", "Angle", ""),
                                                            ("seconds", "Seconds", "")),
                                                 default = "seconds",
                                                 update=maintain_shutter_types)
                            
    shutterspeed_sec = bpy.props.FloatProperty(name="Shutter Speed",
                                min=0.0001,
                                max=1000,
                                precision = 4,
                                default=0.01,
                                unit = 'TIME',
                                update=maintain_max_shutterspeed,
                                description="Amount of time the shutter is open(in seconds)")

    shutterspeed_ang = bpy.props.FloatProperty(name="Shutter Speed",
                                min=0.0001,
                                max=1000,
                                precision = 4,
                                default=180,
                                unit = 'ROTATION',
                                update=maintain_max_shutterspeed,
                                description="Amount of time the shutter is open(in degrees)")   

    option_groups = bpy.props.CollectionProperty(type=AttributeOptionGroup,
                                name="Option Groups",
                                description="Renderman Option Groups")
                                
    renderresult = bpy.props.StringProperty()                            

    scene_code = bpy.props.CollectionProperty(type = CustomCodeCollection)

    scene_code_index = bpy.props.IntProperty(min = -1, max = 1000, default = -1)

    world_code = bpy.props.CollectionProperty(type = CustomCodeCollection)

    world_code_index = bpy.props.IntProperty(min = -1, max = 1000, default = -1)

    attribute_groups = bpy.props.CollectionProperty(type=AttributeOptionGroup)
    
    global_shader = bpy.props.PointerProperty(type = Shader)

    override_shadingrate = bpy.props.BoolProperty(name="Override ShadingRate", description="Override ShadingRate of Objects", default=False)

    shadingrate = bpy.props.FloatProperty(name="ShadingRate", description="", min=0, max=100, default=1)

    #############################################
    #                                           #
    #   Imager Shader Properties                #
    #                                           #
    #############################################


    imager_shader = bpy.props.StringProperty(name="Imager Shader",
                                        description="Name of Imager Shader",
                                        default="",
                                        options={'HIDDEN'},
                                        subtype='NONE')

    imager_shader_parameter = bpy.props.CollectionProperty(type=Collection ,
                                name="ImagerParam",
                                description="Imager Shader Parameter")

    imager_shader_parameter_index = bpy.props.IntProperty(name="Imager Shader Parameter Index",
                        description="",
                        default=-1,
                        min=-1,
                        max=1000)

class RendermanSceneSettings(bpy.types.PropertyGroup):            #Renderman Scene Settings
    shellscript_create = bpy.props.BoolProperty(name="Create shell script", description="Create batchfile/shellscript to start rendering later", default=False)

    shellscript_append = bpy.props.BoolProperty(name="Append", description="Append to existing file", default=False)

    shellscript_file = bpy.props.StringProperty(name="Script File", description="Path to the script file", subtype="FILE_PATH")

    bi_render = bpy.props.BoolProperty(name="Use BI Render Op", description="Use Blender's default render Operator(may crash more likely. Save often!)", default=True)
    requests = bpy.props.CollectionProperty(type = ClientParameters)

    displays = bpy.props.CollectionProperty(type=DisplayDrivers)

    display_index = bpy.props.IntProperty(min = -1, max = 1000, default = -1)

    output_images = bpy.props.CollectionProperty(type = OutputImages)
    
    hider_list = bpy.props.CollectionProperty(type=Hider)

    hider_list_index = bpy.props.IntProperty(  min=-1,
                                                    max=10000,
                                                    default=-1)
                                        
    default_hider = bpy.props.StringProperty()    
       
    rib_structure = bpy.props.PointerProperty(type=RibStructureBase)
    
    var_collection = bpy.props.CollectionProperty( name="Output Value",
                                                    type=VarCollections
                                                    )

    facevertex = bpy.props.BoolProperty(name="facevertex",
                            default = False)
                            
    shaders = bpy.props.PointerProperty(type = Paths)

    shaderpath = bpy.props.StringProperty(subtype='DIR_PATH')

    shaderpath_recursive = bpy.props.BoolProperty(name ="Recursive", description="add sub folders")

    framepadding = bpy.props.IntProperty(default=4,
                        min=1,
                        max=1000)

    passes = bpy.props.CollectionProperty(type=passes)

    passes_index = bpy.props.IntProperty(default=-1,
                                    min=-1,
                                    max=1000,
                                    update=CB_m_render_passes)

    searchpass = bpy.props.StringProperty(name = "Search Pass",
                            default = "")
                            
    exportallpasses = bpy.props.BoolProperty(name="Export All Passes",
                        description="",
                        default=True)

    ##########################################################
    #Settings
    presetname = bpy.props.StringProperty()
    preset_subfolder = bpy.props.StringProperty()
    active_engine = bpy.props.StringProperty()
    basic_expand = bpy.props.BoolProperty(default=False)
    hider_expand = bpy.props.BoolProperty(default=False)
    options_expand = bpy.props.BoolProperty(default=False)
    attributes_expand = bpy.props.BoolProperty(default=False)
    shader_expand = bpy.props.BoolProperty(default=False)
    dir_expand = bpy.props.BoolProperty(default=False)
    drivers_expand = bpy.props.BoolProperty(default=False)

    renderexec = bpy.props.StringProperty(name="Render Executable",
                            description="Render Executable",
                            default="",
                            options={'HIDDEN'},
                            subtype='NONE')

    shaderexec = bpy.props.StringProperty(name="Shader Compiler",
                            description="Shader Compiler Executable",
                            default="",
                            options={'HIDDEN'},
                            subtype='NONE')

    shadersource = bpy.props.StringProperty(name="Source Extension",
                            description="Shader Source Code Extension",
                            default="",
                            options={'HIDDEN'},
                            subtype='NONE')

    shaderinfo = bpy.props.StringProperty(name="Shaderinfo Binary",
                            description="Shader information Tool binary",
                            default="",
                            options={'HIDDEN'},
                            subtype='NONE')

    textureexec = bpy.props.StringProperty(name="Texture Preparation",
                            description ="Texture Preparation Tool",
                            default="",
                            options={'HIDDEN'},
                            subtype="NONE")

    shaderbinary = bpy.props.StringProperty(name="Binary Extension",
                            description="Shader Binary Extension",
                            default="",
                            options={'HIDDEN'},
                            subtype='NONE')

    textureext = bpy.props.StringProperty(name="Texture Extension",
                            description="Texture Extension",
                            default="",
                            options={'HIDDEN'},
                            subtype='NONE')

    displaydrvpath = bpy.props.StringProperty(name="Display Path",
                            description="Path to Display Driver folder",
                            default="",
                            options={'HIDDEN'},
                            subtype='DIR_PATH')
                            
    disp_ext_os_default = bpy.props.BoolProperty(name="OS Lib", description="Default OS Lib extension", default=True)

    disp_ext = bpy.props.StringProperty(name="Extension", description='Custom Display Driver extension(without "."')

    drv_identifier = bpy.props.StringProperty(description = "Prefix or suffix in drivers filename to identify, that its actually a Display Driver")

    default_driver = bpy.props.StringProperty(description = "Default Display Driver")


    #########################################################

    defaultribpath = bpy.props.BoolProperty(default=True)

    ribpath = bpy.props.StringProperty(name="RIB Path",
                            description="Path to Scene RIB File",
                            default="",
                            options={'HIDDEN'},
                            subtype='DIR_PATH')
                                            
    bakedir = bpy.props.StringProperty( name="Bake",
                                            description = "Folder where bake files are stored",
                                            default = "Bakes")                                                                                                                        

    texdir = bpy.props.StringProperty(name="Texturemaps Folder",
                            description="Name of Texture Maps Folder",
                            default="textures",
                            options={'HIDDEN'})

    exportonly = bpy.props.BoolProperty(name="Export Only",
                        description="Only Export Scene Rib File without rendering",
                        default=False,
                        options={'HIDDEN'},
                        subtype='NONE')

    option_groups = bpy.props.CollectionProperty(type=AttributeOptionGroup,
                                name="Option Groups",
                                description="Renderman Option Groups")   
                                
    option_groups_index = bpy.props.IntProperty(min=-1, max=1000, default=-1)


    attribute_groups = bpy.props.CollectionProperty(type=AttributeOptionGroup)
                                
    attribute_groups_index = bpy.props.IntProperty(min=-1, max=1000, default=-1)                            
    
classes = [Collection,
            ImageProcessing,
            DisplayCollection,
            OutputImages,
            EmptyCollections,
            AttributeOptionGroup,
            Shader,
            CustomCodeCollection,
            LightCollection,
            ObjectParameters,
            ClientParameters,
            PathProperties,
            Paths,
            RendermanLightSettings,
            RendermanPixelFilter,
            DisplayDrivers,
            Hider,
            RendermanTexture,
            ParticleExportVars,
            ParticlePasses,
            RibStructure,
            RibStructureBase,
            RendermanCamera,
            VarCollections,
            passes,
            RendermanSceneSettings]
    
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.renderman_settings = bpy.props.PointerProperty(type=RendermanSceneSettings)                       

    bpy.types.Lamp.renderman = bpy.props.CollectionProperty(type=Shader)

    bpy.types.Lamp.renderman_index = bpy.props.IntProperty(min = -1, max = 1000, default = -1)

    Object = bpy.types.Object

    Object.requests = bpy.props.CollectionProperty(type = ClientParameters)

    Object.renderman_camera = bpy.props.PointerProperty(type=RendermanCamera)

    Object.renderman = bpy.props.CollectionProperty(type = ObjectParameters, name="Renderman")

    Object.renderman_index = bpy.props.IntProperty(min = -1, max = 1000, default = -1)

    mesh = bpy.types.Mesh

    mesh.export_normals = bpy.props.BoolProperty(name="Export Normals", default=False)

    mesh.primitive_type = bpy.props.EnumProperty(   name = "PrimitiveType", 
                                                    default="pointspolygons", 
                                                    items=( ("pointspolygons", "PointsPolygons", ""),
                                                            ("points", "Points", ""),
                                                            ("subdivisionmesh", "SubdivisionMesh",""),
                                                            ("quadrics", "Quadrics", "Quadrics")))
                                                                                        
    mesh.export_type = bpy.props.EnumProperty(name = "Export As", default="ReadArchive", items=(  ("ReadArchive", "ReadArchive", ""),
                                                                                ("DelayedReadArchive", "DelayedReadArchive", ""),
                                                                                ("ObjectInstance", "ObjectInstance", "")))

    mesh.size_vgroup = bpy.props.StringProperty(name="Vertex Group", description="Control the siza of each point via Vertex Group", default ="")  

    mesh.points_scale = bpy.props.FloatProperty(name ="Points Scale", description="Scale of Points", min=0, max=10000, default=1)
                                                        
    mesh.export_type = bpy.props.EnumProperty(name = "Export As", default="ReadArchive", items=(  ("ReadArchive", "ReadArchive", ""),
                                                                                ("DelayedReadArchive", "DelayedReadArchive", ""),
                                                                                ("ObjectInstance", "ObjectInstance", "")))                                                     
                                                                                                 
    mat = bpy.types.Material
    tex = bpy.types.Texture

    tex.renderman = bpy.props.PointerProperty(type=RendermanTexture)

    mat.renderman = bpy.props.CollectionProperty(type=Shader)

    mat.renderman_index = bpy.props.IntProperty(min = -1, max = 1000, default = -1)

    psettings = bpy.types.ParticleSettings

    psettings.renderman = bpy.props.CollectionProperty(type = ParticlePasses)

    psettings.renderman_index = bpy.props.IntProperty(min = -1, max = 1000, default = -1)


def unregister():
    bpy.utils.unregister_module(__name__)



