import os

from MDLIO_ByteIO import ByteIO
from goldsrc.MDL_DATA import SourceMdlFileDataV10, SourceMdlBone, SourceMdlBoneController
from progressBar import Progress_bar


class SourceMdlFile10:

    def __init__(self, filepath):
        self.reader = ByteIO(path=filepath + '.mdl', copy_data_from_handle=False, )
        self.filename = os.path.basename(filepath + '.mdl')[:-4]
        self.file_data = SourceMdlFileDataV10()
        self.file_data.read(self.reader)
        self.read_bones()
        self.read_bone_controllers()
        self.read_skin_families()
        # self.read_attachments()
        # self.read_mouths()
        # self.read_bone_flex_drivers()
        # self.read_flex_controllers_ui()
        # self.read_body_parts()
        # self.read_textures()
        # self.read_texture_paths()
        # self.build_flex_frames()
        # self.prepare_models()
        # # self.read_local_animation_descs()
        # self.read_sequences()
        # # print(self.mdl)

    def read_bones(self):
        if self.file_data.bone_count > 0:
            pb = Progress_bar(desc='Reading bones', max_=self.file_data.bone_count, len_=20)
            self.reader.seek(self.file_data.bone_offset, 0)
            for i in range(self.file_data.bone_count):
                pb.draw()
                SourceMdlBone().read(self.reader, self.file_data)
                pb.increment(1)
                pb.draw()

    def read_bone_controllers(self):
        if self.file_data.bone_controller_count > 0:
            pb = Progress_bar(desc='Reading Bone Controllers', max_=self.file_data.bone_controller_count, len_=20)
            for _ in range(self.file_data.bone_controller_count):
                pb.draw()
                SourceMdlBoneController().read(self.reader, self.file_data)
                pb.increment(1)

    def read_skin_families(self):
        if self.file_data.skin_family_count and self.file_data.skin_reference_count:
            self.reader.seek(self.file_data.skin_family_offset)
            for _ in range(self.file_data.skin_family_count):
                skin_ref = []
                for _ in range(self.file_data.skin_reference_count):
                    skin_ref.append(self.reader.read_int16())
                self.file_data.skin_families.append(skin_ref)

    def test(self):
        for bone in self.file_data.bones:
            print(bone)

if __name__ == '__main__':
    model_path = r"E:\PYTHON\io_mesh_SourceMDL\test_data\goldSrc\leet"
    a = SourceMdlFile10(model_path)
    a.test()
    a.file_data.print_info()
