import bpy
import gpu
from gpu_extras.batch import batch_for_shader
import numpy as np

def read_some_data(context, filepath):
    data = np.genfromtxt(filepath, delimiter=",")
    coords = data.reshape(data.shape[0]*2, 3)

    try:
        exists = bpy.data.meshes['footprint']
        bpy.data.meshes.remove(exists)
    except KeyError:
        pass
    
    try:
        obj = bpy.data.objects['footprint']
        bpy.data.objects.remove(obj)
    except KeyError:
        pass
    mesh = bpy.data.meshes.new("footprint")
    indices = np.arange(coords.shape[0]).reshape(-1,2).tolist()
    # print(indices)
    mesh.from_pydata(coords, indices, [])

    obj = bpy.data.objects.new('footprint', mesh)
    bpy.context.collection.objects.link(obj)

    return {'FINISHED'}


# ImportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator


class PSY_OT_ImportFootprint(Operator, ImportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "psyche.footprint"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Import Footprint File"

    # ImportHelper mixin class uses this
    filename_ext = ".csv"

    filter_glob: StringProperty(
        default="*.csv",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    def execute(self, context):
        return read_some_data(context, self.filepath)


# Only needed if you want to add into a dynamic menu
def menu_func_import(self, context):
    self.layout.operator(PSY_OT_ImportFootprint.bl_idname, text="Text Import Operator")


def register():
    bpy.utils.register_class(PSY_OT_ImportFootprint)
    #bpy.types.TOPBAR_MT_file_import.append(menu_func_import)


def unregister():
    bpy.utils.unregister_class(PSY_OT_ImportFootprint)
    #bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)


if __name__ == "__main__":
    register()

    # test call
    bpy.ops.import_test.some_data('INVOKE_DEFAULT')
