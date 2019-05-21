import bpy
from ..base_state import *
from . import discrete_types
import json,os

json_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "para_temp.json")
with open(json_file, 'r') as para_temp:
    methods = json.load(para_temp)

class physika_parameter_ui(physika_base_ui):
    bl_label = 'Parameter'
    physika_state = 'parameter'


    def draw_common_paras(self, context, para_props):
        paras = methods['common']
        self.layout.label('common')
        box = self.layout.box()
        for para, value in paras.items():
            box.column().prop(para_props.common, para)
    
    def draw_paras(self, context, para_props):
        method = para_props.physika_discrete

        cates = methods[method]
        for cate, paras in cates.items():
            if cate == "blender":
                continue
            self.layout.label(cate)
            box = self.layout.box()
            for para, valye in paras.items():
                box.column().prop(eval('para_props.' + method + '.' + cate), para)


        
    def specific_draw(self, context):

        para_props = context.scene.objects.active.physika.physika_para
        
        column = self.layout.column()
        column.label("Set Discrete Method")
        row = column.row(align = True)
        row.prop(para_props, 'physika_discrete', expand = True)

        # self.draw_common_paras(context, para_props)
        # self.draw_specific_paras(context, para_props)
        self.draw_common_paras(context, para_props)
        self.draw_paras(context, para_props)

class physika_parameter_op_previous(physika_base_op_previous):
    physika_state = 'parameter'
    bl_idname = 'physika_parameter_op.previous'

    
class physika_parameter_op_next(physika_base_op_next):
    physika_state = 'parameter'
    bl_idname = 'physika_parameter_op.next'

def register_state():
    state = bpy.data.scenes['Scene'].physika_state_graph.add()
    state.curr = 'parameter'
    state.next = 'simulate'
    state.prev = 'constraint'

from . import set_parameter    
def register():
    set_parameter.register()
    bpy.utils.register_class(physika_parameter_op_previous)
    bpy.utils.register_class(physika_parameter_op_next)
    bpy.utils.register_class(physika_parameter_ui)

def unregister():
    set_parameter.unregister()
    bpy.utils.unregister_class(physika_parameter_op_previous)
    bpy.utils.unregister_class(physika_parameter_op_next)    
    bpy.utils.unregister_class(physika_parameter_ui)
