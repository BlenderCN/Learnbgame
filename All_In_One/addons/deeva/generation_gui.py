# Deeva - Character Generation Platform
# Copyright (C) 2018 Fabrizio Nunnari
#
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


import bpy
from bpy.path import abspath
from bpy_extras.io_utils import ExportHelper

from deeva.generation import AttributesTable
from deeva.generation import IndividualsTable
from deeva.generation_tools import export_mblab_attributes, create_mblab_chars_json_dir

bl_info = {
    "name": "Deeva - Character Generator",
    "description": "Deeva tools to manage attributes and generate random characters.",
    "author": "Fabrizio Nunnari",
    "version": (0, 10),
    "blender": (2, 79, 0),
    "location": "Toolbox > ManuelBastioniLAB > Generation",
    "category": "Characters",
    }


#
# GUIs
#
class ToolsPanel(bpy.types.Panel):
    # bl_idname = "OBJECT_PT_GenerationPanel"
    bl_label = bl_info["name"] + " Tools (v" + (".".join([str(x) for x in bl_info["version"]])) + ")"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context = 'objectmode'
    bl_category = "Deeva"

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        box = row.box()
        box.operator(ExportMBLabAttributes.bl_idname)

        row = layout.row()
        box = row.box()
        box.prop(context.scene, "deeva_generation_attributes_file")
        box.prop(context.scene, "deeva_generation_individuals_file")
        box.prop(context.scene, "deeva_conversion_outdir")
        box.operator(ConvertIndividualsToMBLabJSon.bl_idname)
        box.operator(CreateExtremesJSON.bl_idname)


class GenerationPanel(bpy.types.Panel):
    # bl_idname = "OBJECT_PT_GenerationPanel"
    bl_label = bl_info["name"] + " (v" + (".".join([str(x) for x in bl_info["version"]])) + ")"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context = 'objectmode'
    bl_category = "Deeva"

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        box = row.box()
        box.prop(context.scene, "deeva_generation_project_dir")
        box.operator(ScanProjectDir.bl_idname)

        row = layout.row()
        box = row.box()
        box.prop(context.scene, "deeva_generation_traits_file")
        box.prop(context.scene, "deeva_generation_attributes_file")
        box.prop(context.scene, "deeva_generation_individuals_file")
        box.prop(context.scene, "deeva_generation_ratevotes_file")

        row = layout.row()
        box = row.box()
        box.operator(ComputeGenerationModel.bl_idname)
        box.label("TODO -- list all the generated files/properties.")

        row = layout.row()
        box = row.box()
        box.label("TODO -- Button: load model.")
        box.label("TODO -- grid: list the traits and select their values")
        box.label("TODO -- operator: reset/center traits")


#
# INDIVIDUALS MANAGEMENT
#
class ConvertIndividualsToMBLabJSon(bpy.types.Operator):
    """Generates a set of random individuals."""
    bl_idname = "deeva.convert_individuals"
    bl_label = "Convert Individuals to MBLAB/JSON dir"
    bl_options = {'REGISTER', 'UNDO'}

    # ExportHelper mixin class uses this
    filename_ext = ""
    use_filter_folder = True

    def execute(self, context):
        s = context.scene

        individuals_table = IndividualsTable(individuals_filename=abspath(s.deeva_generation_individuals_file))
        attrib_table = AttributesTable(table_filename=abspath(s.deeva_generation_attributes_file))

        create_mblab_chars_json_dir(individuals=individuals_table,
                                    attributes=attrib_table,
                                    dirpath=abspath(s.deeva_conversion_outdir))

        return {'FINISHED'}


#
# ATTRIBUTES EXPORT
#
class ExportMBLabAttributes(bpy.types.Operator, ExportHelper):
    """Export the attributes used by MBLab to control the shape of the characters.
    The exported csv can be used to populate the variables table in the web platform."""
    bl_idname = "deeva.export_attributes"
    bl_label = "Export MBLab Attributes"
    bl_options = {'REGISTER', 'UNDO'}

    # ExportHelper mixin class uses this
    filename_ext = ".csv"

    @classmethod
    def poll(cls, context):
        if context.active_object is not None:
            if context.active_object.type == 'MESH':
                return True

        return False

    def execute(self, context):
        mesh_obj = context.active_object
        print("Saving to {}".format(self.filepath))

        export_mblab_attributes(mesh_obj=mesh_obj, outfilepath=self.filepath)

        return {'FINISHED'}


