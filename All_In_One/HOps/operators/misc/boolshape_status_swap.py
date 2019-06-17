import bpy
from bpy.props import BoolProperty


class HOPS_OT_BoolshapeStatusSwap(bpy.types.Operator):
    bl_idname = "hops.boolshape_status_swap"
    bl_label = "Hops Boolshape Status Swap"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = """Toggles behavior of Boolean with Csharp / Step

RED - will not be applied / keeps boolean LIVE (new)
GREEN - will be applied on next csharp / step (classic)"""

    red: BoolProperty(name="Red Mode",
                      description="Use Green Shape",
                      default=False)

    @classmethod
    def poll(cls, context):
        object = context.active_object
        if object is None: return False
        return object.type == "MESH" and object.mode == "OBJECT"

    def execute(self, context):
        selected = context.selected_objects

        for obj in selected:
            if self.red:
                obj.hops.status = "BOOLSHAPE2"
            else:
                obj.hops.status = "BOOLSHAPE"

        context.area.tag_redraw()

        return {'FINISHED'}
