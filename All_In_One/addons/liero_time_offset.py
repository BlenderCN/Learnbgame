###################################################
# offset actions in time for each selected object #
# works with standard f-curves and with shapekeys #
###################################################

bl_info = {
    "name": "Time Offset",
    "author": "liero",
    "version": (0, 6),
    "blender": (2, 5, 7),
    "api": 37260,
    "location": "View3D > Properties",
    "description": "Time offset, align and distribute animations of selected objects",
    "category": "Learnbgame",
}

import bpy, random
drag_max = 33

def acciones(objetos):
    act = []
    for obj in objetos:
        try:
            if obj.animation_data:
                act.append(obj.animation_data.action)
            if obj.data.shape_keys and obj.data.shape_keys.animation_data:
                act.append(obj.data.shape_keys.animation_data.action)
        except:
            pass
    total = {} 
    for a in act: total[a] = 1 
    return total.keys()

def offset(act, val):
    for fcu in act.fcurves:
        if bpy.context.window_manager.sel:
            puntos = [p for p in fcu.keyframe_points if p.select_control_point]
        else:
            puntos = fcu.keyframe_points
        for k in puntos:
            k.co[0] += val
            k.handle_left[0] += val
            k.handle_right[0] += val

def align_start(objetos):
    total = {}
    act = acciones(objetos)
    if len(act) > 1:
        if bpy.context.window_manager.cur:
            start = bpy.context.scene.frame_current
        else:
            for a in act: total[a.frame_range[0]] = 1
            L = list(total.keys())
            L.sort()
            start = L[0]
        for a in act: offset(a, start - a.frame_range[0])

def align_mid(objetos):
    min, max = {}, {}
    act = acciones(objetos)
    if len(act) > 1:
        if bpy.context.window_manager.cur:
            x1 = bpy.context.scene.frame_current
        else:
            for a in act: min[a.frame_range[0]] = 1
            L_start = list(min.keys())
            L_start.sort()
            for a in act: max[a.frame_range[1]] = 1
            L_end = list(max.keys())
            L_end.sort()
            x1 = L_start[0] + ((L_end[-1] - L_start[0]) * .5)
        for a in act: 
            x2 = a.frame_range[0] + ((a.frame_range[1] - a.frame_range[0]) * .5)
            offset(a, x1 - x2)

def align_end(objetos):
    total = {}
    act = acciones(objetos)
    if len(act) > 1:
        if bpy.context.window_manager.cur:
            end = bpy.context.scene.frame_current
        else:
            for a in act: total[a.frame_range[1]] = 1
            L = list(total.keys())
            L.sort()
            end = L[-1]
        for a in act: offset(a, end - a.frame_range[1])

def distrib_start(objetos):
    act = acciones(objetos)
    min = []
    if len(act) > 2:
        if bpy.context.window_manager.nam:
            for a in act: min.append((a.name, a.frame_range[0]))
            x, w = 1, 0
        else:
            for a in act: min.append((a.frame_range[0], a.name))
            x, w = 0, 1
        min.sort()
        step = (min[-1][x] - min[0][x]) / (len(act) - 1)
        for i in range(1, len(act) - 1):
            a = bpy.data.actions.get(min[i][w])
            val = min[0][x] + i * step - min[i][x]
            offset(a, val)

def distrib_mid(objetos):
    act = acciones(objetos)
    mid = []
    if len(act) > 2:    
        if bpy.context.window_manager.nam:
            for a in act: mid.append((a.name, a.frame_range[0] + ((a.frame_range[1] - a.frame_range[0]) * .5)))
            x, w = 1, 0
        else:
            for a in act: mid.append((a.frame_range[0] + ((a.frame_range[1] - a.frame_range[0]) * .5), a.name))
            x, w = 0, 1
        mid.sort()
        step = (mid[-1][x] - mid[0][x]) / (len(act) - 1)
        for i in range(1, len(act) - 1):
            a = bpy.data.actions.get(mid[i][w])
            val = mid[0][x] + i * step - mid[i][x]
            offset(a, val)

def distrib_end(objetos):
    act = acciones(objetos)
    max = []
    if len(act) > 2:
        if bpy.context.window_manager.nam:
            for a in act: max.append((a.name, a.frame_range[1]))
            x, w = 1, 0
        else:
            for a in act: max.append((a.frame_range[1], a.name))
            x, w = 0, 1
        max.sort()
        step = (max[-1][x] - max[0][x]) / (len(act) - 1)
        for i in range(1, len(act) - 1):
            a = bpy.data.actions.get(max[i][w])
            val = max[0][x] + i * step - max[i][x]
            offset(a, val)

def viceversa(objetos):
    act = acciones(objetos)
    ref = []
    if len(act) > 1:
        for a in act: ref.append((a.frame_range[0], a.name))
        ref.sort()
        for i in range(len(act)):
            a = bpy.data.actions.get(ref[i][1])
            val = ref[len(act)-1-i][0] - ref[i][0]
            offset(a, val)

def drag(self, context):
    wm = context.window_manager
    if bpy.context.selected_objects:
        for act in acciones(bpy.context.selected_objects):
            offset (act, wm.drag)
    if wm.drag: wm.drag = 0
    refresco()

