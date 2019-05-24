#Manuel Bastioni Lab - Copyright (C) 2016 Manuel Bastioni
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU Affero General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU Affero General Public License for more details.

#You should have received a copy of the GNU Affero General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.


bl_info = {
    "name": "Manuel Bastioni Lab",
    "author": "Manuel Bastioni",
    "version": (1, 2, 0),
    "blender": (2, 7, 7),
    "location": "View3D > Tools > ManuelLab",
    "description": "A complete lab for characters creation",
    "warning": "",
    'wiki_url': "http://www.manuelbastioni.com",
    "category": "Learnbgame",
}

import bpy
import os
import json
from bpy_extras.io_utils import ExportHelper, ImportHelper
from . import humanoid
import time

import logging
log_path = os.path.join(bpy.context.user_preferences.filepaths.temporary_directory, "manuellab_log.txt")
try:
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', filename=log_path, filemode='w', level=logging.INFO)
except PermissionError:
    print("WARNING: Writing permission error for {0}".format(log_path))
    print("The log will be redirected to the console (here)")
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=logging.INFO)
logging.info("ManuelLab version {0}".format(bl_info["version"]))
logging.info("Blender version {0}".format(bpy.app.version))
#import cProfile, pstats, io
#import faulthandler
#faulthandler.enable()

T1 = "humanoid_humanf01"
T1_LABEL = "Caucasian female"
T1_DESCR = "Generate a realistic caucasian female character"

T2 = "humanoid_humanf02"
T2_LABEL = "Asian female"
T2_DESCR = "Generate a realistic asian female character"

T3 = "humanoid_humanf03"
T3_LABEL = "Afro female"
T3_DESCR = "Generate a realistic african female character"

T4 = "humanoid_humanm01"
T4_LABEL = "Caucasian male"
T4_DESCR = "Generate a realistic caucasian male character"

T5 = "humanoid_humanm02"
T5_LABEL = "Asian male"
T5_DESCR = "Generate a realistic asian male character"

T6 = "humanoid_humanm03"
T6_LABEL = "Afro male"
T6_DESCR = "Generate a realistic african male character"

T7 = "humanoid_animef01"
T7_LABEL = "Anime Classic female shojo"
T7_DESCR = "Generate an anime female in shojo style"

T8 = "humanoid_animem01"
T8_LABEL = "Anime Classic male shojo"
T8_DESCR = "Generate an anime male in shojo style"

T9 = "humanoid_animef02"
T9_LABEL = "Anime Modern female shojo"
T9_DESCR = "Generate an anime female in modern shojo style"

T10 = "humanoid_animem02"
T10_LABEL = "Anime Modern male shojo"
T10_DESCR = "Generate an anime female in modern shojo style"


HUMANOID_TYPES = [
    (T1, T1_LABEL, T1_DESCR),
    (T2, T2_LABEL, T2_DESCR),
    (T3, T3_LABEL, T3_DESCR),
    (T4, T4_LABEL, T4_DESCR),
    (T5, T5_LABEL, T5_DESCR),
    (T6, T6_LABEL, T6_DESCR),
    (T7, T7_LABEL, T7_DESCR),
    (T8, T8_LABEL, T8_DESCR),
    (T9, T9_LABEL, T9_DESCR),
    (T10, T10_LABEL, T10_DESCR)]
bpy.types.Scene.characterType = bpy.props.EnumProperty(
    items=HUMANOID_TYPES,
    name="Select",
    default="humanoid_humanf01")

def get_data_directory():
    """
    Try to retrieve the directory for this file.
    """
    addon_directory = os.path.dirname(os.path.realpath(__file__))
    data_dir = os.path.join(addon_directory, "data")
    if os.path.isdir(data_dir):
        return data_dir
    else:
        logging.critical("Database not found. Please check your Blender addons directory. It appears you don't have a manuellab data inside it")
        return None


def realtime_update(self, context):
    """
    Update the character while the prop slider moves.
    """
    global the_humanoid
    if the_humanoid.realtime:
        #time1 = time.time()
        obj = the_humanoid.get_object()
        the_humanoid.update_character(category_name = obj.morphingCategory, mode="update_realtime")
        the_humanoid.sync_gui_according_measures()
        #print("realtime_update: {0}".format(time.time()-time1))


