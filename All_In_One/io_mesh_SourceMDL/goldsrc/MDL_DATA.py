from __future__ import absolute_import
from pprint import pformat
try:
    from .ByteIO import ByteIO
    from .GLOBALS import SourceVector
    # from MDL_DATA import StudioHDRFlags
    from .Utils import get_class_var_name
except:
    from MDLIO_ByteIO import ByteIO
    from GLOBALS import SourceVector
    # from MDL_DATA import StudioHDRFlags
    from Utils import get_class_var_name


class SourceMdlFileDataV10:
    def __init__(self):
        self.id = ''
        self.version = 0
        self.name = ''
        self.file_size = 0
        self.eye_position = SourceVector()
        self.hull_min_position = SourceVector()
        self.hull_max_position = SourceVector()
        self.view_bounding_box_min_position = SourceVector()
        self.view_bounding_box_max_position = SourceVector()

        self.flags = 0

        self.bone_count = 0
        self.bone_offset = 0

        self.bone_controller_count = 0
        self.bone_controller_offset = 0

        self.hitbox_set_count = 0
        self.hitbox_set_offset = 0

        self.local_sequence_count = 0
        self.local_sequence_offset = 0

        self.sequence_group_count = 0
        self.sequence_group_offset = 0



        self.texture_count = 0
        self.texture_offset = 0
        self.texture_data_offset = 0


        self.skin_reference_count = 0
        self.skin_family_count = 0
        self.skin_family_offset = 0

        self.body_part_count = 0
        self.body_part_offset = 0

        self.local_attachment_count = 0
        self.local_attachment_offset = 0

        self.sound_table = 0
        self.sound_index = 0
        self.sound_groups = 0
        self.sound_group_offset = 0

        self.transitions_count = 0
        self.transition_offset = 0

        self.reserved = []
        self.animation_descs = []
        self.anim_blocks = []
        self.anim_block_relative_path_file_name = ""
        self.attachments = []  # type: List[SourceMdlAttachment]
        self.body_parts = []  # type: List[SourceMdlBodyPart]
        self.bones = []  # type: List[SourceMdlBone]
        self.bone_controllers = []  # type: List[SourceMdlBoneController]
        self.bone_table_by_name = []
        self.flex_descs = []  # type: List[SourceMdlFlexDesc]
        self.flex_controllers = []  # type: List[SourceMdlFlexController]
        self.flex_rules = []  # type: List[SourceMdlFlexRule]
        self.hitbox_sets = []
        self.ik_chains = []
        self.ik_locks = []
        self.key_values_text = ""
        self.local_node_names = []
        self.mouths = []  # type: List[SourceMdlMouth]
        self.pose_param_descs = []
        self.sequence_descs = []
        self.skin_families = []  # type: List[List[int]]
        self.surface_prop_name = ""
        self.texture_paths = []  # type: List[str]
        self.textures = []  # type: List[SourceMdlTexture]
        self.section_frame_count = 0
        self.section_frame_min_frame_count = 0
        self.actual_file_size = 0
        self.flex_frames = []  # type: List[FlexFrame]
        self.bone_flex_drivers = []  # type: List[SourceBoneFlexDriver]
        self.flex_controllers_ui = []  # type: List[SourceFlexControllerUI]
        self.eyelid_flex_frame_indexes = []
        self.first_animation_desc = None
        self.first_animation_desc_frame_lines = {}
        self.mdl_file_only_has_animations = False
        self.procedural_bones_command_is_used = False
        self.weight_lists = []
        self.name_offset = 0
        self.bodypart_frames = []  # type: List[List[Tuple[int,SourceMdlBodyPart]]]

    def read(self, reader: ByteIO):
        self.read_header00(reader)
        self.read_header01(reader)

    def read_header00(self, reader: ByteIO):
        self.id = ''.join(list([chr(reader.read_uint8()) for _ in range(4)]))
        self.version = reader.read_uint32()
        print('Found MDL version', self.version)
        # self.checksum = reader.read_uint32()
        self.name = reader.read_ascii_string(64)
        self.file_size = reader.read_uint32()

    def read_header01(self, reader: ByteIO):
        self.eye_position.read(reader)

        self.hull_min_position.read(reader)

        self.hull_max_position.read(reader)

        self.view_bounding_box_min_position.read(reader)

        self.view_bounding_box_max_position.read(reader)

        self.flags = reader.read_uint32()

        self.bone_count = reader.read_uint32()
        self.bone_offset = reader.read_uint32()

        self.bone_controller_count = reader.read_uint32()
        self.bone_controller_offset = reader.read_uint32()

        self.hitbox_set_count = reader.read_uint32()
        self.hitbox_set_offset = reader.read_uint32()

        self.local_sequence_count = reader.read_uint32()
        self.local_sequence_offset = reader.read_uint32()
        self.sequence_group_count = reader.read_uint32()
        self.sequence_group_offset = reader.read_uint32()

        self.texture_count = reader.read_uint32()
        self.texture_offset = reader.read_uint32()
        self.texture_data_offset = reader.read_int32()

        self.skin_reference_count = reader.read_uint32()
        self.skin_family_count = reader.read_uint32()
        self.skin_family_offset = reader.read_uint32()

        self.body_part_count = reader.read_uint32()
        self.body_part_offset = reader.read_uint32()

        self.local_attachment_count = reader.read_uint32()
        self.local_attachment_offset = reader.read_uint32()

        self.sound_table = reader.read_uint32()
        self.sound_index = reader.read_uint32()
        self.sound_groups = reader.read_uint32()
        self.sound_group_offset = reader.read_uint32()

        self.transitions_count = reader.read_uint32()
        self.transition_offset = reader.read_uint32()

        if self.body_part_count == 0 and self.local_sequence_count > 0:
            self.mdl_file_only_has_animations = True

    def print_info(self, indent=0):
        def iprint(indent2, arg, fname=''):
            if indent + indent2:
                print('\t' * (indent + indent2),
                      *(get_class_var_name(self, arg).title().replace('_', ' '), ':', arg) if not fname else (
                          fname, ':', arg))
            else:
                print(*(get_class_var_name(self, arg).title(), ':', arg) if not fname else (fname, ':', arg))

        print('SourceMdlFileData:')
        iprint(1, self.id)
        iprint(1, self.version)
        iprint(1, self.name)
        iprint(1, self.file_size)
        iprint(1, self.flags, 'Flags')
        iprint(1, self.bone_count)
        iprint(1, self.texture_count)
        iprint(1, self.body_part_count, 'Body part count')

        pass

    def __repr__(self):
        return pformat(self.__dict__)

