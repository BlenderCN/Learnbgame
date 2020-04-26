import os.path

# sys.path.append(r'E:\PYTHON\io_mesh_SourceMDL')
try:
    from .ValveFile import ValveFile
    from .Vmesh_IO import VMESH_IO
except:
    from Source2.ValveFile import ValveFile
    from Source2.Vmesh_IO import VMESH_IO
import bpy
from mathutils import Vector


class Vmdl_IO:

    def __init__(self, vmdl_path, import_meshes):
        self.valve_file = ValveFile(vmdl_path)
        self.valve_file.read_block_info()
        self.valve_file.check_external_resources()

        self.name = str(os.path.basename(vmdl_path).split('.')[0])
        # print(self.valve_file.data.data.keys())
        self.remap_table = self.valve_file.data.data['PermModelData_t']['m_remappingTable']
        self.model_skeleton = self.valve_file.data.data['PermModelData_t']['m_modelSkeleton']
        self.bone_names = self.model_skeleton['m_boneName']
        self.bone_positions = self.model_skeleton['m_bonePosParent']
        self.bone_rotations = self.model_skeleton['m_boneRotParent']
        self.bone_parents = self.model_skeleton['m_nParent']
        for res, path in self.valve_file.available_resources.items():
            if 'vmesh' in res and import_meshes:
                vmesh = VMESH_IO(path)
                vmesh.build_skeleton()
                vmesh.build_meshes(self.bone_names, self.remap_table)

if __name__ == '__main__':
    a = Vmdl_IO(r'F:\PYTHON\io_mesh_SourceMDL/test_data/source2/sniper.vmdl_c', True)
    with open('test.h', 'w') as f:
        a.valve_file.dump_structs(f)
