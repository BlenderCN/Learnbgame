'''
Copyright (C) 2015 Diego Gangl
diego@sinestesia.co

Created by Diego Gangl. This file is part of Mirage.

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

import os

import bpy

from . import data
from . import icons
from . import presets

import mirage


class MG_UIL_TerrainFeatures(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            settings = bpy.context.window_manager.mirage.terrain
            icons = mirage.icons_storage['main']

            if item.f_id == 'STRATA':
                toggle = 'use_strata'
                icon = 'IPO_CONSTANT'
            elif item.f_id == 'THERMAL':
                toggle = 'use_thermal'
                icon = 'LAMP_SUN'
            elif item.f_id == 'SLOPES':
                toggle = 'use_slopes'
                icon_value = icons['initial_heights'].icon_id

            if icon:
                layout.label(item.name, icon=icon)
            else:
                layout.label(item.name, icon_value=icon_value)


            layout.prop(settings, toggle, text='')


class MG_UIL_Presets(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            settings = bpy.context.window_manager.mirage.terrain

            layout.label(item.name)


class MG_PT_Presets(bpy.types.Panel):
    bl_idname       = "mirage.presets_panel"
    bl_label        = "Presets"
    bl_space_type   = "VIEW_3D"
    bl_region_type  = "TOOLS"
    bl_category     = data.get_prefs('tab')
    bl_options      = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def draw(self, context):
        """ Draw terrain Panel """
        
        layout   = self.layout
        settings = data.settings('presets')
    
        if len(presets.errors) > 0:
            layout.separator()
            row = layout.row()
            row.label(presets.errors[0], icon='ERROR')
            layout.separator()

            return


        try:
            current_preset = settings.preset_list[settings.index]
        except IndexError:

            # If something was deleted and index was not updated
            # then it's become invalid. Clamp it for good measure.
            settings.index = min(settings.index, 
                                 len(settings.preset_list) -1)


        row = layout.row()
        col = row.column()
        col.template_list("MG_UIL_Presets", "preset_list", settings, "preset_list", settings, "index" )

        col = row.column(align=True)
        col.operator('mirage.preset_save', text='', icon='ZOOMIN')
        col.operator('mirage.preset_delete', text='', icon='ZOOMOUT')

        col.operator('mirage.preset_save', text='', 
                     icon='UI').index = settings.index

        col.separator()
        col.operator('mirage.preset_import', icon='IMPORT', text='')
        col.operator('mirage.preset_export', text='', 
                     icon='EXPORT').index = settings.index


        if len(settings.preset_list) == 0:
            layout.separator()
            row = layout.row()
            row.label('No Presets loaded', icon='INFO')
            layout.separator()
        else:
            layout.separator()
            row = layout.row()
            col = row.column(align=True)
            col.label(text=current_preset.name, icon='SEQ_SEQUENCER')
            col.label(text=current_preset.description)
        
        layout.separator()
        row = layout.row()
        row.scale_y = 1.25
        row.operator('mirage.preset_load')
        layout.separator()



class MG_PT_TerrainProcedural(bpy.types.Panel):
    bl_idname       = "mirage.terrain_procedural_panel"
    bl_label        = "Procedural Terrain"
    bl_space_type   = "VIEW_3D"
    bl_region_type  = "TOOLS"
    bl_category     = data.get_prefs('tab')

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'


    def draw_header(self, context):
        layout = self.layout


    def draw(self, context):
        """ Draw terrain Panel """
        
        layout = self.layout
        settings = data.settings('terrain')
        icons = mirage.icons_storage['main']
        
        row = layout.row()
        row.prop(settings, 'procedural_tab', expand=True)
        layout.separator()
        
        if settings.procedural_tab == 'GENERAL':            

            row = layout.row()
            row.prop(settings, 'detail_level')

            row = layout.row()

            if settings.detail_level != 'custom':
                verts = ((2**int(settings.detail_level))) ** 2 
                text = '{0:,} Vertices'.format(verts)

                row.label(text, icon='VERTEXSEL')
            else:
                col = layout.column(align=True)
                col.prop(settings, 'detail_custom')
                col.prop(settings, 'detail_base')

                verts = settings.detail_custom ** 2 
                text = '{0:,} Vertices'.format(verts)

                row = layout.row()
                row.label(text, icon='VERTEXSEL')


            layout.separator()
            
            col = layout.column(align=True)
                
            col.prop(settings, 'size')
            col.prop(settings, 'max_height')

            layout.separator()


            col = layout.column(align=True)

            layout.separator()
            col.prop(settings, 'plateau_level')
            col.prop(settings, 'sea_level')


            col.prop(settings, 'roughness')
            col.prop(settings, 'alpine')
            col.prop(settings, 'deformation')

            row = col.row(align=True)
            row.prop(settings, 'seed')
            row.prop(settings, 'auto_seed',text='',icon='TIME')
            
            row = layout.row()
            row.prop(settings, 'edges')
            
            if settings.edges == 'SMOOTH' or settings.edges == 'ISLAND':
                row = layout.row()
                row.prop(settings, 'edge_smoothed_factor', slider=True)


        elif settings.procedural_tab == 'FEATURES':            
            row = layout.row()
            row.template_list("MG_UIL_TerrainFeatures", "features_list", settings, "features", settings, "features_index" )

            layout.separator()
            
            try:
                current_feature = settings.features[settings.features_index]
            except:
                print('[MIRAGE] No terrain features? Adding them...')
                data.register_terrain_features()

            if current_feature.f_id == 'STRATA':
                row = layout.row()
                row.enabled = settings.use_strata
                row.label('Stratified (step-like) terrain', icon='INFO')
                layout.separator()
                col = layout.column(align=True)
                col.enabled = settings.use_strata
                col.prop(settings, 'strata_frequency', text='Frequency')
                col.prop(settings, 'strata_strength', text='Strength', slider=True)
                col.prop(settings, 'strata_invert')

            elif current_feature.f_id == 'THERMAL':
                row = layout.row()
                row.enabled = settings.use_thermal
                row.label('Erosion due to temperature changes', icon='INFO')
                layout.separator()
                col = layout.column(align=True)
                col.enabled = settings.use_thermal
                col.prop(settings, 'thermal_talus')
                col.prop(settings, 'thermal_strength', slider=True)

            elif current_feature.f_id == 'SLOPES':
                row = layout.row()
                row.enabled = settings.use_slopes
                row.label('Gradual height change', icon='INFO')
                layout.separator()
                col = layout.column(align=True)
                col.enabled = settings.use_slopes
                col.label('X axis', icon='COLOR_RED')
                col.prop(settings, 'slope_X', slider=True)
                col.prop(settings, 'slope_min_X', slider=True)
                col.prop(settings, 'slope_invert_X')

                layout.separator()
                col = layout.column(align=True)
                col.enabled = settings.use_slopes
                col.label('Y axis', icon='COLOR_GREEN')
                col.prop(settings, 'slope_Y', slider=True)
                col.prop(settings, 'slope_min_Y', slider=True)
                col.prop(settings, 'slope_invert_Y')


        layout.separator()
        layout.separator()

        col = layout.column(align=True)
        row = col.row(align=True)

        enable = (settings.progress == 0)
        
        if enable:
            row.scale_y = 1.25
            row.operator('mirage.generate_terrain')
        else:
            row.scale_y = 1.1
            
            if settings.progress == 100:
                row.label('Linking to scene', icon = 'SCENE_DATA')            
            else:            
                row.label('Generating Terrain', icon = 'SCRIPTWIN')            
             
            row.operator('mirage.cancel_terrain_generation', text='', emboss=False, icon='X')

            
        layout.separator()



class MG_PT_TerrainFile(bpy.types.Panel):
    bl_idname       = "mirage.terrain_file_panel"
    bl_label        = "Terrain from Heightmap"
    bl_space_type   = "VIEW_3D"
    bl_region_type  = "TOOLS"
    bl_category     = data.get_prefs('tab')
    bl_options      = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def draw_header(self, context):
        layout = self.layout

    
    def select_text(self):
        
        if not data.heightmap_icons:
            return 'Select a heightmap'
        else:
            settings = data.settings('terrain')
            return os.path.basename(settings.heightmap_filepath)
        
        
    def draw(self, context):
        """ Draw terrain Panel """

        layout = self.layout
        settings = data.settings('terrain')
        
        if data.heightmap_icons:
            row = layout.row()
            row.template_icon_view(settings, "heightmap_list")

        row = layout.row()
        row.operator('mirage.select_heightmap',
                      text = self.select_text(),
                      icon = 'FILE_FOLDER')

        if data.errors['heightmap_file']:
            row = layout.row()
            row.label(text='The image file could not be loaded', icon='ERROR')


        layout.separator()

        col = layout.column(align=True)


        col.prop(settings, 'size')
        col.prop(settings, 'heightmap_strength')
        col.prop(settings, 'heightmap_detail')

        row = layout.row()
        text = '{0:,} Vertices'.format(settings.heightmap_detail**2)
        row.label(text, icon='VERTEXSEL')


        layout.separator()
        row = layout.row()
        row.scale_y = 1.25
        row.operator('mirage.map_to_terrain')
        layout.separator()




class MG_PT_Trees(bpy.types.Panel):
    bl_idname       = "mirage.tree_panel"
    bl_label        = "Tree Distribution"
    bl_space_type   = "VIEW_3D"
    bl_region_type  = "TOOLS"
    bl_category     = data.get_prefs('tab')
    
    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'
        

    def draw_header(self, context):
        layout = self.layout


    def draw(self, context):
        """ Draw Tree panel """
        
        settings = data.settings('tree')
        layout = self.layout

        col = layout.column(align=True)

        col.prop(settings, 'density')
        col.prop(settings, 'max_slope')
        col.prop(settings, 'max_height')

        row = layout.row()
        row.enabled = not settings.lock_scale_to_terrain
        row.prop(settings, 'scale')

        row = layout.row()
        row.prop(settings, 'lock_scale_to_terrain')

        layout.separator()
        row = layout.row()
        row.prop_search(settings, "src_mesh", bpy.data, "groups")
            

        layout.separator()
        layout.separator()
        row = layout.row()
        row.enabled = settings.src_mesh != ''
        row.scale_y = 1.25

        if context.object and 'Trees' in context.object.modifiers:
            text = 'Update Trees'
        else:
            text = 'Add Trees'

        row.operator('mirage.generate_tree', text = text)
        
        if data.errors['tree_performance']:
            row = layout.row()
            row.label('Display set to "Cross" for performance')
            row.prop(settings, 'show_performance_help', 
                     icon='QUESTION', text='', emboss = False)

            if settings.show_performance_help:
                box = layout.box()
                row = box.row()
                row.label('The viewport becomes too slow with this much geometry,')
                row = box.row()
                row.label('so I have set the display type to show only the position ')
                row = box.row()
                row.label('of particles. This doesn\'t affect rendering.')

                
            layout.separator()

        layout.separator()




class MG_PT_Tools(bpy.types.Panel):
    bl_idname       = "mirage.tools_panel"
    bl_label        = "Tools"
    bl_space_type   = "VIEW_3D"
    bl_region_type  = "TOOLS"
    bl_category     = data.get_prefs('tab')
    
    
    def vgroup_text(self, context, name):
        obj = context.object
        
        if not obj:
            text = 'Generate {0} Group'
            return text.format(name)
        
        if name in obj.vertex_groups:
            text = 'Update {0} Groups'
        else:
            text = 'Generate {0} Groups'
    
        return text.format(name)
    

    def draw_header(self, context):
        layout = self.layout

    
    def draw(self, context):
        """ Draw Tree panel """    
        
        layout = self.layout
        
        height_txt = self.vgroup_text(context, 'Height')
        slope_txt = self.vgroup_text(context, 'Slope')
        belowsea_txt = self.vgroup_text(context, 'Below Sea')
        plateau_txt = self.vgroup_text(context, 'Plateau')
        
        col = layout.column(align=True)        
        col.operator('mirage.make_vgroup_height',text = height_txt) 
        col.operator('mirage.make_vgroup_slope', text = slope_txt)               
        col.operator('mirage.make_vgroup_belowsea', text = belowsea_txt)
        col.operator('mirage.make_vgroup_plateau', text = plateau_txt)

        layout.separator()

        col = layout.column(align=True)        
        col.operator('mirage.export_vgroups')
        col.operator('mirage.export_heightmap')
        col.operator('mirage.export_terrain_as_data')

        layout.separator()
