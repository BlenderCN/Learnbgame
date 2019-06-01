import bpy
import os,mathutils

class MeshLoader(object):
# class MeshLoader(bpy.types.PropertyGroup):
    @classmethod
    def register(cls):
        pass

    @classmethod
    def unregister(cls):
        pass

    def __init__(self, discrete_method,obj_name, ver_num):
        self.discrete_method = discrete_method
        self.obj_name = obj_name
        self.ver_num = ver_num
        
    def get_mesh_filepath(self, frame_id, ext):

        file_name = self.obj_name+ "_" + str(frame_id) +'.' + ext
        file_path = os.path.join('lib', self.discrete_method, 'output', self.obj_name,  file_name)
        return file_path

 
    def get_new_vertices_position_vtk(self, file_path):
        """read from vtk"""
        with open(file_path) as f:
            obj_data = f.readlines()

        vertexs = []
        vertex_data_line_id = 0
        for i in range(len(obj_data)):
            data_split = obj_data[i].split()
            if(len(data_split) > 0 and data_split[0] == 'POINTS'):
                vertex_data_line_id = i + 1
                
        for i in range(self.ver_num):
            for one_data in obj_data[vertex_data_line_id + i].split():
                vertexs.append(float(one_data))

        return vertexs
    
    
    def get_new_vertices_position(self, file_path):
        """ simple read form obj"""

        with open(file_path, 'r') as f:
            obj_data = f.read()

        vertexs = obj_data.split('f')[0].replace('v','').split()
    
        vertexs = list(map(float, vertexs))

        return vertexs
    
    
    def import_frame_mesh(self, frame_id, ext):
        raw_path = os.getcwd()
        script_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
        assert os.path.basename(script_path) == 'blender-physics', 'script_path is wrong'
        os.chdir(script_path)

        file_path = self.get_mesh_filepath(frame_id, ext)

        if ext == 'obj':
            vertexs_new = self.get_new_vertices_position(file_path)
        elif ext == 'vtk':
            vertexs_new = self.get_new_vertices_position_vtk(file_path)
        
        cache_object = bpy.data.objects[self.obj_name]
        cache_object.data.vertices.foreach_set('co', vertexs_new)
        cache_object.data.update()

        """transform"""
        cache_object.data.transform(mathutils.Matrix.Identity(4))        
        cache_object.matrix_world = mathutils.Matrix.Identity(4)
        return cache_object
    

            

    def update_transforms(self):
        cache_object = self.get_cache_object()
        transvect = mathutils.Vector((self.bounds.x, self.bounds.y, self.bounds.z))
        transmat = mathutils.Matrix.Translation(-transvect)
        cache_object.data.transform(transmat)
        domain_object = self._get_domain_object()
        domain_bounds = AABB.from_blender_object(domain_object)

        domain_pos = mathutils.Vector((domain_bounds.x, domain_bounds.y, domain_bounds.z))
        scalex = (math.ceil(domain_bounds.xdim / self.bounds.dx) * self.bounds.dx) / self.bounds.width
        scaley = (math.ceil(domain_bounds.ydim / self.bounds.dx) * self.bounds.dx) / self.bounds.height
        scalez = (math.ceil(domain_bounds.zdim / self.bounds.dx) * self.bounds.dx) / self.bounds.depth
        scale = min(scalex, scaley, scalez)
        cache_object.matrix_world = mathutils.Matrix.Identity(4)
        cache_object.matrix_parent_inverse = domain_object.matrix_world.inverted()
        cache_object.scale = (scale, scale, scale)
        cache_object.location = domain_pos
    
            
        
# def register():
#     bpy.utils.register_class(PhysikaMeshCache)

# def unregister():
#     bpy.utils.unregister_class(PhysikaMeshCache)
        

        
        

        
