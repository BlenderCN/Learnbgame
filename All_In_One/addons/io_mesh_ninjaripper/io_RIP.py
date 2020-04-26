import random,os.path

import bpy
try:
    from .ByteIO import ByteIO
    from .RIP_DATA import *
    from .RIP import RIP
except:
    from ByteIO import ByteIO
    from RIP_DATA import *
    from RIP import RIP

class IO_RIP:
    def __init__(self, path: str = None, import_textures:bool=False,uv_scale = 1,vertex_scale = 1,auto_center = True):
        self.uv_scale = uv_scale
        self.vertex_scale = vertex_scale
        self.auto_center = auto_center
        self.rip = RIP(filepath=path)
        self.rip.read()
        self.rip_header = self.rip.header
        self.name = os.path.basename(path)
        self.create_mesh()
    @staticmethod
    def get_material(mat_name, model_ob):
        if mat_name:
            mat_name = mat_name
        else:
            mat_name = "Material"

        md = model_ob.data
        mat = None
        for candidate in bpy.data.materials:  # Do we have this material already?
            if candidate.name == mat_name:
                mat = candidate
        if mat:
            if md.materials.get(mat.name):  # Look for it on this mesh
                for i in range(len(md.materials)):
                    if md.materials[i].name == mat.name:
                        mat_ind = i
                        break
            else:  # material exists, but not on this mesh
                md.materials.append(mat)
                mat_ind = len(md.materials) - 1
        else:  # material does not exist
            # print("- New material: {}".format(mat_name))
            mat = bpy.data.materials.new(mat_name)
            md.materials.append(mat)
            # Give it a random colour
            randCol = []
            for i in range(3):
                randCol.append(random.uniform(.4, 1))
            mat.diffuse_color = randCol

            mat_ind = len(md.materials) - 1

        return mat_ind

    def create_mesh(self):
        verts, uvs, norms, colors = self.rip_header.get_flat_verts(self.uv_scale,self.vertex_scale)
        if verts:
            self.mesh_obj = bpy.data.objects.new(self.name, bpy.data.meshes.new(self.name+"_mesh"))
            bpy.context.scene.objects.link(self.mesh_obj)
            self.mesh = self.mesh_obj.data
            self.mesh.from_pydata(verts, [], self.rip_header.indexes)
            if self.auto_center:
                bpy.ops.object.select_all(action="DESELECT")
                self.mesh_obj.select = True
                bpy.context.scene.objects.active = self.mesh_obj
                bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
                bpy.ops.object.location_clear(clear_delta=False)

        if uvs:
            for uv in uvs:
                self.mesh.uv_textures.new()
                uv_data = self.mesh.uv_layers[0].data
                for i in range(len(uv_data)):
                    u = uv[self.mesh.loops[i].vertex_index]
                    uv_data[i].uv = u
        if norms:
            normals = []
            for inds in self.rip_header.indexes:
                for v in inds:
                    normals.append(norms[v])
            bpy.ops.object.shade_smooth()
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.normals_make_consistent(inside=False)
            bpy.ops.object.mode_set(mode='OBJECT')
            self.mesh.normals_split_custom_set(normals)
            self.mesh.use_auto_smooth = True