"""The Island module."""

import math
import mathutils

import networkx

from . import geometry, global_def, utils


class Island:
    """Create Island from a set() of faces.

    :param island: a set() of face indexes.
    :type island: set().
    """

    def __init__(self, island):
        self.faceList = island

    def __iter__(self):
        """Iterate throught all face faces forming the island."""
        for i in self.faceList:
            yield i

    def __len__(self):
        """Return the number of faces of this island."""
        return len(self.faceList)

    def __str__(self):
        return str(self.faceList)

    def __repr__(self):
        return repr(self.faceList)

    def __eq__(self, other):
        """Compare two island."""
        return self.faceList == other

# properties
    def BBox(self):
        """Return the bounding box of the island.

        :return: a Rectangle rappresenting the bounding box of the island.
        :rtype: :class:`.Rectangle`
        """
        minX = minY = 1000
        maxX = maxY = -1000
        for face_id in self.faceList:
            face = global_def.bm.faces[face_id]
            for loop in face.loops:
                u, v = loop[global_def.uvlayer].uv
                minX = min(u, minX)
                minY = min(v, minY)
                maxX = max(u, maxX)
                maxY = max(v, maxY)

        return geometry.Rectangle(mathutils.Vector((minX, minY)),
                                  mathutils.Vector((maxX, maxY)))

    def angle(self):
        """Return the island angle.

        :return: the angle of the island in radians.
        :rtype: float
        """
        uvList = []
        for face_id in self.faceList:
            face = global_def.bm.faces[face_id]
            for loop in face.loops:
                uv = loop[global_def.bm.loops.layers.uv.active].uv
                uvList.append(uv)

        angle = mathutils.geometry.box_fit_2d(uvList)
        return angle

    def size(self):
        """Return the island size.

        :return: the size of the island(bounding box).
        :rtype: :class:`.Size`
        """
        bbox = self.BBox()
        sizeX = bbox.right() - bbox.left()
        sizeY = bbox.bottom() - bbox.top()

        return geometry.Size(sizeX, sizeY)

# Transformation
    def move(self, vector):
        """Move the island by vector.

        Move the island by 'vector', by adding 'vector' to the curretnt uv
        coords.

        :param vector: the vector to add.
        :rtype: :class:`mathutils.Vector`
        """
        for face_id in self.faceList:
            face = global_def.bm.faces[face_id]
            for loop in face.loops:
                loop[global_def.bm.loops.layers.uv.active].uv += vector

    def rotate(self, angle):
        """Rotate the island on it's center by 'angle(radians)'.

        :param angle: the angle(radians) of rotation.
        :rtype: float
        """
        center = self.BBox().center()

        for face_id in self.faceList:
            face = global_def.bm.faces[face_id]
            for loop in face.loops:
                uv_act = global_def.bm.loops.layers.uv.active
                x, y = loop[uv_act].uv
                xt = x - center.x
                yt = y - center.y
                xr = (xt * math.cos(angle)) - (yt * math.sin(angle))
                yr = (xt * math.sin(angle)) + (yt * math.cos(angle))
                # loop[global_def.bm.loops.layers.uv.active].uv = trans
                loop[global_def.bm.loops.layers.uv.active].uv.x = xr + center.x
                loop[global_def.bm.loops.layers.uv.active].uv.y = yr + center.y

    def scale(self, scaleX, scaleY):
        """Scale the island by 'scaleX, scaleY'.

        :param scaleX: x scale factor.
        :type scaleX: float
        :param scaleY: y scale factor
        :type scaleY: float
        """
        center = self.BBox().center()
        for face_id in self.faceList:
            face = global_def.bm.faces[face_id]
            for loop in face.loops:
                x = loop[global_def.bm.loops.layers.uv.active].uv.x
                y = loop[global_def.bm.loops.layers.uv.active].uv.y
                xt = x - center.x
                yt = y - center.y
                xs = xt * scaleX
                ys = yt * scaleY
                loop[global_def.bm.loops.layers.uv.active].uv.x = xs + center.x
                loop[global_def.bm.loops.layers.uv.active].uv.y = ys + center.y

    # FIXME: in some case doesn't work as expected...
    def snapToUnselected(self, targetIslands, threshold):
        """Snap this island to 'targetIsland'.

        Use threshold to adjust vertex macthing. targetIsland is the island to
        use to search for nearest vertex.

        :param targetIsland: the target island for snapping
        :type targetIsland: :class:`.Island`
        :param threshold: distance from one vert to the others
        :type threshold: float
        """
        bestMatcherList = []
        # targetIslands.remove(self)
        activeUvLayer = global_def.bm.loops.layers.uv.active

        for face_id in self.faceList:
            face = global_def.bm.faces[face_id]

            for loop in face.loops:
                selectedUVvert = loop[activeUvLayer]
                uvList = []

                for targetIsland in targetIslands:
                    for targetFace_id in targetIsland:
                        targetFace = global_def.bm.faces[targetFace_id]
                        for targetLoop in targetFace.loops:
                            # take the a reference vert
                            targetUvVert = targetLoop[activeUvLayer].uv
                            # get a selected vert and calc it's distance from
                            # the ref
                            # add it to uvList
                            dist = round(
                                utils.vectorDistance(selectedUVvert.uv,
                                                     targetUvVert), 10)
                            uvList.append((dist, targetLoop[activeUvLayer]))

                # for every vert in uvList take the ones with the shortest
                # distnace from ref
                minDist = uvList[0][0]
                bestMatcher = 0

                # 1st pass get lower dist
                for bestDist in uvList:
                    if bestDist[0] <= minDist:
                        minDist = bestDist[0]

                # 2nd pass get the only ones with a match
                for bestVert in uvList:
                    if bestVert[0] <= minDist:
                        bestMatcherList.append((bestVert[0], selectedUVvert,
                                                bestVert[1]))

        for bestMatcher in bestMatcherList:
            if bestMatcher[0] <= threshold:
                bestMatcher[1].uv = bestMatcher[2].uv

    def isIsomorphic(self, other):
        """Test for isomorphism.

        Return a verterx mapping between two island if they are isomorphic
        or 'None' if there is no isomorphism.
        The returned mapped vertex index, correspond to the mesh vertex index
        and not the uv one.

        :param other: the other island
        :type other: :class:`.Island`
        :return: mapping between vertex or None
        :rtype: dict, None
        """
        def graphFromIsland(island):

            edgeVertex = set()
            for face_id in island:
                face = global_def.bm.faces[face_id]
                for edges in face.edges:
                    edgeVert = (edges.verts[0].index, edges.verts[1].index)
                    edgeVertex.add(tuple(sorted(edgeVert,
                                                key=lambda data: data)))

            graph = networkx.Graph(tuple(edgeVertex))

            return graph

        selfGraph = graphFromIsland(self)
        otheGraph = graphFromIsland(other)

        iso = networkx.isomorphism
        graphMatcher = iso.GraphMatcher(selfGraph, otheGraph)

        if graphMatcher.is_isomorphic():
            return graphMatcher.mapping
        else:
            None
