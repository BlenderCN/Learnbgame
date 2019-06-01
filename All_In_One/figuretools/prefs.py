# -*- coding: utf8 -*-
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
# --------------------------------------------------------------------------
# Blender 2.6 FigureTools Addon
# --------------------------------------------------------------------------
#
# Authors:
# Tony Edwards
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.
#
# ***** END GPL LICENCE BLOCK *****
#
import bpy

ADDON_NAME = 'figuretools'
FINISHED = {'FINISHED'}

class RuntimePath(bpy.types.PropertyGroup):
    path = bpy.props.StringProperty(subtype='DIR_PATH')

class AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = ADDON_NAME

    runtimes = bpy.props.CollectionProperty(type=RuntimePath)

    def draw(self, context):
        box = self.layout.box()
        row = box.row()
        row.label(text='Runtime Paths:')

        # Button to add a runtime path.
        row.operator('wm.figuretools_runtime_add', text='', icon='ZOOMIN', emboss=False)

        # Create a layout row for each runtime path.
        for i, runtime in enumerate(self.runtimes):
            runtime_row = box.row()
            runtime_row.prop(runtime, 'path', text='')

            # Button to remove this runtime path.
            runtime_row.operator('wm.figuretools_runtime_remove', text='', icon='X', emboss=False).index = i

class AddRuntime(bpy.types.Operator):
    bl_idname = 'wm.figuretools_runtime_add'
    bl_label = 'FigureTools Add Runtime'
    bl_description = 'Add a new runtime path. Runtime paths will be searched (in order) for textures or other items as needed.'

    def execute(self, context):
        bpy.context.user_preferences.addons[ADDON_NAME].preferences.runtimes.add()
        return FINISHED

class RemoveRuntime(bpy.types.Operator):
    bl_idname = 'wm.figuretools_runtime_remove'
    bl_label = 'FigureTools Remove Runtime'
    bl_description = 'Remove this runtime path.'

    index = bpy.props.IntProperty()

    def execute(self, context):
        bpy.context.user_preferences.addons[ADDON_NAME].preferences.runtimes.remove(self.index)
        return FINISHED
