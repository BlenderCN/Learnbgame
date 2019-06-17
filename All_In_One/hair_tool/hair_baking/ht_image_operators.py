# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# Copyright (C) 2017 JOSECONSCO
# Created by JOSECONSCO

import bpy

class HT_OT_SaveImage(bpy.types.Operator):
    bl_idname = "image.save_img"
    bl_label = "save img"
    bl_description = "Save image"
    bl_options = {"REGISTER","UNDO"}

    image_name: bpy.props.StringProperty()
    image_path: bpy.props.StringProperty()
    image_format: bpy.props.StringProperty(default='PNG')

    def execute(self, context):
        suffix = 'png' if self.image_format=='PNG' else 'tga'
        img_name = self.image_name +'.'+suffix
        if img_name in bpy.data.images.keys():
            outputImg = bpy.data.images[img_name]
            outputImg.file_format = self.image_format
            abs_path = bpy.path.abspath(self.image_path+img_name)
            outputImg.filepath_raw = abs_path
            outputImg.save()
        return {"FINISHED"}