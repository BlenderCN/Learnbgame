import bpy
from .. base_socket_types import RelationalSocket

class ParticleTypeSocket(RelationalSocket, bpy.types.NodeSocket):
    bl_idname = "en_ParticleTypeSocket"
    color = (0.9, 0.9, 0.1, 1)