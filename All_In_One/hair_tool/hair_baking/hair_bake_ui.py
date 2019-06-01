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
# import sys
# dir = 'C:\\Users\\JoseConseco\\AppData\\Local\\Programs\\Python\\Python35\\Lib\\site-packages'
# if not dir in sys.path:
#     sys.path.append(dir )
# import ipdb

class VIEW3D_PT_Hair_Panel_Bake(bpy.types.Panel):
    bl_label = "Hair Bake"
    bl_idname = "hair_tool_bake"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "Tools"
    bl_context = "objectmode"

    def draw(self, context):
        layout = self.layout

        if 'Background' in bpy.data.objects.keys():
            row = layout.row(align=True)
            row.operator("object.bake_hair",icon='RESTRICT_RENDER_OFF')
            layout.prop(context.scene.hair_bake_settings, 'hair_bake_path')
            layout.prop(context.scene.hair_bake_settings, 'hair_bake_file_name')
            layout.prop(context.scene.hair_bake_settings, 'bakeResolution')
            layout.prop(context.scene.hair_bake_settings,'render_quality')
            layout.prop(context.scene.hair_bake_settings, 'output_format')
            col = layout.column(align=True)
            col.prop(context.scene.hair_bake_settings, 'render_passes',expand=True)
            layout.prop(context.scene.hair_bake_settings, 'hair_bake_composite',expand=True)
        row = layout.row(align=True)
        row.operator("object.open_hair_bake")
            
