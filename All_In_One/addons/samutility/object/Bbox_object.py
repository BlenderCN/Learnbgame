import bpy
from mathutils import Vector


def BBox_object_materialise(obj):
    '''Create a cube object to match bounding box of passing object'''

    name = 'BB_' + obj.name

    verts = [Vector(corner) for corner in obj.bound_box]
    print(verts)
    edges = [(4, 7), (5, 6), (4, 5), (6, 7), (0, 4), (0, 1), (1, 5), (1, 2), (2, 6), (2, 3), (3, 7), (0, 3)]
    faces = [[5, 1, 0, 4], [6, 5, 4, 7], [1, 5, 6, 2], [2, 6, 7, 3], [1, 2, 3, 0], [7, 4, 0, 3]]

    me = bpy.data.meshes.new(name=name+"_mesh")
    ##useful for development when the mesh may be invalid.
    # me.validate(verbose=True)

    ob = bpy.data.objects.new(name, me)
    ob.parent = obj
    #ob.location = obj.location
    #ob.rotation_quaternion = obj.rotation_quaternion
    #ob.scale = obj.scale
    ob.show_name = True

    # Link object to scene and make active
    scn = bpy.context.scene
    scn.objects.link(ob)
    scn.objects.active = ob
    ob.select = True

    # Create mesh from given verts, faces.
    me.from_pydata(verts, edges, faces)
    # Update mesh with new data
    me.update()

    return ob

class BBox_from_obj(bpy.types.Operator):
    bl_idname = "samutils.bbox_from_obj"
    bl_label = "Bbox from objects"
    bl_description = "materialize bounding box of selected meshes as a new mesh\n"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return len(context.selected_objects)

    def execute(self, context):
        for ob in bpy.context.selected_objects:
            BBox_object_materialise(ob)
        return {"FINISHED"}

#BBox_operator(C.object)
