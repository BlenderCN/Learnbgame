# camera.py
#  date : 02/02/2017
# author: Laurent Boiron


import bpy

class OP_Gen_cam_lookatsplines(bpy.types.Operator):
    bl_idname = "gdco.gen_cam_lookatspline"
    bl_label = "Gen cameras from spline"
    bl_description = "Generate cameras from origin and lookat splines"

    cam_number = bpy.props.IntProperty(name="camnum",
                                       description="Camera number",
                                       default=10,
                                       min=1,
                                       soft_min=1,
                                       soft_max=200)

    def __init__(self):
        self.target = None
        self.origin = None
        self.camera = None
        self.cams = list()
        self.tgts = list()

    def init(self, ctx):
        self.target = ctx.active_object
        self.origin = ctx.selected_objects[0]
        if self.origin == self.target:
            self.origin = ctx.selected_objects[1]
        self.camera = bpy.data.cameras['camera'] if 'camera' in bpy.data.cameras else bpy.data.cameras.new('camera')


    @classmethod
    def poll(self, ctx):
        return ctx.mode == 'OBJECT' and all([o.type =='CURVE' for o in ctx.selected_objects]) and len(ctx.selected_objects) == 2


    def invoke(self, ctx, event):
        self.init(ctx)
        self.add_cam(ctx.scene, self.cam_number)

        ctx.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}


    def modal(self, ctx, event):
        if event.type == 'ESC':
            for i in range(self.cams):
                o = self.cams.pop()
                t = self.tgts.pop()
                ctx.scene.objects.unlink(o)
                ctx.scene.objects.unlink(t)

            return {'CANCELLED'}

        elif event.type in ('RIGHTMOUSE', 'LEFTMOUSE', 'ENTER'):
            return {'FINISHED'}
        elif event.type == 'WHEELDOWNMOUSE':
            self.cam_number -=  1 if self.cam_number >1 else 0
            if self.cam_number >1 :
                self.remove_cam( ctx.scene )

        elif event.type == 'WHEELUPMOUSE':
            self.cam_number +=  1
            self.add_cam( ctx.scene )
        else:
            return {'PASS_THROUGH'}

        return {'RUNNING_MODAL'}


    def execute(self, ctx):
        self.init(ctx)
        self.add_cam(ctx.scene, self.cam_number)

        return {'FINISHED'}


    def add_cam(self, scene, number=1):
        for i in range(number):
            o,t = create_rigcam(self.camera, self.origin, self.target)
            self.cams.append(o)
            self.tgts.append(t)

            scene.objects.link(o)
            scene.objects.link(t)

        self.update_position()


    def remove_cam(self, scene ):
        o = self.cams.pop()
        t = self.tgts.pop()
        scene.objects.unlink(o)
        scene.objects.unlink(t)

        self.update_position()


    def update_position(self):
        #update position on the curve
        for i,c in enumerate(self.cams):
            c.constraints[0].offset_factor = i / (self.cam_number-1)
            self.tgts[i].constraints[0].offset_factor = i / (self.cam_number-1)


def create_rigcam(camera, origin, target):
    o = bpy.data.objects.new('pov', camera)
    lock_rotpos(o)
    t = bpy.data.objects.new(o.name+'_target', None)
    lock_rotpos(t)
    t.empty_draw_type = 'CUBE'
    t.empty_draw_size = 0.1

    o_fpconst = o.constraints.new(type='FOLLOW_PATH')
    o_fpconst.target = origin
    o_fpconst.use_fixed_location = True
    o_ttconst = o.constraints.new(type='TRACK_TO')
    o_ttconst.target = t
    o_ttconst.track_axis = 'TRACK_NEGATIVE_Z'
    o_ttconst.up_axis = 'UP_Y'

    t_fpconst = t.constraints.new(type='FOLLOW_PATH')
    t_fpconst.target = target
    t_fpconst.use_fixed_location = True

    #o.parent = origin
    #t.parent = target

    return (o,t)



def lock_position(obj):
    obj.lock_location[0] = True
    obj.lock_location[1] = True
    obj.lock_location[2] = True

def lock_rotation(obj):
    obj.lock_rotation[0] = True
    obj.lock_rotation[1] = True
    obj.lock_rotation[2] = True

def lock_rotpos(obj):
    lock_position(obj)
    lock_position(obj)


def register():
    bpy.utils.register_class(OP_Gen_cam_lookatsplines)

def unregister():
    bpy.utils.unregister_class(OP_Gen_cam_lookatsplines)
