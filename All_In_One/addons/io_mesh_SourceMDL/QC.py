import math
import os.path
from pathlib import Path
try:
    from GLOBALS import SourceVector
    from MDL import SourceMdlFile49, SourceMdlModel
    from MDL_DATA import SourceMdlBodyPart, SourceMdlAttachment
    from MDL_DATA_ANIMATIONS import SourceMdlSequenceDesc
    from SMD import SMD
    from VTA import VTA
    from VTX import SourceVtxFile49
    from VVD import SourceVvdFile49
    from math_utilities import convert_rotation_matrix_to_degrees
except:
    from .GLOBALS import SourceVector
    from .MDL import SourceMdlFile49, SourceMdlModel
    from .MDL_DATA import SourceMdlBodyPart, SourceMdlAttachment
    from .MDL_DATA_ANIMATIONS import SourceMdlSequenceDesc
    from .SMD import SMD
    from .VTA import VTA
    from .VTX import SourceVtxFile49
    from .VVD import SourceVvdFile49
    from .math_utilities import convert_rotation_matrix_to_degrees


class QC:
    def __init__(self, mdl, vvd=None, vtx=None):
        self.mdl = mdl  # type:SourceMdlFile49
        self.vvd = vvd  # type:SourceVvdFile49
        self.vtx = vtx  # type:SourceVtxFile49
        self.smd = None
        self.vta = None
        self.fst_model = None

    def write_qc(self, output_dir=os.path.dirname(__file__)):
        fileh = open(os.path.join(output_dir, 'decompiled', self.mdl.filename) + '.qc', 'w')
        self.smd = SMD(self.mdl, self.vvd, self.vtx)
        self.vta = VTA(self.mdl, self.vvd)
        # self.smd.write_meshes()
        self.write_header(fileh)
        self.write_models(fileh)
        self.write_skins(fileh)
        self.write_misc(fileh)
        self.write_sequences(fileh)

    def write_header(self, fileh):
        fileh.write('// Created by SourceIO\n\n')
        fileh.write('$modelname "{}"\n\n'.format(self.mdl.file_data.name[:-4]))

    def write_models(self, fileh):
        for n, bp in enumerate(self.mdl.file_data.body_parts):  # type: SourceMdlBodyPart
            if bp.model_count > 1:
                self.write_bodygroup(fileh, bp)
            if bp.model_count == 1:
                self.write_model(fileh, n, 0, bp.models[0])
                pass  # write model_path
            if bp.model_count == 0:
                print('No models in bodygpoup!!!!')

    def write_model(self, fileh, bp_index, m_index, model: SourceMdlModel):
        to_skip = 0
        name = model.name if model.name else "mesh_{}-{}".format(bp_index, m_index)
        if not self.fst_model:
            self.fst_model = name
        model_name = str(Path(model.name).with_suffix('').with_suffix(''))
        if model.flex_frames and self.vvd:
            fileh.write('$model "{0}" "{0}"'.format(model_name))
            fileh.write('{\n')
            fileh.write('\tflexfile "{}" \n'.format(self.vta.write_vta(model)))
            fileh.write('\t{\n')
            fileh.write("\t\tdefaultflex frame 0\n")
            for n, flex_frame in enumerate(model.flex_frames):
                if flex_frame.has_partner:
                    fileh.write('\t\tflexpair "{}" 1 frame {}\n'.format(flex_frame.flex_name, n + 1 + to_skip))
                    to_skip += 1
                pass
            fileh.write('\t}\n')

            fileh.write('}\n\n')
        else:
            fileh.write('$model "{0}" "{0}"\n\n'.format(model_name))

    def write_bodygroup(self, fileh, bp):
        fileh.write('$bodygroup "{}"\n'.format(bp.name))
        fileh.write('{\n')
        for model in bp.models:  # type: SourceMdlModel
            if model.mesh_count == 0:
                fileh.write("\tblank\n")
            else:
                if not self.fst_model:
                    self.fst_model = model.name
                model_name = str(Path(model.name).with_suffix('').with_suffix(''))
                fileh.write('\tstudio "{}"\n'.format(model_name))
                if model.flex_frames and self.vvd:
                    fileh.write(
                        "//WARNING: this {} have flexes! Additional VTA will be written, you can import them manually\n"
                        "//If you want to compile it back correctly - export as DMX\n".format(model.name)
                    )
                    self.vta.write_vta(model)
        fileh.write('}\n\n')

    def write_skins(self, fileh):
        fileh.write('$texturegroup "skinfamilies"\n{\n')
        for skin_fam in self.mdl.file_data.skin_families:
            fileh.write('{')
            for mat in skin_fam:
                mat_name = self.mdl.file_data.textures[mat].path_file_name
                fileh.write('"{}" '.format(mat_name))
                pass
            fileh.write('}\n')

        fileh.write('\n}\n\n')

    def write_misc(self, fileh):
        fileh.write('$surfaceprop "{}"\n\n'.format(self.mdl.file_data.surface_prop_name))
        deflection = math.acos(self.mdl.file_data.max_eye_deflection)
        deflection = math.degrees(deflection)
        fileh.write('$maxeyedeflection {:.1f}\n\n'.format(deflection))
        fileh.write('$eyeposition {}\n\n'.format(self.mdl.file_data.eye_position.as_string_smd))
        self.write_texture_paths(fileh)
        self.write_attachment(fileh)
        fileh.write('$cbox {} {}\n\n'.format(self.mdl.file_data.view_bounding_box_min_position.as_rounded(3),
                                             self.mdl.file_data.view_bounding_box_max_position.as_rounded(3)))
        fileh.write('$bbox {} {}\n\n'.format(self.mdl.file_data.hull_min_position.as_rounded(3),
                                             self.mdl.file_data.hull_max_position.as_rounded(3)))

    def write_texture_paths(self, fileh):
        for n, texture_path in enumerate(self.mdl.file_data.texture_paths):
            if n == 0 and not texture_path:
                fileh.write('$cdmaterials "{}"\n'.format(texture_path))
            elif texture_path:
                fileh.write('$cdmaterials "{}"\n'.format(texture_path))
        fileh.write('\n')

    def write_attachment(self, fileh):
        for attachment in self.mdl.file_data.attachments:  # type: SourceMdlAttachment
            # $attachment "eyes" "bip_head" 4.63 - 8.34 - 0.51 rotate 0.12 - 3.73 89.99
            bone = self.mdl.file_data.bones[attachment.localBoneIndex]
            fileh.write('$attachment "{}" "{}" {} rotate {}\n'.format(attachment.name, bone.name,
                                                                      SourceVector([attachment.localM14,
                                                                                    attachment.localM24,
                                                                                    attachment.localM34]).as_rounded(2),
                                                                      SourceVector(convert_rotation_matrix_to_degrees(
                                                                          attachment.localM11, attachment.localM21,
                                                                          attachment.localM31, attachment.localM12,
                                                                          attachment.localM22, attachment.localM32,
                                                                          attachment.localM33)).to_degrees().as_rounded(
                                                                          2)))
        fileh.write('\n')

    def write_sequences(self, fileh):
        for sequence in self.mdl.file_data.sequence_descs:  # type: SourceMdlSequenceDesc

            fileh.write('$sequence "{}" '.format(sequence.theName.replace("@", '')))
            fileh.write('{\n')
            fileh.write('\t"{}"\n'.format(self.fst_model))
            fileh.write('\tactivity "{}" 1\n'.format(
                sequence.theActivityName if sequence.theActivityName else "ACT_DIERAGDOLL"))
            fileh.write('\tfadein {:.2f}\n'.format(sequence.fadeInTime))
            fileh.write('\tfadeout {:.2f}\n'.format(sequence.fadeOutTime))
            fileh.write('\tfps {}\n'.format(30))
            fileh.write('}')


if __name__ == '__main__':
    # model_path = r'.\test_data\test_case-2models-with-flexes'
    model_path = r"G:\SteamLibrary\SteamApps\common\SourceFilmmaker\game\Furry\models\Dragon-V0942\Mathew_Kelly\mathew_kelly"
    # model_path = r'G:\SteamLibrary\SteamApps\common\SourceFilmmaker\game\tf_movies\models\player\hwm\spy'
    # model = r'H:\games\Titanfall 2\extr\models\weapons\titan_sniper_rifle\w_titan_sniper_rifle'
    # mdl = SourceMdlFile49(r'.\test_data\pink_raptor')
    mdl = SourceMdlFile49(model_path)
    file_data = SourceVvdFile49(model_path)
    vtx = SourceVtxFile49(model_path)
    # mdl2 = SourceMdlFile53(model)

    # A = QC(mdl)
    # B = QC(mdl1)
    # C = QC(mdl2,mdl2.VVD,mdl2.VTX)
    # C.write_qc()
    A = QC(mdl, file_data, vtx)
    A.write_qc()
    # B.write_qc()
