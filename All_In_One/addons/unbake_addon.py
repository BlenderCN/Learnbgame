#########################################
# resamples baked f-curves to a new     #
# action + f-curve or a 3d bezier curve #
#########################################

bl_info = {
    "name": "unbake f-curve",
    "author": "liero",
    "version": (0, 4),
    "blender": (2, 6, 0),
    "location": "View3D > Properties Panel",
    "description": "Resample baked f-curve to a new Action / f-curve",
    "category": "Learnbgame"
}

import bpy

bpy.types.WindowManager.RGB = bpy.props.BoolProperty(name='Use RGB colors', default=True, description='Use RGB colors for f-curves')
bpy.types.WindowManager.scaleX = bpy.props.FloatProperty(name='X scale', min=.01, max=5, default=.1, description='X scale for 3d curve')
bpy.types.WindowManager.scaleY = bpy.props.FloatProperty(name='Y scale', min=.001, max=5, default=1, description='Z scale for 3d curve')
bpy.types.WindowManager.use_radius = bpy.props.BoolProperty(name='Use Radius', default=False, description='Use Radius / Height to visualize')

class Boton(bpy.types.Panel):
    bl_label = 'unBake selected fcurves'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'

    def draw(self, context):
        wm = context.window_manager
        layout = self.layout
        box = layout.box()
        box.operator('curve.unbake_action')
        box.prop(wm, "RGB")
        box = layout.box()
        box.operator('curve.unbake_bezier')
        column = box.column(align=True)
        column.prop(wm, 'scaleX')
        column.prop(wm, 'scaleY')
        box.prop(wm, 'use_radius')

class UnBakeA(bpy.types.Operator):
    bl_idname = 'curve.unbake_action'
    bl_label = 'unBake to Action'
    bl_description = 'Resample baked f-curve to a new Action / f-curve'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.object and context.object.animation_data)

    def execute(self, context):
        obj = bpy.context.object
        wm = bpy.context.window_manager
        pts = [(c.sampled_points, c.data_path, c.array_index) for c in obj.animation_data.action.fcurves if c.sampled_points and c.select]
        if pts:
            keys = bpy.data.actions.new(name='KEYS')
            for sam, dat, ind in pts:
                fcu = keys.fcurves.new(data_path=dat, index=ind)
                if wm.RGB: fcu.color_mode = 'AUTO_RGB'
                fcu.keyframe_points.add(len(sam))
                for i in range(len(sam)):
                    w = fcu.keyframe_points[i]
                    w.co = w.handle_left = w.handle_right = sam[i].co
            obj.animation_data.action = keys
        return{'FINISHED'}

class UnBakeB(bpy.types.Operator):
    bl_idname = 'curve.unbake_bezier'
    bl_label = 'unBake to 3D'
    bl_description = 'Resample baked f-curve to a 3d Bezier curve'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.object and context.object.animation_data)

    def execute(self, context):
        obj = bpy.context.object
        wm = bpy.context.window_manager
        for c in obj.animation_data.action.fcurves:
            if c.sampled_points and c.select:
                sam = c.sampled_points
                cu = bpy.data.curves.new('path','CURVE')
                cu.dimensions = '3D'
                if wm.use_radius:
                    cu.fill_mode = 'FULL'
                    cu.bevel_resolution = 16
                    cu.resolution_u = 1
                    cu.bevel_depth = 1
                spline = cu.splines.new('BEZIER')
                spline.bezier_points.add(len(sam)-1)
                curva = bpy.data.objects.new('curve',cu)
                bpy.context.scene.objects.link(curva)
                for i in range(len(sam)):
                    w = spline.bezier_points[i]
                    y = wm.scaleY*sam[i].co[1]
                    if wm.use_radius:
                        w.radius = y
                        y = 0
                    coords = (wm.scaleX*sam[i].co[0],y,0)
                    w.co = w.handle_left = w.handle_right = coords
                    
        return{'FINISHED'}

def register():
    bpy.utils.register_class(Boton)
    bpy.utils.register_class(UnBakeA)
    bpy.utils.register_class(UnBakeB)

def unregister():
    bpy.utils.unregister_class(Boton)
    bpy.utils.unregister_class(UnBakeA)
    bpy.utils.unregister_class(UnBakeB)

if __name__ == '__main__':
    register()