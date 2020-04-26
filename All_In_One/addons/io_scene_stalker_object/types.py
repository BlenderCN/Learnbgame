
import bpy


def set_object_flags(self, context):
    object = context.object
    if object:
        objectType = object.stalker.object_type
        s = object.stalker
        if objectType == 'STATIC':
            s.flagDynamic = False
            s.flagProgressive = False
            s.flagUsingLOD = False
            s.flagHOM = False
            s.flagMultipleUsage = False
            s.flagSoundOccluder = False
        elif objectType == 'DYNAMIC':
            s.flagDynamic = True
            s.flagProgressive = False
            s.flagUsingLOD = False
            s.flagHOM = False
            s.flagMultipleUsage = False
            s.flagSoundOccluder = False
        elif objectType == 'PROGRESSIVE_DYNAMIC':
            s.flagDynamic = True
            s.flagProgressive = True
            s.flagUsingLOD = False
            s.flagHOM = False
            s.flagMultipleUsage = False
            s.flagSoundOccluder = False
        elif objectType == 'HOM':
            s.flagDynamic = False
            s.flagProgressive = False
            s.flagUsingLOD = False
            s.flagHOM = True
            s.flagMultipleUsage = False
            s.flagSoundOccluder = False
        elif objectType == 'MULTIPLE_USAGE':
            s.flagDynamic = False
            s.flagProgressive = False
            s.flagUsingLOD = True
            s.flagHOM = False
            s.flagMultipleUsage = True
            s.flagSoundOccluder = False
        elif objectType == 'SOUND_OCCLUDER':
            s.flagDynamic = False
            s.flagProgressive = False
            s.flagUsingLOD = False
            s.flagHOM = False
            s.flagMultipleUsage = False
            s.flagSoundOccluder = True


class StalkerObjectProperties(bpy.types.PropertyGroup):
    bpy_type = bpy.types.Object
    object_type = bpy.props.EnumProperty(items=[
        ('STATIC', 'Static', ''),
        ('DYNAMIC', 'Dynamic', ''),
        ('PROGRESSIVE_DYNAMIC', 'Progressive Dynamic', ''),
        ('HOM', 'HOM', ''),
        ('MULTIPLE_USAGE', 'Multiple Usage', ''),
        ('SOUND_OCCLUDER', 'Sound Occluder', ''),
        ('OTHER', 'Other', '')],
        name='Object Type', default='STATIC', update=set_object_flags)
    flagDynamic = bpy.props.BoolProperty(name='Dynamic', default=False)
    flagProgressive = bpy.props.BoolProperty(name='Progressive', default=False)
    flagUsingLOD = bpy.props.BoolProperty(name='Using LOD', default=False)
    flagHOM = bpy.props.BoolProperty(name='HOM', default=False)
    flagMultipleUsage = bpy.props.BoolProperty(name='Multiple Usage', default=False)
    flagSoundOccluder = bpy.props.BoolProperty(name='Sound Occluder', default=False)
    version = bpy.props.IntProperty(name='Object Format Version', default=16, min=0, max=2**16-1)
    user_data = bpy.props.StringProperty(name='User Data', default='')
    creator = bpy.props.StringProperty(name='Creator', default='')
    create_time = bpy.props.IntProperty(name='Create Time', default=0)
    editor = bpy.props.StringProperty(name='Editor', default='')
    edit_time = bpy.props.IntProperty(name='Edit Time', default=0)
    motion_reference = bpy.props.StringProperty(name='Motion Reference', default='')
    lod_reference = bpy.props.StringProperty(name='LOD Reference', default='')


class StalkerMeshProperties(bpy.types.PropertyGroup):
    bpy_type = bpy.types.Mesh
    version = bpy.props.IntProperty(name='Mesh Format Version', default=17, min=0, max=2**16-1)
    flag_visible = bpy.props.BoolProperty(name='Mesh Flag Visible', default=True)
    flag_locked = bpy.props.BoolProperty(name='Mesh Flag Locked', default=False)
    flag_smooth_group_mask = bpy.props.BoolProperty(name='Mesh Flag Smooth Group Mask', default=False)
    option_1 = bpy.props.IntProperty(name='Mesh Option 1', default=0)
    option_2 = bpy.props.IntProperty(name='Mesh Option 2', default=0)


class StalkerMaterialProperties(bpy.types.PropertyGroup):
    bpy_type = bpy.types.Material
    engine_shader = bpy.props.StringProperty(name='Engine Shader', default='default')
    compiler_shader = bpy.props.StringProperty(name='Compiler Shader', default='default')
    game_material = bpy.props.StringProperty(name='Game Material', default='default')
    two_sided = bpy.props.BoolProperty(name='Two Sided', default=False)
