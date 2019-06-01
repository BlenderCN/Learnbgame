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
import mathutils

from bpy.props import BoolProperty

from . import make_islands
from . import templates
from . import utils
from . import operator_manager

############################
# DISTRIBUTION
############################


class DistributeLEdgesH(templates.UvOperatorTemplate):
    """Distribute left edges equidistantly horizontally."""

    bl_idname = "uv.distribute_ledges_horizontally"
    bl_label = "Distribute Left Edges Horizontally"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        makeIslands = make_islands.MakeIslands()
        selectedIslands = makeIslands.selectedIslands()

        if len(selectedIslands) < 3:
            return {'CANCELLED'}

        selectedIslands.sort(key=lambda island: island.BBox().center().x)

        uvFirstX = selectedIslands[0].BBox().left()
        uvLastX = selectedIslands[-1].BBox().left()

        distX = uvLastX - uvFirstX

        deltaDist = distX / (len(selectedIslands) - 1)

        selectedIslands.pop(0)
        selectedIslands.pop(-1)

        pos = uvFirstX + deltaDist

        for island in selectedIslands:
            vec = mathutils.Vector((pos - island.BBox().left(), 0.0))
            pos += deltaDist
            island.move(vec)

        utils.update()
        return {"FINISHED"}


class DistributeCentersH(templates.UvOperatorTemplate):
    """Distribute centers equidistantly horizontally."""

    bl_idname = "uv.distribute_center_horizontally"
    bl_label = "Distribute Centers Horizontally"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        makeIslands = make_islands.MakeIslands()
        selectedIslands = makeIslands.selectedIslands()

        if len(selectedIslands) < 3:
            return {'CANCELLED'}

        selectedIslands.sort(key=lambda island: island.BBox().center().x)

        uvFirstX = selectedIslands[0].BBox().center().x
        uvLastX = selectedIslands[-1].BBox().center().x

        distX = uvLastX - uvFirstX

        deltaDist = distX / (len(selectedIslands) - 1)

        selectedIslands.pop(0)
        selectedIslands.pop(-1)

        pos = uvFirstX + deltaDist

        for island in selectedIslands:
            vec = mathutils.Vector((pos - island.BBox().center().x, 0.0))
            pos += deltaDist
            island.move(vec)

        utils.update()
        return {"FINISHED"}


class DistributeREdgesH(templates.UvOperatorTemplate):
    """Distribute right edges equidistantly horizontally."""

    bl_idname = "uv.distribute_redges_horizontally"
    bl_label = "Distribute Right Edges Horizontally"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        makeIslands = make_islands.MakeIslands()
        selectedIslands = makeIslands.selectedIslands()

        if len(selectedIslands) < 3:
            return {'CANCELLED'}

        selectedIslands.sort(key=lambda island: island.BBox().center().x)

        uvFirstX = selectedIslands[0].BBox().right()
        uvLastX = selectedIslands[-1].BBox().right()

        distX = uvLastX - uvFirstX

        deltaDist = distX / (len(selectedIslands) - 1)

        selectedIslands.pop(0)
        selectedIslands.pop(-1)

        pos = uvFirstX + deltaDist

        for island in selectedIslands:
            vec = mathutils.Vector((pos - island.BBox().right(), 0.0))
            pos += deltaDist
            island.move(vec)
        utils.update()
        return {"FINISHED"}


class DistributeTEdgesV(templates.UvOperatorTemplate):
    """Distribute top edges equidistantly vertically."""

    bl_idname = "uv.distribute_tedges_vertically"
    bl_label = "Distribute Top Edges Vertically"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        makeIslands = make_islands.MakeIslands()
        selectedIslands = makeIslands.selectedIslands()

        if len(selectedIslands) < 3:
            return {'CANCELLED'}

        selectedIslands.sort(key=lambda island: island.BBox().center().y)

        uvFirstX = selectedIslands[0].BBox().top()
        uvLastX = selectedIslands[-1].BBox().top()

        distX = uvLastX - uvFirstX

        deltaDist = distX / (len(selectedIslands) - 1)

        selectedIslands.pop(0)
        selectedIslands.pop(-1)

        pos = uvFirstX + deltaDist

        for island in selectedIslands:
            vec = mathutils.Vector((0.0, pos - island.BBox().top()))
            pos += deltaDist
            island.move(vec)
        utils.update()
        return {"FINISHED"}


class DistributeCentersV(templates.UvOperatorTemplate):
    """Distribute centers equidistantly vertically."""

    bl_idname = "uv.distribute_center_vertically"
    bl_label = "Distribute Centers Vertically"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        makeIslands = make_islands.MakeIslands()
        selectedIslands = makeIslands.selectedIslands()

        if len(selectedIslands) < 3:
            return {'CANCELLED'}

        selectedIslands.sort(key=lambda island: island.BBox().center().y)

        uvFirst = selectedIslands[0].BBox().center().y
        uvLast = selectedIslands[-1].BBox().center().y

        dist = uvLast - uvFirst

        deltaDist = dist / (len(selectedIslands) - 1)

        selectedIslands.pop(0)
        selectedIslands.pop(-1)

        pos = uvFirst + deltaDist

        for island in selectedIslands:
            vec = mathutils.Vector((0.0, pos - island.BBox().center().y))
            pos += deltaDist
            island.move(vec)
        utils.update()
        return {"FINISHED"}


