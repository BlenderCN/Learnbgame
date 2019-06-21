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
"""
PackIslands Module(attention still wp).

contain the operator used by blender to perform Island Packing
"""

from collections import defaultdict

import bpy.ops
from bpy.props import FloatProperty, BoolProperty, IntProperty
import mathutils

from . import make_islands, templates, utils, operator_manager, global_def


class _Rect:
    """Class rappresenting a rectangle."""

    def __init__(self, x, y, width, height):
        """Initialize the class with origin(x, y), width and height."""
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def __repr__(self):
        """String representation of Rect."""
        return "Rect: x: {0}, y: {1}, width: {2}, height: {3}"\
            .format(self.x, self.y, self.width, self.height)

    def fit(self, other):
        """Test if other can be contained."""
        if other.width <= self.width and other.height <= self.height:
            return True
        else:
            return False


class _Node:
    def __init__(self, rect):
        self.used = False
        self.left = None
        self.right = None
        self.rect = rect

    def __repr__(self):
        return "Node {0}: \n\tUsed: {1}, rect: {2}"\
            .format(hex(id(self)), self.used, self.rect)


class _BinTree:
    def __init__(self, rect):
        self._root = _Node(rect)

    def insert(self, rect):
        width = rect.width
        height = rect.height

        node = self.__findNode(self._root, width, height)

        if node:
            node = self.__splitNode(node, width, height)
            return node
        else:
            return self.__growNode(width, height)

    def __findNode(self, node, width, height):
        if node.used:
                return self.__findNode(node.left, width, height) or \
                    self.__findNode(node.right, width, height)

        elif round(width, 5) <= round(node.rect.width, 5) and \
             round(height, 5) <= round(node.rect.height, 5):
            return node
        else:
            return None

    def __splitNode(self, node, width, height):
        node.used = True

        lRect = _Rect(node.rect.x, node.rect.y + height,
                      width, node.rect.height - height)
        print("Left: ", lRect)
        node.left = _Node(lRect)

        rRect = _Rect(node.rect.x + width, node.rect.y,
                      node.rect.width - width, node.rect.height)
        print("Right: ", rRect)
        node.right = _Node(rRect)

        return node

    def __growNode(self, width, height):
        canGrowLeft = (width <= self._root.rect.width)
        canGrowRight = (width <= self._root.rect.height)

        shouldGrowRight = canGrowRight and \
            (self._root.rect.height >= (self._root.rect.width + width))
        shouldGrowLeft = canGrowLeft and \
            (self._root.rect.width >= (self._root.rect.height + height))

        if shouldGrowRight:
            return self.__growRight(width, height)
        elif shouldGrowLeft:
            return self.__growLeft(width, height)
        elif canGrowRight:
            return self.__growRight(width, height)
        elif canGrowLeft:
            return self.__growLeft(width, height)
        else:
            return None

    def __growRight(self, width, height):
        print("growing right")
        self._root.used = True
        self._root.rect.width += width
        # self._root.left = self._root
        self._root.right = _Node(_Rect(self._root.rect.width - width, 0,
                                       width, self._root.rect.height))

        node = self.__findNode(self._root, width, height)
        if node:
            return self.__splitNode(node, width, height)
        else:
            return None

    def __growLeft(self, width, height):
        print("growing Left")
        self._root.used = True
        self._root.rect.height += height
        # self._root.right = None
        self._root.left = _Node(_Rect(0, self._root.rect.height - height,
                                      self._root.rect.width, height))

        node = self.__findNode(self._root, width, height)
        if node:
            return self.__splitNode(node, width, height)
        else:
            return None


class PackIslands_not_working(templates.UvOperatorTemplate):
    """Pack UV Islands in the uv space."""

    bl_idname = "uv.pack_pile_islands"
    bl_label = "Pack Pile Islands"
    bl_options = {'REGISTER', 'UNDO'}

    selectedOnly = BoolProperty(
        name="Selection Only",
        description="Pack only selected islands",
        default=False
    )

    islandMargin = FloatProperty(
        name="Margin",
        description="Margin between islands",
        default=0,
        min=0,
        max=1,
        soft_min=0,
        soft_max=1,
        step=1,
        precision=4)

    pile = BoolProperty(
        name="Pile",
        description="Pile similar island to save uv space",
        default=False
    )

    numOfPiles = IntProperty(
        name="Number of piles",
        description="number of piles to create",
        default=1,
        min=1,
        max=2**31-1,
        soft_min=1,
        soft_max=10,
        step=1
    )

    def execute(self, context):
        """Execute the script."""
        def getMax(island):
            bbox = island.BBox()
            width = bbox.right() - bbox.left()
            height = bbox.top() - bbox.bottom()
            val = max(width, height)
            return val

        makeIslands = make_islands.MakeIslands()
        islands = makeIslands.getIslands()
        selectedIslands = makeIslands.selectedIslands()
        activeIsland = makeIslands.activeIsland()
        hiddenIslands = makeIslands.hiddenIslands()

        # choose which island should be used
        usableIslands = islands
        if self.selectedOnly:
            usableIslands = selectedIslands
        # sort island with maxside:
        usableIslands.sort(key=lambda island: getMax(island), reverse=True)

        # bin pack the island
        islandBBox = usableIslands[0].BBox()
        width = islandBBox.right() - islandBBox.left()
        height = islandBBox.top() - islandBBox.bottom()
        rect = _Rect(0, 0, width, height)
        btree = _BinTree(rect)

        for island in usableIslands:
            islandBBox = island.BBox()
            width = islandBBox.right() - islandBBox.left()
            height = islandBBox.top() - islandBBox.bottom()
            rect = _Rect(0, 0, width, height)
            node = btree.insert(rect)
            if node:
                vector = mathutils.Vector((node.rect.x, node.rect.y)) - island.BBox().bottomLeft()
                island.move(vector)

        # scale the islands to fit uv space
        # get the whole BBox:
        bbox = utils.GBBox(usableIslands)
        width = bbox.right() - bbox.left()
        height = bbox.top() - bbox.bottom()
        scale = 1 / max(width, height)

        for island in usableIslands:
            for face_id in island:
                    face = global_def.bm.faces[face_id]
                    for loop in face.loops:
                        x = loop[global_def.bm.loops.layers.uv.active].uv.x
                        y = loop[global_def.bm.loops.layers.uv.active].uv.y
                        loop[global_def.bm.loops.layers.uv.active].uv.x = x * scale
                        loop[global_def.bm.loops.layers.uv.active].uv.y = y * scale
        utils.update()
        return{'FINISHED'}

    def draw(self, context):
        """Draw the operator props."""
        layout = self.layout
        layout.prop(self, "selectedOnly")
        layout.prop(self, "islandMargin")
        layout.prop(self, "pile")
        if self.pile:
            layout.prop(self, "numOfPiles")


