# Miscellaneous useful functions

# stdlib imports
from array import array
from hashlib import sha256
# blender imports
from mathutils import Matrix, Vector
# Internal imports
from ..NMS.classes import Vector4f


#region Misc


def get_all_actions(obj):
    """Retrieve all actions given a blender object. Includes NLA-actions
       Full credit to this code goes to misnomer on blender.stackexchange
       (cf. https://blender.stackexchange.com/questions/14204/how-to-tell-which-object-uses-which-animation-action)
    """
    # slightly modified to return the name of the object, and the action
    if obj.animation_data:
        if obj.animation_data.action:
            yield (obj.name, obj.NMSAnimation_props.anim_name,
                   obj.animation_data.action)
        for track in obj.animation_data.nla_tracks:
            for strip in track.strips:
                yield obj.name, obj.NMSAnimation_props.anim_name, strip.action


def get_children(obj, curr_children, obj_types, condition=lambda x: True,
                 just_names=False):
    # return a flattened list of all the children of an object of a specified
    # type.
    # condition is a function applied to the child, and if it returns true,
    # then add the child to the list
    # if just_name is True, then only return the names, otherwise return the
    # actual objects themselves
    if type(obj_types) == str:
        obj_types = [obj_types]
    # otherwise we'll just assume that it is a list of strings
    for child in obj.children:
        if (child.NMSNode_props.node_types in obj_types and
                condition(child) is True):
            if just_names:
                curr_children.append(child.name)
            else:
                curr_children.append(child)
        curr_children += get_children(child, list(), obj_types, condition,
                                      just_names)
    return curr_children


# simple function to take a list and move the entry at the ith index to the the
# index 'index' (in the new list with the value pop'd)
def movetoindex(lst, i, index):
    k = lst.pop(i)          # this will break if i > len(lst)...
    return lst[:index] + [k] + lst[index:]


def nmsHash(data):
    """
    Lazy hash function for mesh data
    This is simply the last 16 hexadecimal degits of a sha256 hash
    """
    if isinstance(data, list):
        d = array('f')
        for verts in data:
            d.extend(verts)
    else:
        d = data
    return int(sha256(d).hexdigest()[-16:], 16)


def object_is_animated(ob):
    # this will check a blender object to see if it's parent has any anim data
    # (and it's parent recursively)
    if ob.animation_data is not None:
        # in this case just return true that the object has animation data
        return True
    else:
        if ob.parent is not None:
            return object_is_animated(ob.parent)
        else:
            return False


# !OBSOLETE
def patterned(lst, **kwargs):
    # this will return the values in the list in a patterned order
    # the generator will yield the pattern name, and the entry in the list
    patterns = dict()
    indexes = set()
    mapping = dict()
    for key in kwargs:
        patterns[key] = kwargs[key]
        for index in kwargs[key]:
            mapping[index] = key
        indexes.update(set(kwargs[key]))
    max_index = max(indexes)
    # missing = set(range(max_index+1)) - indexes

    i = 0       # current index in list
    k = 0       # current sub-index
    while i < len(lst):
        try:
            yield mapping[k], lst[i]
        except IndexError:
            pass
        i += 1
        if k < max_index:
            k += 1
        else:
            k = 0


def traverse(obj):
    # a custom generator to iterate over the tree of all the children on the
    # scene (including the Model object)
    # this returns objects from the branches inwards (which *shouldn't* be a
    # problem...)
    for child in obj.Children:
        for subvalue in traverse(child):
            yield subvalue
    else:
        yield obj


#region Transform Functions


def apply_local_transforms(rotmat, verts, norms, tangents, chverts):
    norm_mat = rotmat.inverted().transposed()

    print(len(verts), len(norms), len(tangents), len(chverts))
    for i in range(len(verts)):
        # Load Vertex
        vert = rotmat * Vector((verts[i]))
        # Store Transformed
        verts[i] = (vert[0], vert[1], vert[2], 1.0)
        # Load Normal
        norm = norm_mat * Vector((norms[i]))
        norm.normalize()
        # Store Transformed normal
        norms[i] = (norm[0], norm[1], norm[2], 1.0)
        # Load Tangent
        tang = norm_mat * Vector((tangents[i]))
        tang.normalize()
        # Store Transformed tangent
        tangents[i] = (tang[0], tang[1], tang[2], 1.0)
    for i in range(len(chverts)):
        chvert = rotmat * Vector((chverts[i]))
        # chvert = chverts[i]
        chverts[i] = Vector4f(x=chvert[0], y=chvert[1], z=chvert[2], t=1.0)


def calc_tangents(faces, verts, norms, uvs):
    """ Calculate the tangents.

    Parameters
    ----------
    faces : Unknown
    verts : Unknown
    norms : Unknown
    uvs : Unknown

    Returns
    -------
    tangents : Unknown
    """
    tangents = []
    # Init tangents
    for i in range(len(verts)):
        tangents.append(Vector((0, 0, 0, 0)))
    # We assume that verts length will be a multiple of 3 since
    # the mesh has been triangulated

    trisNum = len(faces)
    # Iterate in triangles
    for i in range(trisNum):
        tri = faces[i]
        vert_1 = tri[0]
        vert_2 = tri[1]
        vert_3 = tri[2]

        # Get Point Positions
        P0 = Vector((verts[vert_1]))
        P1 = Vector((verts[vert_2])) - P0
        P2 = Vector((verts[vert_3])) - P0

        P0_uv = Vector((uvs[vert_1]))
        P1_uv = Vector((uvs[vert_2])) - P0_uv
        P2_uv = Vector((uvs[vert_3])) - P0_uv
        # Keep only the 1st uvmap
        P1_uv = P1_uv.xy
        P2_uv = P2_uv.xy

        # Matrix determinant
        D = P1_uv[0] * P2_uv[1] - P2_uv[0] * P1_uv[1]
        D = 1.0 / max(D, 0.0001)  # Store the inverse right away

        # Apply equation
        tang = D * (P2_uv[1] * P1 - P1_uv[1] * P2)

        # Orthogonalize Gram-Shmidt
        n = Vector(norms[vert_1])
        tang = tang - n * tang.dot(n)
        # tang.normalize()

        # Add to existing
        # Vert_1
        tangents[vert_1] += tang
        # Vert_2
        tangents[vert_2] += tang
        # Vert_3
        # tang3 = Vector(tangents[vert_3]) + tang;
        # tang3.normalize()
        tangents[vert_3] += tang

    # Fix tangents
    for i in range(len(verts)):
        tang = tangents[i]
        tang.normalize()
        # (tangents[i].x, tangents[i].z, -tangents[i].y, 1.0)
        tangents[i] = (tangents[i].x, tangents[i].y, tangents[i].z, 1.0)

    return tangents


def transform_to_NMS_coords(ob):
    # this will return the local transform, rotation and scale of the object in
    # the NMS coordinate system

    M = Matrix()
    M[0] = Vector((1.0, 0.0, 0.0, 0.0))
    M[1] = Vector((0.0, 0.0, 1.0, 0.0))
    M[2] = Vector((0.0, -1.0, 0.0, 0.0))
    M[3] = Vector((0.0, 0.0, 0.0, 1.0))

    Minv = Matrix()
    Minv[0] = Vector((1.0, 0.0, 0.0, 0.0))
    Minv[1] = Vector((0.0, 0.0, -1.0, 0.0))
    Minv[2] = Vector((0.0, 1.0, 0.0, 0.0))
    Minv[3] = Vector((0.0, 0.0, 0.0, 1.0))

    return (M*ob.matrix_local*Minv).decompose()