class DistributeBEdgesV(templates.UvOperatorTemplate):
    """Distribute bottom edges equidistantly vertically."""

    bl_idname = "uv.distribute_bedges_vertically"
    bl_label = "Distribute Bottom Edges Vertically"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        makeIslands = make_islands.MakeIslands()
        selectedIslands = makeIslands.selectedIslands()

        if len(selectedIslands) < 3:
            return {'CANCELLED'}

        selectedIslands.sort(key=lambda island: island.BBox().center().y)

        uvFirst = selectedIslands[0].BBox().bottom()
        uvLast = selectedIslands[-1].BBox().bottom()

        dist = uvLast - uvFirst

        deltaDist = dist / (len(selectedIslands) - 1)

        selectedIslands.pop(0)
        selectedIslands.pop(-1)

        pos = uvFirst + deltaDist

        for island in selectedIslands:
            vec = mathutils.Vector((0.0, pos - island.BBox().bottom()))
            pos += deltaDist
            island.move(vec)
        utils.update()
        return {"FINISHED"}

# TODO:
# class RemoveOverlaps(templates.UvOperatorTemplate):

#     """Remove overlaps on islands"""
#     bl_idname = "uv.remove_overlaps"
#     bl_label = "Remove Overlaps"
#     bl_options = {'REGISTER', 'UNDO'}

#     def execute(self, context):
#         makeIslands = make_islands.MakeIslands()
#         islands = makeIslands.getIslands()

#         islandEdges = []
#         uvData = []
#         for island in islands:
#             edges = []

#             for face_id in island:
#                 face = bm.faces[face_id]

#                 for loop in face.loops:
#                     edgeVert1 = loop.edge.verts[0].index
#                     edgeVert2 = loop.edge.verts[1].index
#                     edges.append((edgeVert1, edgeVert2))
#                     uv = loop[bm.loops.layers.uv.active].uv
#                     vertIndex = loop.vert.index
#                     uvData.append((vertIndex, uv))
#             islandEdges.append(edges)
#         return {"FINISHED"}


class EqualizeHGap(templates.UvOperatorTemplate):
    """Equalize horizontal gap between island."""

    bl_idname = "uv.equalize_horizontal_gap"
    bl_label = "Equalize Horizontal Gap"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        makeIslands = make_islands.MakeIslands()
        selectedIslands = makeIslands.selectedIslands()

        if len(selectedIslands) < 3:
            return {'CANCELLED'}

        selectedIslands.sort(key=lambda island: island.BBox().center().x)

        averageDist = utils.averageIslandDist(selectedIslands)

        for i in range(len(selectedIslands)):
            # break if the last island is the same as the next one
            if selectedIslands.index(selectedIslands[i + 1]) == \
                    selectedIslands.index(selectedIslands[-1]):
                break
            elem1 = selectedIslands[i].BBox().right()
            elem2 = selectedIslands[i + 1].BBox().left()

            dist = elem2 - elem1
            increment = averageDist.x - dist

            vec = mathutils.Vector((increment, 0.0))
            selectedIslands[i + 1].move(vec)
        utils.update()
        return {"FINISHED"}


class EqualizeVGap(templates.UvOperatorTemplate):
    """Equalize vertical gap between island."""

    bl_idname = "uv.equalize_vertical_gap"
    bl_label = "Equalize Vertical Gap"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        makeIslands = make_islands.MakeIslands()
        selectedIslands = makeIslands.selectedIslands()

        if len(selectedIslands) < 3:
            return {'CANCELLED'}

        selectedIslands.sort(key=lambda island: island.BBox().center().y)

        averageDist = utils.averageIslandDist(selectedIslands)

        for i in range(len(selectedIslands)):
            if selectedIslands.index(selectedIslands[i + 1]) ==\
                    selectedIslands.index(selectedIslands[-1]):
                break
            elem1 = selectedIslands[i].BBox().bottom()
            elem2 = selectedIslands[i + 1].BBox().top()

            dist = elem2 - elem1

            increment = averageDist.y - dist

            vec = mathutils.Vector((0.0, increment))
            selectedIslands[i + 1].move(vec)
        utils.update()
        return {"FINISHED"}


class EqualizeScale(templates.UvOperatorTemplate):
    """Equalize the islands scale to the active one."""

    bl_idname = "uv.equalize_scale"
    bl_label = "Equalize Scale"
    bl_options = {'REGISTER', 'UNDO'}

    keepProportions = BoolProperty(
        name="Keep Proportions",
        description="Mantain proportions during scaling",
        default=False)

    useYaxis = BoolProperty(
        name="Use Y axis",
        description="Use y axis as scale reference, default is x",
        default=False)

    def execute(self, context):
        makeIslands = make_islands.MakeIslands()
        selectedIslands = makeIslands.selectedIslands()
        activeIsland = makeIslands.activeIsland()

        if not activeIsland:
            self.report({"ERROR"}, "No active face")
            return {"CANCELLED"}

        activeSize = activeIsland.size()
        selectedIslands.remove(activeIsland)

        for island in selectedIslands:
            size = island.size()
            scaleX = activeSize.width / size.width
            scaleY = activeSize.height / size.height

            if self.keepProportions:
                if self.useYaxis:
                    scaleX = scaleY
                else:
                    scaleY = scaleX

            island.scale(scaleX, scaleY)

        utils.update()
        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "keepProportions")
        if self.keepProportions:
            layout.prop(self, "useYaxis")


#################################
# REGISTRATION
#################################
_om = operator_manager.om
_om.addOperator(DistributeBEdgesV)
_om.addOperator(DistributeCentersH)
_om.addOperator(DistributeCentersV)
_om.addOperator(DistributeLEdgesH)
_om.addOperator(DistributeREdgesH)
_om.addOperator(DistributeTEdgesV)

_om.addOperator(EqualizeHGap)
_om.addOperator(EqualizeVGap)
_om.addOperator(EqualizeScale)
