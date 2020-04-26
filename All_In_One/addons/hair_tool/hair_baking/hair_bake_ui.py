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

class  HT_OP_Hair_Panel_Bake(bpy.types.Panel):
    bl_label = "Hair Bake"
    bl_idname = "hair_tool_bake"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Hair Tool'
    # bl_context = "object"

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
            layout.prop(context.scene.hair_bake_settings, 'hair_bake_composite',expand=True)
            col = layout.column(align=True)
            col.prop(context.scene.hair_bake_settings, 'render_passes',expand=True)
            layout.separator()
            col = layout.box()
            col.label(text='Global Particle Hair Settings')
            col.prop(context.scene.hair_bake_settings, 'particle_display_step')
            col.prop(context.scene.hair_bake_settings, 'particle_width')
            col.prop(context.scene.hair_bake_settings, 'particle_shape')
        row = layout.row(align=True)
        row.operator("object.open_hair_bake")
            