def refresco():
    f = bpy.context.scene.frame_current
    bpy.context.scene.frame_set(f)

class Reset(bpy.types.Operator):
    bl_idname = 'offset.reset'
    bl_label = 'Reset'
    bl_description = 'Reset sliders to zero'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        context.window_manager.off = 0
        context.window_manager.rand = 0
        return{'FINISHED'}

class Apply(bpy.types.Operator):
    bl_idname = 'offset.apply'
    bl_label = 'Apply'
    bl_description = 'Apply Time Offset to selected objects'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return(bpy.context.selected_objects)

    def execute(self, context):
        for act in acciones(bpy.context.selected_objects):
            r = int(random.random() * context.window_manager.rand)
            offset(act, context.window_manager.off + r)
        refresco()
        return{'FINISHED'} 

class Flip(bpy.types.Operator):
    bl_idname = 'offset.flip'
    bl_label = 'Flip'
    bl_description = 'Reverse the order of actions'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return(bpy.context.selected_objects)

    def execute(self, context):
        viceversa(bpy.context.selected_objects)
        refresco()
        return{'FINISHED'}

class A1(bpy.types.Operator):
    bl_idname = 'offset.a_start'
    bl_label = 'Start'
    bl_description = 'Align animations to StartPoint'
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return(bpy.context.selected_objects)

    def execute(self, context):
        align_start(bpy.context.selected_objects)
        refresco()
        return{'FINISHED'}

class A2(bpy.types.Operator):
    bl_idname = 'offset.a_center'
    bl_label = 'Center'
    bl_description = 'Align animations to MidPoint'
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return(bpy.context.selected_objects)

    def execute(self, context):
        align_mid(bpy.context.selected_objects)
        refresco()
        return{'FINISHED'}

class A3(bpy.types.Operator):
    bl_idname = 'offset.a_end'
    bl_label = 'End'
    bl_description = 'Align animations to EndPoint'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (bpy.context.selected_objects)

    def execute(self, context):
        align_end(bpy.context.selected_objects)
        refresco()
        return{'FINISHED'}

class D1(bpy.types.Operator):
    bl_idname = 'offset.d_start'
    bl_label = 'Start'
    bl_description = 'Distribute animations by StartPoint'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (bpy.context.selected_objects)

    def execute(self, context):
        distrib_start(bpy.context.selected_objects)
        refresco()
        return{'FINISHED'}

class D2(bpy.types.Operator):
    bl_idname = 'offset.d_center'
    bl_label = 'Center'
    bl_description = 'Distribute animations by MidPoint'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (bpy.context.selected_objects)

    def execute(self, context):
        distrib_mid(bpy.context.selected_objects)
        refresco()
        return{'FINISHED'}

class D3(bpy.types.Operator):
    bl_idname = 'offset.d_end'
    bl_label = 'End'
    bl_description = 'Distribute animations by EndPoint'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (bpy.context.selected_objects)

    def execute(self, context):
        distrib_end(bpy.context.selected_objects)
        refresco()
        return{'FINISHED'}

class GUI(bpy.types.Panel):
    bl_label = 'Time Offset'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw(self, context):
        wm = context.window_manager
        layout = self.layout
        column = layout.column(align=True)
        column.prop(wm,'off',slider=True)
        column.prop(wm,'rand',slider=True)
        row = layout.row(align=True)
        row.operator('offset.apply')
        row.operator('offset.reset')
        layout.label(text="Align / Distribute actions:")
        row = layout.row(align=True)
        row.operator('offset.a_start')
        row.operator('offset.a_center')
        row.operator('offset.a_end')
        row = layout.row(align=True)
        row.operator('offset.d_start')
        row.operator('offset.d_center')
        row.operator('offset.d_end')
        row = layout.row()
        row.prop(wm,'cur')
        row.prop(wm,'nam')
        row.prop(wm,'sel')
        layout.prop(wm,'drag',slider=True)
        row = layout.row()
        row.operator('offset.flip')

bpy.types.WindowManager.off = bpy.props.IntProperty(name='Time Offset', min=-1000, soft_min=-250, max=1000, soft_max=250, default=0, description='Offset value for f-curves in selected objects')
bpy.types.WindowManager.rand = bpy.props.IntProperty(name='Random', min=-1000, soft_min=-250, max=1000, soft_max=250, default=0, description='Random offset')
bpy.types.WindowManager.drag = bpy.props.IntProperty(name='Drag', min=-drag_max, max=drag_max, default=0, description='Drag to offset f-curves', update=drag)
bpy.types.WindowManager.cur = bpy.props.BoolProperty(name='Cursor', description='Use current time as reference for Alignment')
bpy.types.WindowManager.nam = bpy.props.BoolProperty(name='Names', description='Use alphabeticall order for Distribution')
bpy.types.WindowManager.sel = bpy.props.BoolProperty(name='Selected', description='Only offset selected keyframes in selected objects')

clases = [Apply, Reset, Flip, A1, A2, A3, D1, D2, D3, GUI]

def register():
    for c in clases:
        bpy.utils.register_class(c)

def unregister():
    for c in clases:
        bpy.utils.unregister_class(c)

if __name__ == '__main__':
    register()