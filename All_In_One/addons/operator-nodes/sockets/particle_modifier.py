import bpy
from .. base_socket_types import RelationalSocket

class ParticleModifierSocket(RelationalSocket, bpy.types.NodeSocket):
    bl_idname = "en_ParticleModifierSocket"
    color = (0.9, 0.3, 0.3, 1)