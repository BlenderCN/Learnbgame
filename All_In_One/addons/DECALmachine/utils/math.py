import sys
from mathutils import Vector, Matrix
from . debug import draw_vector


def remap(value, srcMin, srcMax, resMin, resMax):
    srcRange = srcMax - srcMin
    if srcRange == 0:
        return resMin
    else:
        resRange = resMax - resMin
        return (((value - srcMin) * resRange) / srcRange) + resMin


def flatten_matrix(mx):
    dimension = len(mx)
    return [mx[j][i] for i in range(dimension) for j in range(dimension)]


def get_center_between_points(point1, point2, center=0.5):
    return point1 + (point2 - point1) * center


def get_loc_matrix(location):
    return Matrix.Translation(location)


def get_rot_matrix(rotation):
    return rotation.to_matrix().to_4x4()


def get_sca_matrix(scale):
    scale_mx = Matrix()
    for i in range(3):
        scale_mx[i][i] = scale[i]
    return scale_mx


def create_bbox(obj=None, coords=None):
    minx = miny = minz = sys.maxsize
    maxx = maxy = maxz = -sys.maxsize

    if obj:
        coords = [v.co for v in obj.data.vertices]

    if coords:
        for co in coords:
            minx = co.x if co.x < minx else minx
            miny = co.y if co.y < miny else miny
            minz = co.z if co.z < minz else minz

            maxx = co.x if co.x > maxx else maxx
            maxy = co.y if co.y > maxy else maxy
            maxz = co.z if co.z > maxz else maxz


        coords = [(minx, miny, minz), (maxx, miny, minz), (maxx, maxy, minz), (minx, maxy, minz),
                  (minx, miny, maxz), (maxx, miny, maxz), (maxx, maxy, maxz), (minx, maxy, maxz)]

        edge_indices = [(0, 1), (1, 2), (2, 3), (3, 0),
                        (4, 5), (5, 6), (6, 7), (7, 4),
                        (0, 4), (1, 5), (2, 6), (3, 7)]

        tri_indices = [(0, 1, 2), (0, 2, 3),
                       (4, 5, 6), (4, 6, 7),
                       (0, 1, 5), (0, 5, 4),
                       (3, 0, 3), (3, 4, 7),
                       (1, 2, 6), (1, 6, 5),
                       (2, 3, 7), (2, 7, 6)]

        return coords, edge_indices, tri_indices


def get_bbox_dimensions(coords):
    width = (Vector(coords[1]) - Vector(coords[0])).length
    depth = (Vector(coords[3]) - Vector(coords[0])).length
    height = (Vector(coords[4]) - Vector(coords[0])).length

    return width, depth, height


def get_midpoint(coords):
    avg = Vector()
    for co in coords:
        avg += Vector(co)

    return avg / len(coords)


def create_rotation_matrix_from_normal(obj, normal, location=Vector((0, 0, 0)), debug=False):
    objup = Vector((0, 0, 1)) @ obj.matrix_world.inverted()

    dot = normal.dot(objup)
    if abs(round(dot, 6)) == 1:
        # use x instead of z as the up axis
        objup = Vector((1, 0, 0)) @ obj.matrix_world.inverted()

    tangent = objup.cross(normal)
    binormal = tangent.cross(-normal)

    if debug:
        objloc, _, _ = obj.matrix_world.decompose()
        draw_vector(objup, objloc, color=(1, 0, 0))

        draw_vector(normal, location)
        draw_vector(tangent, location, color=(0, 1, 0))
        draw_vector(binormal, location, color=(0, 0, 1))

        # print(round(binormal.length, 6))

    # create rotation matrix from coordnate vectors, see http://renderdan.blogspot.com/2006/05/rotation-matrix-from-axis-vectors.html
    rotmx = Matrix()
    rotmx[0].xyz = tangent.normalized()
    rotmx[1].xyz = binormal.normalized()
    rotmx[2].xyz = normal.normalized()

    # transpose, because blender is column major?
    return rotmx.transposed()


def resample_coords(coords, cyclic, segments=None, shift=0, debug=False):
    """
    Resamples a sequence of coordinates

    source: https://github.com/CGCookie/addon_common/pull/3/commits/ec20c8b01b97366c386a03ce47996adbeca2043c

    args:
        coords:   list of vert locations of type Mathutils.Vector
        segments: number of segments to divide path into
        cyclic:   True if the verts are a complete loop
        shift:    for cyclic verts chains, shifting the verts along
                  the loop can provide better alignment with previous
                  loops.  This should be -1 to 1 representing a percentage of segment length.
                  e.g., a shift of 0.5 with 8 segments will shift the verts 1/16th of the loop length

    return:
        new_coords: list of new vert locations of type Mathutils.Vector
    """

    # determine number of segments
    if not segments:
        segments = len(coords) - 1


    if len(coords) < 2:
        # There are not enough verts to do anything!
        return coords

    # zero out the shift in case the vert chain insn't cyclic
    if not cyclic and shift != 0:  # not PEP but it shows that we want shift = 0
        print('Not shifting because this is not a cyclic vert chain')
        shift = 0

    # calc_length
    arch_len = 0
    cumulative_lengths = [0]  # TODO: make this the right size and dont append

    for i in range(0, len(coords) - 1):
        v0 = coords[i]
        v1 = coords[i + 1]
        V = v1 - v0
        arch_len += V.length
        cumulative_lengths.append(arch_len)

    if cyclic:
        v0 = coords[-1]
        v1 = coords[0]
        V = v1 - v0
        arch_len += V.length
        cumulative_lengths.append(arch_len)
        segments += 1
        # print(cumulative_lengths)

    # identify vert indicies of import
    # this will be the largest vert which lies at
    # no further than the desired fraction of the curve

    # initialze new vert array and seal the end points
    if cyclic:
        new_coords = [[None]] * segments
        # new_coords[0] = verts[0]
    else:
        new_coords = [[None]] * (segments + 1)
        new_coords[0] = coords[0]
        new_coords[-1] = coords[-1]

    # index to save some looping through the cumulative lengths list
    # now we are leaving it 0 becase we may end up needing the beginning of the loop last
    # and if we are subdividing, we may hit the same cumulative lenght several times.
    # for now, use the slow and generic way, later developsomething smarter.
    n = 0

    for i in range(0, segments - 1 + cyclic * 1):
        desired_length_raw = (i + 1 + cyclic * -1) / segments * arch_len + shift * arch_len / segments
        # print('the length we desire for the %i segment is %f compared to the total length which is %f' % (i, desired_length_raw, arch_len))
        # like a mod function, but for non integers?
        if desired_length_raw > arch_len:
            desired_length = desired_length_raw - arch_len
        elif desired_length_raw < 0:
            desired_length = arch_len + desired_length_raw  # this is the end, + a negative number
        else:
            desired_length = desired_length_raw

        # find the original vert with the largets legnth
        # not greater than the desired length
        # I used to set n = J after each iteration
        for j in range(n, len(coords) + 1):

            if cumulative_lengths[j] > desired_length:
                break

        extra = desired_length - cumulative_lengths[j- 1]

        if j == len(coords):
            new_coords[i + 1 + cyclic * -1] = coords[j - 1] + extra * (coords[0] - coords[j - 1]).normalized()
        else:
            new_coords[i + 1 + cyclic * -1] = coords[j - 1] + extra * (coords[j] - coords[j - 1]).normalized()

    if debug:
        print(len(coords), len(new_coords))
        print(cumulative_lengths)
        print(arch_len)

    return new_coords
