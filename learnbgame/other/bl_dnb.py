import bmesh
import bpy

bl_info = {
    "name": "Dandelion + Burdock",
    "author": "Multiple Authors",
    "version": (0, 0, 1),
    "blender": (2, 69, 0),
    "location": "View3D > Add > Mesh",
    "description": "Dandelion + Burdock tools",
    "category": "Add Mesh",
}

def pixels_add(object, quad_size):
    me = object.data

    # Get a BMesh representation
    bm = bmesh.new()   # create an empty BMesh
    bm.from_mesh(me)   # fill it in from a Mesh

    new_me = bpy.data.meshes.new('newmesh')
    new_ob = bpy.data.objects.new('newObj', new_me)
    bpy.context.scene.objects.link(new_ob)
    new_bm = bmesh.new()
    new_bm.from_mesh(new_me)

    bm_uvs = bm.loops.layers.uv.verify()

    for face in bm.faces:
        # Get the center of the face
        center = face.calc_center_median()

        verts = []
        for vert in face.verts:
            # Find the position of the new vert
            delta = vert.co - center
            delta.normalize()
            out = center + delta * (quad_size / 2)
            out = bpy.context.object.matrix_world * out
            verts.append(new_bm.verts.new(out))


        new_bm.faces.new(verts)

        # add uvs to the new face
        new_uvs = new_bm.loops.layers.uv.verify()
        new_bm.faces.layers.tex.verify()

        # match the uv's from the old face to the new
        new_bm.faces.ensure_lookup_table()
        new_face = new_bm.faces[-1]
        for lo, ln in zip(face.loops, new_face.loops):
            ouv = lo[bm_uvs]
            nuv = ln[new_uvs]
            nuv.uv = ouv.uv

    new_bm.to_mesh(new_me)

    # Finish up, write the bmesh back to the mesh
    bm.to_mesh(me)


class MESH_OT_dnb_pixels_add(bpy.types.Operator):
    bl_idname = "mesh.dnb_pixels_add"
    bl_label = "Add pixels from mesh"
    bl_options = {'REGISTER', 'UNDO'}

    quad_size = bpy.props.FloatProperty(
        name="Quad size",
        description="Quand size",
        min=0.001,
        max=10.0,
        default=0.1
    )

    def execute(self, context):
        pixels_add(context.object, self.quad_size)
        return {'FINISHED'}


class INFO_MT_mesh_dnb_add(bpy.types.Menu):
    bl_idname = "INFO_MT_mesh_dnb_add"
    bl_label = "d+b"

    def draw(self, context):
        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'
        layout.operator("mesh.dnb_pixels_add",
                        text="Add pixels")


def menu_func(self, context):
    lay_out = self.layout
    lay_out.operator_context = 'INVOKE_REGION_WIN'
    lay_out.separator()
    lay_out.menu("INFO_MT_mesh_dnb_add", text="d+b")

def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_mesh_add.append(menu_func)

def unregister():
    bpy.types.INFO_MT_mesh_add.remove(menu_func)
    bpy.utils.unregister_module(__name__)


if __name__ == "__main__":
    register()