def change_units(self, context):
    """
    """
    global the_humanoid
    the_humanoid.sync_gui_according_measures()


def expression_update(self, context):
    """
    Update the character while prop slider moves
    """
    global the_humanoid
    obj = the_humanoid.get_object()
    filepath = os.path.join(
        the_humanoid.data_path,
        the_humanoid.name,
        "expressions",
        "".join([obj.expressions, ".json"]))

    the_humanoid.import_character(filepath, reset_name = "Expression", reset_unassigned=False)
    if obj.realtime_expression_fitting:
        the_humanoid.correct_expressions()

def preset_update(self, context):
    """
    Update the character while prop slider moves
    """
    global the_humanoid
    obj = the_humanoid.get_object()
    filepath = os.path.join(
        the_humanoid.data_path,
        the_humanoid.name,
        "presets",
        "".join([obj.preset, ".json"]))
    the_humanoid.import_character(filepath, mix=obj.mix_characters)

def ethnic_update(self, context):

    global the_humanoid
    obj = the_humanoid.get_object()
    filepath = os.path.join(
        the_humanoid.data_path,
        the_humanoid.name,
        "phenotypes",
        "".join([obj.ethnic, ".json"]))
    the_humanoid.import_character(filepath, mix=obj.mix_characters)


def pose_update(self, context):
    """
    Load pose quaternions
    """
    global the_humanoid
    obj = the_humanoid.get_object()
    filepath = os.path.join(
        the_humanoid.data_path,
        the_humanoid.name,
        "poses",
        "".join([obj.static_pose, ".json"]))
    the_humanoid.load_pose(filepath)


class ConvertToShapekeys(bpy.types.Operator):
    """
    Convert the expression morphings to Blender standard shape keys
    """
    bl_label = 'Apply parameters as Shape Keys'
    bl_idname = 'covert.shapekeys'
    bl_description = 'Finalize, converting the parameters in shapekeys. Warning: after the conversion the character will be no longer modifiable in this script'
    bl_context = 'objectmode'
    bl_options = {'REGISTER', 'INTERNAL'}

    def execute(self, context):
        """
        Fit the expressions to character and then convert them.
        """
        global the_humanoid
        the_humanoid.correct_expressions(correct_all=True)
        the_humanoid.m_engine.convert_all_to_blshapekeys()
        return {'FINISHED'}

class ResetParameters(bpy.types.Operator):
    """
    Reset all morphings.
    """
    bl_label = 'Reset All'
    bl_idname = 'reset.allproperties'
    bl_description = 'Reset all character parameters'
    bl_context = 'objectmode'
    bl_options = {'REGISTER', 'INTERNAL'}

    def execute(self, context):
        global the_humanoid
        the_humanoid.reset_character()
        return {'FINISHED'}


class Reset_category(bpy.types.Operator):
    """
    Reset the parameters for the currently selected category
    """
    bl_label = 'Reset category'
    bl_idname = 'reset.categoryonly'
    bl_description = 'Reset the parameters for the current category'
    bl_context = 'objectmode'
    bl_options = {'REGISTER', 'INTERNAL'}

    def execute(self, context):
        global the_humanoid
        the_humanoid.reset_category()
        return {'FINISHED'}


class CharacterGenerator(bpy.types.Operator):
    """
    Generate a new character using the specified parameters.
    """
    bl_label = 'Generate'
    bl_idname = 'character.generator'
    bl_description = 'Generate a new character according the parameters.'
    bl_context = 'objectmode'
    bl_options = {'REGISTER', 'INTERNAL'}

    def execute(self, context):
        global the_humanoid
        the_humanoid.generate_character()
        return {'FINISHED'}


class ExpCharacter(bpy.types.Operator, ExportHelper):
    """Export parameters for the character"""
    bl_idname = "export.character"
    bl_label = "Export character"
    filename_ext = ".json"
    filter_glob = bpy.props.StringProperty(
        default="*.json",
        options={'HIDDEN'},
        )
    bl_context = 'objectmode'

    def execute(self, context):
        global the_humanoid
        the_humanoid.export_character(self.filepath)
        return {'FINISHED'}

