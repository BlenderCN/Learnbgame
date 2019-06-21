import sys
from pprint import pprint

def split(array, n=3):
    return [array[i:i + n] for i in range(0, len(array), n)]


try:
    from .MDLIO_ByteIO import ByteIO
    from .VTX_DATA import *
except Exception:
    from MDLIO_ByteIO import ByteIO
    from VTX_DATA import *


class SourceVtxFile49:
    def __init__(self, path=None, file=None):
        self.final = False
        if path:
            self.reader = ByteIO(path=path + ".dx90.vtx")
        elif file:
            self.reader = file
        # print('Reading VTX file')
        self.vtx = SourceVtxFileData()
        self.read_source_vtx_header()
        # self.read_source_vtx_body_parts()

    def read_source_vtx_header(self):
        self.vtx.read(self.reader)

    def test(self):
        v_acc = 0
        i_acc = 0
        t_acc = 0
        for body_part in self.vtx.vtx_body_parts:
            print(body_part)
            for model in body_part.vtx_models:
                print('\t' * 1, model)
                for lod in model.vtx_model_lods:
                    print('\t' * 2, lod)
                    for mesh in lod.vtx_meshes:
                        print('\t' * 3, mesh)
                        for strip_group in mesh.vtx_strip_groups:
                            v_acc += strip_group.vertex_count
                            i_acc += strip_group.index_count
                            t_acc += strip_group.topology_indices_count
                            print('\t' * 4, strip_group)
                            # pprint(split(strip_group.vtx_indexes))
                            topo_shit = split(list(strip_group.topology),176)
                            print(len(topo_shit))
                            for topo in topo_shit:
                                print(topo)
                            # print(split(topo_shit, 176))
                            # with open('topology.bin', 'wb+') as fp:
                            #     fp.write(strip_group.topology)
                            for strip in strip_group.vtx_strips:
                                print('\t' * 5, strip)
                                # strip.vertex_count
                                if StripHeaderFlags.STRIP_IS_QUADLIST_EXTRA in strip.flags or StripHeaderFlags.STRIP_IS_QUADLIST_REG in strip.flags:
                                    pass

                                # return
        print('total_verts', v_acc)
        print('total_inds', i_acc)
        print('total_topology', t_acc)


if __name__ == '__main__':
    with open('log.log', "w") as f:  # replace filepath & filename
        with f as sys.stdout:
            # model_path = r'G:\SteamLibrary\SteamApps\common\SourceFilmmaker\game\usermod\models\red_eye\tyranno\raptor_subD'
            model_path = r'./test_data\subd'
            # model_path = r'.\test_data\l_pistol_noenv'
            # model_path = r'test_data\geavy'
            # model_path = r'G:\SteamLibrary\SteamApps\common\SourceFilmmaker\game\tf\models\player\heavy'
            # model_path = r'G:\SteamLibrary\SteamApps\common\SourceFilmmaker\game\usermod\models\red_eye\rick-and-morty\pink_raptor'
            # MDL_edit('E:\\MDL_reader\\sexy_bonniev2')
            a = SourceVtxFile49(model_path)
            # a = SourceVtxFile49(r'test_data\kali')
            # a = SourceVtxFile49(r'test_data\kali')

            a.test()
