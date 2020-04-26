import bpy

from . enums import CustomProperty, PrimType
from . update_utils import update_func

class OpUpdateGeometry(bpy.types.Operator):
    bl_idname = "ndp.update_geometry"
    bl_label = "Update non-destructive prim's geometry"
    bl_description = "Updates mesh geometry according to attached props"

    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        if (context.area is not None) and (context.area.type != 'VIEW_3D'):
            return False
        try:
            if not context.object.data.ndp_props.is_ndp:
                return False
            return True
        except:
            return False

    def execute(self, context):
        prim_name = context.object.data.ndp_props.prim_type
        
        if not prim_name or prim_name == PrimType.Unknown.name.upper():
            raise "Prim Name not supplied or not supported: {}".format(str(prim_name))

        obj = context.object

        update_func[prim_name.upper()](self, context, obj)
        return {'FINISHED'}