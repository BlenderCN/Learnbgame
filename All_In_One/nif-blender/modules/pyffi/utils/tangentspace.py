"""A module for tangent space calculation."""

# ***** BEGIN LICENSE BLOCK *****
#
# Copyright (c) 2007-2012, Python File Format Interface
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#
#    * Redistributions in binary form must reproduce the above
#      copyright notice, this list of conditions and the following
#      disclaimer in the documentation and/or other materials provided
#      with the distribution.
#
#    * Neither the name of the Python File Format Interface
#      project nor the names of its contributors may be used to endorse
#      or promote products derived from this software without specific
#      prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# ***** END LICENSE BLOCK *****

from pyffi.utils import mathutils


def getTangentSpace(vertices=None,
                    normals=None,
                    uvs=None,
                    triangles=None,
                    orientation=False,
                    orthogonal=True
                    ):
    """Calculate tangent space data.

    >>> vertices = [(0,0,0), (0,1,0), (1,0,0)]
    >>> normals = [(0,0,1), (0,0,1), (0,0,1)]
    >>> uvs = [(0,0), (0,1), (1,0)]
    >>> triangles = [(0,1,2)]
    >>> getTangentSpace(vertices = vertices, normals = normals, uvs = uvs, triangles = triangles)
    ([(0.0, 1.0, 0.0), (0.0, 1.0, 0.0), (0.0, 1.0, 0.0)], [(1.0, 0.0, 0.0), (1.0, 0.0, 0.0), (1.0, 0.0, 0.0)])

    :param vertices: A list of vertices (triples of floats/ints).
    :param normals: A list of normals (triples of floats/ints).
    :param uvs: A list of uvs (pairs of floats/ints).
    :param triangles: A list of triangle indices (triples of ints).
    :param orientation: Set to ``True`` to return orientation (this is used by
        for instance Crysis).
    :return: Two lists of vectors, tangents and binormals. If C{orientation}
        is ``True``, then returns an extra list with orientations (containing
        floats which describe the total signed surface of all faces sharing
        the particular vertex).
    """

    # validate input
    if len(vertices) != len(normals) or len(vertices) != len(uvs):
        raise ValueError(
            "lists of vertices, normals, and uvs must have the same length")

    bin_norm = [(0, 0, 0) for i in range(len(vertices))]
    tan_norm = [(0, 0, 0) for i in range(len(vertices))]
    orientations = [0 for i in range(len(vertices))]

    # calculate tangents and binormals from vertex and texture coordinates
    for t1, t2, t3 in triangles:
        # skip degenerate triangles
        if t1 == t2 or t2 == t3 or t3 == t1:
            continue

        # get vertices, uvs, and directions of the triangle
        v1 = vertices[t1]
        v2 = vertices[t2]
        v3 = vertices[t3]
        w1 = uvs[t1]
        w2 = uvs[t2]
        w3 = uvs[t3]
        v2v1 = mathutils.vecSub(v2, v1)
        v3v1 = mathutils.vecSub(v3, v1)
        w2w1 = mathutils.vecSub(w2, w1)
        w3w1 = mathutils.vecSub(w3, w1)

        # surface of triangle in texture space
        r = w2w1[0] * w3w1[1] - w3w1[0] * w2w1[1]

        # sign of surface
        r_sign = (1 if r >= 0 else -1)

        # contribution of this triangle to tangents and binormals
        sdir = (
            r_sign * (w3w1[1] * v2v1[0] - w2w1[1] * v3v1[0]),
            r_sign * (w3w1[1] * v2v1[1] - w2w1[1] * v3v1[1]),
            r_sign * (w3w1[1] * v2v1[2] - w2w1[1] * v3v1[2]))
        try:
            sdir = mathutils.vecNormalized(sdir)
        except ZeroDivisionError:  # catches zero vector
            continue  # skip triangle
        except ValueError:  # catches invalid data
            continue  # skip triangle

        tdir = (
            r_sign * (w2w1[0] * v3v1[0] - w3w1[0] * v2v1[0]),
            r_sign * (w2w1[0] * v3v1[1] - w3w1[0] * v2v1[1]),
            r_sign * (w2w1[0] * v3v1[2] - w3w1[0] * v2v1[2]))
        try:
            tdir = mathutils.vecNormalized(tdir)
        except ZeroDivisionError:  # catches zero vector
            continue  # skip triangle
        except ValueError:  # catches invalid data
            continue  # skip triangle

        # vector combination algorithm could possibly be improved
        for i in (t1, t2, t3):
            tan_norm[i] = mathutils.vecAdd(tan_norm[i], tdir)
            bin_norm[i] = mathutils.vecAdd(bin_norm[i], sdir)
            orientations[i] += r

    # convert into orthogonal space
    xvec = (1, 0, 0)
    yvec = (0, 1, 0)
    for i, norm in enumerate(normals):
        if abs(1 - mathutils.vecNorm(norm)) > 0.01:
            raise ValueError(
                "tangentspace: unnormalized normal in list of normals (%s, norm is %f)" % (norm, mathutils.vecNorm(norm)))
        try:
            # turn norm, bin_norm, tan_norm into a base via Gram-Schmidt
            bin_norm[i] = mathutils.vecSub(bin_norm[i],
                                           mathutils.vecscalarMul(norm,
                                                                  mathutils.vecDotProduct(norm,
                                                                                          bin_norm[i]
                                                                                          )
                                                                  )
                                           )
            bin_norm[i] = mathutils.vecNormalized(bin_norm[i])
            tan_norm[i] = mathutils.vecSub(tan_norm[i],
                                           mathutils.vecscalarMul(norm,
                                                                  mathutils.vecDotProduct(norm,
                                                                                          tan_norm[i]
                                                                                          )
                                                                  )
                                           )
            tan_norm[i] = mathutils.vecSub(tan_norm[i],
                                           mathutils.vecscalarMul(bin_norm[i],
                                                                  mathutils.vecDotProduct(norm,
                                                                                          bin_norm[i]
                                                                                          )
                                                                  )
                                           )
            tan_norm[i] = mathutils.vecNormalized(tan_norm[i])
        except ZeroDivisionError:
            # insuffient data to set tangent space for this vertex
            # in that case pick a space
            bin_norm[i] = mathutils.vecCrossProduct(xvec, norm)
            try:
                bin_norm[i] = mathutils.vecNormalized(bin_norm[i])
            except ZeroDivisionError:
                bin_norm[i] = mathutils.vecCrossProduct(yvec, norm)
                bin_norm[i] = mathutils.vecNormalized(bin_norm[i])
            tan_norm[i] = mathutils.vecCrossProduct(norm, bin_norm[i])

    # return result
    if orientation:
        return tan_norm, bin_norm, orientations
    else:
        return tan_norm, bin_norm

if __name__ == "__main__":
    import doctest
    doctest.testmod()
