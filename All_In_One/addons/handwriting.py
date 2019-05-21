##########################################
# animates points radii to grow a curve  #
# select a curve or a mesh / text object #
##########################################

bl_info = {
    "name": "Handwriting",
    "author": "liero, meta-androcto",
    "version": (1, 0),
    "blender": (2, 6, 3),
    "location": "View3D > Tool Shelf",
    "description": "Writes a curve by animating its point's radii",
    "category": "Learnbgame"
}

import bpy
bpy.types.WindowManager.f_start = bpy.props.IntProperty(name='Start frame', min=1, max=2500, default=1, description='Start frame / Hidden object')
bpy.types.WindowManager.length = bpy.props.IntProperty(name='Duration', min=1, soft_max=1000, max=2500, default=100, description='Animation Length')
bpy.types.WindowManager.f_fade = bpy.props.IntProperty(name='Fade after', min=0, soft_max=250, max=2500, default=0, description='Fade after this frames / Zero means no fade')
bpy.types.WindowManager.delay = bpy.props.IntProperty(name='Grow time', min=0, max=50, default=5, description='Frames it takes a point to grow')
bpy.types.WindowManager.tails = bpy.props.BoolProperty(name='Tails', default=True, description='Set radius to zero for open splines endpoints')
bpy.types.WindowManager.keepr = bpy.props.BoolProperty(name='Radius', default=True, description='Try to keep radius data from original curve')

class PANEL(bpy.types.Panel):
    bl_label = 'Handwriting Tool'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'

    def draw(self, context):
        wm = context.window_manager
        obj = bpy.context.object
        layout = self.layout
        column = layout.column(align=True)
        column.label(text='Writing Tools:')
        column.operator("gpencil.draw", text="Write With Grease Pencil").mode = 'DRAW'
        column.operator("gpencil.convert", text="Convert to Curve")

        if obj.type == 'CURVE':
            column = layout.column(align=True)
            column.label(text='Curve Tools:')
            column.prop(obj.data, 'bevel_depth')
            column.prop(obj.data, 'bevel_resolution')
            column.prop(obj.data, 'resolution_u')

        column = layout.column(align=True)
        column.label(text='Curve Animation:')
        column.prop(wm,'delay')
        column.prop(wm,'f_fade')

        column = layout.column()
        row = layout.row()
        row.prop(wm,'tails')
        row.prop(wm,'keepr')
		
        column = layout.column(align=True)
        column.label(text='Animation Tools:')
        column.prop(wm,'f_start')
        column.prop(wm,'length')

        column = layout.column(align=True)
        column.operator('curve.grow')

        box = self.layout.box()
        column = box.column(align=True)
        column.label(text='Specials Menu:')
        column.label(text='Animate Curve from Text')
        column.label(text="Animate Curve from Mesh")
        column.operator('curve.grow')

        column = layout.column(align=True)
        column.label(text='Remove Keyframes:')
        column.operator('curve.reset')
        row = self.layout.row()

class CRECE(bpy.types.Operator):
    bl_idname = 'curve.grow'
    bl_label = 'Run Script'
    bl_description = 'Keyframe points radius'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.object and context.object.type in ['MESH','FONT','CURVE'])

    def execute(self, context):
        wm, obj = context.window_manager, bpy.context.object

        # convert a mesh to curve
        if obj.type == 'MESH':
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.delete(type='ONLY_FACE')
            bpy.ops.object.mode_set()
            bpy.ops.object.convert(target='CURVE')
            for sp in obj.data.splines:
                sp.type = 'BEZIER'

        # convert a text to curve
        if obj.type == 'FONT':
            bpy.ops.object.mode_set()
            bpy.ops.object.convert(target='CURVE')

        # make the curve visible
        try: obj.data.fill_mode = 'FULL'
        except: obj.data.use_fill_front = obj.data.use_fill_back = False
        if not obj.data.bevel_resolution:
            obj.data.bevel_resolution = 5
        if not obj.data.bevel_depth:
            obj.data.bevel_depth = 0.1

        # get points data and beautify
        actual, total = wm.f_start, 0
        for sp in obj.data.splines:
            total += len(sp.points) + len(sp.bezier_points)
        step = wm.length / total
        for sp in obj.data.splines:
            sp.radius_interpolation = 'BSPLINE'
            po = [p for p in sp.points] + [p for p in sp.bezier_points]
            if not wm.keepr:
                for p in po: p.radius = 1
            if wm.tails and not sp.use_cyclic_u:
                po[0].radius = po[-1].radius = 0
                po[1].radius = po[-2].radius = .65
            ra = [p.radius for p in po]

        # record the keyframes
            for i in range(len(po)):
                bpy.context.scene.frame_set(actual)
                po[i].radius = 0
                po[i].keyframe_insert('radius')
                actual += step
                bpy.context.scene.frame_set(actual + wm.delay)
                po[i].radius = ra[i]
                po[i].keyframe_insert('radius')

                if wm.f_fade:
                    bpy.context.scene.frame_set(actual + wm.f_fade - step)
                    po[i].radius = ra[i]
                    po[i].keyframe_insert('radius')
                    bpy.context.scene.frame_set(actual + wm.delay + wm.f_fade)
                    po[i].radius = 0
                    po[i].keyframe_insert('radius')

        bpy.context.scene.frame_set(wm.f_start)
        return{'FINISHED'}

class RESET(bpy.types.Operator):
    bl_idname = 'curve.reset'
    bl_label = 'Clear animation'
    bl_description = 'Remove animation / curve radius data'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.object and context.object.type == 'CURVE')

    def execute(self, context):
        obj = bpy.context.object
        obj.data.animation_data_clear()
        for sp in obj.data.splines:
            po = [p for p in sp.points] + [p for p in sp.bezier_points]
            for p in po:
                p.radius = 1
        return{'FINISHED'}

def register():
    bpy.utils.register_class(PANEL)
    bpy.utils.register_class(CRECE)
    bpy.utils.register_class(RESET)

def unregister():
    bpy.utils.unregister_class(PANEL)
    bpy.utils.unregister_class(CRECE)
    bpy.utils.unregister_class(RESET)

if __name__ == '__main__':
    register()