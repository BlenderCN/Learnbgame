import bpy

from . float import FloatSocket
from . color import ColorSocket
from . vector import VectorSocket
from . object import ObjectSocket
from . integer import IntegerSocket
from . boolean import BooleanSocket
from . control_flow import ControlFlowSocket
from . particle_type import ParticleTypeSocket
from . particle_emitter import ParticleEmitterSocket
from . particle_modifier import ParticleModifierSocket

data_flow_socket_classes = [
    FloatSocket,
    ColorSocket,
    VectorSocket,
    ObjectSocket,
    IntegerSocket,
    BooleanSocket,
    ParticleTypeSocket,
    ParticleEmitterSocket,
    ParticleModifierSocket
]

socket_classes = data_flow_socket_classes + [ControlFlowSocket]

def register():
    for cls in socket_classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in socket_classes:
        bpy.utils.unregister_class(cls)

def get_data_flow_socket_classes():
    return data_flow_socket_classes[:]