class SourceMdlBone:

    def __init__(self):

        self.boneOffset = 0
        self.name = ""
        self.parentBoneIndex = 0
        self.flags = 0
        self.boneControllerIndex = []
        self.position = SourceVector()
        self.rotation = SourceVector()
        self.pos_scale = SourceVector()
        self.rot_scale = SourceVector()


    def read(self, reader: ByteIO, mdl: SourceMdlFileDataV10):
        self.boneOffset = reader.tell()
        self.name = reader.read_ascii_string(32)
        self.parentBoneIndex = reader.read_int32()
        self.flags = reader.read_int32()
        self.boneControllerIndex = [reader.read_int32() for _ in range(6)]
        self.position.read(reader)
        self.rotation.read(reader)
        self.scale = [reader.read_float() for _ in range(6)]
        mdl.bones.append(self)

    def __repr__(self):
        return '<Bone "{}" pos:{} rot: {}>'.format(self.name,self.position.as_rounded(2),
                                                                 self.rotation.as_rounded(2),)

class SourceMdlBoneController:
    def __init__(self):
        self.boneIndex = 0
        self.type = 0
        self.startBlah = 0
        self.endBlah = 0
        self.restIndex = 0
        self.inputField = 0
        self.unused = []

    def read(self, reader: ByteIO, mdl: SourceMdlFileDataV10):
        self.boneIndex = reader.read_uint32()
        self.type = reader.read_uint32()
        self.startBlah = reader.read_uint32()
        self.endBlah = reader.read_uint32()
        self.restIndex = reader.read_uint32()
        self.inputField = reader.read_uint32()
        if mdl.version > 10:
            self.unused = [reader.read_uint32() for _ in range(8)]
        mdl.bone_controllers.append(self)
        return self

    def __str__(self):
        return '<BoneController bone index:{}>'.format(self.boneIndex)

    def __repr__(self):
        return '<BoneController bone index:{}>'.format(self.boneIndex)


if __name__ == '__main__':
    model = r"E:\PYTHON\io_mesh_SourceMDL\test_data\goldSrc\leet.mdl"
    reader = ByteIO(path=model)
    mdl = SourceMdlFileDataV10()
    mdl.read(reader)
    mdl.print_info()