from pathlib import Path

if "bpy" in locals():
    import importlib
else:
    from .rose.zms import *

import bpy
from bpy.props import StringProperty, BoolProperty
from bpy_extras.io_utils import ImportHelper


class ImportZMS(bpy.types.Operator, ImportHelper):
    bl_idname = "rose.import_zms"
    bl_label = "ROSE Mesh (.zms)"
    bl_options = {"PRESET"}

    filename_ext = ".zms"
    filter_glob = StringProperty(default="*.zms", options={"HIDDEN"})
    load_texture = BoolProperty(
        name = "Load texture",
        description = ( "Automatically detect and load a texture if "
                        "one can be found (uses file name)"),
        default=True,
    )

    texture_extensions = [".DDS", ".dds", ".PNG", ".png"]

    def execute(self, context):
        filepath = Path(self.filepath)
        filename = filepath.stem
        zms = ZMS(str(filepath))

        mesh = self.mesh_from_zms(zms, filename)

        obj = bpy.data.objects.new(filename, mesh)
        
        scene = context.scene
        scene.objects.link(obj)
        scene.update()

        return {"FINISHED"}

    def mesh_from_zms(self, zms, filename):
        mesh = bpy.data.meshes.new(filename)

        #-- Vertices
        verts = []
        for v in zms.vertices:
            verts.append((v.position.x, v.position.y, v.position.z))

        #-- Faces
        faces = []
        for i in zms.indices:
            faces.append((i.x, i.y, i.z))

        #-- Mesh
        mesh.from_pydata(verts, [], faces)

        #-- UV
        if zms.uv1_enabled():
            mesh.uv_textures.new(name="uv1")
        if zms.uv2_enabled():
            mesh.uv_textures.new(name="uv2")
        if zms.uv3_enabled():
            mesh.uv_textures.new(name="uv3")
        if zms.uv4_enabled():
            mesh.uv_textures.new(name="uv4")

        for loop_idx, loop in enumerate(mesh.loops):
            vi = loop.vertex_index

            if zms.uv1_enabled():
                u = zms.vertices[vi].uv1.x
                v = zms.vertices[vi].uv1.y
                mesh.uv_layers["uv1"].data[loop_idx].uv = (u,1-v)

        #-- Material
        mat = bpy.data.materials.new(filename)
        mat.use_nodes = True

        nodes = mat.node_tree.nodes
        mat_node = nodes["Diffuse BSDF"]
        tex_node = nodes.new(type="ShaderNodeTexImage")

        if self.load_texture:
            # Check if DDS or PNG exists
            for ext in self.texture_extensions:
                filepath = Path(self.filepath)
                p = filepath.with_suffix(ext)
                if not p.is_file():
                    continue

                image = bpy.data.images.load(str(p))
                tex_node.image = image

        links = mat.node_tree.links
        links.new(mat_node.inputs["Color"], tex_node.outputs["Color"])
        mesh.materials.append(mat)

        mesh.update(calc_edges=True)
        return mesh
