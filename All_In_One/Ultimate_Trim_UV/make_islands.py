# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; version 2
#  of the License.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

from collections import defaultdict

# from global_def import *
from . import global_def, island, utils


class MakeIslands:
    """Create and get Island.

    Scan the current edit mesh for uv islands.
    """

    def __init__(self):
        """Scan the uv data and create the islands."""
        utils.InitBMesh()
        self.__islands = []
        self.__bm = global_def.bm
        self.__uvlayer = global_def.uvlayer

        self.__selectedIslands = set()
        self.__hiddenFaces = set()

        face_to_verts = defaultdict(set)
        vert_to_faces = defaultdict(set)

        for face in self.__bm.faces:
            for loop in face.loops:
                vertID = loop[self.__uvlayer].uv.to_tuple(5), loop.vert.index
                face_to_verts[face.index].add(vertID)
                vert_to_faces[vertID].add(face.index)

                if face.select:
                    if loop[self.__uvlayer].select:
                        self.__selectedIslands.add(face.index)
                else:
                    self.__hiddenFaces.add(face.index)

        faces_left = set(face_to_verts.keys())

        while len(faces_left) > 0:
            face_id = list(faces_left)[0]
            current_island = set()

            face_to_visit = [face_id]
            faces_left.remove(face_id)

            # BDF search of face
            while len(face_to_visit) > 0:
                current_island.add(face_id)
                cur_face = face_to_visit.pop(0)
                # and add all faces that share uvs with this face
                verts = face_to_verts[cur_face]
                # search for connected faces: faces that have same vertex index
                # and same uv
                for vert in verts:
                    connected_faces = vert_to_faces[vert]
                    for face in connected_faces:
                        current_island.add(face)
                        if face in faces_left:
                            face_to_visit.append(face)
                            faces_left.remove(face)
            # finally add the discovered island to the list of islands
            self.__islands.append(island.Island(current_island))

    def getIslands(self):
        """Return all the uv islands found.

        :rtype: :class:`.Island`
        """
        return self.__islands

    def activeIsland(self):
        """Return the active island(the island containing the active face).

        :rtype: :class:`.Island`
        """
        for _island in self.__islands:
            try:
                if self.__bm.faces.active.index in _island:
                    return island.Island(_island)
            except:
                return None

    def selectedIslands(self):
        """Return a list of selected islands.

        :rtype: :class:`.Island`
        """
        selectedIslands = []
        for _island in self.__islands:
            if not self.__selectedIslands.isdisjoint(_island):
                selectedIslands.append(island.Island(_island))
        return selectedIslands

    def hiddenIslands(self):
        """Return a list of hidden islands.

        :rtype: :class:`.Island`
        """
        _hiddenIslands = []
        for _island in self.__islands:
            if not self.__hiddenFaces.isdisjoint(_island):
                _hiddenIslands.append(island.Island(_island))
        return _hiddenIslands