#
# Rendering of the extremes
#
class CreateExtremesJSON(bpy.types.Operator):

    """Create render for all chracters"""
    bl_idname = "mbastauto.create_extremes_json"
    bl_label = "Save extremes' JSON"
    bl_options = {'REGISTER'}

    # Used to select the directory output.
    # See: https://blender.stackexchange.com/questions/14738/use-filemanager-to-select-directory-instead-of-file/126596#126596
    directory = bpy.props.StringProperty(
        name="Outdir Path",
        description="Path used to save the JSONs of all extremes"
        )

    @classmethod
    def poll(cls, context):
        if context.active_object is not None:
            if context.active_object.type == 'MESH':
                return True

        return False

    def execute(self, context):
        import json
        import os

        # https://docs.blender.org/api/blender_python_api_2_71_release/bpy.types.FileSelectParams.html
        print("Saving Extremes to dir ... '" + self.directory + "'")

        scene = context.scene

        attrib_table = AttributesTable(table_filename=abspath(scene.deeva_generation_attributes_file))

        json_template = {
            "metaproperties": {},
            "manuellab_vers": [1, 6, 1],
            "materialproperties": {},
            "structural": {}  # this is the field that will contain the values of the physical attributes.
        }

        #
        # Render the default character (as reference)
        structural = {}
        for attr_id in attrib_table.attribute_ids():
            attr_name = attrib_table.attribute_name(attr_id=attr_id)
            structural[attr_name] = 0.5
        json_template["structural"] = structural
        with open(os.path.join(self.directory, 'default.json'), "w") as fp:
            json.dump(obj=json_template, fp=fp, indent=2)

        #
        # Now, structural has all items at 0.0
        assert len(structural) == len(attrib_table.attribute_ids())
        for k in structural.keys():
            assert structural[k] == 0.5

        #
        # Render each feature min/max
        for attr_id in attrib_table.attribute_ids():
            attr_name = attrib_table.attribute_name(attr_id=attr_id)
            assert structural[attr_name] == 0.5

            attr_min, attr_max = attrib_table.attribute_range(attr_id=attr_id)
            structural[attr_name] = attr_min
            with open(os.path.join(self.directory, attr_name+'_min.json'), "w") as fp:
                json.dump(obj=json_template, fp=fp, indent=2)
            structural[attr_name] = attr_max
            with open(os.path.join(self.directory, attr_name+'_max.json'), "w") as fp:
                json.dump(obj=json_template, fp=fp, indent=2)
            structural[attr_name] = 0.5

        #
        # Render all features at min
        structural = {}
        for attr_id in attrib_table.attribute_ids():
            attr_name = attrib_table.attribute_name(attr_id=attr_id)
            attr_min, attr_max = attrib_table.attribute_range(attr_id=attr_id)
            structural[attr_name] = attr_min
        json_template["structural"] = structural
        with open(os.path.join(self.directory, 'All_min.json'), "w") as fp:
            json.dump(obj=json_template, fp=fp, indent=2)

        #
        # Render all features at max
        structural = {}
        for attr_id in attrib_table.attribute_ids():
            attr_name = attrib_table.attribute_name(attr_id=attr_id)
            attr_min, attr_max = attrib_table.attribute_range(attr_id=attr_id)
            structural[attr_name] = attr_max
        json_template["structural"] = structural
        with open(os.path.join(self.directory, 'All_max.json'), "w") as fp:
            json.dump(obj=json_template, fp=fp, indent=2)

        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        # Open browser, take reference to 'self' read the path to selected
        # dir, put path in predetermined data structures
        return {'RUNNING_MODAL'}
        # Tells Blender to hang on for the slow user input


