import struct
import importlib.util
from . import mwm_functions as mwm

bpy_spec = importlib.util.find_spec("bpy")
if bpy_spec is not None:
    is_blender = True
    import bpy
    from bpy.types import Operator
    from bpy.props import StringProperty
    from bpy_extras.io_utils import ImportHelper
else:
    # We're probably not in Blender if bpy cannot be imported.
    is_blender = False


def load(operator, context):
    file = open(operator.filepath, "rb")

    version_number = mwm.load_mwm_header(file)

    print("Version: %s" % version_number)

    if version_number > 1066002:
        print("This is at least version 1066002")
        load_01066002(operator, context, file, version_number)
    else:
        print("Model format is older than 1066002")
        file.seek(0)
        load_classic(operator, context, file, version_number)

    return {'FINISHED'}


def load_01066002(operator, context, file, version):
    index = mwm.load_index(file)

    print("Loading vertex data")
    vertex_data = mwm.load_mesh_data(index, file)

    print("Loading model parameters")
    model_params = mwm.load_mesh_sections(index, file)

    print("Loading model parts")
    model_parts = mwm.load_mesh_parts(index, file, version)

    for i in range(len(model_parts)):
        profile_mesh = bpy.data.meshes.new("Base_Profile_Data")
        profile_mesh.from_pydata(vertex_data.positions, [], model_parts[i].faces)

        profile_mesh.update()

        profile_object = bpy.data.objects.new("Base_Profile", profile_mesh)
        profile_object.data = profile_mesh

        scene = context.scene
        scene.objects.link(profile_object)
        profile_object.select = True


# This might be broken now.
def load_classic(operator, context, file):
    # reading the header
    section = mwm.read_string(file)
    flag = mwm.read_long(file)
    version = mwm.read_string(file)

    dummies = mwm.load_dummies(file)
    vertex_data = mwm.load_vertext_data(file)
    model_params = mwm.load_mesh_sections(file)
    model_parts = mwm.load_mesh_parts(file, version)

    file.close()

    for i in range(len(model_parts)):
        profile_mesh = bpy.data.meshes.new("Base_Profile_Data")
        profile_mesh.from_pydata(vertex_data.positions, [], model_parts[i].faces)

        profile_mesh.update()

        profile_object = bpy.data.objects.new("Base_Profile", profile_mesh)
        profile_object.data = profile_mesh

        scene = context.scene
        scene.objects.link(profile_object)
        profile_object.select = True

    return True
