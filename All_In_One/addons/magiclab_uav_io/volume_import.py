import csv
import bmesh
import bpy

from io_mesh_ply import import_ply
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty
from bpy.types import Operator


def inport_csv_boxes(filename):
    """ import original csv format bounds as a pointcloud """
    cos = []
    with open(filename) as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in spamreader:
            cos.append([float(i) for i in row])
    mesh = bpy.data.meshes.new("volume")
    bm = bmesh.new()
    for v_co in cos:
        bm.verts.new(v_co)
    bm.verts.ensure_lookup_table()
    bm.to_mesh(mesh)
    ob = bpy.data.objects.new("volume", mesh)
    bpy.context.scene.objects.link(ob)
    ob.layers = bpy.context.scene.layers
    return ob


class ImportCaptureVolume(Operator, ImportHelper):
    """ Import Captured Volume as a ply mesh, cleanup ancap display """
    bl_idname = "object.magiclab_volume_import"
    bl_label = "Magiclab Capture Volume Import"

    filename_ext = ".ply"

    filter_glob = StringProperty(
        default="*.ply",
        options={'HIDDEN'},
        maxlen=255,
        )

    def execute(self, context):
        import_ply.load_ply(self.filepath) # we could use load poly mesh instead
        ob = context.scene.objects.active  # active object
        # cleanups
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.remove_doubles()
        bpy.ops.mesh.normals_make_consistent()
        bpy.ops.object.editmode_toggle()
        # assign a material
        mat = ob.active_material = bpy.data.materials.new("UAVs_hull")
        mat.alpha = 0.1
        mat.game_settings.alpha_blend = "ALPHA"
        ob.show_transparent = True
        return {'FINISHED'}


def register():
    bpy.utils.register_class(ImportCaptureVolume)


def unregister():
    bpy.utils.unregister_class(ImportCaptureVolume)
