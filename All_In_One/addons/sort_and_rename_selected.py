# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
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

# <pep8-80 compliant>

bl_info = {
    "name": "Sort and Rename selected objects",
    "author": "Agnieszka Pas",
    "version": (1, 0, 0),
    "blender": (2, 78, 0),
    "location": "View3D > Tools Panel > Tools Tab",
    "description": "Sort selected objects by location and rename them",
    'wiki_url': 'https://github.com/agapas/sort-and-rename-selected#readme',
    "warning": "",
    "category": "Learnbgame",
}

# ------- TODO ----------------------
# add functionality for NewNameBases enum:
#   if it's value is not 'none':
#      take base-name from enum otherwise from NewBaseName


import bpy
from bpy.types import Operator, Panel
from bpy.props import StringProperty, BoolProperty, EnumProperty


def sort_by_locX(objects, desc):
    return sorted(objects, key=lambda obj: obj.location.x, reverse=desc)


def sort_by_locY(objects, desc):
    return sorted(objects, key=lambda obj: obj.location.y, reverse=desc)


def sort_by_locZ(objects, desc):
    return sorted(objects, key=lambda obj: obj.location.z, reverse=desc)


def sort_by_location(selected, scene):
    main_desc = scene.PrimaryAxisDesc
    desc = scene.SecondaryAxisDesc
    main_axis = scene.PrimarySortAxis
    axis = scene.SecondarySortAxis

    sorted_objs = []

    if main_axis == 'X':
        sorted_objs = sort_by_locX(selected, main_desc)
    elif main_axis == 'Y':
        sorted_objs = sort_by_locY(selected, main_desc)
    elif main_axis == 'Z':
        sorted_objs = sort_by_locZ(selected, main_desc)

    if axis == 'X':
        return sort_by_locX(sorted_objs, desc)
    elif axis == 'Y':
        return sort_by_locY(sorted_objs, desc)
    elif axis == 'Z':
        return sort_by_locZ(sorted_objs, desc)


def setName(p_objects, p_newName, p_startIn=0, p_numDigits=3, p_numbered=False):
    id = p_startIn
    cont = 1
    numberDigits = p_numDigits
    replacingName = p_newName

    if p_numbered == True:
        replacingName += ".000"

    for obj in p_objects:
        if p_startIn == 0 or p_numbered == False:
            obj.name = replacingName
        else:
            addZero = 0
            for i in range(1,numberDigits):
                mod = int(id / (pow(10,i)))
                if mod == 0:
                    addZero += 1

            newNameId = str(id)
            for i in range(0,addZero):
                newNameId = '0' + newNameId

            oldName = obj.name
            obj.name = ''
            newName = p_newName + '.' + newNameId
            obj.name = newName
            id += 1


class SortAndRenameOperator(Operator):
    bl_idname = "object.sort_rename"
    bl_label = "Sort and Rename"

    selection_list = []

    def execute(self, context):
        scene = context.scene
        newName = scene.NewBaseName
        numbered = scene.WithNumber
        startIn = 1
        numDigits = 3

        self.selection_list = sort_by_location(context.selected_objects, scene)

        if context.scene.WithNumberFrom != '':
            startIn = int(context.scene.WithNumberFrom)
            numDigits = len(context.scene.WithNumberFrom)

        setName(
            self.selection_list,
            newName,
            p_startIn=startIn,
            p_numDigits=numDigits,
            p_numbered=numbered
        )

        return{'FINISHED'}


class SortAndRenamePanel(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_label = "Sort & Rename"
    bl_context = "objectmode"
    bl_category = "Tools"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout

        # ----------- SORTING BY LOCATION ------------------ #
        col = layout.column()
        row = col.row()
        row.label("Sort by Location:")

        box = col.box()
        row = box.row()
        row.alignment = 'LEFT'
        row.label(text='Axis 1:')
        row.alignment = 'RIGHT'
        row.prop(context.scene, "PrimarySortAxis", text="")
        row = box.row()
        row.alignment = 'RIGHT'
        row.prop(context.scene, 'PrimaryAxisDesc')

        box = col.box()
        row = box.row()
        row.alignment = 'LEFT'
        row.label(text='Axis 2:')
        row.alignment = 'RIGHT'
        row.prop(context.scene, "SecondarySortAxis", text="")
        row = box.row()
        row.alignment = 'RIGHT'
        row.prop(context.scene, 'SecondaryAxisDesc')

        # ----------- NEW NAME ------------------ #
        row = col.row()
        row.label("New Name Settings:")
        box = col.box()

        row = box.row()
        row.alignment = 'LEFT'
        row.label(text='Name:')
        row.alignment = 'RIGHT'
        row.prop(context.scene, "NewBaseName", text="")

        row = box.row()
        row.alignment = 'RIGHT'
        row.prop(context.scene, "WithNumber")

        row = box.row()
        row.alignment = 'LEFT'
        row.label(text='from:')
        row.alignment = 'RIGHT'
        row.prop(context.scene, "WithNumberFrom", text="")

        row = col.row()
        row.operator("object.sort_rename", "Sort and Rename")


def register():
    bpy.types.Scene.NewBaseName = bpy.props.StringProperty(
        name="New Name",
        default="",
        description="The new base-name for the selected objects")

    bpy.types.Scene.WithNumberFrom = bpy.props.StringProperty(
        name="from",
        default="001")

    bpy.types.Scene.WithNumber = bpy.props.BoolProperty(
        name="numbered",
        default=True,
        description="Add number at the end of new base-name")

    # bpy.types.Scene.NewNameBases = bpy.props.EnumProperty(
    #     name="New Name Options",
    #     description="Select new name or type your custom name",
    #     items=(
    #         ('none', "None", "Type own custom base-name as the Name"),
    #         ('obj', "Obj", "Set base-name as: Obj"),
    #         ('taperObj', "taperObj", "Set base-name as: taperObj")),
    #     default='none'
    # )

    bpy.types.Scene.PrimarySortAxis = bpy.props.EnumProperty(
        name="Primary Axis",
        description="Select primary axis to sort by",
        items=(
            ('X', "X", "Sort by X location value"),
            ('Y', "Y", "Sort by Y location value"),
            ('Z', "Z", "Sort by Z location value")),
        default='Y'
    )

    bpy.types.Scene.SecondarySortAxis = bpy.props.EnumProperty(
        name="Secondary Axis",
        description="Select secondary axis to sort by",
        items=(
            ('X', "X", "Sort by X location value"),
            ('Y', "Y", "Sort by Y location value"),
            ('Z', "Z", "Sort by Z location value")),
        default='X'
    )

    bpy.types.Scene.PrimaryAxisDesc = bpy.props.BoolProperty(
        name="descending",
        default=True,
        description="Descending order of the primary sorting")

    bpy.types.Scene.SecondaryAxisDesc = bpy.props.BoolProperty(
        name="descending",
        default=False,
        description="Descending order of the secondary sorting")

    bpy.utils.register_module(__name__)

def unregister():
    del bpy.types.Scene.NewBaseName
    del bpy.types.Scene.WithNumberFrom
    del bpy.types.Scene.WithNumber

    # del bpy.types.Scene.NewNameBases
    del bpy.types.Scene.PrimarySortAxis
    del bpy.types.Scene.PrimaryAxisDesc
    del bpy.types.Scene.SecondarySortAxis
    del bpy.types.Scene.SecondaryAxisDesc

    bpy.utils.unregister_module(__name__)


if __name__ == "__main__":
    register()
