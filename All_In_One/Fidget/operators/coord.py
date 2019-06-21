
import bpy
import bpy_extras.view3d_utils


class ViewportCoord(bpy.types.Operator):
    bl_idname = "fidget.getcoord"
    bl_label = "coord get"
    bl_description = "get vertex coordinates"

    list_location_2d = []

    def execute(self, context):
        region = context.region
        rv3d = context.space_data.region_3d
        object = bpy.context.object

        coords = [(object.matrix_world * v.co) for v in object.data.vertices]

        for v in coords:
            v_2d = bpy_extras.view3d_utils.location_3d_to_region_2d(region, rv3d, v, default=None)
            self.list_location_2d.append(v_2d)

        print(self.list_location_2d)
        print("  ")
        print("  ")

        self.list_location_2d[:] = []

        return {'FINISHED'}
