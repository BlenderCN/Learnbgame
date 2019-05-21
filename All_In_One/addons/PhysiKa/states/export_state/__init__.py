import bpy
from ..base_state import *



class physika_export_ui(physika_base_ui):
    bl_label = 'Export'
    physika_state = 'export'

    def draw_export_path(self, context):
        export_props = context.scene.physika_export
        self.layout.separator()
        column = self.layout.column(align = True)
        split = column.split(percentage=0.333,align = True)
        column_left = split.column(align = True)
        column_right = split.column(align = True)
        column_left.operator('physika_operators.export_result',
                             text='Export Results',
                             icon='FILE')
        column_right.prop(export_props, 'export_path')
    
    def specific_draw(self, context):
        column = self.layout.column()
        column.label('Export results files path')
        self.draw_export_path(context)
        

class physika_export_op_previous(physika_base_op_previous):
    physika_state = 'export'
    bl_idname = 'physika_export_op.previous'

    
class physika_export_op_next(physika_base_op_next):
    physika_state = 'export'
    bl_idname = 'physika_export_op.next'

def register_state():
    state = bpy.data.scenes['Scene'].physika_state_graph.add()
    state.curr = 'export'
    state.next = 'None'
    state.prev = 'animate'

from . import (export_operators, export_properties)    
def register():
    export_properties.register()
    export_operators.register()
    bpy.utils.register_class(physika_export_op_previous)
    bpy.utils.register_class(physika_export_op_next)
    bpy.utils.register_class(physika_export_ui)

    
def unregister():
    export_properties.unregister()
    export_operators.unregister()
    bpy.utils.unregister_class(physika_export_op_previous)
    bpy.utils.unregister_class(physika_export_op_next)    
    bpy.utils.unregister_class(physika_export_ui)

