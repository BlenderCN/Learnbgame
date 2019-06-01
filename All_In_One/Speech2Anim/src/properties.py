import bpy
import os

def make_path_absolute(key):
    """ 
    Prevent Blender's relative paths of doom 
    http://sinestesia.co/blog/tutorials/avoid-relative-paths/
    """

    # This can be a collection property or addon preferences
    props = bpy.context.scene.speech2anim_data
    sane_path = lambda p: os.path.abspath(bpy.path.abspath(p))

    if key in props and props[key].startswith('//'):
        props[key] = sane_path(props[key])

class Speech2AnimVideo(bpy.types.PropertyGroup):
    """ Video list item """
    name = bpy.props.StringProperty()
    path = bpy.props.StringProperty(
        name='Video path',
        description='Absolute path to video',
        subtype='FILE_PATH'
    )

class Speech2AnimTrainingProps(bpy.types.PropertyGroup):
    initialized = bpy.props.BoolProperty()
    training_videos_path = bpy.props.StringProperty(
        name='Training Videos folder',
        description='Path to Training Videos folder',
        update = lambda s,c:make_path_absolute('training_videos_path'),
        subtype='DIR_PATH'
    )
    training_model_path = bpy.props.StringProperty(
        name='Output Model',
        description='Model to be trained with the videos found in the folder',
        update = lambda s,c:make_path_absolute('training_model_path'),
        subtype='FILE_PATH'
    )
    animate_model_path = bpy.props.StringProperty(
        name='Input Model',
        description='Model to use to animate the selected armature',
        update = lambda s,c:make_path_absolute('animate_model_path'),
        subtype='FILE_PATH'
    )
    input_file = bpy.props.StringProperty(
        name='Audio input file',
        description='Reference audio file to animate the selected armature (*.wav)',
        update = lambda s,c:make_path_absolute('input_file'),
        subtype='FILE_PATH',
        
    )
    #################
    # config
    #################
    config_type = bpy.props.EnumProperty(
        name='Configuration file',
        description='Determines which configuration file to use',
        default='DEFAULT',
        items=[
            ('DEFAULT', 'Default', 'Use default configuration file'),
            ('EXTERNAL', 'External', 'Use custom external configuration file')
        ]

    )
    animation_config_type = bpy.props.EnumProperty(
        name='Anim Configuration file',
        description='Determines which configuration file to use for animation',
        default='DEFAULT',
        items=[
            ('DEFAULT', 'Default', 'Use default configuration file'),
            ('EXTERNAL', 'External', 'Use custom external configuration file')
        ]

    )
    external_config_path = bpy.props.StringProperty(
        name='Config file',
        description='Path to the external configuration file',
        update = lambda s,c:make_path_absolute('external_config_path'),
        subtype='FILE_PATH',
    )
    external_animation_config_path = bpy.props.StringProperty(
        name='Config file',
        description='Path to the external configuration file',
        update = lambda s,c:make_path_absolute('external_animation_config_path'),
        subtype='FILE_PATH',
    )
    ########
    # List
    ########
    selected_training_video_index = bpy.props.IntProperty()

    training_videos_list = bpy.props.CollectionProperty(type=Speech2AnimVideo)
    
    """
    overwrite_model = bpy.props.BoolProperty(
        name='Overwrite',
        description='If selected, overwrites the model. Error otherwise'
    )
    """    

def register():
    bpy.utils.register_module(__name__)
    bpy.types.Scene.speech2anim_data = bpy.props.PointerProperty(type=Speech2AnimTrainingProps)

def unregister():
    del bpy.types.Scene.speech2anim_data
    bpy.utils.unregister_module(__name__)
