import bpy
from time import time

def logTime(func, *args, **kwargs):
    def wrapped(*args, **kwargs):
        t1 = time()
        result = func(*args, **kwargs)
        t2 = time()
        print(func.__name__, "took", t2-t1, "seconds")
        return result
    return wrapped

def clip(val, lo, hi):
    return min(hi, max(lo, val))

def optional(value, default):
    """ Returns a given default value, instead of None. """
    if value is not None:
        return value
    return default

def optionalKey(obj, id, default=None, allowGetNone=False):
    """
    Extracts an optional property, capturing exceptions.
    If object is a dict, use id as a key and return default is the key is not set.
    If object is no dict, assume id is an attribute and return default if it is not found.
    Unless allowGetNone is set, if the item/attribute is None, default will be returned.
    """
    try:
        if type(obj) is dict:
            return obj[id] if allowGetNone else optional(obj[id], default)
        assert type(id) is str, "attribute identifier should be a string"
        return getattr(obj, id) if allowGetNone else optional(getattr(obj, id), default)
    except (KeyError, AttributeError):
        return default

def linkAndSelect(obj, context=bpy.context):
    context.scene.objects.link(obj)
    bpy.ops.object.select_all(action = "DESELECT")
    obj.select = True
    context.scene.objects.active = obj

def makeDiffuseMaterial(col, name="Diffuse"):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = col
    mat.specular_intensity = 0
    return mat

def mergeMeshPydata(*args):
    """
    Merge the pydata for different meshes.
    The arguments are lists/tuples, containing the data for each mesh.
    These must be ordered the same way and the first entry of each must contain the vertices.
    E.g.:  mergeMeshPydata([verts1, edges1, faces1], (verts2, edges2, faces2), ...)
    You can also just pass one, or more than two index sets (edges/faces) per tuple.
    The result tuple has the same ordering as the inputs.
    """
    result = [x.copy() for x in args[0]]
    for tup in args[1:]:
        assert len(tup)==len(result), "all tuples must be of the sampe length"
        offset = len(result[0])
        result[0].extend(tup[0])
        for i in range(1, len(result)):
            result[i].extend( [idx+offset for idx in idxtup] for idxtup in tup[i] )
    return result

class MeshMerger:
    """
    Combine meshes that are present as vertex and face lists (see bpy.types.Mesh.from_pydata).
    In addition, each of the meshes can be assigned a material.
    """
    def __init__(self):
        self.vertices    = []
        self.faces       = []
        self.materialIndices = [0]
        self.materials   = []
    
    def add(self, verts, faces, material=None):
        """Add new vertices and faces. If a material is given, it will be assigned to all the new faces."""
        self.vertices, self.faces = mergeMeshPydata((self.vertices, self.faces), (verts, faces))
        self.materialIndices.append(len(self.faces))
        self.materials.append(material)
    
    def buildMesh(self, name):
        """Create a Blender mesh from the previously added data."""
        newMesh = bpy.data.meshes.new(name)
        newMesh.from_pydata(self.vertices, [], self.faces)
        newMesh.update()
        
        #assert False, (self.materialIndices, len(self.faces))
        for mat, fromIdx, toIdx in zip(self.materials, self.materialIndices[:-1], self.materialIndices[1:]):
            if mat is not None:
                newMesh.materials.append(mat)
                for p in range(fromIdx, toIdx):
                    newMesh.polygons[p].material_index = len(newMesh.materials)-1
        return newMesh

def isIterable(val):
    try:
        iter(val)
        return True
    except TypeError:
        return False