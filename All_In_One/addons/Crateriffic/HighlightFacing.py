import bpy
import bmesh
from mathutils import Vector

# This extra utility function handles transforming world coordinates to normalized device coordinates
from bpy_extras.object_utils import world_to_camera_view


class PSY_OT_HighlightFacing(bpy.types.Operator):
    bl_idname = "mesh.highlight_visible"
    bl_label = "Highlight Facing"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.object.type == 'MESH'

    def invoke(self, context, event):
        return self.execute(context)

    def execute(self, context):
        print("Invoking Highlight Visible")
        # Check if a mesh object is selected
        try:
            bpy.ops.object.mode_set(mode='EDIT')
        except:
            self.report({'ERROR'}, "Must select a mesh object")
            return {'CANCELLED'}

        obj = bpy.context.edit_object
        me = obj.data

        # Get a BMesh representation
        mesh = bmesh.from_edit_mesh(me)
        # bm.from_mesh(me)

        mesh.faces.active = None

        cam = bpy.data.objects["Camera"]
        cam_rotation = cam.rotation_euler
        cam_dir = Vector((0, 0, 1))
        cam_dir.rotate(cam_rotation)
        print("Camera direction:", cam_dir)

        try:
            color_layer = mesh.loops.layers.color['Col']
        except:
            color_layer = mesh.loops.layers.color.new("Col")

        # NOTE: This does not yet correctly handle occluded geometry!
        for v in mesh.verts:
            color = (1, 1, 1, 1)

            p = world_to_camera_view(bpy.context.scene, cam, v.co)
            # Check if vertex is visible to camera
            if (0 < p.x < 1) and (0 < p.y < 1):
                # v.select = True
                # Check faces connected to vertex
                # NOTE: This is not ALL faces adjacent to a vertex. :-/
                for face in v.link_faces:
                    direction = face.normal - cam.location

                    if direction.dot(face.normal) < 0:
                        face.select = True
                        color = (1, 0, 1, 1)

            for face in v.link_faces:
                # Color faces depending on dot product direction
                for loop in face.loops:
                    loop[color_layer] = color


        # Show the updates in the viewport
        # and recalculate n-gon tessellation.
        bmesh.update_edit_mesh(me, True)
        bpy.ops.object.mode_set(mode='OBJECT')

        return {'FINISHED'}


def register():
    bpy.utils.register_class(HighlightFacingOperator)

    print("%s registration complete" % bl_info.get("name"))


def unregister():
    bpy.utils.unregister_class(HighlightFacingOperator)

    print("%s unregistering complete" % bl_info.get("name"))
