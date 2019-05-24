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
            return obj.__getitem__(id) if allowGetNone else optional(obj.__getitem__(id), default)
        assert type(id) is str, "attribute identifier should be a string"
        return obj.__getattribute__(id) if allowGetNone else optional(obj.__getattribute__(id), default)
    except KeyError or AttributeError:
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