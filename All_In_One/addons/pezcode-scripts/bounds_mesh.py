import bpy
import mathutils

class ObjectBoundsMesh(bpy.types.Operator):
    bl_idname = "object.bounds_mesh"
    bl_label = "Mesh from bounding box"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def execute(self, context):

        selected = [obj for obj in context.selected_objects if obj.type == 'MESH']
        if len(selected) < 1:
            self.report({'ERROR'}, "No meshes selected")
            return {'CANCELLED'}

        objects = []

        for obj in selected:
            # get bounding box (local coordinates) and calculate median and dimensions
            min, max = self.min_max_from_bound(obj.bound_box)
            median = (min + max) / 2.0
            dim = max - min
            # combine local dimensions with object scale
            scale = mathutils.Vector(a * b for a, b in zip(dim, obj.scale))
            pos = obj.matrix_world * median
            bpy.ops.mesh.primitive_cube_add(radius=0.5, location=pos, rotation=obj.rotation_euler)
            new_obj = context.active_object
            new_obj.scale = scale
            new_obj.draw_type = 'WIRE'
            new_obj.name = obj.name + '_bounds'
            objects.append(new_obj)

        for obj in objects:
            obj.select = True

        return {'FINISHED'}

    def min_max_from_bound(self, bound):
        min = mathutils.Vector([bound[0][0], bound[0][1], bound[0][2]])
        max = mathutils.Vector([bound[4][0], bound[2][1], bound[1][2]])
        return min, max