#
# SCAN The project dir in order to find all the needed tables.
#
class ScanProjectDir(bpy.types.Operator):
    """Scan the project dir and locate all the files needed to compute the models and run the generation"""
    bl_idname = "deeva.scan_project_dir"
    bl_label = "Scan Project Dir"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        import os
        import re

        #
        # Look for the tables
        prj_dir = context.scene.deeva_generation_project_dir
        if not os.path.exists(prj_dir):
            raise Exception("Project dir '{}' doesn't exist".format(prj_dir))

        tables_dir = os.path.join(prj_dir, "tables")
        if not os.path.exists(tables_dir):
            raise Exception("Tables dir '{}' doesn't exist".format(tables_dir))

        table_files = os.listdir(tables_dir)

        for table_file in table_files:

            # e.g.: 'GEN-5-Anke Thesis 100 Indiv-INDIVIDUALS'
            if re.match("^GEN-.+-INDIVIDUALS.csv$", table_file):
                context.scene.deeva_generation_individuals_file = os.path.join(tables_dir, table_file)

            # e.g.: VS-5-Face 9 variables-ATTRIBUTES.csv
            elif re.match("^VS-.+-ATTRIBUTES.csv$", table_file):
                context.scene.deeva_generation_attributes_file = os.path.join(tables_dir, table_file)

            # e.g.: VS-6-Anke's Thesis 5 Traits-TRAITS.csv
            elif re.match("^VS-.+-TRAITS.csv$", table_file):
                context.scene.deeva_generation_traits_file = os.path.join(tables_dir, table_file)

            # e.g.: WIZ-2-AnkeThesisWizard-RATEVOTES.csv
            elif re.match("^WIZ-.+-RATEVOTES.csv$", table_file):
                context.scene.deeva_generation_ratevotes_file = os.path.join(tables_dir, table_file)

        return {'FINISHED'}


#
# Compute Model
class ComputeGenerationModel(bpy.types.Operator):
    """Analyses the votes and computes the linear model needed for the generation."""
    bl_idname = "deeva.compute_generation_model"
    bl_label = "Compute Generation Model"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        self.report({'ERROR'}, "Not implemented, yet.")
        return {'CANCELLED'}


#
# Register & Unregister ###
#
def register():
    bpy.types.Scene.deeva_generation_individuals_file = bpy.props.StringProperty(
        name="generation_individuals",
        default="",
        description="The CSV with the individuals table, as downloaded from the web platform, ending in '-INDIVIDUALS.csv'.",
        subtype='FILE_PATH'
    )

    bpy.types.Scene.deeva_conversion_outdir = bpy.props.StringProperty(
        name="conversion_outdir",
        default="",
        description="The directory where to put the MBLab json files.",
        subtype='DIR_PATH'
    )

    bpy.types.Scene.deeva_generation_attributes_file = bpy.props.StringProperty(
        name="generation_attributes",
        default="",
        description="The CSV attributes table, as downloaded from the web platform, ending in '-ATTRIBTUES.csv'.",
        subtype='FILE_PATH'
    )

    bpy.types.Scene.deeva_generation_traits_file = bpy.props.StringProperty(
        name="generation_traits",
        default="",
        description="The CSV traits table, as downloaded from the web platform, ending in '-TRAITS.csv'.",
        subtype='FILE_PATH'
    )

    bpy.types.Scene.deeva_generation_ratevotes_file = bpy.props.StringProperty(
        name="generation_ratevotes",
        default="",
        description="The CSV traits table, as downloaded from the web platform, ending in '-RATEVOTES.csv'.",
        subtype='FILE_PATH'
    )

    bpy.types.Scene.deeva_generation_project_dir = bpy.props.StringProperty(
        name="generation_project_dir",
        default="",
        description="The directory where the 'tables' dir is located and all the models will be written.",
        subtype='DIR_PATH'
    )

    bpy.utils.register_class(ExportMBLabAttributes)
    bpy.utils.register_class(ToolsPanel)
    bpy.utils.register_class(GenerationPanel)
    bpy.utils.register_class(ConvertIndividualsToMBLabJSon)
    bpy.utils.register_class(CreateExtremesJSON)
    bpy.utils.register_class(ScanProjectDir)
    bpy.utils.register_class(ComputeGenerationModel)


def unregister():
    bpy.utils.unregister_class(ExportMBLabAttributes)
    bpy.utils.unregister_class(ToolsPanel)
    bpy.utils.unregister_class(GenerationPanel)
    bpy.utils.unregister_class(ConvertIndividualsToMBLabJSon)
    bpy.utils.unregister_class(CreateExtremesJSON)
    bpy.utils.unregister_class(ScanProjectDir)
    bpy.utils.unregister_class(ComputeGenerationModel)

    del bpy.types.Scene.deeva_generation_individuals_file
    del bpy.types.Scene.deeva_conversion_outdir
    del bpy.types.Scene.deeva_generation_attributes_file
    del bpy.types.Scene.deeva_generation_traits_file
    del bpy.types.Scene.deeva_generation_ratevotes_file
    del bpy.types.Scene.deeva_generation_project_dir


#
# Invoke register if started from editor
if __name__ == "__main__":
    register()
