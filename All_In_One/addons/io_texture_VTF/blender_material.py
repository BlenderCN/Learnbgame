import bpy
from pathlib import Path

from .vmt import VMT
from .vtf import import_texture


class BlenderMaterial:
    def __init__(self, vmt: VMT):
        vmt.parse()
        self.vmt = vmt
        self.textures = {}

    def load_textures(self):
        for key, texture in self.vmt.textures.items():
            name = Path(texture).stem
            if bpy.data.images.get(name, False):
                self.textures[key] = bpy.data.images.get(name, False)
            else:
                image = import_texture(texture, True, False)
                if image:
                    self.textures[key] = image

    def find_material_case_insensitive(self, material_name):
        for mat in bpy.data.materials.items():
            if mat[0].lower() == material_name.lower():
                print('Material matched case-insensitively')
                return mat[1]
        return None

    def create_material(self, override=True):
        mat_name = self.vmt.filepath.stem
        if bpy.data.materials.get(mat_name) or self.find_material_case_insensitive(
                mat_name) and not override:
            return 'EXISTS'

        mat = bpy.data.materials.get(mat_name)
        print("Loading mat:" + mat_name)
        if not mat:
            print("Attempting to resolve materials case-insensitively")
            mat = self.find_material_case_insensitive(mat_name)

        if not mat:
            print("Material not found, create a new one")
            bpy.data.materials.new(mat_name)
            mat = bpy.data.materials.get(mat_name)

        print('Assigning textures to material')

        mat.use_nodes = True
        nodes = mat.node_tree.nodes

        # remove the default node for 2.80
        default_node = nodes.get('Principled BSDF', None)
        if default_node is not None:
            nodes.remove(default_node)
        else:
            # default node is Diffuse in Blender 2.79
            default_node = nodes.get('Diffuse BSDF', None)
            if default_node is not None:
                nodes.remove(default_node)

        out = nodes.get('ShaderNodeOutputMaterial', None)
        if not out:
            out = nodes.get('Material Output', None)
            if not out:
                out = nodes.new('ShaderNodeOutputMaterial')
        out.location = (0, 0)
        bsdf = nodes.new('ShaderNodeBsdfPrincipled')
        bsdf.location = (100, 0)
        mat.node_tree.links.new(bsdf.outputs["BSDF"], out.inputs['Surface'])
        if self.textures.get('$basetexture', False):
            tex = nodes.new('ShaderNodeTexImage')
            tex.image = self.textures.get('$basetexture')
            tex.location = (200, -100)
            mat.node_tree.links.new(
                tex.outputs["Color"],
                bsdf.inputs['Base Color'])
        if self.textures.get('$bumpmap', False):
            tex = nodes.new('ShaderNodeTexImage')
            tex.image = self.textures.get('$bumpmap')
            tex.location = (200, -50)
            tex.color_space = 'NONE'
            normal = nodes.new("ShaderNodeNormalMap")
            normal.location = (150, -50)
            mat.node_tree.links.new(
                tex.outputs["Color"],
                normal.inputs['Color'])
            mat.node_tree.links.new(
                normal.outputs["Normal"],
                bsdf.inputs['Normal'])
        if self.textures.get('$phongexponenttexture', False):
            tex = nodes.new('ShaderNodeTexImage')
            tex.image = self.textures.get('$phongexponenttexture')
            tex.location = (200, 0)
            # mat.node_tree.links.new(tex.outputs["Color"], bsdf.inputs['Base Color'])
