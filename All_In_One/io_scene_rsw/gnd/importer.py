import os
import bpy
import bpy_extras
import bmesh
import math
from mathutils import Vector, Matrix, Quaternion
from bpy.props import StringProperty, BoolProperty, FloatProperty
from ..gnd.reader import GndReader
from ..utils.utils import get_data_path


class GndImportOptions(object):
    def __init__(self, should_import_lightmaps: bool = True, lightmap_factor: float = 0.5):
        self.should_import_lightmaps = should_import_lightmaps
        self.lightmap_factor = lightmap_factor


class GndImportOperator(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = 'io_scene_rsw.gnd_import'  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = 'Import Ragnarok Online GND'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'

    filename_ext = ".gnd"

    filter_glob = StringProperty(
        default="*.gnd",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    should_import_lightmaps = BoolProperty(
        default=True
    )

    lightmap_factor = FloatProperty(
        default=0.5,
        min=0.0,
        max=1.0,
        subtype='FACTOR'
    )

    @staticmethod
    def import_gnd(filepath, options: GndImportOptions):
        gnd = GndReader.from_file(filepath)
        name = os.path.splitext(os.path.basename(filepath))[0]
        directory_name = os.path.dirname(filepath)

        mesh = bpy.data.meshes.new(name)
        mesh_object = bpy.data.objects.new(name, mesh)

        if options.should_import_lightmaps:
            '''
            Generate light map image.
            '''
            lightmap_size = int(math.ceil(math.sqrt(len(gnd.lightmaps) * 64) / 8) * 8)
            lightmap_tiles_per_dimension = lightmap_size / 8
            pixel_count = lightmap_size * lightmap_size
            pixels = [0.0] * (pixel_count * 4)
            for i, lightmap in enumerate(gnd.lightmaps):
                x, y = int(i % lightmap_tiles_per_dimension) * 8, int(i / lightmap_tiles_per_dimension) * 8
                for y2 in range(8):
                    for x2 in range(8):
                        idx = y2 * 8 + x2
                        lum = lightmap.luminosity[idx]
                        j = int(((y + y2) * lightmap_size) + (x + x2)) * 4
                        r = lum / 255.0
                        pixels[j + 0] = r
                        pixels[j + 1] = r
                        pixels[j + 2] = r
                        pixels[j + 3] = 1.0
            lightmap_image = bpy.data.images.new('lightmap', lightmap_size, lightmap_size)
            lightmap_image.pixels = pixels

            ''' Create light map texture. '''
            lightmap_texture = bpy.data.textures.new('lightmap', type='IMAGE')
            lightmap_texture.image = lightmap_image

        ''' Create materials. '''
        materials = []
        for i, texture in enumerate(gnd.textures):
            texture_path = texture.path
            material = bpy.data.materials.new(texture_path)
            material.diffuse_intensity = 1.0
            material.specular_intensity = 0.0
            materials.append(material)

            ''' Load diffuse texture. '''
            diffuse_texture = bpy.data.textures.new(texture_path, type='IMAGE')
            data_path = get_data_path(directory_name)
            texpath = os.path.join(data_path, 'texture', texture_path)
            try:
                diffuse_texture.image = bpy.data.images.load(texpath, check_existing=True)
            except RuntimeError:
                pass

            ''' Add diffuse texture slot to material. '''
            diffuse_texture_slot = material.texture_slots.add()
            diffuse_texture_slot.texture = diffuse_texture

            if options.should_import_lightmaps:
                ''' Add light map texture slot to material.'''
                lightmap_texture_slot = material.texture_slots.add()
                lightmap_texture_slot.texture = lightmap_texture
                lightmap_texture_slot.diffuse_color_factor = options.lightmap_factor
                lightmap_texture_slot.blend_type = 'MULTIPLY'

        bm = bmesh.new()
        bm.from_mesh(mesh)

        for y in range(gnd.height):
            for x in range(gnd.width):
                tile_index = y * gnd.width + x
                tile = gnd.tiles[tile_index]
                if tile.face_indices[0] != -1:  # +Z
                    bm.verts.new(((x + 0) * gnd.scale, (y + 0) * gnd.scale, -tile[0]))
                    bm.verts.new(((x + 1) * gnd.scale, (y + 0) * gnd.scale, -tile[1]))
                    bm.verts.new(((x + 1) * gnd.scale, (y + 1) * gnd.scale, -tile[3]))
                    bm.verts.new(((x + 0) * gnd.scale, (y + 1) * gnd.scale, -tile[2]))
                if tile.face_indices[1] != -1:  # +Y
                    adjacent_tile = gnd.tiles[tile_index + gnd.width]
                    bm.verts.new(((x + 0) * gnd.scale, (y + 1) * gnd.scale, -tile[2]))
                    bm.verts.new(((x + 1) * gnd.scale, (y + 1) * gnd.scale, -tile[3]))
                    bm.verts.new(((x + 1) * gnd.scale, (y + 1) * gnd.scale, -adjacent_tile[1]))
                    bm.verts.new(((x + 0) * gnd.scale, (y + 1) * gnd.scale, -adjacent_tile[0]))
                if tile.face_indices[2] != -1:  # +X
                    adjacent_tile = gnd.tiles[tile_index + 1]
                    bm.verts.new(((x + 1) * gnd.scale, (y + 1) * gnd.scale, -tile[3]))
                    bm.verts.new(((x + 1) * gnd.scale, (y + 0) * gnd.scale, -tile[1]))
                    bm.verts.new(((x + 1) * gnd.scale, (y + 0) * gnd.scale, -adjacent_tile[0]))
                    bm.verts.new(((x + 1) * gnd.scale, (y + 1) * gnd.scale, -adjacent_tile[2]))

        bm.verts.ensure_lookup_table()

        vertex_offset = 0
        for y in range(gnd.height):
            for x in range(gnd.width):
                tile_index = y * gnd.width + x
                tile = gnd.tiles[tile_index]
                for face_index in filter(lambda x: x >= 0, tile.face_indices):
                    face = gnd.faces[face_index]
                    vertex_indices = [vertex_offset + i for i in range(4)]
                    bmface = bm.faces.new([bm.verts[x] for x in vertex_indices])
                    bmface.material_index = face.texture_index
                    vertex_offset += 4

        bm.faces.ensure_lookup_table()

        bm.to_mesh(mesh)

        ''' Add materials to mesh. '''
        uv_texture = mesh.uv_textures.new()
        lightmap_uv_texture = mesh.uv_textures.new()
        for material in materials:
            ''' Create UV map. '''
            mesh.materials.append(material)
            material.texture_slots[0].uv_layer = uv_texture.name
            if options.should_import_lightmaps:
                material.texture_slots[1].uv_layer = lightmap_uv_texture.name

        '''
        Assign texture coordinates.
        '''
        uv_texture = mesh.uv_layers[0]
        lightmap_uv_layer = mesh.uv_layers[1]
        for face_index, face in enumerate(gnd.faces):
            uvs = list(face.uvs)
            '''
            Since we are adding quads and not triangles, we need to
            add the UVs in quad clockwise winding order.
            '''
            uvs = [uvs[x] for x in [0, 1, 3, 2]]
            for i, uv in enumerate(uvs):
                # UVs have to be V-flipped
                uv = uv[0], 1.0 - uv[1]
                uv_texture.data[face_index * 4 + i].uv = uv
            if options.should_import_lightmaps:
                x1 = (face.lightmap_index % lightmap_tiles_per_dimension) / lightmap_tiles_per_dimension
                y1 = int(face.lightmap_index / lightmap_tiles_per_dimension) / lightmap_tiles_per_dimension
                x2 = x1 + (1.0 / lightmap_tiles_per_dimension)
                y2 = y1 + (1.0 / lightmap_tiles_per_dimension)
                lightmap_uvs = [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]
                for i, uv in enumerate(lightmap_uvs):
                    lightmap_uv_layer.data[face_index * 4 + i].uv = uv

        bpy.context.scene.objects.link(mesh_object)
        return mesh_object

    def execute(self, context):
        options = GndImportOptions(
            should_import_lightmaps=self.should_import_lightmaps,
            lightmap_factor=self.lightmap_factor
        )
        GndImportOperator.import_gnd(self.filepath, options)
        return {'FINISHED'}

    @staticmethod
    def menu_func_import(self, context):
        self.layout.operator(GndImportOperator.bl_idname, text='Ragnarok Online GND (.gnd)')

