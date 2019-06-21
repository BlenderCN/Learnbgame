import bpy
import bgl
import bmesh
from bpy_extras.view3d_utils import location_3d_to_region_2d
from bpy_extras.object_utils import object_data_add
from mathutils import Vector, Euler
from mathutils.bvhtree import BVHTree
from .utils import linspace


class PSY_OT_RayScan(bpy.types.Operator):
    bl_idname = "mesh.rayscan"
    bl_label = "Ray Scan"
    bl_options = {'REGISTER', 'UNDO'}

    # BUG: Changing these values no longer updates the displayed points. :/
    count_x = bpy.props.IntProperty(name="X Samples", min=1, default=200)
    count_y = bpy.props.IntProperty(name="Y Samples", min=1, default=200)

    points = []


    @classmethod
    def poll(cls, context):
        return context.object.type == 'MESH'


    def invoke(self, context, event):
        if context.object.type != 'MESH':
            self.report({'ERROR_INVALID_CONTEXT'}, "Must select Mesh object")
            return {'CANCALLED'}

        args = (self, context)
        return self.execute(context)


    def scan(self, bvh, angle_x, angle_y, count_x, count_y, camera_location, camera_rotation):
        new_points = []
        print("Points x:", self.count_x, " Points y:", self.count_y)
        points_x = linspace(-angle_x/2, angle_x/2, self.count_x)
        points_y = linspace(-angle_y/2, angle_y/2, self.count_y)

        for py in points_y:
            for px in points_x:
                ray_dir = Vector((0, 0, -1))
                # NOTE: From perspective of camera, rotating around x produces vertical tilt.
                # BUG: Noticable distortion! Points may go outside FOV!
                ray_dir.rotate(Euler((py, px, 0)))
                ray_dir.rotate(camera_rotation)

                # Cast a ray towards the center of the camera view
                # BUG: Does not account for cases when the object has been rotated!!!!
                #      May need to transform camera position and ray into object space. :/
                loc, norm, index, distance = bvh.ray_cast(camera_location, ray_dir)
                if loc is not None:
                    new_points.append(loc)
        
        return new_points


    def execute(self, context):
        self.points.clear()
        bvh = BVHTree.FromObject(context.object, context.depsgraph)

        # Get object data
        # TODO: Make these into properties stored external to the operator
        camera = bpy.data.objects['Camera']

        # Find out which direction the camera is pointing
        angle_x = camera.data.angle_x
        angle_y = camera.data.angle_y

        self.points = self.scan(bvh, angle_x, angle_y, self.count_x, self.count_y, 
                                camera.location, camera.rotation_euler)
        try:
            exists = bpy.data.meshes['scan']
            bpy.data.meshes.remove(exists)
        except KeyError:
            pass
        
        try:
            obj = bpy.data.objects['scan']
            bpy.data.objects.remove(obj)
        except KeyError:
            pass
        # Add a mesh to the scene containing the points
        mesh = bpy.data.meshes.new("scan")
        mesh.from_pydata(self.points, [], [])

        obj = bpy.data.objects.new('scan', mesh)
        bpy.context.collection.objects.link(obj)
        # obj.select = False

        return {'FINISHED'}
