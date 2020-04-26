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

import operator

from collections import defaultdict

from . import global_def, make_islands, templates, utils, operator_manager

import networkx


class Match_Islands(templates.UvOperatorTemplate):
    """Match UV Island by moving their vertex."""

    bl_idname = "uv.match_islands"
    bl_label = "Match Islands"
    bl_options = {'REGISTER', 'UNDO'}

    def graphFromIsland(self, island):
        """Return a networkx graph rappresenting the island."""
        # vertexList = set()
        # print("out: ", island)

        # for face_id in island:
        #     face = global_def.bm.faces[face_id]
        #     for vert in face.verts:
        #         vertexList.add(vert)

        # vertexList = sorted(vertexList, key=lambda data: data.index)
        # numOfVertex = len(vertexList)

        edgeVertex = set()
        for face_id in island:
            face = global_def.bm.faces[face_id]
            for edges in face.edges:
                edgeVert = (edges.verts[0].index, edges.verts[1].index)
                edgeVertex.add(tuple(sorted(edgeVert, key=lambda data: data)))

        g = networkx.Graph(tuple(edgeVertex))

        return g

    def execute(self, context):

        makeIslands = make_islands.MakeIslands()
        selectedIslands = makeIslands.selectedIslands()
        activeIsland = makeIslands.activeIsland()

        if not activeIsland:
            self.report({"ERROR"}, "No active face")
            return {"CANCELLED"}

        if len(selectedIslands) > 1:
            if(operator.contains(selectedIslands, activeIsland)):
                selectedIslands.remove(activeIsland)

        activeIslandVert = set()
        for face_id in activeIsland:
            face = global_def.bm.faces[face_id]
            for vert in face.verts:
                activeIslandVert.add(vert.index)

        # numOfVertex = len(activeIslandVert)

        # map each uv vert to corresponding vert for selectedIslands
        uv_to_vert = dict((i, list()) for i in range(len(global_def.bm.verts)))
        perIslandVerts = dict((i, set()) for i in range(len(selectedIslands)))
        # activeIslandUVData = dict((i, list()) for i in range(numOfVertex))
        for island in selectedIslands:
            for face_id in island:
                face = global_def.bm.faces[face_id]
                for loop in face.loops:
                    index = loop.vert.index
                    uv_to_vert[index].append(loop[global_def.uvlayer])
                    perIslandVerts[selectedIslands.index(island)].add(index)

        activeIslandUVData = defaultdict(list)
        for face_id in activeIsland:
            face = global_def.bm.faces[face_id]
            for loop in face.loops:
                index = loop.vert.index
                activeIslandUVData[index].append(loop[global_def.uvlayer])

        # build a edge list
        # activeIslandGraph = self.graphFromIsland(activeIsland)
        # selectedIslandsGraph = []

        # for island in selectedIslands:
        #     graph = self.graphFromIsland(island)
        #     selectedIslandsGraph.append(graph)

        # now test for isomorphism aginst activeIsland:
        # for islandGraph in selectedIslandsGraph:
        #     iso = networkx.isomorphism
        #     graphMatcher = iso.GraphMatcher(islandGraph, activeIslandGraph)
        #     if graphMatcher.is_isomorphic():
        #         vertexMapping = graphMatcher.mapping
        for island in selectedIslands:
            vertexMapping = island.isIsomorphic(activeIsland)
            if vertexMapping:
                islandIndex = selectedIslands.index(island)
                for vertIndex in perIslandVerts[islandIndex]:
                    mappedVert = vertexMapping[vertIndex]
                    for uv_loop in uv_to_vert[vertIndex]:
                        for active_uv_loop in activeIslandUVData[mappedVert]:
                            uv_loop.uv = active_uv_loop.uv

        utils.update()
        return{'FINISHED'}


#################################
# REGISTRATION
#################################
_om = operator_manager.om
_om.addOperator(Match_Islands)
