# -*- coding: utf8 -*-
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
# --------------------------------------------------------------------------
# Blender Mitsuba Add-On
# --------------------------------------------------------------------------
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
# ***** END GPL LICENSE BLOCK *****

# System Libs
import os
import sys
import traceback

# Blender Libs
import bpy
from bpy.types import Operator
from bpy.props import BoolProperty, StringProperty
from bl_operators.presets import AddPresetBase

from .. import MitsubaAddon
from ..outputs import MtsLog
from ..export.scene import SceneExporter


@MitsubaAddon.addon_register_class
class MITSUBA_OT_preset_engine_add(AddPresetBase, Operator):
    '''Save the current settings as a preset'''
    bl_idname = 'mitsuba.preset_engine_add'
    bl_label = 'Add Mitsuba Engine settings preset'
    preset_menu = 'MitsubaRender_MT_engine_presets'
    preset_subdir = 'mitsuba/engine'

    def execute(self, context):
        self.preset_values = [
            'bpy.context.scene.mitsuba_engine.%s' % v['attr'] for v in bpy.types.mitsuba_engine.get_exportable_properties()
        ]

        return super().execute(context)


@MitsubaAddon.addon_register_class
class EXPORT_OT_mitsuba(Operator):
    bl_idname = 'export.mitsuba'
    bl_label = 'Export Mitsuba Scene (.xml)'

    filter_glob = StringProperty(default='*.xml', options={'HIDDEN'})
    use_filter = BoolProperty(default=True, options={'HIDDEN'})
    filename = StringProperty(name='Target filename', subtype='FILE_PATH')
    directory = StringProperty(name='Target directory')

    api_type = StringProperty(default='FILE', options={'HIDDEN'})
    write_files = BoolProperty(default=True, options={'HIDDEN'})
    write_all_files = BoolProperty(default=True, options={'HIDDEN'})

    scene = StringProperty(options={'HIDDEN'}, default='')

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        try:
            if self.properties.scene == '':
                scene = context.scene

            else:
                scene = bpy.data.scenes[self.properties.scene]

            scene_exporter = SceneExporter()
            scene_exporter.set_properties(self.properties)
            scene_exporter.set_scene(scene)

            export_result = scene_exporter.export()

            if not export_result or 'CANCELLED' in export_result:
                self.report({'ERROR'}, "Unsucessful export!")
                return {'CANCELLED'}

            return {'FINISHED'}

        except:
            typ, value, tb = sys.exc_info()
            elist = traceback.format_exception(typ, value, tb)
            MtsLog("Caught exception: %s" % ''.join(elist))
            self.report({'ERROR'}, "Unsucessful export!")

            return {'CANCELLED'}


def menu_func(self, context):
    default_path = os.path.splitext(os.path.basename(bpy.data.filepath))[0] + ".xml"
    self.layout.operator("export.mitsuba", text="Export Mitsuba scene...").filename = default_path

bpy.types.INFO_MT_file_export.append(menu_func)
