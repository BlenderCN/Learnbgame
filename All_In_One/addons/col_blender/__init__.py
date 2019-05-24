import bpy, struct, os, bmesh

bl_info = {
    "name": "Import COL",
    "author": "Spencer Alves",
    "version": (1,0,0),
    "blender": (2, 6, 2),
    "location": "Import",
    "description": "Import J3D COL collision data",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Learnbgame",
}

# ImportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator

def importFile(fname):
    print("Reading", fname)
    bm = bmesh.new()
    fin = open(fname, 'rb')
    numCoords, coordsOffset, numGroups = struct.unpack('>III', fin.read(12))
    print("numCoords =", numCoords, "coordsOffset =", coordsOffset, "numGroups =", numGroups)

    fin.seek(coordsOffset)
    #m.vertices.add(numCoords)
    for i in range(numCoords):
        x, y, z = struct.unpack('>fff', fin.read(12))
        #m.vertices[i].co = (z, x, y)
        bm.verts.new((z, x, y))
    bm.verts.ensure_lookup_table()

    fin.seek(12)
    m = bpy.data.meshes.new(os.path.splitext(os.path.split(fname)[-1])[0])
    for i in range(numGroups):
        unknownOffset0, unknown2, numTriIndices, unknown3, indicesOffset, unknownOffset1, unknownOffset2 = struct.unpack(">IHHIIII", fin.read(24))
        print("unknownOffset0 =", unknownOffset0, "unknown2 =", unknown2, "numTriIndices =", numTriIndices, "unknown3 =", unknown3, "indicesOffset =", indicesOffset, "unknownOffset1 =", unknownOffset1, "unknownOffset2 =", unknownOffset2)
        # unknownOffset1 and unknownOffset2 are 1 byte/index (3/tri)
        # unknownOffset0 is sometimes 0 or 16
        mat = bpy.data.materials.new(str(i))
        m.materials.append(mat)
        t = fin.tell()
        fin.seek(indicesOffset)
        #baseTriIndex = len(m.tessfaces)
        #baseTriIndex = len(bm.faces)
        #m.tessfaces.add(numTriIndices)
        for j in range(numTriIndices):
            #m.tessfaces[j+baseTriIndex].vertices[:3] = struct.unpack('>HHH', fin.read(6))
            try: face = bm.faces.new([bm.verts[idx] for idx in struct.unpack('>HHH', fin.read(6))])
            except ValueError: continue
            #m.tessfaces[j+baseTriIndex].material_index = i
            face.material_index = i
        fin.seek(t)
    o = bpy.data.objects.new(m.name, m)
    bm.to_mesh(m)
    bm.free()
    #m.update()
    fin.close()
    bpy.context.scene.objects.link(o)

class ImportCOL(Operator, ImportHelper):
    bl_idname = "import_scene.col"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Import COL"

    # ImportHelper mixin class uses this
    filename_ext = ".col"

    filter_glob = StringProperty(
            default="*.col",
            options={'HIDDEN'},
            )

    def execute(self, context):
        importFile(self.filepath)
        return {'FINISHED'}

# Only needed if you want to add into a dynamic menu
def menu_func_import(self, context):
    self.layout.operator(ImportCOL.bl_idname, text="Import J3D COL collision data (*.col)")


def register():
    bpy.utils.register_class(ImportCOL)
    bpy.types.INFO_MT_file_import.append(menu_func_import)


def unregister():
    bpy.utils.unregister_class(ImportCOL)
    bpy.types.INFO_MT_file_import.remove(menu_func_import)


if __name__ == "__main__":
    register()

    # test call
    #bpy.ops.import_scene.bmd('INVOKE_DEFAULT')
