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
from bpy.props import StringProperty
from bpy_extras.io_utils import ImportHelper, axis_conversion
import gzip
import json
import os.path

from . utils import ftlog

class DSONImporter(bpy.types.Operator, ImportHelper):
    """Load a DAZ DSON file"""
    bl_idname = 'import_scene.dson'
    bl_label = 'Import DSON'

    filter_glob = StringProperty(default='*.duf;*.dsf', options={'HIDDEN'})

    def execute(self, context):
        dson_file_path = self.filepath

        # Current importer loads geometry from an obj file, so we look for one
        # with the same name as the .duf file.
        obj_file_path = os.path.splitext(dson_file_path)[0] + '.obj'

        # TODO: Validate existence of obj file and warn if it doesn't exist.
        #       Need research the 'Blender' conventions for notifications.

        ftlog('Importing %s' % obj_file_path)
        self._load_obj(context, obj_file_path)

        ftlog('Loading %s' % dson_file_path)
        self.dson = self._load_dson(dson_file_path)

        return {'FINISHED'}

    def _load_dson(self, dson_file_path):
        dson_file = None

        # DSON files are optionally compressed, so we try reading it as
        # uncompressed first and then compressed.
        try:
            dson_file = json.load(open(dson_file_path, 'r'))
        except ValueError:
            dson_bytes = gzip.open(dson_file_path, 'r').read()
            dson_file = json.loads(dson_bytes.decode('utf-8'))

        return dson_file

    def _load_obj(self, context, obj_file_path):
        # We just use Blender's existing obj importer. The obj should not have
        # a corresponding .mtl file, since we will get materials from the dson
        # file. Didn't see a way to make mtl loading optional, so we just hope
        # there isn't a mtl file loaded and there are issues materials.
        from io_scene_obj.import_obj import load as load_obj

        # Blender and DAZStudio use different axis orientations, so adjust obj
        # to work with Blender (same as native obj importer).
        global_matrix = axis_conversion(
            from_forward='-Z',
            from_up='Y').to_4x4()
        load_obj(self, context, obj_file_path,
            use_split_groups=False,
            use_image_search=False,
            global_matrix=global_matrix)
