# ##### BEGIN GPL LICENSE BLOCK #####
#
#  Copyright (C) 2018 Nikolai Janakiev
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 3
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


import bpy
import logging
import importlib
from bpy.props import BoolProperty, StringProperty, PointerProperty, EnumProperty, CollectionProperty

logger = logging.getLogger(__name__)


class ConfigurationPropertyGroup(bpy.types.PropertyGroup):
    log = logging.getLogger('bpy.types.ConfigurationPropertyGroup')

    def get_items(self, context):
        return [(item.name, item.name, '') for item in self.scene_names]

    override        = BoolProperty(name='Override', default=False)

    output_folder   = StringProperty(name='', default='output')
    output_name     = StringProperty(name='')

    scene_names     = CollectionProperty(type=bpy.types.PropertyGroup)
    scene_name      = EnumProperty(name='Scenes',
                        items=get_items,
                        update=lambda self, context : self.execute(context))

    config_filepath = StringProperty(name='Configuraton',
                        description='Path of configuraton',
                        default='', options={'HIDDEN'},
                        subtype='FILE_PATH')

    def execute(self, context):
        self.log.debug('execute called')
        cf = context.scene.cookie_factory

        try:
            composition = importlib.import_module(cf.scene_name)
            if "composition" in locals():
                logger.debug('reload composition')
                importlib.reload(composition)

            self.log.debug('Running ' + cf.scene_name)
            comp = composition.Composition(context)
        except ImportError as e:
            self.log.error(e)


class CookieFactoryPanel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_label = 'Cookie Factory'
    bl_context = 'objectmode'
    bl_category =  'Cookie Factory'

    def draw(self, context):
        layout = self.layout
        properties = context.scene.cookie_factory

        layout.label('Configuration')
        layout.prop(properties, 'config_filepath', text='')
        layout.operator('cookie_factory.import_configuration')
        layout.prop(properties, 'scene_name', text='')

        col = layout.column(align=True)
        col.label('Output Folder')
        col.prop(properties, 'output_folder')
        col.label('Output Name')
        col.prop(properties, 'output_name')

        layout.prop(properties, 'override')

        row = layout.row(align=True)
        row.operator('cookie_factory.render')
        row.operator('cookie_factory.animation')


def register():
    bpy.utils.register_class(ConfigurationPropertyGroup)
    bpy.types.Scene.cookie_factory = PointerProperty(type=ConfigurationPropertyGroup)

    bpy.utils.register_class(CookieFactoryPanel)
    logger.debug('panel registered')

def unregister():
    bpy.utils.unregister_class(CookieFactoryPanel)

    del bpy.types.Scene.cookie_factory
    bpy.utils.unregister_class(ConfigurationPropertyGroup)
    logger.debug('panel unregistered')
