###########################################################################
# connect all particles in active system with a continuous animated curve #
###########################################################################

bl_info = {
    "name": "Connect Particles",
    "author": "liero",
    "version": (0, 4, 0),
    "blender": (2, 6, 1),
    "location": "View3D > Tool Shelf",
    "description": "Create a continuous animated curve from particles in active system.",
    "category": "Learnbgame",
}

import bpy

class TraceAllParticles(bpy.types.Operator):
    bl_idname = 'particles.connect'
    bl_label = 'Connect Particles'
    bl_description = 'Create a continuous animated curve from particles in active system.'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (bpy.context.object and bpy.context.object.particle_systems)

    def execute(self, context):
        obj = bpy.context.object
        sce = bpy.context.scene
        wm = bpy.context.window_manager
        ps = obj.particle_systems.active
        set = ps.settings

        if set.distribution == 'GRID':
            self.report('INFO',"Grid distribution mode for particles not supported.")
            return{'FINISHED'}

        # create a new curve
        tracer = bpy.data.curves.new('Splines','CURVE')
        curva = bpy.data.objects.new('Tracer',tracer)
        sce.objects.link(curva)
        spline = tracer.splines.new('BEZIER')
        spline.bezier_points.add(set.count-1)

        # make the curve visible
        tracer.dimensions = '3D'
        tracer.fill_mode = 'FULL'
        if not tracer.bevel_resolution: tracer.bevel_resolution = 1
        if not tracer.bevel_depth: tracer.bevel_depth = 0.025
        if not tracer.resolution_u: tracer.bevel_resolution = 32

        # material for the curve
        if 'mat' not in bpy.data.materials:
            mat = bpy.data.materials.new('mat')
            mat.diffuse_color = [0]*3
            mat.use_shadeless = True
        tracer.materials.append(bpy.data.materials.get('mat'))

        # set animation range
        if wm.auto:
            f_start = int(set.frame_start)
            f_end = int(set.frame_end + set.lifetime)
        else:
            if wm.f_end <= wm.f_start:
                 wm.f_end = wm.f_start + 1
            f_start = wm.f_start
            f_end = wm.f_end
        print ('range: ', f_start, '/', f_end)

        # animate points location
        for t in range(f_start, f_end):
            sce.frame_set(t)
            if not (t-f_start) % wm.step:
                print ('done frame: ',t)
                for i in range(set.count):
                    if ps.particles[i].alive_state != 'UNBORN':
                        e = i
                    spline.bezier_points[i].co = ps.particles[e].location
                    spline.bezier_points[i].handle_left = ps.particles[e].location
                    spline.bezier_points[i].handle_right = ps.particles[e].location
                    spline.bezier_points[i].handle_right_type=wm.modo
                    spline.bezier_points[i].handle_left_type=wm.modo
                    spline.bezier_points[i].keyframe_insert('co')
                    spline.bezier_points[i].keyframe_insert('handle_left')
                    spline.bezier_points[i].keyframe_insert('handle_right')

        sce.frame_set(f_start)

        return{'FINISHED'}

class PanelCP(bpy.types.Panel):
    bl_label = 'Connect Particles'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'

    def draw(self, context):
        wm = context.window_manager
        obj = context.object
        layout = self.layout
        column = layout.column()
        column.operator('particles.connect')
        column.prop(wm, 'auto')
        if not wm.auto:
            column.prop(wm, 'f_start')
            column.prop(wm, 'f_end')
        column.prop(wm, 'step')
        column.prop(wm, 'modo')
        if obj.type == 'CURVE':
            column = layout.column(align=True)
            column.label(text='Active curve settings:')
            column.prop(obj.data, 'bevel_depth')
            column.prop(obj.data, 'bevel_resolution')
            column.prop(obj.data, 'resolution_u')

bpy.types.WindowManager.auto = bpy.props.BoolProperty(name='Auto Time Range', default=True, description='Calculate Time Range from particles life')
bpy.types.WindowManager.f_start = bpy.props.IntProperty( name='Start Frame', description='Start frame', min=1, max=5000, default=1)
bpy.types.WindowManager.f_end = bpy.props.IntProperty( name='End Frame', description='End frame', min=1, max=5000, default=250)
bpy.types.WindowManager.step = bpy.props.IntProperty( name='Step', description='Sample one every this number of frames', min=1, max=50, default=5)
bpy.types.WindowManager.modo = bpy.props.EnumProperty( name="", items=[('VECTOR','Vector',''),('AUTO','Auto','')], description='Spline Type for the bezier points', default='AUTO')


def register():
    bpy.utils.register_class(TraceAllParticles)
    bpy.utils.register_class(PanelCP)

def unregister():
    bpy.utils.unregister_class(TraceAllParticles)
    bpy.utils.unregister_class(PanelCP)

if __name__ == '__main__':
    register()