class ExpMeasures(bpy.types.Operator, ExportHelper):
    """Export parameters for the character"""
    bl_idname = "export.measures"
    bl_label = "Export measures"
    filename_ext = ".json"
    filter_glob = bpy.props.StringProperty(
        default="*.json",
        options={'HIDDEN'},
        )
    bl_context = 'objectmode'

    def execute(self, context):
        global the_humanoid
        the_humanoid.export_measures(self.filepath)
        return {'FINISHED'}


class ImpCharacter(bpy.types.Operator, ImportHelper):
    """
    Import parameters for the character
    """
    bl_idname = "import.character"
    bl_label = "Import character"
    filename_ext = ".json"
    filter_glob = bpy.props.StringProperty(
        default="*.json",
        options={'HIDDEN'},
        )
    bl_context = 'objectmode'

    def execute(self, context):
        global the_humanoid
        the_humanoid.import_character(self.filepath)
        return {'FINISHED'}

class ImpMeasures(bpy.types.Operator, ImportHelper):
    """
    Import parameters for the character
    """
    bl_idname = "import.measures"
    bl_label = "Import measures"
    filename_ext = ".json"
    filter_glob = bpy.props.StringProperty(
        default="*.json",
        options={'HIDDEN'},
        )
    bl_context = 'objectmode'

    def execute(self, context):
        global the_humanoid
        the_humanoid.import_measures(self.filepath)
        return {'FINISHED'}

class SaveProxy(bpy.types.Operator):
    """
    Save the proxy file in an user temp directory
    """

    bl_label = 'Store Proxy'
    bl_idname = 'proxy.save'
    bl_description = 'Register proxy for auto fitting'
    bl_context = 'objectmode'
    bl_options = {'REGISTER', 'INTERNAL'}

    def execute(self, context):
        global the_humanoid
        the_humanoid.save_proxy()
        return {'FINISHED'}

class LoadProxy(bpy.types.Operator):
    """
    For each proxy in the scene, load the data and then fit it.
    """

    bl_label = 'Fit Proxy'
    bl_idname = 'proxy.load'
    bl_description = 'Fit all registered proxies to the character'
    bl_context = 'objectmode'
    bl_options = {'REGISTER', 'INTERNAL'}

    def execute(self, context):
        global the_humanoid
        the_humanoid.load_proxy()
        return {'FINISHED'}


class ApplyMeasures(bpy.types.Operator):
    """
    Fit the character to the measures
    """

    bl_label = 'Auto calculate'
    bl_idname = 'measures.apply'
    bl_description = 'Fit the character to the measures'
    bl_context = 'objectmode'
    bl_options = {'REGISTER', 'INTERNAL'}

    def execute(self, context):
        global the_humanoid
        the_humanoid.automodelling(use_measures_from_GUI=True)
        return {'FINISHED'}

class AutoModelling(bpy.types.Operator):
    """
    Fit the character to the measures
    """

    bl_label = 'Auto modelling'
    bl_idname = 'auto.modelling'
    bl_description = 'Auto modelling'
    bl_context = 'objectmode'
    bl_options = {'REGISTER', 'INTERNAL'}

    def execute(self, context):
        global the_humanoid
        the_humanoid.automodelling(use_measures_from_current_obj=True)
        return {'FINISHED'}

class AutoModellingMix(bpy.types.Operator):
    """
    Fit the character to the measures
    """

    bl_label = 'Smooth'
    bl_idname = 'auto.modellingmix'
    bl_description = 'Auto modelling2'
    bl_context = 'objectmode'
    bl_options = {'REGISTER', 'INTERNAL'}

    def execute(self, context):
        global the_humanoid
        the_humanoid.automodelling(use_measures_from_current_obj=True, mix = True)
        return {'FINISHED'}

class ResetPose(bpy.types.Operator):
    """
    For each proxy in the scene, load the data and then fit it.
    """

    bl_label = 'Reset pose'
    bl_idname = 'pose.reset'
    bl_description = 'Reset the character pose'
    bl_context = 'objectmode'
    bl_options = {'REGISTER', 'INTERNAL'}

    def execute(self, context):
        global the_humanoid
        the_humanoid.reset_pose()
        return {'FINISHED'}



