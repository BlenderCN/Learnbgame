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

from . import make_islands, templates, utils, operator_manager


#####################
# ALIGN
#####################

class AlignSXMargin(templates.UvOperatorTemplate):
    """Align left margin."""

    bl_idname = "uv.align_left_margin"
    bl_label = "Align left margin"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        makeIslands = make_islands.MakeIslands()
        selectedIslands = makeIslands.selectedIslands()

        targetElement = None

        if context.scene.relativeItems == 'UV_SPACE':
            targetElement = 0.0
        elif context.scene.relativeItems == 'ACTIVE':
            activeIsland = makeIslands.activeIsland()
            if activeIsland:
                targetElement = activeIsland.BBox().left()
            else:
                self.report({"ERROR"}, "No active face")
                return {"CANCELLED"}
        elif context.scene.relativeItems == 'CURSOR':
            targetElement = context.space_data.cursor_location.x

        if context.scene.selectionAsGroup:
            groupBox = utils.GBBox(selectedIslands)
            if context.scene.relativeItems == 'ACTIVE':
                selectedIslands.remove(makeIslands.activeIsland())
            for island in selectedIslands:
                vector = mathutils.Vector(
                    (targetElement - groupBox.left(), 0.0))
                island.move(vector)

        else:
            for island in selectedIslands:
                vector = mathutils.Vector(
                    (targetElement - island.BBox().left(), 0.0))
                island.move(vector)

        utils.update()
        return {'FINISHED'}


class AlignRxMargin(templates.UvOperatorTemplate):
    """Align right margin."""

    bl_idname = "uv.align_right_margin"
    bl_label = "Align right margin"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        makeIslands = make_islands.MakeIslands()
        selectedIslands = makeIslands.selectedIslands()

        targetElement = None

        if context.scene.relativeItems == 'UV_SPACE':
            targetElement = 1.0
        elif context.scene.relativeItems == 'ACTIVE':
            activeIsland = makeIslands.activeIsland()
            if activeIsland:
                targetElement = activeIsland.BBox().right()
            else:
                self.report({"ERROR"}, "No active face")
                return {"CANCELLED"}
        elif context.scene.relativeItems == 'CURSOR':
            targetElement = context.space_data.cursor_location.x

        if context.scene.selectionAsGroup:
            groupBox = utils.GBBox(selectedIslands)
            if context.scene.relativeItems == 'ACTIVE':
                selectedIslands.remove(makeIslands.activeIsland())
            for island in selectedIslands:
                vector = mathutils.Vector(
                    (targetElement - groupBox.right(), 0.0))
                island.move(vector)

        else:
            for island in selectedIslands:
                vector = mathutils.Vector(
                    (targetElement - island.BBox().right(), 0.0))
                island.move(vector)

        utils.update()
        return {'FINISHED'}


##################################################
class AlignTopMargin(templates.UvOperatorTemplate):
    """Align top margin."""

    bl_idname = "uv.align_top_margin"
    bl_label = "Align top margin"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        makeIslands = make_islands.MakeIslands()
        selectedIslands = makeIslands.selectedIslands()

        targetElement = None

        if context.scene.relativeItems == 'UV_SPACE':
            targetElement = 1.0
        elif context.scene.relativeItems == 'ACTIVE':
            activeIsland = makeIslands.activeIsland()
            if activeIsland:
                targetElement = activeIsland.BBox().top()
            else:
                self.report({"ERROR"}, "No active face")
                return {"CANCELLED"}
        elif context.scene.relativeItems == 'CURSOR':
            targetElement = context.space_data.cursor_location.y

        if context.scene.selectionAsGroup:
            groupBox = utils.GBBox(selectedIslands)
            if context.scene.relativeItems == 'ACTIVE':
                selectedIslands.remove(makeIslands.activeIsland())
            for island in selectedIslands:
                vector = mathutils.Vector(
                    (0.0, targetElement - groupBox.top()))
                island.move(vector)

        else:
            for island in selectedIslands:
                vector = mathutils.Vector(
                    (0.0, targetElement - island.BBox().top()))
                island.move(vector)

        utils.update()
        return {'FINISHED'}


