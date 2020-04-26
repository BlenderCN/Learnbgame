import bpy


class RetopoShading(bpy.types.Operator):
    """Setup the viewport to a retopo shading, activate the X-ray to the 
    selected object and the Hidden Wire on"""
    bl_idname = "object.retopo_shading"
    bl_label = "Retopo shading"

    def execute(self, context):
        sltd_obj = context.selected_objects
        area = None
        for a in bpy.data.window_managers[0].windows[0].screen.areas:
            if a.type == 'VIEW_3D':
                area = a
                break

        if area:
            space = area.spaces[0]
        else:
            space = bpy.context.space_data

        if space.show_occlude_wire == True:
            space.show_occlude_wire = False
            for obj in sltd_obj:
                if obj.type == "MESH":
                    context.active_object.show_x_ray = False

        else:
            space.show_occlude_wire = True
            for obj in sltd_obj:
                if obj.type == "MESH":
                    context.active_object.show_x_ray = True

        return {'FINISHED'}


def register():
    bpy.utils.register_class(RetopoShading)


def unregister():
    bpy.utils.unregister_class(RetopoShading)


if __name__ == "__main__":
    register()
