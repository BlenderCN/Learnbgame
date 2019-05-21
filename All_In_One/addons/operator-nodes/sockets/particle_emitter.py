import bpy
from .. base_socket_types import RelationalSocket

class ParticleEmitterSocket(RelationalSocket, bpy.types.NodeSocket):
    bl_idname = "en_ParticleEmitterSocket"
    color = (1, 1, 1, 1)