class InitCharacter(bpy.types.Operator):
    bl_idname = "init.character"
    bl_label = "Init character"
    bl_description = 'Create the character selected above'
    bl_context = 'objectmode'
    bl_options = {'REGISTER', 'INTERNAL'}

    def init_character(self):
        """
        Append the base character from the blend library.
        """

        global the_humanoid
        logging.info("Starting character lab...")
        scn = bpy.context.scene
        data_path = get_data_directory()
        library_name = "humanoid_library.blend"
        if data_path:
            lib_path = os.path.join(data_path, library_name)
            obj = humanoid.get_character_object()
            if not obj:
                try:
                    with bpy.data.libraries.load(lib_path) as (data_from, data_to):
                        data_to.objects = [scn.characterType]

                except:
                    self.report({'ERROR'}, "{0} not found".format(lib_path))
                    logging.critical("{0} not found".format(lib_path))
                    return None
                if scn.characterType in bpy.data.objects:
                    if not bpy.data.objects[scn.characterType].name in scn.object_bases:
                        scn.objects.link(bpy.data.objects[scn.characterType])
                        scn.objects.link(bpy.data.objects["_".join(["skeleton", scn.characterType])])
                        bpy.data.objects[scn.characterType].parent = bpy.data.objects["_".join(["skeleton", scn.characterType])]
                        the_humanoid = humanoid.Humanoid(
                            realtime_update,
                            expression_update,
                            preset_update,
                            pose_update,
                            ethnic_update,
                            change_units,
                            data_path,
                            bpy.data.objects[scn.characterType],
                            bl_info["version"])
                        the_humanoid.sync_gui_according_measures()
                    else:
                        logging.warning("The object {0} is already linked to the scene".format(bpy.data.objects[scn.characterType].name))
                        return None

                else:
                    self.report({'ERROR'}, "Init failed. Check the log file: {0}".format(log_path))
                    logging.critical("{0} not found in library {1}".format(scn.characterType, library_name))
                    return None
            else:
                the_humanoid = humanoid.Humanoid(
                    realtime_update,
                    expression_update,
                    preset_update,
                    pose_update,
                    ethnic_update,
                    change_units,
                    data_path,
                    obj,
                    bl_info["version"])
                the_humanoid.sync_morphdata_to_all_obj_props()
        else:
            self.report({'ERROR'}, "Init failed. Check the log file: {0}".format(log_path))
            return None
        if not the_humanoid:
            self.report({'ERROR'}, "Init failed. Check the log file: {0}".format(log_path))

    def execute(self, context):
        self.init_character()
        return {'FINISHED'}


