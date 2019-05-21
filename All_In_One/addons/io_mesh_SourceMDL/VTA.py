import os.path
from typing import List

try:
    from MDL import SourceMdlFile49, SourceVector
    from MDL_DATA import SourceMdlBone, SourceMdlFlexDesc, SourceMdlFlex, SourceMdlVertAnim, SourceMdlMesh, \
        SourceMdlBodyPart, SourceMdlModel, FlexFrame
    from VVD import SourceVvdFile49
    from VVD_DATA import SourceVertex
except:
    from .MDL import SourceMdlFile49, SourceVector
    from .MDL_DATA import SourceMdlBone, SourceMdlFlexDesc, SourceMdlFlex, SourceMdlVertAnim, SourceMdlMesh, \
        SourceMdlBodyPart, SourceMdlModel, FlexFrame
    from .VVD import SourceVvdFile49
    from .VVD_DATA import SourceVertex


class VTA:

    def __init__(self, mdl, vvd, output_dir=os.path.dirname(__file__)):
        self.mdl = mdl  # type: SourceMdlFile49
        self.vvd = vvd  # type: SourceVvdFile49
        self.output_dir = output_dir
        self.global_vertex_offset = 0

    def write_vta(self, model: SourceMdlModel):
        fileh = open(os.path.join(self.output_dir, 'decompiled', model.name) + '.vta',
                     'w')
        self.write_header(fileh)
        self.write_nodes(fileh)
        self.write_skeleton(fileh, model)
        self.write_base(fileh)
        for n, flex_frame in enumerate(model.flex_frames):
            self.write_flex(fileh, flex_frame, n + 1)
        return model.name + ".vta"

    def write_base(self, fileh):
        fileh.write('vertexanimation\n')
        fileh.write('\ttime {} #{}\n'.format(0, 'basis shape key'))
        for vert_index in range(self.vvd.file_data.lod_vertex_count[0]):
            if self.vvd.file_data.fixup_count:
                vert = self.vvd.file_data.fixed_vertexes_by_lod[0][vert_index]
            else:
                vert = self.vvd.file_data.vertexes[vert_index]
            fileh.write("\t\t{} {} {}\n".format(vert_index, vert.position.as_string_smd, vert.normal.as_string_smd))

    def write_flex(self, fileh, flex_frame: FlexFrame, time):

        fileh.write('\ttime {} #{}\n'.format(time, flex_frame.flex_name))
        for flex, vertex_offset in zip(flex_frame.flexes, flex_frame.vertex_offsets):
            for fvert in flex.the_vert_anims:  # type: SourceMdlVertAnim
                vert_index = fvert.index
                vert = self.vvd.file_data.vertexes[vert_index + vertex_offset]  # type: SourceVertex
                delta = vert.position + SourceVector(fvert.the_delta)
                ndelta = vert.normal + SourceVector(fvert.the_n_delta)
                fileh.write("\t\t{} {} {}\n".format(vert_index, delta.as_string_smd, ndelta.as_string_smd))

    def write_header(self, fileh):
        fileh.write('//Created with SourceIO\n')
        fileh.write('version 1\n')

    def write_nodes(self, fileh):
        bones = self.mdl.file_data.bones  # type: List[SourceMdlBone]
        fileh.write('nodes\n')
        for num, bone in enumerate(bones):
            fileh.write('\t{} "{}" {}\n'.format(num, bone.name, bone.parentBoneIndex))
        fileh.write('end\n')

    def write_skeleton(self, fileh, model: SourceMdlModel):
        flexes = model.flex_frames  # type: List[FlexFrame]
        fileh.write('skeleton\n')
        fileh.write("\ttime {} #{}\n".format(0, "basis shape key"))
        for num, flex in enumerate(flexes):
            fileh.write("\ttime {} #{}\n".format(num + 1, flex.flex_name))
        fileh.write('end\n')

    def write_end(self, fileh):
        fileh.close()


if __name__ == '__main__':
    mdl = SourceMdlFile49(r'.\test_data\nick_hwm')
    vvd = SourceVvdFile49(r'.\test_data\nick_hwm')

    A = VTA(mdl, vvd)
    # A.write_vta()