class AlignLowMargin(templates.UvOperatorTemplate):
    """Align low margin."""

    bl_idname = "uv.align_low_margin"
    bl_label = "Align low margin"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        makeIslands = make_islands.MakeIslands()
        selectedIslands = makeIslands.selectedIslands()

        targetElement = None

        if context.scene.relativeItems == 'UV_SPACE':
            targetElement = 0.0
        elif context.scene.relativeItems == 'ACTIVE':
            activeIsland = makeIslands.activeIsland()
            if activeIsland:
                targetElement = activeIsland.BBox().bottom()
            else:
                self.report({"ERROR"}, "No active face")
                return {"CANCELLED"}
        elif context.scene.relativeItems == 'CURSOR':
            targetElement = context.space_data.cursor_location.y

        if context.scene.selectionAsGroup:
            groupBox = utils.GBBox(selectedIslands)
            if context.scene.relativeItems == 'ACTIVE':
                selectedIslands.remove(makeIslands.activeIsland())
            for island in selectedIslands:
                vector = mathutils.Vector(
                    (0.0, targetElement - groupBox.bottom))
                island.move(vector)

        else:
            for island in selectedIslands:
                vector = mathutils.Vector(
                    (0.0, targetElement - island.BBox().bottom()))
                island.move(vector)

        utils.update()
        return {'FINISHED'}


class AlignHAxis(templates.UvOperatorTemplate):
    """Align horizontal axis."""

    bl_idname = "uv.align_horizontal_axis"
    bl_label = "Align horizontal axis"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        makeIslands = make_islands.MakeIslands()
        selectedIslands = makeIslands.selectedIslands()

        targetElement = None

        if context.scene.relativeItems == 'UV_SPACE':
            targetElement = 0.5
        elif context.scene.relativeItems == 'ACTIVE':
            activeIsland = makeIslands.activeIsland()
            if activeIsland:
                targetElement = activeIsland.BBox().center().y
            else:
                self.report({"ERROR"}, "No active face")
                return {"CANCELLED"}
        elif context.scene.relativeItems == 'CURSOR':
            targetElement = context.space_data.cursor_location.y

        if context.scene.selectionAsGroup:
            groupBoxCenter = utils.GBBox(selectedIslands).center()
            if context.scene.relativeItems == 'ACTIVE':
                selectedIslands.remove(makeIslands.activeIsland())
            for island in selectedIslands:
                vector = mathutils.Vector(
                    (0.0, targetElement - groupBoxCenter.y))
                island.move(vector)

        else:
            for island in selectedIslands:
                vector = mathutils.Vector(
                    (0.0, targetElement - island.BBox().center().y))
                island.move(vector)

        utils.update()
        return {'FINISHED'}


class AlignVAxis(templates.UvOperatorTemplate):
    """Align vertical axis."""

    bl_idname = "uv.align_vertical_axis"
    bl_label = "Align vertical axis"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        makeIslands = make_islands.MakeIslands()
        selectedIslands = makeIslands.selectedIslands()

        targetElement = None

        if context.scene.relativeItems == 'UV_SPACE':
            targetElement = 0.5
        elif context.scene.relativeItems == 'ACTIVE':
            activeIsland = makeIslands.activeIsland()
            if activeIsland:
                targetElement = activeIsland.BBox().center().x
            else:
                self.report({"ERROR"}, "No active face")
                return {"CANCELLED"}
        elif context.scene.relativeItems == 'CURSOR':
            targetElement = context.space_data.cursor_location.x

        if context.scene.selectionAsGroup:
            groupBoxCenter = utils.GBBox(selectedIslands).center()
            if context.scene.relativeItems == 'ACTIVE':
                selectedIslands.remove(makeIslands.activeIsland())
            for island in selectedIslands:
                vector = mathutils.Vector(
                    (targetElement - groupBoxCenter.x, 0.0))
                island.move(vector)

        else:
            for island in selectedIslands:
                vector = mathutils.Vector(
                    (targetElement - island.BBox().center().x, 0.0))
                island.move(vector)

        utils.update()
        return {'FINISHED'}


#########################################
class AlignRotation(templates.UvOperatorTemplate):
    """Align island rotation."""

    bl_idname = "uv.align_rotation"
    bl_label = "Align island rotation"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        makeIslands = make_islands.MakeIslands()
        selectedIslands = makeIslands.selectedIslands()
        activeIsland = makeIslands.activeIsland()

        if not activeIsland:
            self.report({"ERROR"}, "No active face")
            return {"CANCELLED"}

        activeAngle = activeIsland.angle()

        for island in selectedIslands:
            uvAngle = island.angle()
            deltaAngle = activeAngle - uvAngle
            deltaAngle = round(-deltaAngle, 5)
            island.rotate(deltaAngle)

        utils.update()
        return {'FINISHED'}


#################################
# REGISTRATION
#################################
_om = operator_manager.om
_om.addOperator(AlignHAxis)
_om.addOperator(AlignVAxis)
_om.addOperator(AlignRotation)
_om.addOperator(AlignRxMargin)
_om.addOperator(AlignSXMargin)
_om.addOperator(AlignLowMargin)
_om.addOperator(AlignTopMargin)
