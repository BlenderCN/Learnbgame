import bpy

class GridControl(bpy.types.Operator):
    """Show or hide the Grid"""
    bl_idname = "view.grid_control"
    bl_label = "Show and Hide Grid"

    def execute(self, context):
        area = None
        for a in bpy.data.window_managers[0].windows[0].screen.areas:
            if a.type == 'VIEW_3D':
                area = a
                break

        if area:
            space = area.spaces[0]
        else:
            space = bpy.context.space_data

        if space.show_floor == True:
            space.show_floor = False
            space.show_axis_x = False
            space.show_axis_y = False
            # space.show_axis_z = False
        else:
            space.show_floor = True
            space.show_axis_x = True
            space.show_axis_y = True
            # space.show_axis_z = True

        return {'FINISHED'}

def register():
    bpy.utils.register_class(GridControl)


def unregister():
    bpy.utils.unregister_class(GridControl)