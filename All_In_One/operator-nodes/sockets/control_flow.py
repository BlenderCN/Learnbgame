import bpy
from .. base_socket_types import ControlFlowBaseSocket

class ControlFlowSocket(ControlFlowBaseSocket, bpy.types.NodeSocket):
    bl_idname = "en_ControlFlowSocket"
    color = (0, 1, 0, 1)