#####################################################
# a simple toy to play with the slow parent option  #
#####################################################

bl_info = {
    "name": "Slow Parent Fun",
    "author": "liero",
    "version": (0, 4, 1),
    "blender": (2, 6, 1),
    "location": "View3D > Properties",
    "description": "Some buttons to play with recursive slow parenting",
    "category": "Learnbgame"
}

import bpy, random

bpy.types.WindowManager.copies = bpy.props.IntProperty(name='Number', min=1, max=100, default=50, description='Number of copies')
bpy.types.WindowManager.offset = bpy.props.IntProperty(name='Time Offset', min=1, max=25, default=2, description='Time Offset in frames')
bpy.types.WindowManager.size = bpy.props.FloatProperty(name='End Scale', min=0, max=5, default=0, description='Object trail End Size')
bpy.types.WindowManager.loc = bpy.props.BoolProperty(name='Loc', default=True, description='Add noise to position')
bpy.types.WindowManager.rot = bpy.props.BoolProperty(name='Rot', default=False, description='Add noise to rotation')
bpy.types.WindowManager.sca = bpy.props.BoolProperty(name='Sca', default=False, description='Add noise to scale')

bpy.types.WindowManager.extra = bpy.props.BoolProperty(name='Location / Rotation Offset', default=False, description='Add some initial offset to each new copy')
bpy.types.WindowManager.addLocX = bpy.props.FloatProperty(name='LocX', min=-5, max=5, default=0, description='add Location X')
bpy.types.WindowManager.addLocY = bpy.props.FloatProperty(name='LocY', min=-5, max=5, default=0, description='add Location Y')
bpy.types.WindowManager.addLocZ = bpy.props.FloatProperty(name='LocZ', min=-5, max=5, default=0, description='add Location Z')
bpy.types.WindowManager.addRotX = bpy.props.IntProperty(name='RotX', min=-45, max=45, default=0, description='add Rotation X')
bpy.types.WindowManager.addRotY = bpy.props.IntProperty(name='RotY', min=-45, max=45, default=0, description='add Rotation Y')
bpy.types.WindowManager.addRotZ = bpy.props.IntProperty(name='RotZ', min=-45, max=45, default=0, description='add Rotation Z')

class SlowPanel(bpy.types.Panel):
    bl_label = 'Slow Parenting Tools'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'

    def draw(self, context):
        wm = context.window_manager
        layout = self.layout
        layout.operator('slow.add_kids', icon="ZOOMIN")
        column = layout.column(align=True)
        column.prop(wm,'copies')
        column.prop(wm,'offset')
        column.prop(wm,'size')
        column = layout.column(align=True)
        column.prop(wm,'extra')
        if wm.extra:
            row = column.row(align=True)
            row.prop(wm,'addLocX')
            row.prop(wm,'addRotX')
            row = column.row(align=True)
            row.prop(wm,'addLocY')
            row.prop(wm,'addRotY')
            row = column.row(align=True)
            row.prop(wm,'addLocZ')
            row.prop(wm,'addRotZ')
        column = layout.column(align=True)
        column.operator('slow.add_noise', icon="AUTO")
        box = column.box()
        row = box.row(align=True)
        row.prop(wm,'loc')
        row.prop(wm,'rot')
        row.prop(wm,'sca')
        layout.operator('slow.reset_start', icon="BACK")
        layout.operator('slow.remove_kids', icon="X")

