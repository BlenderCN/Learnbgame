from ctypes import (
    Structure,
    LittleEndianStructure,
    c_uint, c_uint8, c_uint16, c_float, c_char, c_short, c_ushort, c_byte, c_ubyte,
)

from albam.engines.mtframework.defaults import DEFAULT_MATERIAL
from albam.lib.structure import DynamicStructure


def unk_data_depends_on_other_unk(tmp_struct):
    if tmp_struct.unk_08:
        return c_ubyte * (tmp_struct.bones_array_offset - 176)
    else:
        return c_ubyte * 0


class Mod156(DynamicStructure):
    _fields_ = (('id_magic', c_char * 4),
                ('version', c_ubyte),
                ('version_rev', c_byte),
                ('bone_count', c_ushort),
                ('mesh_count', c_short),
                ('material_count', c_ushort),
                ('vertex_count', c_uint),
                ('face_count', c_uint),
                ('edge_count', c_uint),
                ('vertex_buffer_size', c_uint),
                ('vertex_buffer_2_size', c_uint),
                ('texture_count', c_uint),
                ('group_count', c_uint),
                ('bone_palette_count', c_uint),
                ('bones_array_offset', c_uint),
                ('group_offset', c_uint),
                ('textures_array_offset', c_uint),
                ('meshes_array_offset', c_uint),
                ('vertex_buffer_offset', c_uint),
                ('vertex_buffer_2_offset', c_uint),
                ('index_buffer_offset', c_uint),
                ('reserved_01', c_uint),
                ('reserved_02', c_uint),
                ('sphere_x', c_float),
                ('sphere_y', c_float),
                ('sphere_z', c_float),
                ('sphere_w', c_float),
                ('box_min_x', c_float),
                ('box_min_y', c_float),
                ('box_min_z', c_float),
                ('box_min_w', c_float),
                ('box_max_x', c_float),
                ('box_max_y', c_float),
                ('box_max_z', c_float),
                ('box_max_w', c_float),
                ('unk_01', c_uint),
                ('unk_02', c_uint),
                ('unk_03', c_uint),
                ('unk_04', c_uint),
                ('unk_05', c_uint),
                ('unk_06', c_uint),
                ('unk_07', c_uint),
                ('unk_08', c_uint),
                ('unk_09', c_uint),
                ('unk_10', c_uint),
                ('unk_11', c_uint),
                ('reserved_03', c_uint),
                ('unk_12', unk_data_depends_on_other_unk),
                ('bones_array', lambda s: Bone * s.bone_count),
                ('bones_unk_matrix_array', lambda s: (c_float * 16) * s.bone_count),
                ('bones_world_transform_matrix_array', lambda s: (c_float * 16) * s.bone_count),
                ('bones_animation_mapping', lambda s: (c_ubyte * 256) if s.bone_palette_count else c_ubyte * 0),
                ('bone_palette_array', lambda s: BonePalette * s.bone_palette_count),
                ('group_data_array', lambda s: GroupData * s.group_count),
                ('textures_array', lambda s: (c_char * 64) * s.texture_count),
                ('materials_data_array', lambda s: MaterialData * s.material_count),
                ('meshes_array', lambda s: Mesh156 * s.mesh_count),
                ('meshes_array_2_size', c_uint),
                ('meshes_array_2', lambda s: MeshBox * s.meshes_array_2_size),
                ('vertex_buffer', lambda s: c_ubyte * s.vertex_buffer_size),
                ('vertex_buffer_2', lambda s: c_ubyte * s.vertex_buffer_2_size),
                # TODO: investigate the padding
                ('index_buffer', lambda s: c_ushort * (s.face_count - 1)),
                )


class Bone(Structure):
    _fields_ = (('anim_map_index', c_ubyte),
                ('parent_index', c_ubyte),  # 255: root
                ('mirror_index', c_ubyte),
                ('palette_index', c_ubyte),
                ('unk_01', c_float),
                ('parent_distance', c_float),
                # Relative to the parent bone
                ('location_x', c_float),
                ('location_y', c_float),
                ('location_z', c_float),
                )


