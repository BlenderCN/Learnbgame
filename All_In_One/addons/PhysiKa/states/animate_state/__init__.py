import bpy
from ..base_state import *



class physika_animate_ui(physika_base_ui):
    bl_label = 'Animate'
    physika_state = 'animate'
    
    def specific_draw(self, context):
        box = self.layout.box()

        column = box.column(align=True)
        column.operator("physika_operators.animate",
                          text = "Animate")

class physika_animate_op_previous(physika_base_op_previous):
    physika_state = 'animate'
    bl_idname = 'physika_animate_op.previous'

    
class physika_animate_op_next(physika_base_op_next):
    physika_state = 'animate'
    bl_idname = 'physika_animate_op.next'

def register_state():
    state = bpy.data.scenes['Scene'].physika_state_graph.add()
    state.curr = 'animate'
    state.next = 'export'
    state.prev = 'simulate'


from . import animate_operators
def register():
    animate_operators.register()
    bpy.utils.register_class(physika_animate_op_previous)
    bpy.utils.register_class(physika_animate_op_next)
    bpy.utils.register_class(physika_animate_ui)

def unregister():
    animate_operators.unregister()
    bpy.utils.unregister_class(physika_animate_op_previous)
    bpy.utils.unregister_class(physika_animate_op_next)    
    bpy.utils.unregister_class(physika_animate_ui)

