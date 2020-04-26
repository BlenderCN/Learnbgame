
import bpy
from . import utils


class WarCraft3ArmatureSequenceList(bpy.types.PropertyGroup):
    name = bpy.props.StringProperty()


class WarCraft3ArmatureProperties(bpy.types.PropertyGroup):
    bpy_type = bpy.types.Armature
    sequencesList = bpy.props.CollectionProperty(type=WarCraft3ArmatureSequenceList)
    sequencesListIndex = bpy.props.IntProperty(update=utils.set_animation)


class WarCraft3BoneProperties(bpy.types.PropertyGroup):
    bpy_type = bpy.types.Bone
    nodeType = bpy.props.EnumProperty(
        items=[
            ('NONE', 'None', ''),
            ('BONE', 'Bone', ''),
            ('HELPER', 'Helper', ''),
            ('ATTACHMENT', 'Attachment', ''),
            ('EVENT', 'Event', ''),
            ('COLLISION_SHAPE', 'Collision Shape', '')
            ],
        name='Node Type',
        update=utils.set_bone_node_type,
        default='NONE'
        )