class BonePalette(Structure):
    _fields_ = (('unk_01', c_uint),
                ('values', c_ubyte * 32),
                )

    _comments_ = {'unk_01': 'Seems to be the count of meaninful values out of the 32 bytes, needs verification'}


class MeshBox(Structure):
    _fields_ = (('unk_01', c_float * 16),
                ('unk_02', c_float * 16),
                ('unk_03', c_float * 4),
                )


class GroupData(Structure):
    _fields_ = (('group_index', c_uint),
                ('unk_02', c_float),
                ('unk_03', c_float),
                ('unk_04', c_float),
                ('unk_05', c_float),
                ('unk_06', c_float),
                ('unk_07', c_float),
                ('unk_08', c_float),
                )
    _comments_ = {'group_index': "In ~25% of all RE5 mods, this value doesn't match the index"}


class MaterialData(Structure):
    _defaults_ = DEFAULT_MATERIAL
    _fields_ = (('unk_01', c_ushort),
                ('unk_flag_01', c_uint16, 1),
                ('unk_flag_02', c_uint16, 1),
                ('unk_flag_03', c_uint16, 1),
                ('unk_flag_04', c_uint16, 1),
                ('unk_flag_05', c_uint16, 1),
                ('unk_flag_06', c_uint16, 1),
                ('unk_flag_07', c_uint16, 1),
                ('unk_flag_08', c_uint16, 1),
                ('unk_flag_09', c_uint16, 1),
                ('unk_flag_10', c_uint16, 1),
                ('unk_flag_11', c_uint16, 1),
                # Always set to zero since 8 bones is not yet supported
                ('flag_8_bones_vertex', c_uint16, 1),
                ('unk_flag_12', c_uint16, 1),
                ('unk_flag_13', c_uint16, 1),
                ('unk_flag_14', c_uint16, 1),
                ('unk_flag_15', c_uint16, 1),
                ('unk_02', c_ushort),
                ('unk_03', c_short),
                ('unk_04', c_ushort),
                ('unk_05', c_ushort),
                ('unk_06', c_ushort),
                ('unk_07', c_ushort),
                ('unk_08', c_ushort),
                ('unk_09', c_ushort),
                ('unk_10', c_ushort),
                ('unk_11', c_ushort),
                ('texture_indices', c_uint * 8),
                ('unk_12', c_float),
                ('unk_13', c_float),
                ('unk_14', c_float),
                ('unk_15', c_float),
                ('unk_16', c_float),
                ('unk_17', c_float),
                ('unk_18', c_float),
                ('unk_19', c_float),
                ('unk_20', c_float),
                ('unk_21', c_float),
                ('unk_22', c_float),
                ('unk_23', c_float),
                ('unk_24', c_float),
                ('unk_25', c_float),
                ('unk_26', c_float),
                ('unk_27', c_float),
                ('unk_28', c_float),
                ('unk_29', c_float),
                ('unk_30', c_float),
                ('unk_31', c_float),
                ('unk_32', c_float),
                ('unk_33', c_float),
                ('unk_34', c_float),
                ('unk_35', c_float),
                ('unk_36', c_float),
                ('unk_37', c_float),)


