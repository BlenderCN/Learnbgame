import bpy
from ..base_state import *



class physika_simulate_ui(physika_base_ui):
    bl_label = "Simulate"
    physika_state = 'simulate'
    
    def specific_draw(self, context):

        column = self.layout.column()
        column.operator("physika_operators.bake_physika_simulation",
                        text = "Bake")
class physika_simulate_op_previous(physika_base_op_previous):
    physika_state = 'simulate'
    bl_idname = 'physika_simulate_op.previous'

    
class physika_simulate_op_next(physika_base_op_next):
    physika_state = 'simulate'
    bl_idname = 'physika_simulate_op.next'

def register_state():
    state = bpy.data.scenes['Scene'].physika_state_graph.add()
    state.curr = 'simulate'
    state.next = 'animate'
    state.prev = 'parameter'

from . import (bake_operators)    
def register():
    bake_operators.register()
    bpy.utils.register_class(physika_simulate_op_previous)
    bpy.utils.register_class(physika_simulate_op_next)
    bpy.utils.register_class(physika_simulate_ui)
def unregister():
    bake_operators.unregister()
    bpy.utils.unregister_class(physika_simulate_op_previous)
    bpy.utils.unregister_class(physika_simulate_op_next)    
    bpy.utils.unregister_class(physika_simulate_ui)

