#######################################################################
# will add unique noise modifiers to each of selected object f-curves #
# first record a keyframe for this to work (to generate the f-curves) #
#######################################################################

bl_info = {
    "name": "Add Noise Modifiers",
    "author": "liero",
    "version": (0, 1),
    "blender": (2, 5, 7),
    "location": "View3D > Tool Shelf",
    "description": "Add noise modifiers to f-curves in all selected objects...",
    "category": "Learnbgame",
}

import bpy, random

bpy.types.WindowManager.fc_tipo = bpy.props.EnumProperty( name="", items=[('select','Select',''), ('available','Available',''), ('scale','Scaling',''), ('rotation','Rotation',''), ( 'location','Location','')], description='Add noise to this type of keyframed f-curve', default='rotation')
bpy.types.WindowManager.amplitude = bpy.props.FloatProperty( name='Amplitude', description='Amplitude', min=0, max=25, default=5)
bpy.types.WindowManager.time_scale = bpy.props.FloatProperty( name='Time Scale', description='Time Scale', min=0, max=250, default=50)

def acciones(objetos):
    act = []
    for obj in objetos:
        if obj.animation_data:
            act.append(obj.animation_data.action)
    return act

class AddNoise(bpy.types.Operator):
    bl_idname = 'animation.add_noise'
    bl_label = 'Add'
    bl_description = 'Add noise modifiers to selected objects f-curves'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return(bpy.context.selected_objects)

    def execute(self, context):
        wm = context.window_manager
        error = 1
        for act in acciones(bpy.context.selected_objects):
            for fc in act.fcurves:
                if fc.data_path.find(wm.fc_tipo) > -1 or wm.fc_tipo == 'available':
                    for m in fc.modifiers:
                        if m.type == 'NOISE': fc.modifiers.remove(m)
                    n = fc.modifiers.new('NOISE')
                    n.strength = wm.amplitude
                    n.scale = wm.time_scale
                    n.phase = int(random.random() * 999)
                    error = 0
        if error: self.report({'INFO'}, 'First create some keyframes for this objects')
        return{'FINISHED'}

class RemoveNoise(bpy.types.Operator):
    bl_idname = 'animation.remove_noise'
    bl_label = 'Remove'
    bl_description = 'Remove noise modifiers from selected objects f-curves'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return(bpy.context.selected_objects)

    def execute(self, context):
        wm = context.window_manager
        for act in acciones(bpy.context.selected_objects):
            for fc in act.fcurves:
                if fc.data_path.find(wm.fc_tipo) > -1 or wm.fc_tipo == 'available':
                    for m in fc.modifiers:
                        if m.type == 'NOISE':
                            fc.modifiers.remove(m)
        return{'FINISHED'} 

class RemoveData(bpy.types.Operator):
    bl_idname = 'animation.remove_data'
    bl_label = 'Clear Animation Data'
    bl_description = 'Remove all actions / keyframes from selected objects'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return(bpy.context.selected_objects)

    def execute(self, context):
        sel = bpy.context.selected_objects
        for obj in sel: obj.animation_data_clear()
        for act in acciones(sel): act.user_clear()

        return{'FINISHED'} 

class NModPanel(bpy.types.Panel):
    bl_label = 'Noise Modifiers'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'

    def draw(self, context):
        wm = context.window_manager
        layout = self.layout
        column = layout.column(align=True)
        column.prop(wm,'fc_tipo')
        row = column.row(align=True)
        row.operator('animation.add_noise')
        row.operator('animation.remove_noise')
        column = layout.column(align=True)
        column.prop(wm,'amplitude')
        column.prop(wm,'time_scale')
        layout.operator('animation.remove_data')

def register():
    bpy.utils.register_class(AddNoise)
    bpy.utils.register_class(RemoveNoise)
    bpy.utils.register_class(RemoveData)
    bpy.utils.register_class(NModPanel)

def unregister():
    bpy.utils.unregister_class(AddNoise)
    bpy.utils.unregister_class(RemoveNoise)
    bpy.utils.unregister_class(RemoveData)
    bpy.utils.unregister_class(NModPanel)

if __name__ == '__main__':
    register()