class Mesh156(LittleEndianStructure):
    _fields_ = (('group_index', c_ushort),
                ('material_index', c_ushort),
                ('constant', c_ubyte),  # always 1
                ('level_of_detail', c_ubyte),
                ('unk_01', c_ubyte),
                ('vertex_format', c_ubyte),
                ('vertex_stride', c_ubyte),
                ('unk_02', c_ubyte),
                ('unk_03', c_ubyte),
                ('unk_flag_01', c_uint8, 1),
                ('unk_flag_02', c_uint8, 1),
                ('unk_flag_03', c_uint8, 1),
                ('unk_flag_04', c_uint8, 1),
                ('unk_flag_05', c_uint8, 1),
                ('use_cast_shadows', c_uint8, 1),
                ('unk_flag_06', c_uint8, 1),
                ('unk_flag_07', c_uint8, 1),
                ('vertex_count', c_ushort),
                ('vertex_index_end', c_ushort),
                ('vertex_index_start_1', c_uint),
                ('vertex_offset', c_uint),
                ('unk_05', c_uint),
                ('face_position', c_uint),
                ('face_count', c_uint),
                ('face_offset', c_uint),
                ('unk_06', c_ubyte),
                ('unk_07', c_ubyte),
                ('vertex_index_start_2', c_ushort),
                ('vertex_group_count', c_ubyte),
                ('bone_palette_index', c_ubyte),
                ('unk_08', c_ubyte),
                ('unk_09', c_ubyte),
                ('unk_10', c_ushort),
                ('unk_11', c_ushort),
                )


class VertexFormat0(Structure):
    _fields_ = (('position_x', c_float),
                ('position_y', c_float),
                ('position_z', c_float),
                ('normal_x', c_ubyte),
                ('normal_y', c_ubyte),
                ('normal_z', c_ubyte),
                ('normal_w', c_ubyte),
                ('tangent_x', c_ubyte),
                ('tangent_y', c_ubyte),
                ('tangent_z', c_ubyte),
                ('tangent_w', c_ubyte),
                ('uv_x', c_ushort),  # half float
                ('uv_y', c_ushort),  # half float
                ('uv2_x', c_ushort),  # half float
                ('uv2_y', c_ushort),  # half float
                ('uv3_x', c_ushort),  # half float
                ('uv3_y', c_ushort),  # half float
                )


class VertexFormat(Structure):
    # http://forum.xentax.com/viewtopic.php?f=10&t=3057&start=165
    _fields_ = (('position_x', c_short),
                ('position_y', c_short),
                ('position_z', c_short),
                ('position_w', c_short),
                ('bone_indices', c_ubyte * 4),
                ('weight_values', c_ubyte * 4),
                ('normal_x', c_ubyte),
                ('normal_y', c_ubyte),
                ('normal_z', c_ubyte),
                ('normal_w', c_ubyte),
                ('tangent_x', c_ubyte),
                ('tangent_y', c_ubyte),
                ('tangent_z', c_ubyte),
                ('tangent_w', c_ubyte),
                ('uv_x', c_ushort),  # half float
                ('uv_y', c_ushort),  # half float
                ('uv2_x', c_ushort),  # half float
                ('uv2_y', c_ushort),  # half float
                )


class VertexFormat2(VertexFormat):
    pass


class VertexFormat3(VertexFormat):
    pass


class VertexFormat4(VertexFormat):
    pass


class VertexFormat5(Structure):
    _fields_ = (('position_x', c_short),
                ('position_y', c_short),
                ('position_z', c_short),
                ('position_w', c_short),
                ('bone_indices', c_ubyte * 8),
                ('weight_values', c_ubyte * 8),
                ('normal_x', c_ubyte),
                ('normal_y', c_ubyte),
                ('normal_z', c_ubyte),
                ('normal_w', c_ubyte),
                ('uv_x', c_ushort),  # half float
                ('uv_y', c_ushort),  # half float
                )


class VertexFormat6(VertexFormat5):
    pass


class VertexFormat7(VertexFormat5):
    pass


class VertexFormat8(VertexFormat5):
    pass


VERTEX_FORMATS_TO_CLASSES = {0: VertexFormat0,
                             1: VertexFormat,
                             2: VertexFormat2,
                             3: VertexFormat3,
                             4: VertexFormat4,
                             5: VertexFormat5,
                             6: VertexFormat6,
                             7: VertexFormat7,
                             8: VertexFormat8,
                             }


CLASSES_TO_VERTEX_FORMATS = {v: k for k, v in VERTEX_FORMATS_TO_CLASSES.items()}