the_humanoid = None
class ManuelLabPanel(bpy.types.Panel):

    bl_label = "ManuelbastioniLAB {0}.{1}.{2}".format(bl_info["version"][0],bl_info["version"][1],bl_info["version"][2])
    bl_idname = "OBJECT_PT_characters01"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context = 'objectmode'
    bl_category = "ManuelLab"


    def draw(self, context):

        global the_humanoid
        scn = bpy.context.scene

        gui_mode = humanoid.check_humanoid(the_humanoid)
        if gui_mode == (True, False, False):
            box = self.layout.box()
            box.alert = True
            box.label("I detected an existent", icon="INFO")
            box.label("humanoid mesh in the ")
            box.label("current scene.")
            box.label("I'll try to init it.")
            box.operator("init.character")
        if gui_mode == (False, True, False):
            box = self.layout.box()
            box.prop(scn, 'characterType')
            box.operator("init.character")
        if gui_mode == (False, False, True):
            obj = the_humanoid.get_object()
            box = self.layout.box()
            box.label("MAIN")
            box.prop(obj, "preset")
            box.prop(obj, "ethnic")
            box.prop(obj, 'mix_characters')
            box.operator("reset.allproperties", icon="RECOVER_AUTO")

            box = self.layout.box()
            box.prop(obj, 'show_expressions')
            if obj.show_expressions:
                box.label("EXPRESSIONS")
                box.prop(obj, "expressions")
                box.prop(obj, 'realtime_expression_fitting')

            box = self.layout.box()
            box.prop(obj, 'random_generator')
            if obj.random_generator:
                box.label("RANDOM GENERATOR")
                box.prop(obj, "random_engine")
                box.label("Preserve:")
                prop_id = 0
                while prop_id < len(the_humanoid.generator_bool_props)-1:
                    row = box.row()
                    row.prop(obj, the_humanoid.generator_bool_props[prop_id])
                    row.prop(obj, the_humanoid.generator_bool_props[prop_id+1])
                    prop_id += 2

                if obj.set_tone_and_mass:
                    for prop in the_humanoid.generator_float_props:
                        box.prop(obj, prop)
                box.operator("character.generator", icon="FILE_REFRESH")

            box = self.layout.box()
            box.prop(obj, 'show_poses')
            if obj.show_poses:
                box.label("POSE")
                box.prop(obj, "static_pose")
                box.operator("pose.reset", icon='ARMATURE_DATA')

            box = self.layout.box()
            box.prop(obj, 'show_parameters')
            if obj.show_parameters:

                if the_humanoid.exist_measure_database():
                    split = box.split()
                    column1 = split.column()
                    column2 = split.column()
                    column2.label("DIMENSIONS")
                    column2.prop(obj, 'use_inch')
                    column2.prop(obj, 'measure_filter')
                    column2.operator("measures.apply")
                    m_unit = "cm"
                    if obj.use_inch:
                        m_unit = "Inches"
                    column2.label("Height: {0} {1}".format(round(getattr(obj, "body_height_Z", 0),3),m_unit))
                    for measure in sorted(the_humanoid.measures.keys()):                        
                        if measure != "body_height_Z":
                            if hasattr(obj, measure):
                                if obj.measure_filter in measure:
                                    column2.prop(obj, measure)
                else:                                        
                    column1 = box.column()                    
                    column1.label("Measure data not present", icon='INFO')


                the_humanoid.realtime = True
                column1.label("PARAMETERS")
                column1.operator("reset.allproperties", icon="RECOVER_AUTO")
                column1.operator("reset.categoryonly")
                column1.prop(obj, "morphingCategory")
                for prop in the_humanoid.categories[obj.morphingCategory].get_all_properties():
                    if hasattr(obj, prop):
                        column1.prop(obj, prop)

            box = self.layout.box()
            if the_humanoid.exist_measure_database():
                box.enabled = True
            else:
                box.enabled = False
            box.prop(obj, 'show_automodelling')
            if obj.show_automodelling:
                box.label("AUTOMODELLING")
                box.operator("auto.modelling")
                box.operator("auto.modellingmix")
            box = self.layout.box()
            if the_humanoid.is_there_proxies():
                box.enabled = True
            else:
                box.enabled = False
            box.prop(obj, 'show_proxies')
            if obj.show_proxies:
                box.label("PROXIES")
                box.operator("proxy.save", icon="MOD_CLOTH")
                box.operator("proxy.load", icon="MOD_CLOTH")
            box = self.layout.box()
            box.prop(obj, 'show_files')
            if obj.show_files:
                box.label("LOAD/SAVE")
                box.label("Character data (.json)")
                box.prop(obj, 'export_proportions')
                box.operator("export.character", icon='EXPORT')
                box.operator("import.character", icon='IMPORT')
                if the_humanoid.exist_measure_database():
                    box.label("Character measures (.json)")
                    box.operator("export.measures", icon='EXPORT')
                    box.operator("import.measures", icon='IMPORT')
                else:
                    box.label("Measure data not present", icon='INFO')

            box = self.layout.box()
            box.prop(obj, 'finalize_character')
            if obj.finalize_character:

                box.label("FINALIZE")
                box.operator("covert.shapekeys", icon='FREEZE')

            box = self.layout.box()
            box.prop(obj, 'utilities')
            if obj.utilities:
                box.label("UTILITIES")
                if "Subsurf" in obj.modifiers:
                    row = box.row()
                    row.label("Enable subdivision", icon = "MOD_SUBSURF")
                    row.prop(obj.modifiers['Subsurf'], "show_viewport")
                    #box.prop(obj.modifiers['Subsurf'], "levels")

def register():
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()





