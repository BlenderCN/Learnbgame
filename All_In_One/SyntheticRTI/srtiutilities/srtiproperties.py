
import bpy
from .srtifunc import *

####Global values###
file_lines = []

 ######RNA PROPERTIES######

class light(bpy.types.PropertyGroup):
    light = bpy.props.PointerProperty(name="Light object",
        type = bpy.types.Object,
        description = "A lamp")

class camera(bpy.types.PropertyGroup):
    camera = bpy.props.PointerProperty(name = "Camera object",
        type = bpy.types.Object,
        description = "A camera")

class value(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty(update = update_value_name)
    min = bpy.props.FloatProperty(default = 0)
    max = bpy.props.FloatProperty(default = 1)
    steps = bpy.props.IntProperty(default = 2, min = 2)

class srti_props(bpy.types.PropertyGroup):
    #path to the .lp file
    light_file_path = bpy.props.StringProperty(name="Lights file Path",
        subtype='FILE_PATH',
        default="*.lp",
        description = 'Path to the lights file.')
        
    #output folder path in use if overwrite_folder = true
    output_folder = bpy.props.StringProperty(name="Save file directory",
        subtype='DIR_PATH',
        description = 'Path to the lights file.')
      
    #output name in use if overwrite_name = true
    save_name = bpy.props.StringProperty(name="Save file name",
        default = "Image",
        description = "Export file name")
    
    #main parente empty pointer
    main_parent = bpy.props.PointerProperty(name="Main Parent",
        type=bpy.types.Object,
        description = "Main parent of the group")

    #pointer to object affected by value changes
    main_object = bpy.props.PointerProperty(name="Main object",
        type=bpy.types.Object,
        description = "Main object to apply material")
     
    #boolean to overwrite the output folder path   
    overwrite_folder = bpy.props.BoolProperty(name = "Overwrite export folder",
        default = False,
        description = "Overwrite export folder path")

    #boolean to overwrite the output folder name
    overwrite_name = bpy.props.BoolProperty(name = "Overwrite output name",
        default = False,
        description = "Overwrite output name")
    
    #modified = bpy.props.BoolProperty(name = "Boolean if not animated", default = True)

    selected_value_index = bpy.props.IntProperty()

    list_lights = bpy.props.CollectionProperty(type = light)
    list_cameras = bpy.props.CollectionProperty(type = camera)
    list_values = bpy.props.CollectionProperty(type = value)

def register():
    print("-"*40)
    print("registering properties")
    print(__name__)
    
    ##register properties
    bpy.utils.register_class(light)
    bpy.utils.register_class(camera)
    bpy.utils.register_class(value)
    bpy.utils.register_class(srti_props)
    bpy.types.Scene.srti_props = bpy.props.PointerProperty(type = srti_props)
