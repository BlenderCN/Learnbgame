import bpy
from . gravity import GravityNode
from . attract import AttractNode
from . move_view import MoveViewNode
from . condition import ConditionNode
from . float_math import FloatMathNode
from . rotate_view import RotateViewNode
from . group_input import GroupInputNode
from . vector_math import VectorMathNode
from . move_object import MoveObjectNode
from . group_output import GroupOutputNode
from . particle_info import ParticleInfoNode
from . point_emitter import PointEmitterNode
from . kill_particle import KillParticleNode
from . rotate_object import RotateObjectNode
from . particle_type import ParticleTypeNode
from . combine_vector import CombineVectorNode
from . on_update_event import OnUpdateEventNode
from . spawn_particle import SpawnParticleNode
from . key_press_event import KeyPressEventNode
from . separate_vector import SeparateVectorNode
from . age_trigger import ParticleAgeTriggerNode
from . mouse_click_event import MouseClickEventNode
from . get_parent_object import GetObjectParentNode
from . object_transforms import ObjectTransformsNode
from . set_object_attribute import SetObjectAttributeNode
from . change_particle_color import ChangeParticleColorNode
from . change_particle_velocity import ChangeParticleVelocityNode
from . offset_vector_with_object import OffsetVectorWithObjectNode
from . change_particle_direction import ChangeParticleDirectionNode
from . operators_VSE_filter import SequencerFilterNode
from . operators_VSE_move import SequencerMoveNode
from . operators_VSE_selection import SequencerSelectionNode
from . operators_VSE_sort import SequencerSortNode

node_classes = [
    GravityNode,
    AttractNode,
    MoveViewNode,
    FloatMathNode,
    ConditionNode,
    RotateViewNode,
    GroupInputNode,
    MoveObjectNode,
    VectorMathNode,
    GroupOutputNode,
    ParticleInfoNode,
    PointEmitterNode,
    KillParticleNode,
    ParticleTypeNode,
    RotateObjectNode,
    SpawnParticleNode,
    KeyPressEventNode,
    OnUpdateEventNode,
    CombineVectorNode,
    SeparateVectorNode,
    MouseClickEventNode,
    GetObjectParentNode,
    ObjectTransformsNode,
    SetObjectAttributeNode,
    ParticleAgeTriggerNode,
    ChangeParticleColorNode,
    OffsetVectorWithObjectNode,
    ChangeParticleVelocityNode,
    ChangeParticleDirectionNode,
    SequencerFilterNode,
    SequencerMoveNode,
    SequencerSelectionNode,
    SequencerSortNode
]

def register():
    for cls in node_classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in node_classes:
        bpy.utils.unregister_class(cls)