class PackIslands(templates.UvOperatorTemplate):
    """Pack UV Islands in the uv space."""

    bl_idname = "uv.pack_pile_islands"
    bl_label = "Pack Pile Islands"
    bl_options = {'REGISTER', 'UNDO'}

    selectedOnly = BoolProperty(
        name="Selection Only",
        description="Pack only selected islands",
        default=False
    )

    rotate = BoolProperty(
        name="Rotate",
        description="Rotate island",
        default=False
    )

    islandMargin = FloatProperty(
        name="Margin",
        description="Margin between islands",
        default=0,
        min=0,
        max=1,
        soft_min=0,
        soft_max=1,
        step=1,
        precision=4)

    pile = BoolProperty(
        name="Pile",
        description="Pile similar island to save uv space",
        default=False
    )

    numOfPiles = IntProperty(
        name="Number of piles",
        description="Number of piles to create for each similar islands",
        default=1,
        min=1,
        max=2**31-1,
        soft_min=1,
        soft_max=10,
        step=1
    )

    def execute(self, context):
        """Execute the script."""
        def getMax(island):
            bbox = island.BBox()
            width = bbox.right() - bbox.left()
            height = bbox.top() - bbox.bottom()
            val = max(width, height)
            return val

        def makePiles(self, data):
            newDict = defaultdict(list)
            for islandIndex in data:
                mList = data[islandIndex].copy()
                mList.insert(0, islandIndex)
                numOfIsoIsland = len(mList)
                chunk = numOfIsoIsland // self.numOfPiles
                remainder = numOfIsoIsland % self.numOfPiles
                pad = 0
                for i in range(0, numOfIsoIsland):
                    bit = 0
                    if remainder:
                        bit = 1
                    for j in range(1, chunk + bit):
                        if len(mList) > pad + j:
                            newDict[mList[pad]].append(mList[pad+j])
                    pad += chunk+bit
                    if remainder:
                        remainder -= 1
            return newDict

        makeIslands = make_islands.MakeIslands()
        islands = makeIslands.getIslands()
        selectedIslands = makeIslands.selectedIslands()
        activeIsland = makeIslands.activeIsland()
        hiddenIslands = makeIslands.hiddenIslands()

        # search for isomorphic island
        isoIslandVisited = []
        isoIsland = defaultdict(list)
        if self.pile:
            for island in selectedIslands:
                for other in selectedIslands:
                    if island in isoIslandVisited or island == other:
                        continue
                    isoVerts = island.isIsomorphic(other)
                    if isoVerts:
                        isoIsland[selectedIslands.index(island)].append(selectedIslands.index(other))
                        isoIslandVisited.append(other)

            isoIsland = makePiles(self, isoIsland)
            # remove isomorphic island from selection
            for island in isoIsland.values():
                for other in island:
                    for face_id in selectedIslands[other]:
                        face = global_def.bm.faces[face_id]
                        face.select = False

            print(isoIsland)
        utils.update()
        bpy.ops.uv.pack_islands(rotate=self.rotate, margin=self.islandMargin)

        if self.pile and len(islands) != 0:
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

            for islandIndex in isoIsland:
                for isoIndex in isoIsland[islandIndex]:
                    islandVerts = perIslandVerts[islandIndex]
                    isoVerts = perIslandVerts[isoIndex]
                    vertmap = selectedIslands[islandIndex].isIsomorphic(selectedIslands[isoIndex])
                    for v in islandVerts:
                        mappedVert = vertmap[v]
                        for uv_loop in uv_to_vert[v]:
                            for iso_uv_loop in uv_to_vert[mappedVert]:
                                iso_uv_loop.uv = uv_loop.uv

            # reselct faces
            for island in isoIsland.values():
                for other in island:
                    for face_id in selectedIslands[other]:
                        face = global_def.bm.faces[face_id]
                        face.select = True
        utils.update()
        return{'FINISHED'}

    def draw(self, context):
        """Draw the operator props."""
        layout = self.layout
        layout.prop(self, "selectedOnly")
        layout.prop(self, "rotate")
        layout.prop(self, "islandMargin")
        layout.prop(self, "pile")
        if self.pile:
            layout.prop(self, "numOfPiles")


#################################
# REGISTRATION
#################################
_om = operator_manager.om
_om.addOperator(PackIslands)
