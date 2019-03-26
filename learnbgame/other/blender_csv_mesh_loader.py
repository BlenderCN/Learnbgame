import bpy
import bmesh
from os.path import basename
from bpy.props import StringProperty


bl_info = {
    "name": "CSV mesh loader",
    "author": "Drunkar",
    "version": (0, 1),
    "blender": (2, 7, 9),
    "location": "View3D > Add > Mesh > CSV mesh loader",
    "description": "Create mesh or curve from csv of node positions.",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Object"
}


addon_keymaps = []


class CSVMeshLoader(bpy.types.Operator):

    bl_idname = "animation.csv_mesh_loader"
    bl_label = "CSV mesh loader"
    bl_description = "Create mesh or curve from csv of node positions."
    bl_options = {'REGISTER', 'UNDO'}

    filepath = StringProperty(subtype="FILE_PATH")
    filter_glob = StringProperty(
        default="*.csv",
        options={'HIDDEN'}
    )

    # main
    def execute(self, context):
        print(self.filepath)
        verts = []
        with open(self.filepath, "r") as f:
            for line in f:
                verts.append([float(i) for i in line.strip().split(",")])
        obj_name = basename(self.filepath).replace(".csv", "").replace(".CSV", "")
        self._mcreate_mash_from_verts(obj_name, verts)
        return {'FINISHED'}

    def _mcreate_mash_from_verts(self, obj_name, verts):
        mesh = bpy.data.meshes.new("mesh")
        obj = bpy.data.objects.new(obj_name, mesh)
        scene = bpy.context.scene
        scene.objects.link(obj)
        scene.objects.active = obj
        obj.select = True

        mesh = bpy.context.object.data
        bm = bmesh.new()

        prev_vert = None
        for i, v in enumerate(verts):
            vert = bm.verts.new(v)
            if i > 0:
                bm.edges.new((prev_vert, vert))
            prev_vert = vert

        bm.to_mesh(mesh)
        bm.free()

    def invoke(self, context, event):
        wm = context.window_manager
        # ファイルブラウザ表示
        wm.fileselect_add(self)

        return {'RUNNING_MODAL'}


def menu_func(self, context):
    self.layout.operator(CSVMeshLoader.bl_idname,
                         text="CSV mesh loader")


def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_mesh_add.append(menu_func)


def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_mesh_add.remove(menu_func)


if __name__ == "__main__":
    register()