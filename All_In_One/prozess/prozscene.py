'''
Read files created with 'prozblend.py'.
To use: create a new Prozess with the path to the root directory of the exported scene.
'''

import array
import collections
from os import path
import imp

RawVertex = collections.namedtuple('Vertex', 'px py pz nx ny nz')
Vertex = collections.namedtuple('Vertex', 'px py pz nx ny nz u v')
Face = collections.namedtuple('Face', 'flags v n u')
Mesh = collections.namedtuple('Mesh', 'vertex index')

expectedVertexAttribs = 8 # pos(xyz) normal(xyz) texcoord(uv)

def importscene(blenderscenedir):
    scenepath = path.join(blenderscenedir, 'scene.py')
    return imp.load_source('scene', scenepath)

class Scene(object):
    def __init__(self, blenderscenedir):
        dir = path.normpath(blenderscenedir)
        self.rootdir = dir
        try:
            self.scene = importscene(dir)
        except ImportError:
            raise Exception('Could not find scene', dir)
        
    def scenedir(self):
        return self.rootdir

    def sceneinfo(self):
        return self.scene.scene
    
    def objects(self, type=None):
        if type == None: 
            return self.scene.objects
        return [obj for obj in self.scene.objects.itervalues() if obj['type'] == type]
    
    def cameras(self):
        return self.objects('CAMERA')
    
    def lights(self):
        return self.objects('LAMP')
    
    def meshes(self):
        return self.objects('MESH')
    
    def data_camera(self, name):
        return self.scene.cameras[name]
    
    def data_cameras(self):
        return self.scene.cameras
    
    def data_mesh(self, mesh):
        return self.scene.meshes[mesh]
    
    def data_meshes(self):
        return self.scene.meshes
    
    def data_material(self, mat):
        return self.scene.materials[mat]
    
    def data_materials(self):
        return self.scene.materials
    
    def data_texture(self, texture):
        return self.scene.textures[texture]
    
    def data_textures(self):
        return self.scene.textures
    
    def data_image(self, image):
        return self.scene.images[image]
    
    def data_images(self):
        return self.scene.images
    
    def meshnames(self):
        return self.scene.meshes.keys()
    
    def load_meshes(self):
        meshes = dict()
        for mesh in self.meshnames():
            print('Loading mesh: ', mesh, ' from scene: ', self.mesh_dir(mesh))
            meshes[mesh] = self.load_mesh(mesh)
        return meshes
        
    def vertexstride(self, buffer):
        '''
        Get the number of bytes between consecutive vertices.
        '''
        return expectedVertexAttribs * buffer.itemsize # attribcount * sizeof(float)
    
    def buffersize(self, buffer):
        '''
        Get the number of bytes in a VBO (or IBO, index buffer object).
        '''
        return len(buffer) * buffer.itemsize

    def mesh_dir(self, meshname):
        return path.join(path.join(self.rootdir, 'meshes'), meshname)
    
    def image_dir(self):
        return path.join(self.rootdir, 'images')
    
    def vertex_file(self, meshname):
        return path.join(self.mesh_dir(meshname), 'vertex.txt')
            
    def face_file(self, meshname):
        return path.join(self.mesh_dir(meshname), 'face.txt')
    
    def load_vertices(self, meshname):
        vertices = []
        append = vertices.append
        with open(self.vertex_file(meshname), 'r') as f:
            for line in f:
                append(RawVertex(*map(float, line.split())))
        return vertices
    
    def load_faces(self, meshname):
        faces = []
        with open(self.face_file(meshname), 'r') as f:
            for line in f:
                vertices = array.array('I')
                flags = array.array('I')
                normal = array.array('f')
                uv = array.array('f')
                faces.append(Face(flags, vertices, normal, uv))
                
                current_array = None
                current_converter = None
                for x in line.split():
                    if x.isalpha():
                        if x == 'v':
                            current_array = vertices
                            current_converter = int
                        elif x == 'f':
                            current_array = flags
                            current_converter = int
                        elif x == 'n':
                            current_array = normal
                            current_converter = float
                        elif x == 'u':
                            current_array = uv
                            current_converter = float
                    else:
                        current_array.append(current_converter(x))
        return faces
    
    def is_face_smooth(self, f):
        return len(f.n) == 0
        
    def is_face_unwrapped(self, f):
        return len(f.u) != 0
        
    def load_mesh(self, name):
        # TODO: don't need to have all raw faces in memory, just the vertices
        # read the faces lazily from disk while creating the index-/vertex-buffers.
        faces = self.load_faces(name)
        rawvertices = self.load_vertices(name)
        
        vertexbuffer = array.array('f')
        indexbuffer = array.array('I')
        vertices = dict()
        
        for f in faces:
            unwrapped = self.is_face_unwrapped(f)
            smooth = self.is_face_smooth(f)
            uv_index = 0
            
            indices = []
            
            for raw_index in f.v:
                v = rawvertices[raw_index]
                
                if unwrapped:
                    uv_u = f.u[uv_index*2]
                    uv_v = f.u[uv_index*2 + 1]
                    uv_index += 1
                else:
                    uv_u = 0
                    uv_v = 0
                
                if smooth: # use the vertex normal as-is
                    vertex = Vertex(*v, u=uv_u, v=uv_v)
                else: # use the face normal
                    vertex = Vertex(v.px, v.py, v.pz, f.n[0], f.n[1], f.n[2], uv_u, uv_v)
                    
                try_index = len(vertices)
                actual_index = vertices.setdefault(vertex, try_index)
                
                if actual_index == try_index:
                    vertexbuffer.extend(vertex)
                    
                indices.append(actual_index)
                
            indexbuffer.extend(indices[0:3])
            if len(indices) != 3:
                assert len(indices) == 4
                indexbuffer.extend((indices[2], indices[3], indices[0]))

        return Mesh(vertexbuffer, indexbuffer)
