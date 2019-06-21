import bpy
from bpy.props import (
    BoolProperty,
    PointerProperty
)

class physika_base_ui(bpy.types.Panel):
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "physics"
    bl_category = "PhysiKa"
    #bl_label=''
    @classmethod
    def poll(cls, context):
        obj_props = context.scene.objects.active.physika
        return obj_props.is_active and obj_props.state == cls.physika_state
    
    def get_previous(self, context):
        for state in context.scene.physika_state_graph:
            if state.curr == self.physika_state:
                return state.prev

    def get_next(self,context):
        for state in context.scene.physika_state_graph:
            if state.curr == self.physika_state:
                return state.next
    def specific_draw(self, context):
        pass

    def is_able_next(self):
        return True
    def is_able_prev(self):
        return True
    def draw(self, context):
        box = self.layout.box()
        column = box.column(align = True)
        
        split = column.split(percentage = 0.5)
        column_left = split.column()
        column_left.enabled = self.is_able_prev()
        column_right = split.column()
        column_right.enabled = self.is_able_next()
        if(self.get_previous(context) != 'None'):
            column_left.operator('physika_' + self.bl_label + '_op.previous',text = "Previous")
        if(self.get_next(context) != 'None'):
            column_right.operator('physika_' + self.bl_label + '_op.next', text = "Next")
            
        self.specific_draw(context)
class defrive_class(physika_base_ui):
    bl_label = "teste"

    
class physika_base_op_next(bpy.types.Operator):
    # bl_idname = ".next"
    bl_label = "Next step in "
    bl_description = "Jump to state "
    bl_options = {'REGISTER'}

    
    @classmethod
    def poll(cls,context):
        obj_props = context.scene.objects.active.physika
        return obj_props.is_active and obj_props.state == cls.physika_state
    
    def get_next(self,context):
        for state in context.scene.physika_state_graph:
            if state.curr == self.physika_state:
                return state.next
    def specific_exec(self, context):
        pass
    def execute(self, context):
        self.specific_exec(context)
        obj_props = context.scene.objects.active.physika
        obj_props.state = self.get_next(context)
        return {'FINISHED'}

class physika_base_op_previous(bpy.types.Operator):
    # bl_idname = ".next"
    bl_label = "Next step in "
    bl_description = "Jump to state "
    bl_options = {'REGISTER'}
    
    @classmethod
    def poll(cls,context):
        obj_props = context.scene.objects.active.physika
        return obj_props.is_active and obj_props.state == cls.physika_state

    def specific_exec(self, context):
        pass
    
    def get_previous(self, context):
        for state in context.scene.physika_state_graph:
            if state.curr == self.physika_state:
                return state.prev
    
    def execute(self, context):
        self.specific_exec(context)
        obj_props = context.scene.objects.active.physika
        obj_props.state = self.get_previous(context)        
        return {'FINISHED'}

def register_state():
    pass
    
