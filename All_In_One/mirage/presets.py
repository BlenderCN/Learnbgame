'''
Copyright (C) 2015 Diego Gangl
<diego@sinestesia.co>

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
import json
import shutil

import bpy
from bpy.props import StringProperty, IntProperty

from . import data
from . import utils


# -------------------------------------------------------------------------------
# VARIABLES
# -------------------------------------------------------------------------------

errors      = []
presets_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           'saved_presets')



# -------------------------------------------------------------------------------
# MAIN FUNCTIONS
# -------------------------------------------------------------------------------

def load_all_presets(root_dir = None):
    """ Load all presets in preset directory """
    
    def iterate(file_name):
        """ Load a single preset from a file """
        
        try:
            with open(file_name, 'r') as stream:
                preset_data = json.loads(stream.read())
                item        = settings.preset_list.add() 

                item['name']        = preset_data['name']
                item['description'] = preset_data['description']
                item['filepath']    = file_name


        except FileNotFoundError:
            print('[MIRAGE] Can\'t find preset {0}!'.format(file_name))

        except PermissionError:
            print(('[MIRAGE] Please check permissions '
                   'on file {0}').format(file_name))


    # ------------------------------------------------------------------------
    
    settings = data.settings('presets')

    if not root_dir:
        root_dir = presets_dir

    if not os.access(root_dir, os.W_OK):
        errors.append('Can\'t find preset directory')
        return False

    for dir_name, subdirs, files in os.walk(root_dir): 

        for file_name in files:
            file_path = os.path.join(dir_name, file_name)
            iterate(file_path)

    
    print('[MIRAGE] Preset list built')



def load_preset_data(index):
    """ Load all data from a preset file """

    try:
        settings = data.settings('presets')
        preset_data = settings.preset_list[index]

        with open(preset_data.filepath, 'r') as stream:
            output = json.loads(stream.read())

        return output

    except KeyError:
        print('[MIRAGE] Preset {0} was never loaded'.format(name))
        return False



def preset_exists(name):
    """ Check if a preset exists already """

    filepath = os.path.join(presets_dir, name + '.json') 

    return os.access(filepath, os.R_OK)


def save_preset(name, data):
    """ Write preset file """

    preset_data = json.dumps(data)
    filepath    = os.path.join(presets_dir, name + '.json') 

    try:
        with open(filepath, 'w') as stream:
            stream.write(preset_data)

        return filepath

    except (PermissionError, OSError):
        print('[MIRAGE] Can\'t write preset "{0}"!'.format(filepath))
        return False



def delete_preset(name):
    """ Delete preset file """

    filepath = os.path.join(presets_dir, name + '.json') 

    try:
        os.remove(filepath)
        return True

    except FileNotFoundError:
        print('[MIRAGE] Can\'t delete preset {0}!'.format(name))
        return False
        
    except PermissionError:
        print('[MIRAGE] is not allowed to delete preset {0}!'.format(name))
        print('[MIRAGE] Please check permissions on file {0}'.format(filepath))
        return False



def import_file(filepath):
    """ Copy a preset file to the presets directory """

    # This looks like a very roundabout way of
    # copying, but allows to validate the json

    with open(filepath, 'r') as stream:
        preset_data = json.loads(stream.read())

    name     = preset_data['name']
    output   = os.path.join(presets_dir, name + '.json')

    settings = data.settings('presets')

    for preset_item in settings.preset_list:
        if preset_item.name == name:
            raise NameError
    
    with open(output ,'w') as stream:
        stream.write(json.dumps(preset_data))

    # Add to current preset list
    item                = settings.preset_list.add() 

    item['name']        = preset_data['name']
    item['description'] = preset_data['description']
    item['filepath']    = output



# -------------------------------------------------------------------------------
# Operators
# -------------------------------------------------------------------------------

class OT_DeleteTerrainPreset(bpy.types.Operator):
    bl_idname       = "mirage.preset_delete"
    bl_label        = "Delete Preset"
    bl_description  = "Delete preset"
    bl_options      = {"REGISTER"}


    @classmethod
    def poll(cls, context):
        settings = data.settings('presets')
        return len(settings.preset_list) > 0


    def invoke(self, context, event):
        """ Show settings dialog """
        
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        """ Delete a preset """

        settings = data.settings('presets')
        error    = False

        try:
            name   = settings.preset_list[settings.index].name
            result = delete_preset(name)
        except KeyError:
            error = True

        if error or not result:
            self.report({'ERROR'}, 'Failed to delete preset')
            return {'CANCELLED'}
                
        settings.preset_list.remove(settings.index)

        if settings.index > len(settings.preset_list) - 1:
            settings.index = len(settings.preset_list) - 1

        utils.force_redraw()
        self.report({'INFO'}, 'Deleted preset "{0}"'.format(name))
        return {'FINISHED'}


class OT_SaveTerrainPreset(bpy.types.Operator):
    bl_idname       = "mirage.preset_save"
    bl_label        = "Save Preset"
    bl_description  = "Save settings as preset"
    bl_options      = {"REGISTER"}

    name = StringProperty(
        name = "Name",
        description = 'name for this preset',
        default = '',
    )

    description = StringProperty(
        name = "Description",
        description = 'description of this preset',
        default = '',
    )

    index = IntProperty(
        name = "Index",
        description = 'Index of preset (to edit)',
        default = -1,
    )

    def invoke(self, context, event):
        """ Show settings dialog """
        
        settings = data.settings('presets')
        if self.index > -1 and len(settings.preset_list) == 0:
            self.report({'INFO'}, 'Please add a preset first')
            return {'CANCELLED'}

        return context.window_manager.invoke_props_dialog(self)


    def draw(self, context):
        """ Draw settings dialog """

        info = data.settings('presets')

        self.layout.separator()

        if self.index > -1:
            self.name        = info.preset_list[info.index].name
            self.description = info.preset_list[info.index].description

        row = self.layout.row()
        row.prop(self, 'name')

        row = self.layout.row()
        row.prop(self, 'description')

        if self.index > -1:
            row = self.layout.row()
            row.label('This preset\'s settings will be overwritten', 
                      icon='INFO')




    def execute(self, context):
        """ Save a preset """
        
        settings    = data.settings('terrain')
        info        = data.settings('presets')

        if self.name == '':
            self.report({'ERROR'}, 'Please give this preset a name')
            return {'CANCELLED'}

        if preset_exists(self.name) and self.index == -1:
            self.report({'ERROR'}, ('A preset called "{0}" '
                                    'already exists').format(self.name))
            return {'CANCELLED'}

        preset_data  = {
                    'name'          : self.name,
                    'description'   : self.description,
                    'version'       : 2.0,

                    'filetype'      : 'Mirage Preset',
                    'type'          : 'terrain',

                    'detail_level'  : settings.detail_level,
                    'detail_custom' : settings.detail_custom,

                    'seed'          : settings.seed,
                    'auto_seed'     : settings.auto_seed,

                    'size'          : settings.size,
                    'max_height'    : settings.max_height,
                    'alpine'        : settings.alpine,
                    'deformation'   : settings.deformation,
                    'roughness'     : settings.roughness,
                    'plateau_level' : settings.plateau_level,
                    'sea_level'     : settings.sea_level,

                    'edge'          : settings.edges,
                    'edge_smooth'   : settings.edge_smoothed_factor,

                    'use_thermal'   : settings.use_thermal,
                    'use_strata'    : settings.use_strata,
                    'use_slopes'    : settings.use_slopes,

                    'slopes'        : {
                                         'x' : settings.slope_X,
                                         'y' : settings.slope_Y,

                                         'min_x' : settings.slope_min_X,
                                         'min_y' : settings.slope_min_Y,

                                         'invert_x' : settings.slope_invert_X,
                                         'invert_y' : settings.slope_invert_Y,
                                      },

                    'thermal'       : {
                                         'talus'     : settings.thermal_talus,
                                         'strength'  : settings.thermal_strength,
                                      },

                    'strata'        : {
                                         'frequency' : settings.strata_frequency,
                                         'strength'  : settings.strata_strength,
                                         'invert'    : settings.strata_invert,
                                      },
                }

        if self.index > -1:
            old_preset  = info.preset_list[self.index]
            old_name    = old_preset.name
            removed_old = delete_preset(old_name)

            if not removed_old:
                self.report({'ERROR'}, 'Failed to save preset!')
                return {'CANCELLED'}

            info.preset_list.remove(self.index) 


        result = save_preset(self.name, preset_data)

        if not result:
            self.report({'ERROR'}, 'Failed to save preset!')
            return {'CANCELLED'}

        else:
            item                = info.preset_list.add() 

            item['name']        = self.name
            item['description'] = self.description
            item['filepath']    = result

            utils.force_redraw()

            if self.index == -1:
                self.name = ''
                self.description = ''

            self.report({'INFO'}, 'Saved preset "{0}"'.format(self.name))
            return {'FINISHED'}



class OT_LoadTerrainPreset(bpy.types.Operator):
    bl_idname       = "mirage.preset_load"
    bl_label        = "Use Preset"
    bl_description  = "Load preset settings"
    bl_options      = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        settings = data.settings('presets')
        return len(settings.preset_list) > 0

    def execute(self, context):
        """ Load a preset from the preset list """

        preset      = data.settings('presets')
        settings    = data.settings('terrain')

        if self.name == '':
            self.report({'ERROR'}, 'No preset selected!')
            return {'CANCELLED'}

        preset_data = load_preset_data(preset.index)

        if not preset_data:
            self.report({'ERROR'}, 'Can\'t load preset')
            return {'CANCELLED'}

        else:

            settings.detail_level   = preset_data['detail_level']
            settings.detail_custom  = preset_data['detail_custom']

            settings.size           = preset_data['size']
            settings.max_height     = preset_data['max_height']

            settings.auto_seed      = preset_data['auto_seed']
            settings.seed           = preset_data['seed']

            settings.sea_level      = preset_data['sea_level']
            settings.plateau_level  = preset_data['plateau_level']
            settings.roughness      = preset_data['roughness']
            settings.alpine         = preset_data['alpine']
            settings.deformation    = preset_data['deformation']

            settings.edges                  = preset_data['edge']
            settings.edge_smoothed_factor   = preset_data['edge_smooth']

            settings.use_slopes     = preset_data['use_slopes']
            settings.use_thermal    = preset_data['use_thermal']
            settings.use_strata     = preset_data['use_strata']

            settings.strata_frequency   = preset_data['strata']['frequency']
            settings.strata_strength    = preset_data['strata']['strength']
            settings.strata_invert      = preset_data['strata']['invert']

            settings.thermal_talus      = preset_data['thermal']['talus']
            settings.thermal_strength   = preset_data['thermal']['strength']

            settings.slope_X          = preset_data['slopes']['x']
            settings.slope_Y          = preset_data['slopes']['y']
            settings.slope_min_X      = preset_data['slopes']['min_x']
            settings.slope_min_Y      = preset_data['slopes']['min_y']
            settings.slope_invert_X   = preset_data['slopes']['invert_x']
            settings.slope_invert_Y   = preset_data['slopes']['invert_y']

            self.report({'INFO'}, 'Loaded preset {0}'.format(preset_data['name']))

            return {'FINISHED'}


class OT_ImportPreset(bpy.types.Operator):
    bl_idname       = "mirage.preset_import"
    bl_label        = "Import Preset"
    bl_description  = "Import preset from file"
    bl_options      = {"REGISTER"}

    filepath        = StringProperty(subtype="FILE_PATH")
    filter_glob     = StringProperty(
                                     default="*.json",
                                     options={'HIDDEN'},
                                    )

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


    def execute(self, context):
        """ Import a preset from a file """

        settings    = data.settings('presets')

        try:
            import_file(self.filepath)
            settings.index = len(settings.preset_list) - 1

        except ValueError:
            self.report({'ERROR'}, 'Invalid preset file')
            return {'CANCELLED'}

        except NameError:
            self.report({'ERROR'}, 'A preset with that name exists already')
            return {'CANCELLED'}

        except PermissionError:
            self.report({'ERROR'}, 'Not allowed to read preset file')
            return {'CANCELLED'}

        utils.force_redraw()
        self.report({'INFO'}, 'Imported preset')
        return {'FINISHED'}


class OT_ExportPreset(bpy.types.Operator):
    bl_idname       = "mirage.preset_export"
    bl_label        = "Export Preset"
    bl_description  = "Export preset to a file"
    bl_options      = {"REGISTER"}

    filepath        = StringProperty(subtype="FILE_PATH")
    index           = IntProperty(min=0, options={'HIDDEN'}) 
    filter_glob     = StringProperty(
                                     default="*.json",
                                     options={'HIDDEN'},
                                    )

    @classmethod
    def poll(cls, context):
        settings = data.settings('presets')
        return len(settings.preset_list) > 0


    def invoke(self, context, event):

        settings    = data.settings('presets')
        home        = os.path.expanduser('~')
        name        = settings.preset_list[self.index].name + '.json'

        self.filepath = os.path.join(home, name)

        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


    def execute(self, context):
        """ Import a preset from a file """

        settings     = data.settings('presets')

        try:
            src_path = settings.preset_list[self.index].filepath

        except IndexError:
            self.report({'ERROR'}, 'Wrong preset index')
            return {'CANCELLED'}

        
        try:
            shutil.copyfile(src_path, self.filepath)

        except OSError:
            self.report({'ERROR'}, 'Couldn\'t write preset file!')
            return {'CANCELLED'}


        self.report({'INFO'}, 'Exported preset to {0}'.format(self.filepath))
        return {'FINISHED'}
        
