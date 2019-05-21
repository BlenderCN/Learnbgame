#####################################################################
# particle tracer - creates a spline from each particle of a system #
# simple setting: Start/End = 1 | Amount<250 | play with Effectors  #
#####################################################################

bl_info = {
    "name": "Particle Tracer",
    "author": "liero",
    "version": (0, 2),
    "blender": (2, 5, 7),
    "location": "View3D > Tool Shelf",
    "description": "Trace curves from the movement of each particle in active system",
    "category": "Learnbgame"
}

import bpy

def ntracer(name_C,name_S):
    tracer = bpy.data.curves.new(name_S,'CURVE')
    tracer.dimensions = '3D'
    curva = bpy.data.objects.new(name_C,tracer)
    bpy.context.scene.objects.link(curva)
    tracer.materials.append(bpy.data.materials.get('mat'))
    try: tracer.fill_mode = 'FULL'
    except: tracer.use_fill_front = tracer.use_fill_back = False
    tracer.resolution_u = bpy.context.window_manager.u_res
    tracer.bevel_resolution = bpy.context.window_manager.b_res
    tracer.bevel_depth = bpy.context.window_manager.bev
    return tracer

class TraceParticles(bpy.types.Operator):
    bl_idname = 'particles.trace'
    bl_label = 'Trace Particles'
    bl_description = 'Create a curve from each particle in active system'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (bpy.context.object and bpy.context.object.particle_systems)

    def execute(self, context):
        obj = bpy.context.object
        wm = bpy.context.window_manager
        ps = obj.particle_systems.active

        if 'mat' not in bpy.data.materials:
            mat = bpy.data.materials.new('mat')
            mat.diffuse_color = [0,.5,1]
            mat.emit = 0.5

        if not wm.multi:
            tracer = ntracer('Tracer', 'Splines')

        for x in ps.particles:
            if wm.multi:
                tracer = ntracer('Tracer.000', 'Spline.000')
                print (tracer.name)
            spline = tracer.splines.new('BEZIER')
            spline.bezier_points.add((x.lifetime - 1) // wm.step)
            for t in list(range(int(x.lifetime))):
                bpy.context.scene.frame_set(t + x.birth_time)
                if not t % wm.step:
                    p = spline.bezier_points[t // wm.step]
                    p.co = x.location
                    p.handle_right_type='AUTO'
                    p.handle_left_type='AUTO'

        return{'FINISHED'}

class PanelTP(bpy.types.Panel):
    bl_label = 'Trace Particles'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'

    def draw(self, context):
        wm = bpy.context.window_manager
        layout = self.layout
        column = layout.column()
        column.operator('particles.trace')
        column.prop(wm, 'step')
        column.prop(wm, 'multi')
        if wm.multi:
            column = layout.column(align=True)
            column.prop(wm, 'bev')
            column.prop(wm, 'b_res')
            column.prop(wm, 'u_res')

bpy.types.WindowManager.step = bpy.props.IntProperty( name='Frame Step', description='Sample one every this number of frames.', min=1, max=50, default=5)
bpy.types.WindowManager.multi = bpy.props.BoolProperty(name='Multiple Curves', default=False, description='Generate multiple curves or just one object for the whole system')
bpy.types.WindowManager.bev = bpy.props.FloatProperty(name='Bevel', min=.005, max=1, default=.025, precision=3, step=.5, description='Bevel Depth for curves')
bpy.types.WindowManager.b_res = bpy.props.IntProperty(name='B Resolution', min=0, max=32, default=3, description='Bevel Resolution for curves')
bpy.types.WindowManager.u_res = bpy.props.IntProperty(name='Resolution U', min=1, max=64, default=16, description='Resolution U for curves')

def register():
    bpy.utils.register_class(TraceParticles)
    bpy.utils.register_class(PanelTP)

def unregister():
    bpy.utils.unregister_class(TraceParticles)
    bpy.utils.unregister_class(PanelTP)

if __name__ == '__main__':
    register()