# Copyright 1996-2018 Cyberbotics Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

bl_info = {
    'name': 'Webots format',
    'author': 'Fabien Rohrer',
    'version': (1, 0, 0),
    'blender': (2, 79, 0),
    'location': 'File > Import-Export',
    'description': 'Export Webots',
    'warning': '',
    'wiki_url': 'https://github.com/omichel/blender-webots-exporter/wiki',
    'support': 'COMMUNITY',
    'category': 'Import-Export',
}

if 'bpy' in locals():
    import importlib
    if 'export_webots' in locals():
        importlib.reload(export_webots)

import bpy
from bpy.props import (
    BoolProperty,
    FloatProperty,
    StringProperty,
)
from bpy_extras.io_utils import (
    ExportHelper,
    orientation_helper_factory,
    axis_conversion,
    path_reference_mode,
)


IOX3DOrientationHelper = orientation_helper_factory('IOX3DOrientationHelper', axis_forward='Z', axis_up='Y')


class ExportWebots(bpy.types.Operator, ExportHelper, IOX3DOrientationHelper):
    """Export selection to Webots file (.wbt)"""
    bl_idname = 'scene.wbt'
    bl_label = 'Export Webots'
    bl_options = {'PRESET'}

    filename_ext = '.wbt'
    filter_glob = StringProperty(default='*.wbt', options={'HIDDEN'})

    use_selection = BoolProperty(
        name='Selection Only',
        description='Export selected objects only',
        default=False,
    )
    use_mesh_modifiers = BoolProperty(
        name='Apply Modifiers',
        description='Use transformed mesh data from each object',
        default=True,
    )
    converstion_file_path = StringProperty(
        name='Custom conversion File Path',
        description='File path targeting the JSON file containing the custom Blender->Webots conversion rules.',
        default=''
    )
    global_scale = FloatProperty(
        name='Scale',
        min=0.01, max=1000.0,
        default=1.0,
    )

    path_mode = path_reference_mode

    def execute(self, context):
        from . import export_webots
        from mathutils import Matrix

        keywords = self.as_keywords(ignore=('axis_forward', 'axis_up', 'global_scale', 'check_existing', 'filter_glob'))
        global_matrix = axis_conversion(to_forward=self.axis_forward, to_up=self.axis_up).to_4x4() * Matrix.Scale(self.global_scale, 4)
        keywords['global_matrix'] = global_matrix

        return export_webots.save(context, **keywords)


def menu_func_export(self, context):
    self.layout.operator(ExportWebots.bl_idname, text='Webots (.wbt)')


def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_export.remove(menu_func_export)


if __name__ == '__main__':
    register()
