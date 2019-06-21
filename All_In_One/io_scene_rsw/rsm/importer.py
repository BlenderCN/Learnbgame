import os
import bpy
import bpy_extras
import bmesh
import math
from mathutils import Vector, Matrix, Quaternion
from bpy.props import StringProperty, BoolProperty, FloatProperty
from ..utils.utils import get_data_path
from ..rsm.reader import RsmReader


class RsmImportOptions(object):
    def __init__(self, should_import_smoothing_groups:bool = True):
        self.should_import_smoothing_groups = should_import_smoothing_groups

class RsmImportOperator(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = 'io_scene_rsw.rsm_import'  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = 'Import Ragnarok Online RSM'
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'

    filename_ext = ".rsm"

    filter_glob = StringProperty(
        default="*.rsm",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    should_import_smoothing_groups = BoolProperty(
        default=True
    )

    @staticmethod
    def import_rsm(filepath, options):
        rsm = RsmReader.from_file(filepath)
        data_path = get_data_path(filepath)
        materials = []
        for texture_path in rsm.textures:
            material = bpy.data.materials.new(texture_path)
            material.diffuse_intensity = 1.0
            material.specular_intensity = 0.0

            # TODO: search backwards until we hit the "data" directory (or slough off bits until we
            # hit hte data directory?)

            ''' Create texture. '''
            texture = bpy.data.textures.new(texture_path, type='IMAGE')

            if data_path != '':
                texpath = os.path.join(data_path, 'texture', texture_path)
                try:
                    texture.image = bpy.data.images.load(texpath, check_existing=True)
                except RuntimeError:
                    pass

            texture_slot = material.texture_slots.add()
            texture_slot.texture = texture

            materials.append(material)

        nodes = {}
        for node in rsm.nodes:
            mesh = bpy.data.meshes.new(node.name)
            mesh_object = bpy.data.objects.new(os.path.relpath(filepath, data_path), mesh)

            nodes[node.name] = mesh_object

            if node.parent_name in nodes:
                mesh_object.parent = nodes[node.parent_name]

            ''' Add UV map to each material. '''
            uv_texture = mesh.uv_textures.new()
            material.texture_slots[0].uv_layer = uv_texture.name

            bm = bmesh.new()
            bm.from_mesh(mesh)

            for texture_index in node.texture_indices:
                mesh.materials.append(materials[texture_index])

            for vertex in node.vertices:
                bm.verts.new(vertex)

            bm.verts.ensure_lookup_table()

            '''
            Build smoothing group face look-up-table.
            '''
            smoothing_group_faces = dict()
            for face_index, face in enumerate(node.faces):
                try:
                    bmface = bm.faces.new([bm.verts[x] for x in face.vertex_indices])
                    bmface.material_index = face.texture_index
                except ValueError as e:
                    # TODO: we need more solid error handling here as a duplicate face throws off the UV assignment.
                    raise NotImplementedError
                if options.should_import_smoothing_groups:
                    bmface.smooth = True
                    if face.smoothing_group not in smoothing_group_faces:
                        smoothing_group_faces[face.smoothing_group] = []
                    smoothing_group_faces[face.smoothing_group].append(face_index)

            bm.faces.ensure_lookup_table()
            bm.to_mesh(mesh)

            '''
            Assign texture coordinates.
            '''
            uv_texture = mesh.uv_layers[0]
            for face_index, face in enumerate(node.faces):
                uvs = [node.texcoords[x] for x in face.texcoord_indices]
                for i, uv in enumerate(uvs):
                    # UVs have to be V-flipped (maybe)
                    uv = uv[1:]
                    uv = uv[0], 1.0 - uv[1]
                    uv_texture.data[face_index * 3 + i].uv = uv

            '''
            Apply transforms.
            '''
            offset = Vector((node.offset[0], node.offset[2], node.offset[1] * -1.0))

            if mesh_object.parent is None:
                mesh_object.location = offset * -1
            else:
                mesh_object.location = offset

            mesh_object.scale = node.scale

            bpy.context.scene.objects.link(mesh_object)

            '''
            Apply smoothing groups.
            '''
            if options.should_import_smoothing_groups:
                bpy.ops.object.select_all(action='DESELECT')
                mesh_object.select = True
                bpy.context.scene.objects.active = mesh_object
                for smoothing_group, face_indices in smoothing_group_faces.items():
                    '''
                    Select all faces in the smoothing group.
                    '''
                    bpy.ops.object.mode_set(mode='OBJECT')
                    for face_index in face_indices:
                        mesh.polygons[face_index].select = True
                    bpy.ops.object.mode_set(mode='EDIT')
                    bpy.ops.mesh.select_mode(type='FACE')
                    '''
                    Mark boundary edges as sharp.
                    '''
                    bpy.ops.mesh.region_to_loop()
                    bpy.ops.mesh.mark_sharp()
                bpy.ops.object.mode_set(mode='OBJECT')
                '''
                Add edge split modifier.
                '''
                edge_split_modifier = mesh_object.modifiers.new('EdgeSplit', type='EDGE_SPLIT')
                edge_split_modifier.use_edge_angle = False
                edge_split_modifier.use_edge_sharp = True
                bpy.ops.object.select_all(action='DESELECT')

        main_node = nodes[rsm.main_node]
        if main_node is not None:
            bpy.ops.object.select_all(action='DESELECT')
            mesh_object.select = True
            bpy.context.scene.objects.active = mesh_object
            bpy.ops.object.transform_apply(location=True, scale=True, rotation=True)
            mesh_object.select = False
            bpy.ops.object.select_all(action='DESELECT')

        return nodes[rsm.main_node]

    def execute(self, context):
        options = RsmImportOptions(
            should_import_smoothing_groups=self.should_import_smoothing_groups
        )
        RsmImportOperator.import_rsm(self.filepath, options)
        return {'FINISHED'}

    @staticmethod
    def menu_func_import(self, context):
        self.layout.operator(RsmImportOperator.bl_idname, text='Ragnarok Online RSM (.rsm)')