class SlowFamily(bpy.types.Operator):
    bl_idname = 'slow.add_kids'
    bl_label = 'Add Child Copies'
    bl_description = 'Creates a trail of copies recursively parented to this object'
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        scn = bpy.context.scene
        wm = context.window_manager
        z = a = bpy.context.object
        if z:
            z.select = True
            for i in range(wm.copies):
                s = 1 + (wm.size-1) / wm.copies * i
                bpy.ops.object.duplicate()
                b = bpy.context.active_object
                b.scale = (s,s,s)
                b.location[0] += wm.addLocX
                b.location[1] += wm.addLocY
                b.location[2] += wm.addLocZ
                b.rotation_euler[0] += wm.addRotX
                b.rotation_euler[1] += wm.addRotY
                b.rotation_euler[2] += wm.addRotZ
                a.select = False
                scn.objects.active = a
                bpy.ops.object.parent_set()
                b.use_slow_parent = True
                b.slow_parent_offset = wm.offset
                scn.objects.active = b
                a = b
            a.select = False
            z.select = True
            scn.objects.active = z
        return{'FINISHED'}

class RemoveKids(bpy.types.Operator):
    bl_idname = 'slow.remove_kids'
    bl_label = 'Clear Copies'
    bl_description = 'Remove all copies parented to this object'
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        z = bpy.context.object
        if z:
            bpy.ops.object.mode_set()
            bpy.ops.object.select_grouped(type='CHILDREN_RECURSIVE')
            bpy.ops.object.delete()
        return{'FINISHED'}

class ResetStart(bpy.types.Operator):
    bl_idname = 'slow.reset_start'
    bl_label = 'Rewind to Start'
    bl_description = 'Moves stuff to start position'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scn = bpy.context.scene
        for i in range(250):
            scn.frame_set(scn.frame_start)
        return{'FINISHED'}

class AddNoise(bpy.types.Operator):
    bl_idname = 'slow.add_noise'
    bl_label = 'Auto Animation'
    bl_description = 'Add | Remove noise to Delta Transformations'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        z = bpy.context.object
        wm = context.window_manager

        if wm.loc:
            z.delta_location = (0,0,0)
            z.keyframe_insert('delta_location', frame=1)
            for c in [c for c in z.animation_data.action.fcurves if c.data_path=='delta_location']:
                for m in c.modifiers: c.modifiers.remove(m)
                m = c.modifiers.new('NOISE')
                m.strength, m.scale, m.phase = 25, 50, random.randint(1,999)
        else:
            try:
                z.keyframe_delete('delta_location', frame=1)
                z.delta_location = (0,0,0)
            except: pass

        if wm.rot:
            z.delta_rotation_euler = (0,0,0)
            z.keyframe_insert('delta_rotation_euler', frame=1)
            for c in [c for c in z.animation_data.action.fcurves if c.data_path=='delta_rotation_euler']:
                for m in c.modifiers: c.modifiers.remove(m)
                m = c.modifiers.new('NOISE')
                m.strength, m.scale, m.phase = 15, 100, random.randint(1,999)
        else:
            try:
                z.keyframe_delete('delta_rotation_euler', frame=1)
                z.delta_rotation_euler = (0,0,0)
            except: pass

        if wm.sca:
            z.delta_scale = (1,1,1)
            z.keyframe_insert('delta_scale', frame=1)
            for c in [c for c in z.animation_data.action.fcurves if c.data_path=='delta_scale']:
                for m in c.modifiers: c.modifiers.remove(m)
                m = c.modifiers.new('NOISE')
                m.strength, m.scale, m.phase = 5, 25, random.randint(1,999)
        else:
            try:
                z.keyframe_delete('delta_scale', frame=1)
                z.delta_scale = (1,1,1)
            except: pass
            
        return{'FINISHED'}


def register():
    bpy.utils.register_class(SlowPanel)
    bpy.utils.register_class(SlowFamily)
    bpy.utils.register_class(RemoveKids)
    bpy.utils.register_class(AddNoise)
    bpy.utils.register_class(ResetStart)

def unregister():
    bpy.utils.unregister_class(SlowPanel)
    bpy.utils.unregister_class(SlowFamily)
    bpy.utils.unregister_class(RemoveKids)
    bpy.utils.unregister_class(AddNoise)
    bpy.utils.unregister_class(ResetStart)

if __name__ == '__main__':
    register()