'''
Copyright (C) 2018 SmugTomato

Created by SmugTomato

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
import bpy
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator

from .rcol.geom import Geom


class ImportGeom(Operator, ImportHelper):
    """Sims 3 GEOM Importer"""
    bl_idname = "s3geom.import"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Sims 3 GEOM (.simgeom)"

    # ImportHelper mixin class uses this
    filename_ext = ".simgeom"

    filter_glob = StringProperty(
            default="*.simgeom",
            options={'HIDDEN'},
            maxlen=255,  # Max internal buffer length, longer would be clamped.
            )

    use_strict = BoolProperty(
            name="Strict",
            description="Stop import process when reading unexpected TGI value(s) in header",
            default=False,
            )

    def execute(self, context):
        geom = Geom.from_file(self.filepath)
        if not geom:
            return {'CANCELLED'}
        elif not geom.read_data(strict=self.use_strict):
            print("\nCancelled at", geom.reader.offset, "/", len(geom.reader.data))
            return {'CANCELLED'}

        # Do stuff here

        return {'FINISHED'}
