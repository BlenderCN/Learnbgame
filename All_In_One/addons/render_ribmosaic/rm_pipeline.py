# #############################################################################
# AUTHOR BLOCK:
# #############################################################################
#
# RIB Mosaic RenderMan(R) IDE, see <http://sourceforge.net/projects/ribmosaic>
# by Eric Nathen Back aka WHiTeRaBBiT, 01-24-2010
# This script is protected by the GPL: Gnu Public License
# GPL - http://www.gnu.org/copyleft/gpl.html
#
# #############################################################################
# GPL LICENSE BLOCK:
# #############################################################################
#
# Script Copyright (C) Eric Nathen Back
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
#
# #############################################################################
# COPYRIGHT BLOCK:
# #############################################################################
#
# The RenderMan(R) Interface Procedures and Protocol are:
# Copyright 1988, 1989, 2000, 2005 Pixar
# All Rights Reserved
# RenderMan(R) is a registered trademark of Pixar
#
# #############################################################################
# COMMENT BLOCK:
# #############################################################################
#
# Pipeline management module providing pipeline creation, destruction, loading
# as well as XML element/attributes read/write and panel/slmeta generation.
#
# This script is PEP 8 compliant
#
# Search TODO for incomplete code
# Search FIXME for improper code
# Search XXX for broken code
#
# #############################################################################
# END BLOCKS
# #############################################################################

import os
import sys
import xml.etree.ElementTree as ET
import bpy


# #### Global variables

MODULE = os.path.dirname(__file__).split(os.sep)[-1]
exec("from " + MODULE + " import rm_error")
exec("from " + MODULE + " import rm_context")
exec("import " + MODULE + " as rm")

# if DEBUG_PRINT set true then each method will print
# its method name and important vars to console io
DEBUG_PRINT = False

# #############################################################################
# PIPELINE MANAGER CLASS
# #############################################################################

# #### Global object responsible for managing XML pipeline data


class PipelineManager():
    """
    The pipeline manager is responsible for loading and parsing pipelines into
    an XML tree. It provides methods for returning lists of items for various
    areas of the XML. It provides methods for parsing export ready RIB with all
    scripts and paths resolved. It provides a data structure to the UI for
    drawing all pipeline panels. It also has methods for compiling shader
    info data and generating shader panels.
    """

    # #### Public attributes

    revisions = 0  # Track any changes to pipeline tree

    # #### Private attributes

    _pipeline_tree = None  # XML tree containing all pipelines
    _pipeline_texts = []  # Track pipeline files in text editor
    _pipeline_addon = []  # Track addon pipelines
    _pipeline_panels = {}  # Track pipeline panel classes and properties

    # Error messsages
    _error_con = ", check console for details"
    _error_load = "Failed to load XML" + _error_con
    _error_unload = "Failed to unload XML" + _error_con
    _error_register = "Failed to register pipeline" + _error_con
    _error_unregister = "Failed to unregister pipeline" + _error_con

    # Collection property types
    _category_windows = {'shader_panels': ['WORLD', 'OBJECT', 'CAMERA',
                                          'CURVE', 'SURFACE', 'LAMP',
                                          'MESH', 'META', 'MATERIAL'],
                         'utility_panels': ['RENDER', 'SCENE', 'WORLD',
                                          'OBJECT', 'CURVE', 'SURFACE',
                                          'LAMP', 'CAMERA', 'MESH',
                                          'META', 'MATERIAL', 'PARTICLE'],
                         'command_panels': ['SCENE', 'TEXTURE']}

    # Description of the pipeline elements. Common keys are as follows:
    # comment = comments on element or attribute
    # text = element's text (between begin end tags)
    # tail = element's ending text
    # method = how values are applied in UI:
    #          SET replaces current value
    #          ADD value as comma separated list
    #          PATH uses file manager to replace current path
    # options = options/defaults, when list > 1 used as an enumerator
    # default = index in options to use as default value
    # attributes = attributes defined in element
    # sub_elements = list of other element keys that are sub elements
    # user_elements = list of other element keys that can be created by user
    _pipeline_elements = {
        # Root element
        'pipeline': {
            'comment': "Contains all elements of pipeline data,\n"
                      "this element's text is display in help dialog\n"
                      "(text's leading and trailing whitespace stripped)",
            'text': "\n\n",
            'tail': None,
            'sub_elements': [
                'python_scripts',
                'shader_sources',
                'shader_panels',
                'utility_panels',
                'command_panels'],
            'user_elements': [],
            'attributes': {
                'build': {
                    'method': "SET",
                    'options': ["True", "False"],
                    'default': 0,
                    'comment': "Generate slmeta files when building\n"
                              "pipeline's shader library"},
                'compile': {
                    'method': "SET",
                    'options': ["True", "False"],
                    'default': 0,
                    'comment': "Compile shader sources when building\n"
                              "pipeline's shader library"},
                'dependecies': {
                    'method': "ADD",
                    'options': [""],
                    'default': 0,
                    'comment': "List of other required pipelines,\n"
                              "if not present a warning is issued\n"
                              "(comma separated list)"},
                'enabled': {
                    'method': "SET",
                    'options': ["True", "False"],
                    'default': 0,
                    'comment': "Enable or disable pipeline in system,\n"
                              "(when disabled all panels and RIB ignored)"},
                'filepath': {
                    'method': "SET",
                    'options': [""],
                    'default': 0,
                    'comment': "Internal use only (tracks text datablock"
                     " name)"},
                'filter': {
                    'method': "ADD",
                    'options': [""],
                    'default': 0,
                    'comment': "Strings for render pass panel filtering\n"
                              "(comma separated list of filter names)"},
                'library': {
                    'method': "PATH",
                    'options': [""],
                    'default': 0,
                    'comment': "Filepath to folder containing RenderMan"
                              " shaders\n"
                              "Once specified pipeline maintains all shaders\n"
                              "in library and panels can be added and"
                              " updated"},
                'version': {
                    'method': "SET",
                    'options': [""],
                    'default': 0,
                    'comment': "RIB Mosaic version the pipeline was created}"
                              " with,\n"
                              "a warning is issued when run on a newer"
                              " version"}}},
        # Python script elements
        'python_scripts': {
            'comment': "Contains elements defining Python scripts\n"
                      "(usually executed by links however can also just"
                      " be text)",
            'text': "\n",
            'tail': "\n\n",
            'sub_elements': [],
            'user_elements': [
                'python_script'],
            'attributes': {}},
        'python_script': {
            'comment': "Element's text used as Python code for link"
                       " execution\n"
                       "(text's leading and trailing whitespace stripped)",
            'text': "\n",
            'tail': "\n",
            'sub_elements': [],
            'user_elements': [],
            'attributes': {
                'description': {
                    'method': "SET",
                    'options': [""],
                    'default': 0,
                    'comment': "Description about element's usage"
                              " (used in UI)"},
                'filepath': {
                    'method': "FILE",
                    'options': [""],
                    'default': 0,
                    'comment': "If set, the external file to update/save"
                               " to"}}},
        # Shader source elements
        'shader_sources': {
            'comment': "Contains elements defining shader sources\n"
                      "(automatically exported and compiled)",
            'text': "\n",
            'tail': "\n\n",
            'sub_elements': [],
            'user_elements': [
                'shader_source'],
            'attributes': {}},
        'shader_source': {
            'comment': "Element's text exported and compiled as shader"
                      " RSL code\n"
                      "(text's leading and trailing whitespace stripped)",
            'text': "\n",
            'tail': "\n",
            'sub_elements': [],
            'user_elements': [],
            'attributes': {
                'description': {
                    'method': "SET",
                    'options': [""],
                    'default': 0,
                    'comment': "Description about element's usage"
                              "(used in UI)"},
                'filepath': {
                    'method': "FILE",
                    'options': [""],
                    'default': 0,
                    'comment': "If set, the external file to update/save"
                    " to"}}},
        # Shader panel elements
        'shader_panels': {
            'comment': "Contains elements defining shader panels",
            'text': "\n",
            'tail': "\n\n",
            'sub_elements': [],
            'user_elements': [
                'shader_panel'],
            'attributes': {
                'filter': {
                    'method': "ADD",
                    'options': ["SHADER"],
                    'default': 0,
                    'comment': "Strings for render pass panel filtering\n"
                              "(comma separated list of filter names)"}}},
        'shader_panel': {
            'comment': "UI panel representing shader RIB code",
            'text': "\n",
            'tail': "\n",
            'sub_elements': [
                'rib',
                'regexes',
                'properties',
                'layout'],
            'user_elements': [],
            'attributes': {
                'register': {
                    'method': "SET",
                    'options': ["True", "False"],
                    'default': 0,
                    'comment': "Automatically register panel with Blender\n"
                              "(leave disabled for rarely used panels)"},
                'enabled': {
                    'method': "SET",
                    'options': ["True", "False"],
                    'default': 0,
                    'comment': "Initially enable panel on all datablocks"},
                'duplicate': {
                    'method': "SET",
                    'options': ["True", "False"],
                    'default': 0,
                    'comment': "Allow panel to be duplicated by user"},
                'delete': {
                    'method': "SET",
                    'options': ["True", "False"],
                    'default': 0,
                    'comment': "Allow panel to be deleted by user"},
                'type': {
                    'method': "SET",
                    'options': ["SURFACE",
                               "DISPLACEMENT",
                               "LIGHT",
                               "VOLUME",
                               "IMAGER"],
                    'default': 0,
                    'comment': "RSL shader type category"},
                'library': {
                    'method': "PATH",
                    'options': [""],
                    'default': 0,
                    'comment': "RIB safe path to compiled shader,\n"
                              "prepended to shader name in RIB call"},
                'slmeta': {
                    'method': "PATH",
                    'options': [""],
                    'default': 0,
                    'comment': "Filepath to slmeta panel was generated from,\n"
                              "used to update panel to external changes"},
                'description': {
                    'method': "SET",
                    'options': [""],
                    'default': 0,
                    'comment': "Text shown in the panel's info dialog,\n"
                              "(use \\n for multiple lines)"},
                'filter': {
                    'method': "ADD",
                    'options': [""],
                    'default': 0,
                    'comment': "Strings for render pass panel filtering\n"
                              "(comma separated list of filter names)"},
                'windows': {
                    'method': "ADD",
                    'options': ["MATERIAL",
                               "WORLD",
                               "OBJECT",
                               "CAMERA",
                               "CURVE",
                               "SURFACE",
                               "MESH",
                               "META",
                               "LAMP"],
                    'default': 0,
                    'comment': "Assign panel to Blender \"Properties\""
                              " windows\n"
                              "(comma separated list of property names)"}}},
        # Utility panel elements
        'utility_panels': {
            'comment': "Contains elements defining utility panels",
            'text': "\n",
            'tail': "\n\n",
            'sub_elements': [],
            'user_elements': [
                'utility_panel'],
            'attributes': {
                'filter': {
                    'method': "ADD",
                    'options': ["UTILITY"],
                    'default': 0,
                    'comment': "Strings for render pass panel filtering\n"
                              "(comma separated list of filter names)"}}},
        'utility_panel': {
            'comment': "UI panel representing RIB code options and attributes",
            'text': "\n",
            'tail': "\n",
            'sub_elements': [],
            'user_elements': [
                'read',
                'begin',
                'end',
                'regexes',
                'properties',
                'layout'],
            'attributes': {
                'register': {
                    'method': "SET",
                    'options': ["True", "False"],
                    'default': 0,
                    'comment': "Automatically register panel with Blender\n"
                              "(leave disabled for rarely used panels)"},
                'enabled': {
                    'method': "SET",
                    'options': ["True", "False"],
                    'default': 0,
                    'comment': "Initially enable panel on all datablocks"},
                'duplicate': {
                    'method': "SET",
                    'options': ["True", "False"],
                    'default': 1,
                    'comment': "Allow panel to be duplicated by user"},
                'delete': {
                    'method': "SET",
                    'options': ["True", "False"],
                    'default': 1,
                    'comment': "Allow panel to be deleted by user"},
                'type': {
                    'method': "SET",
                    'options': ["OPTION",
                               "ATTR",
                               "DISPLAY",
                               "FORMAT"
                               "RIB"],
                    'default': 4,
                    'comment': "Used to sort multiple panels when exporting"},
                'description': {
                    'method': "SET",
                    'options': [""],
                    'default': 0,
                    'comment': "Text shown in the panel's info dialog,\n"
                              "(use \\n for multiple lines)"},
                'filter': {
                    'method': "ADD",
                    'options': [""],
                    'default': 0,
                    'comment': "Strings for render pass panel filtering\n"
                              "(comma separated list of filter names)"},
                'windows': {
                    'method': "ADD",
                    'options': ["RENDER",
                               "SCENE",
                               "WORLD",
                               "OBJECT",
                               "CURVE",
                               "SURFACE",
                               "LAMP",
                               "CAMERA",
                               "MESH",
                               "META",
                               "MATERIAL",
                               "PARTICLE"],
                    'default': 0,
                    'comment': "Assign panel to Blender \"Properties\""
                              " windows\n"
                              "(comma separated list of property names)"}}},
        # Command panel elements
        'command_panels': {
            'comment': "Contains elements defining command panels",
            'text': "\n",
            'tail': "\n",
            'sub_elements': [],
            'user_elements': [
                'command_panel'],
            'attributes': {
                'filter': {
                    'method': "ADD",
                    'options': ["COMMAND"],
                    'default': 0,
                    'comment': "Strings for render pass panel filtering\n"
                              "(comma separated list of filter names)"}}},
        'command_panel': {
            'comment': "UI panel representing command line shell/batch script",
            'text': "\n",
            'tail': "\n",
            'sub_elements': [
                'begin',
                'middle',
                'end',
                'regexes',
                'properties',
                'layout'],
            'user_elements': [],
            'attributes': {
                'register': {
                    'method': "SET",
                    'options': ["True", "False"],
                    'default': 0,
                    'comment': "Automatically register panel with Blender\n"
                              "(leave disabled for rarely used panels)"},
                'enabled': {
                    'method': "SET",
                    'options': ["True", "False"],
                    'default': 0,
                    'comment': "Initially enable panel on all datablocks"},
                'duplicate': {
                    'method': "SET",
                    'options': ["True", "False"],
                    'default': 1,
                    'comment': "Allow panel to be duplicated by user"},
                'delete': {
                    'method': "SET",
                    'options': ["True", "False"],
                    'default': 1,
                    'comment': "Allow panel to be deleted by user"},
                'type': {
                    'method': "SET",
                    'options': ["OPTIMIZE",
                               "COMPILE",
                               "INFO",
                               "RENDER"
                               "POSTRENDER"],
                    'default': 3,
                    'comment': "Determine type and order of command"
                    " execution"},
                'execute': {
                    'method': "SET",
                    'options': ["True", "False"],
                    'default': 0,
                    'comment': "Execute this commend script after export\n"
                              "(TIP: use link here to trigger scripts for"
                              " farms)"},
                'extension': {
                    'method': "SET",
                    'options': [".sh.bat"],
                    'default': 0,
                    'comment': "File extension used for exported command"
                              " script"},
                'description': {
                    'method': "SET",
                    'options': [""],
                    'default': 0,
                    'comment': "Text shown in the panel's info dialog,\n"
                              "(use \\n for multiple lines)"},
                'filter': {
                    'method': "ADD",
                    'options': [""],
                    'default': 0,
                    'comment': "Strings for render pass panel filtering\n"
                              "(comma separated list of filter names)"},
                'windows': {
                    'method': "ADD",
                    'options': ["SCENE",
                               "TEXTURE"],
                    'default': 0,
                    'comment': "Assign panel to Blender \"Properties\""
                              " windows\n"
                              "(comma separated list of property names)"}}},
        # RIB code elements
        'rib': {
            'comment': "Element's text exported as shader's RIB code\n"
                      "(text's leading and trailing whitespace stripped)",
            'text': "\n",
            'tail': "\n",
            'sub_elements': [],
            'user_elements': [],
            'attributes': {
                'target': {
                    'method': "PATH",
                    'options': [""],
                    'default': 0,
                    'comment': "Filepath of file/s to target during export\n"
                              "If null the export path and archive is target\n"
                              "Use the *.ext wildcard to target multiple"
                              " files\n"
                              "\n"
                              "The element's text is exported for each match\n"
                              "Context's .target_path and .target_name"
                              " are set"}}},
        'read': {
            'comment': "Element's text exported with RiReadArchive RIB code,\n"
                      "use to insert or replace code in parent archive\n"
                      "(text's leading and trailing whitespace stripped)",
            'text': "\n",
            'tail': "\n",
            'sub_elements': [],
            'user_elements': [],
            'attributes': {
                'target': {
                    'method': "PATH",
                    'options': [""],
                    'default': 0,
                    'comment': "Filepath of file/s to target during export\n"
                              "If null the export path and archive is target\n"
                              "Use the *.ext wildcard to target multiple}"
                              " files\n"
                              "\n"
                              "The element's text is exported for each match\n"
                              "Context's .target_path and .target_name are"
                              " set"}}},
        'begin': {
            'comment': "Element's text exported at the beginning of archive\n"
                      "(text's leading and trailing whitespace stripped)",
            'text': "\n",
            'tail': "\n",
            'sub_elements': [],
            'user_elements': [],
            'attributes': {
                'target': {
                    'method': "PATH",
                    'options': [""],
                    'default': 0,
                    'comment': "Filepath of file/s to target during export\n"
                              "If null the export path and archive is target\n"
                              "Use the *.ext wildcard to target multiple"
                              " files\n"
                              "\n"
                              "The element's text is exported for each match\n"
                              "Context's .target_path and .target_name"
                              " are set"}}},
        'middle': {
            'comment': "Element's text exported at the middle of archive\n"
                      "(text's leading and trailing whitespace stripped)",
            'text': "\n",
            'tail': "\n",
            'sub_elements': [],
            'user_elements': [],
            'attributes': {
                'target': {
                    'method': "PATH",
                    'options': [""],
                    'default': 0,
                    'comment': "Filepath of file/s to target during export\n"
                              "If null the export path and archive is target\n"
                              "Use the *.ext wildcard to target multiple"
                              " files\n"
                              "\n"
                              "The element's text is exported for each match\n"
                              "Context's .target_path and .target_name are"
                              " set"}}},
        'end': {
            'comment': "Element's text exported at the end of archive\n"
                      "(text's leading and trailing whitespace stripped)",
            'text': "\n",
            'tail': "\n",
            'attributes': {
                'target': {
                    'method': "PATH",
                    'options': [""],
                    'default': 0,
                    'comment': "Filepath of file/s to target during export\n"
                              "If null the export path and archive is target\n"
                              "Use the *.ext wildcard to target multiple"
                              " files\n"
                              "\n"
                              "The element's text is exported for each match\n"
                              "Context's .target_path and .target_name are"
                              " set"}}},
        # Regex panel elements
        'regexes': {
            'comment': "Contains elements defining regular expressions,\n"
                      "which are applied to archive this panel is exported to",
            'text': "\n",
            'tail': "\n",
            'sub_elements': [],
            'user_elements': [
                'regex'],
            'attributes': {
                'target': {
                    'method': "PATH",
                    'options': [""],
                    'default': 0,
                    'comment': "Filepath of file/s to target during export\n"
                              "If null the export path and archive is target\n"
                              "Use the *.ext wildcard to target multiple"
                              " files\n"
                              "\n"
                              "The regexes are applied to each matching"
                              " target"}}},
        'regex': {
            'comment': "String replacement regular expression to apply to"
                      " target",
            'text': None,
            'tail': "\n",
            'sub_elements': [],
            'user_elements': [],
            'attributes': {
                'matches': {
                    'method': "SET",
                    'options': ["0"],
                    'default': 0,
                    'comment': "Number of matches per archive (0 = all"
                              " matches)"},
                'regex': {
                    'method': "SET",
                    'options': [""],
                    'default': 0,
                    'comment': "The regular expression to apply"},
                'replace': {
                    'method': "SET",
                    'options': [""],
                    'default': 0,
                    'comment': "The string to replace matches with"}}},
        # Property panel elements
        'properties': {
            'comment': "Contains elements defining properties used by layout",
            'text': "\n",
            'tail': "\n",
            'sub_elements': [],
            'user_elements': [
                'property'],
            'attributes': {}},
        'property': {
            'comment': "Datablock property to use for layout control",
            'text': None,
            'tail': "\n",
            'sub_elements': [],
            'user_elements': [],
            'attributes': {
                'description': {
                    'method': "SET",
                    'options': [""],
                    'default': 0,
                    'comment': "Text shown for property's control tooltip"},
                'type': {
                    'method': "SET",
                    'options': ["INT",
                               "FLOAT",
                               "STRING",
                               "BOOL",
                               "ENUM",
                               "COLOR",
                               "VECTOR",
                               "POINT",
                               "NORMAL",
                               "HPOINT",
                               "MATRIX"],
                    'default': 0,
                    'comment': "Property types:\n"
                               "FLOAT = floating point\n"
                               "STRING = character string\n"
                               "BOOL = boolean\n"
                               "ENUM = enumerator\n"
                               "COLOR = float (3)rgb color\n"
                               "VECTOR = float (3)\n"
                               "POINT = float (3)\n"
                               "NORMAL =  float (3)\n"
                               "HPOINT = float (4)\n"
                              "(see Blender's API for details)"},
                'default': {
                    'method': "SET",
                    'options': ["",
                               "0",
                               "0.0",
                               "True",
                               "enum1",
                               "(0, 0, 0)",
                               "(0, 0, 0, 0)",
                               "(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,"
                               " 0, 0)"],
                    'default': 0,
                    'comment': "Initial default value of property"},
                'items': {
                    'method': "SET",
                    'options': ["",
                               "[('1', 'enum1', 'desc'), ('2', 'enum2',"
                                " 'desc')]"],
                    'default': 0,
                    'comment': "Enumerator items (see Blender's API)"},
                'size': {
                    'method': "SET",
                    'options': ["",
                               "3",
                               "4",
                               "16"],
                    'default': 0,
                    'comment': "Vector size (for types such as COLOR, HPOINT, "
                              "MATRIX see Blender's API)"},
                'min': {
                    'method': "SET",
                    'options': [""],
                    'default': 0,
                    'comment': "Minimum number (see Blender's API)"},
                'max': {
                    'method': "SET",
                    'options': [""],
                    'default': 0,
                    'comment': "Maximum number (see Blender's API)"},
                'softmin': {
                    'method': "SET",
                    'options': [""],
                    'default': 0,
                    'comment': "Soft minimum number (see Blender's API)"},
                'softmax': {
                    'method': "SET",
                    'options': [""],
                    'default': 0,
                    'comment': "Soft maximum number (see Blender's API)"},
                'maxlen': {
                    'method': "SET",
                    'options': [""],
                    'default': 0,
                    'comment': "Maximum string length (see Blender's API)"},
                'step': {
                    'method': "SET",
                    'options': [""],
                    'default': 0,
                    'comment': "Float step (see Blender's API)"},
                'precision': {
                    'method': "SET",
                    'options': [""],
                    'default': 0,
                    'comment': "Float precision (see Blender's API)"},
                'link': {
                    'method': "SET",
                    'options': [""],
                    'default': 0,
                    'comment': "Blender datapath of property to link to,\n"
                              "use to control this property from another"}}},
        # Layout panel elements
        'layout': {
            'comment': "Contains elements defining containers and widgets\n"
                      "used for building panel layouts",
            'text': "\n",
            'tail': "\n",
            'sub_elements': [],
            'user_elements': [
                'container',
                'widget'],
            'attributes': {}},
        'container': {
            'comment': "Row, column and split layout containers for panel"
                      " widgets",
            'text': "\n",
            'tail': "\n",
            'sub_elements': [],
            'user_elements': [
                'container',
                'widget'],
            'attributes': {
                'type': {
                    'method': "SET",
                    'options': ["ROW",
                               "COLUMN",
                               "SPLIT"],
                    'default': 0,
                    'comment': "Layout container types:\n"
                              "ROW = align layout in a row\n"
                              "COLUMN = align layout in a column\n"
                              "SPLIT = align layout in a split column\n"
                              "(see Blender's API for details)"},
                'box': {
                    'method': "SET",
                    'options': ["True", "False"],
                    'default': 1,
                    'comment': "Draw layout container in box"},
                'align': {
                    'method': "SET",
                    'options': ["True", "False"],
                    'default': 1,
                    'comment': "Align buttons to one another"},
                'enabled': {
                    'method': "SET",
                    'options': ["True", "False"],
                    'default': 0,
                    'comment': "If disabled widgets are greyed and not"
                              " editable"},
                'active': {
                    'method': "SET",
                    'options': ["True", "False"],
                    'default': 0,
                    'comment': "If inactive widgets are greyed and editable"},
                'visible': {
                    'method': "SET",
                    'options': ["True", "False"],
                    'default': 0,
                    'comment': "Don't draw layout if disabled"},
                'percent': {
                    'method': "SET",
                    'options': [""],
                    'default': 0,
                    'comment': "Split layout percentage (see Blender's"
                               " API)"}}},
        'widget': {
            'comment': "Control widget drawn in contained layout",
            'text': None,
            'tail': "\n",
            'sub_elements': [],
            'user_elements': [
                'container',
                'widget'],
            'attributes': {
                'type': {
                    'method': "SET",
                    'options': ["PROP",
                               "PROPSEARCH",
                               "BUTTON",
                               "LINK",
                               "INFO",
                               "FILE",
                               "SEP",
                               "LABEL"],
                    'default': 0,
                    'comment': "Widget type:\n"
                              "SEP = layout separator\n"
                              "LABEL = text label\n"
                              "PROP = property control\n"
                              "PROPSEARCH = collection search\n"
                              "BUTTON = RIB Mosaic button\n"
                              "LINK = RIB Mosaic link dialog\n"
                              "INFO = RIB Mosaic info dialog\n"
                              "FILE = RIB Mosaic file dialog"},
                'prop': {
                    'method': "SET",
                    'options': [""],
                    'default': 0,
                    'comment': "Property element to use for PROP/SEARCH"},
                'text': {
                    'method': "SET",
                    'options': [""],
                    'default': 0,
                    'comment': "Text to display"},
                'icon': {
                    'method': "SET",
                    'options': [""],
                    'default': 0,
                    'comment': "Blender icon or null (see Blender's API)"},
                'expand': {
                    'method': "SET",
                    'options': ["True", "False"],
                    'default': 1,
                    'comment': "Expands enumerators (see Blender's API)"},
                'slider': {
                    'method': "SET",
                    'options': ["True", "False"],
                    'default': 1,
                    'comment': "Draw INT/FLOAT as slider (see Blender's API)"},
                'toggle': {
                    'method': "SET",
                    'options': ["True", "False"],
                    'default': 1,
                    'comment': "Draw BOOL as toggle button (see Blender's"
                              " API)"},
                'trigger': {
                    'method': "SET",
                    'options': [""],
                    'default': 0,
                    'comment': "Usage depends on widget type:\n"
                              "BUTTON = should contain EXEC links to trigger\n"
                              "PROPSEARCH = full data path to collection\n"
                              "INFO = Text to display in dialog\n"
                              "LINK = XML path to property element to set\n"
                              "FILE = datablock property to save path to"}}}}

    # #### Private methods

    def __init__(self):
        """Initializes XML data structure and parser"""

        root = ET.Element("pipelines")
        self._pipeline_tree = ET.ElementTree(root)

    def _new_element(self, xmlpath, ename, etext="", etail="\n",
                     eindex=-1, decorate=True, attribs={}, **extras):
        """Generates a new XML element at specified XML path with given name
        and passing attribs dictionary as element attributes.

        xmlpath = the full XML path to the tree to add element
        ename = name of new element
        etext = text between tags (if null creates with closed tags)
        etail = text after element tags
        eindex = index in parent element to insert (default appends)
        decorate = add tabs to new elements to decorate XML
        attribs = dictionary to use as element attributes
        extras = add to or override attribs

        return = the new element object
        """

        if DEBUG_PRINT:
            print("PipelineManager._new_element()")
            print("xmlpath: " + xmlpath)
            print("ename: " + ename)

        try:
            element = self.get_element(xmlpath)

            children = element.getchildren()
            childlen = len(children)
            attribs = dict(attribs)

            for x in extras:
                attribs[x] = extras[x]

            sub = ET.Element(ename, attribs)
            sub.tail = etail

            # Apply element text
            if etext:
                sub.text = etext

            # Set index to end if appending
            if eindex == -1:
                eindex = childlen

            # Apply XML tab decoration
            if decorate:
                # Set tabs according to XML path depth
                tabs = "\t".join(["" for i in range(xmlpath.count("/") + 2)])

                # Adjust tabs in previous element tail or parent text
                if eindex == 0 or not children:
                    p = element

                    if p.text:
                        p.text = p.text.rstrip("\t") + tabs
                else:
                    p = children[eindex - 1]

                    if p.tail:
                        p.tail = p.tail.rstrip("\t") + tabs

                # Apply tabs to element text
                if etext:
                    sub.text += tabs

                # Add tabs to tail (one less tab if last element)
                if etail:
                    if eindex == childlen:
                        sub.tail += tabs[:-1]
                    else:
                        sub.tail += tabs

            element.insert(eindex, sub)
        except:
            raise rm_error.RibmosaicError(
                "PipelineManager._new_element: Could not create element,"
                " check console", sys.exc_info())

        return sub

    def _load_xml(self, text, description=True):
        """Parses specified text name as XML into the pipeline tree.

        text = the name of the Blender text file
        description = print pipeline description to console
        return = the generated tree element
        """

        if DEBUG_PRINT:
            print("PipelineManager._load_xml()")

        try:
            text_data = bpy.data.texts[text]
            text_xml = text_data.as_string()
            element = ET.XML(text_xml)
             # Update attr with current filename
            element.attrib["filepath"] = text
        except:
            raise rm_error.RibmosaicError(
                "PipelineManager._load_xml: Could not parse XML,"
                " check console", sys.exc_info())

        # Don't load this pipeline if one already has the same element name
        if self._pipeline_tree.findall(element.tag):
            raise rm_error.RibmosaicError("PipelineManager._load_xml: %s"
                                " Pipeline already loaded" % element.tag)

        self._pipeline_tree.getroot().append(element)

        # Print pipeline description silently to console
        if description:
            rm.RibmosaicInfo("PipelineManager._load_xml: " +
                element.tag + " description...")

            for l in self.list_help(element.tag):
                print(l)

        return element

    def _unload_xml(self, xmlpath, decoration=True):
        """Removes specified pipeline element from pipeline tree.

        xmlpath = the full XML path to the element tree to remove
        decoration = adjust any XML decoration around removed element
        return = the text file this pipeline was loaded from
        """

        if DEBUG_PRINT:
            print("PipelineManager._unload_xml()")
            print("xmlpath: " + xmlpath)

        try:
            # Get elements
            element = self.get_element(xmlpath)

            # Get XML path to parent element
            parentpath = "/".join(xmlpath.split("/")[:-1])

            parent = self.get_element(parentpath)

            if DEBUG_PRINT:
                print("parentpath: ", parentpath)
                print("parent: ", parent)
                print("element: ", element)

            # Retrieve filepath attribute for return if exists
            if element is not None and "filepath" in element.attrib:
                filename = element.attrib["filepath"]
            else:
                filename = ""

            # Preform XML decoration cleanup if specified
            if decoration and parent is not None:
                # Set tabs according to XML path depth
                tabs = "\t".join(["" for i in range(xmlpath.count("/") + 1)])

                children = parent.getchildren()
                childlen = len(children)
                index = children.index(element)

                # If only one element then adjust parent text if it exists
                if childlen == 1:
                    if parent.text is not None:
                        parent.text = parent.text.rstrip("\t") + tabs[:-1]
                # If the last element then adjust previous element
                elif index == childlen - 1:
                    p = children[index - 1]
                    if p.tail is not None:
                        p.tail = p.tail.rstrip("\t") + tabs[:-1]

            # Get rid of it
            parent.remove(element)
        except:
            raise rm_error.RibmosaicError(
                "PipelineManager._unload_xml: Could not unload pipeline,"
                " check console", sys.exc_info())

        return filename

    def _write_xml(self, pipeline):
        """Writes pipeline element's XML data to the Blender text file
        specified in its "filepath" attribute.

        pipeline = the element tag name in the tree to write to text
        """

        if DEBUG_PRINT:
            print("PipelineManager._write_xml()")
        try:
            element = self.get_element(pipeline)
            text = element.attrib["filepath"]

            if text in bpy.data.texts:
                text_data = bpy.data.texts[text]
            else:
                text_data = bpy.context.blend_data.texts.new(text)

            xml ='<?xml version=\'1.0\' encoding=\'UTF-8\'?>\n'
            xml += ET.tostring(element, encoding="UTF-8").decode("UTF-8")
            text_data.from_string(xml)

            self.revisions += 1
        except:
            raise rm_error.RibmosaicError(
                "PipelineManager._write_xml: Could not write pipeline to text,"
                " check console", sys.exc_info())

    def _register_panel(self, pipeline, category, panel):
        """Generates Blender panels from pipeline panel elements and populate
        self._pipeline_panels with the resulting classes and properties. Once
        generated the classes are then registered with Blender.

        pipeline = pipeline containing panel elements
        category = sub element containing panel elements
        panel = name of element containing panel layout
        """

        def unfold_layout(xmlpath, prefix="", layout="layout", depth=0):
            """Generates layout code for each layout element in xmlpath
            and appends them to specified layout object. Returns a list
            of strings each containing layout declaration.

            xmlpath = XML path to nested layout elements
            depth = Index number of layout element depth
            prefix = prefix to code string (such as tabs)
            layout = layout object to append elements to
            """

            code = []
            if DEBUG_PRINT:
                print("PipelineManager._register_panel().unfold_layout()")
                print("xmlpath: " + xmlpath)

            # Generate code from sub elements
            for l_name in self.list_elements(xmlpath):
                h = ""  # Layout header
                l = []  # Layout code
                p = []  # Parameter code
                l_var = l_name + str(depth)
                l_path = xmlpath + "/" + l_name
                l_attrs = {'type':  "", 'text': -1, 'box': "", 'align': "",
                           'percent': "",
                           'enabled': "", 'active': "", 'visible': "",
                           'prop': "",
                           'expand': "", 'slider': "", 'toggle': "",
                           'icon': "",
                           'trigger': ""}

                # Get layout attributes
                for a in self.list_attributes(l_path):
                    if a in l_attrs:
                        l_attrs[a] = self.get_attr(ec, l_path, a,
                                                   (a != 'trigger'))

                # Generate code according to type
                l_type = l_attrs['type']

                if l_type == 'ROW' or l_type == 'COLUMN' or l_type == 'SPLIT':
                    if l_attrs['box'] and eval(l_attrs['box']):
                        box = ".box()"
                    else:
                        box = ""

                    if l_type == 'ROW':
                        h = prefix + l_var + " = " + layout + box + ".row("
                    elif l_type == 'COLUMN':
                        h = prefix + l_var + " = " + layout + box + ".column("
                    elif l_type == 'SPLIT':
                        h = prefix + l_var + " = " + layout + box + ".split("

                    if l_attrs['align']:
                        l.append("align=" + l_attrs['align'])
                    if l_attrs['percent']:
                        l.append("percentage=" + l_attrs['percent'])

                    if l_attrs['enabled']:
                        p.append(prefix + l_var + ".enabled=" +
                                 l_attrs['enabled'])
                    if l_attrs['active']:
                        p.append(prefix + l_var + ".active=" +
                                 l_attrs['active'])
                    if l_attrs['visible']:
                        p.append(prefix + "if " + l_attrs['visible'] + ":")
                        t = "\t"
                    else:
                        t = ""

                    # Put it all together
                    code.append(h + ", ".join(l) + ")")
                    code.extend(p)
                    code.extend(unfold_layout(l_path, prefix + t,
                                l_var, depth + 1))
                else:
                    if l_type == 'SEP':
                        h = prefix + layout + ".separator("
                    elif l_type == 'LABEL':
                        h = prefix + layout + ".label("
                    elif l_type == 'BUTTON' or l_type == 'FILE' or \
                         l_type == 'LINK' or l_type == 'INFO':
                        if l_type == 'BUTTON':
                            l.append("'wm.ribmosaic_xml_button'")
                        elif l_type == 'FILE':
                            l.append("'wm.ribmosaic_xml_file'")
                        elif l_type == 'INFO':
                            l.append("'wm.ribmosaic_xml_info'")
                        elif l_type == 'LINK':
                            l.append("'wm.ribmosaic_xml_link'")

                            # Force icon according to link state
                            link_path = ec._resolve_links(l_attrs['trigger'])

                            if link_path and self.get_attr(ec, link_path,
                              "link"):
                                l_attrs['icon'] = 'LINKED'
                            else:
                                l_attrs['icon'] = 'UNLINKED'

                        h = prefix + "op = " + layout + ".operator("
                        p.append(prefix + "op.context = self.bl_context")
                        p.append(prefix + "op.xmlpath = '" + l_path + "'")
                        p.append(prefix + "op.event = '" +
                                 l_attrs['trigger'] + "'")
                    elif l_type == 'PROPSEARCH' or l_type == 'PROP':
                        prop = "".join(l_path.split("/")[:3]) + l_attrs['prop']
                        attr = rm.PropertyHash(prop)
                        pv = prefix + layout

                        if l_type == 'PROPSEARCH':
                            h = pv + ".prop_search("
                            l.append("data, '" + attr + "'")
                            l.append(", '".join(l_attrs['trigger']
                                     .rsplit(".", 1)) + "'")
                        elif l_type == 'PROP':
                            h = pv + ".prop("
                            l.append("data, '" + attr + "'")

                    # Put it all together
                    if h:
                        if l_attrs['text'] != -1:
                            l.append("text='" + l_attrs['text'] + "'")
                        if l_attrs['icon']:
                            l.append("icon='" + l_attrs['icon'] + "'")
                        if l_type == 'PROP' and l_attrs['expand']:
                            l.append("expand=" + l_attrs['expand'])
                        if l_type == 'PROP' and l_attrs['slider']:
                            l.append("slider=" + l_attrs['slider'])
                        if l_type == 'PROP' and l_attrs['toggle']:
                            l.append("toggle=" + l_attrs['toggle'])

                        code.append(h + ", ".join(l) + ")")
                        code.extend(p)
            return code

        if DEBUG_PRINT:
            print("PipelineManager._register_panel()")

        ec = rm_context.ExportContext()
        ec.context_pipeline = pipeline
        ec.context_category = category
        ec.context_panel = panel

        classes = []
        properties = []
        local = {'panel': None}
        label = pipeline + " - " + panel
        path = "/".join([pipeline, category, panel])
        data_types = ('CURVE', 'SURFACE', 'LAMP', 'CAMERA', 'MESH', 'META')
        w_attrs = {'enabled': 'True', 'delete': "False", 'duplicate': "False",
                   'register': 'True', 'windows': ""}

        # Get layout attributes
        for a in self.list_attributes(path):
            if a in w_attrs:
                w_attrs[a] = self.get_attr(ec, path, a)

        register = eval(w_attrs['register'])  # Will we are registering panel?
        windows = [w.strip() for w in w_attrs['windows'].split(",")]
        window_list = [w for w in windows if w and w not in data_types]
        data_list = [w for w in windows if w and w in data_types]
        scene_only = ('SCENE' in window_list and 'RENDER' in window_list)

        if data_list:
            window_list.append('DATA')

        filters = {'DATA': {'validate': "", 'type': "",
                        'filter': str(tuple(data_list))},
                'RENDER': {'validate': "", 'type': "",
                        'filter': "()"},
                'SCENE': {'validate': "", 'type': "",
                        'filter': "()"},
                'WORLD': {'validate': "world", 'type': "",
                        'filter': "()"},
                'OBJECT': {'validate': "object", 'type': "",
                        'filter': "('MESH', 'CURVE', 'SURFACE', 'META',"
                                  " 'EMPTY')"},
                'MATERIAL': {'validate': "material", 'type': "",
                        'filter': "()"},
                'PARTICLE': {'validate': "particle_system", 'type': "",
                        'filter': "()"},
                'TEXTURE': {'validate': "texture", 'type': "IMAGE",
                        'filter': "()"}}

        props = {'CURVE': "bpy.types.Curve",
                'SURFACE': "bpy.types.SurfaceCurve",
                'LAMP': "bpy.types.Lamp",
                'CAMERA': "bpy.types.Camera",
                'MESH': "bpy.types.Mesh",
                'META': "bpy.types.MetaBall",
                'RENDER': "bpy.types.Scene",
                'SCENE': "bpy.types.Scene",
                'WORLD': "bpy.types.World",
                'OBJECT': "bpy.types.Object",
                'MATERIAL': "bpy.types.Material",
                'PARTICLE': "bpy.types.ParticleSettings",
                'TEXTURE': "bpy.types.Texture"}

        # Choose panel icon according to panel type
        if category == "shader_panels":
            category_id = 'SP'
            attr = self.get_attr(ec, path, 'type', False)

            # Choose panel icon according to shader type
            if attr == 'SURFACE':
                icon = 'MATSPHERE'
            elif attr == 'DISPLACEMENT':
                icon = 'MESH_ICOSPHERE'
            elif attr == 'ATMOSPHERE':
                icon = 'MAT_SPHERE_SKY'
            elif attr == 'INTERIOR':
                icon = 'MAT_SPHERE_SKY'
            elif attr == 'EXTERIOR':
                icon = 'MAT_SPHERE_SKY'
            elif attr == 'IMAGER':
                icon = 'RETOPO'
            elif attr == 'LIGHTSOURCE':
                icon = 'LAMP'
            elif attr == 'AREALIGHTSOURCE':
                icon = 'SOLID'
            else:
                icon = 'WORLD'
        elif category == "utility_panels":
            icon = 'SCRIPTWIN'
            category_id = 'UP'
        elif category == "command_panels":
            icon = 'CONSOLE'
            category_id = 'CP'
        else:
            icon = 'OOPS'

        # Generate a panel for every window the panel filters assign it to
        for w in [w for w in window_list if w in filters.keys() and register]:
            name = w + "_PT_" + pipeline + "_" + category_id + "_" + panel
            e_attr = rm.PropertyHash(pipeline + category + panel + 'enabled')

            prop = []
            head = ["from " + MODULE + " import rm_panel",
                    "class " + name + "(rm_panel.RibmosaicPropertiesPanel, "
                    "bpy.types.Panel):",
                    "\tbl_space_type = 'PROPERTIES'",
                    "\tbl_region_type = 'WINDOW'",
                    "\tbl_label = '" + label + "'",
                    "\tbl_context = '" + w.lower() + "'",
                    "\tpanel_context = bl_context",
                    "\tfilter_type = " + filters[w]['filter'],
                    "\tvalidate_context = '" + filters[w]['validate'] + "'",
                    "\tvalidate_context_type = '" + filters[w]['type'] + "'",
                    "\tcontext_pipeline = '" + pipeline + "'",
                    "\tcontext_category = '" + category + "'",
                    "\tcontext_panel = '" + panel + "'"]
            func = ["\t",
                    "\tdef draw_header(self, context):",
                    "\t\tlayout = self.layout",
                    "\t\trow = layout.row(align=True)",
                    "\t\tdata = self._context_data(context, "
                    "self.bl_context)['data']",
                    "\t\tsub = row.row()",
                    "\t\tif data." + e_attr + ":",
                    "\t\t\top  = sub.operator('wm.ribmosaic_panel_disable', "
                    "text='', icon='PINNED')",
                    "\t\telse:",
                    "\t\t\top  = sub.operator('wm.ribmosaic_panel_enable', "
                    "text='', icon='UNPINNED')",
                    "\t\top.xmlpath = '" + path + "'",
                    "\t\top.context = self.bl_context",
                    "\t\tsub.enabled = True",
                    "\t\tsub = row.row()",
                    "\t\top = sub.operator('wm.ribmosaic_panel_duplicate', "
                    "text='', icon='ZOOMIN')",
                    "\t\top.xmlpath = '" + path + "'",
                    "\t\top.context = self.bl_context",
                    "\t\tsub.enabled = " + w_attrs['duplicate'],
                    "\t\tsub = row.row()",
                    "\t\top = sub.operator('wm.ribmosaic_panel_delete', "
                    "text='', icon='X')",
                    "\t\top.xmlpath = '" + path + "'",
                    "\t\tsub.enabled = " + w_attrs['delete'],
                    "\t\tsub = row.row()",
                    "\t\top = sub.operator('wm.ribmosaic_xml_info', "
                    "text='', icon='INFO')",
                    "\t\top.xmlpath = '" + path + "'",
                    "\t\top.context = self.bl_context",
                    "\t\top.event = '@[ATTR:" + path + ".description:]@'",
                    "\t\tsub.enabled = True",
                    "\t\tlayout.label(text='', icon='" + icon + "')"]
            draw = ["\t",
                    "\tdef draw(self, context):",
                    "\t\tlayout = self.layout",
                    "\t\tdata = self._context_data(context, "
                    "self.bl_context)['data']"]
            tail = ["",
                    "bpy.utils.register_class(" + name + ")",
                    "panel = " + name]

            # Unfold nested layout elements into layout draw code
            draw.extend(unfold_layout(path + "/layout", "\t\t"))

            # Add geometry window types if DATA
            if w == 'DATA':
                window_types = data_list
            else:
                window_types = [w]

            # Validate window filters against panel's category
            for wt in window_types:
                if wt not in self._category_windows[category]:
                    raise rm_error.RibmosaicError(
                        "PipelineManager._register_panel: Panel '" + panel +
                        "' in panels category '" + category +
                        "' using wrong windows filter '" + wt + "'")

            # Scene and Render share the same datablock
            # so only process for SCENE
            if scene_only and w == 'RENDER':
                window_types = []

            # Generate per window properties
            for wt in window_types:
                prop.append(props[wt] + "." + e_attr +
                            " = bpy.props.BoolProperty(" +
                            "name='enabled', default=" + w_attrs['enabled'] +
                            ")")
                properties.append("del " + props[wt] + "." + e_attr)

            # Generate panel's control properties
            for p in self.list_elements(path + "/properties"):
                # Setup property structure
                attr = rm.PropertyHash(pipeline + category + panel + p)
                prop_path = path + "/properties/" + p
                attrs = {'type': "", 'description': "", 'default': "",
                        'min': "",
                        'max': "", 'softmin': "", 'softmax': "", 'maxlen': "",
                        'step': "", 'precision': "", 'items': "", 'size': "",
                        'event': "", 'link': ""}

                # Apply element attributes to structure
                for a in self.list_attributes(prop_path):
                    if a in attrs:
                        attrs[a] = self.get_attr(ec, prop_path, a)

                        # Escape any strings with single quotes
                        if (a == 'description' or a == 'default') and\
                          "'" in attrs[a]:
                            attrs[a] = attrs[a].replace("'", "\\'")

                # Generate control properties
                for wt in window_types:
                    # Setup common attributes
                    p_str = ""
                    p_name = "name='" + p + "'"
                    p_desc = ", description='" + attrs['description'] + "'"

                    if attrs['default']:
                        p_defnum = ", default=" + attrs['default']
                        p_defstr = ", default='" + attrs['default'] + "'"
                    else:
                        p_defnum = ""
                        p_defstr = ""

                    # Break it down by type
                    if attrs['type'] == 'INT':
                        p_str = props[wt] + "." + attr + \
                                " = bpy.props.IntProperty(" + \
                                p_name + p_desc + p_defnum
                    elif attrs['type'] == 'FLOAT':
                        p_str = props[wt] + "." + attr + \
                                " = bpy.props.FloatProperty(" + \
                                p_name + p_desc + p_defnum
                    elif attrs['type'] == 'STRING':
                        p_str = props[wt] + "." + attr + \
                                " = bpy.props.StringProperty(" + \
                                p_name + p_desc + p_defstr
                    elif attrs['type'] == 'ENUM':
                        p_str = props[wt] + "." + attr + \
                                " = bpy.props.EnumProperty(" + \
                                p_name + p_desc + p_defstr
                    elif attrs['type'] == 'BOOL':
                        p_str = props[wt] + "." + attr + \
                                " = bpy.props.BoolProperty(" + \
                                p_name + p_desc + p_defnum
                    elif attrs['type'] == 'COLOR':
                        p_str = props[wt] + "." + attr + \
                                " = bpy.props.FloatVectorProperty(" + \
                                p_name + p_desc + p_defnum + \
                                ", subtype='COLOR'"

                        if not attrs['size']:
                            attrs['size'] = "3"
                    elif attrs['type'] == 'VECTOR' or \
                         attrs['type'] == 'POINT' or \
                         attrs['type'] == 'NORMAL':
                        p_str = props[wt] + "." + attr + \
                                " = bpy.props.FloatVectorProperty(" + \
                                p_name + p_desc + p_defnum + \
                                ", subtype='XYZ'"

                        if not attrs['size']:
                            attrs['size'] = "3"
                    elif attrs['type'] == 'HPOINT':
                        p_str = props[wt] + "." + attr + \
                                " = bpy.props.FloatVectorProperty(" + \
                                p_name + p_desc + p_defnum + \
                                ", subtype='QUATERNION'"

                        if not attrs['size']:
                            attrs['size'] = "4"
                    elif attrs['type'] == 'MATRIX':
                        p_str = props[wt] + "." + attr + \
                                " = bpy.props.FloatVectorProperty(" + \
                                p_name + p_desc + p_defnum + \
                                ", subtype='MATRIX'"

                        if not attrs['size']:
                            attrs['size'] = "16"

                    # Apply attributes if specified
                    if attrs['min']:
                        p_str += ", min=" + attrs['min']
                    if attrs['max']:
                        p_str += ", max=" + attrs['max']
                    if attrs['softmin']:
                        p_str += ", soft_min=" + attrs['softmin']
                    if attrs['softmax']:
                        p_str += ", soft_max=" + attrs['softmax']
                    if attrs['maxlen']:
                        p_str += ", maxlen=" + attrs['maxlen']
                    if attrs['step']:
                        p_str += ", step=" + attrs['step']
                    if attrs['precision']:
                        p_str += ", precision=" + attrs['precision']
                    if attrs['items']:
                        p_str += ", items=" + attrs['items']
                    if attrs['size']:
                        p_str += ", size=" + attrs['size']

                    # Apply property to class and removal list
                    if p_str:
                        p_str += ")"

                        prop.append(p_str)
                        properties.append("del " + props[wt] + "." + attr)
                        prop.append("")

            if DEBUG_PRINT:
                print("\n".join(prop + head + func + draw + tail))

            try:
                exec("\n".join(prop), globals(), local)
                exec("\n".join(head + func + draw + tail), globals(), local)
            except:
                raise rm_error.RibmosaicError(
                    "PipelineManager._register_panel:"
                    " Failed to generate panel " + path, sys.exc_info())

            classes.append(local['panel'])
            if DEBUG_PRINT:
                print('panel: ', local['panel'])

        if pipeline not in self._pipeline_panels:
            self._pipeline_panels[pipeline] = {}

        if category not in self._pipeline_panels[pipeline]:
            self._pipeline_panels[pipeline][category] = {}

        if panel in self._pipeline_panels[pipeline][category]:
            self._unregister_panel(pipeline, category, panel)

        self._pipeline_panels[pipeline][category][panel] = {}
        self._pipeline_panels[pipeline][category][panel]['classes'] = classes
        self._pipeline_panels[pipeline][category][panel]['props'] = properties

    def _unregister_panel(self, pipeline, category, panel):
        """Unregister specified panel if already registered.

        pipeline = pipeline containing panel
        category = sub element containing panel
        panel = name of panel to unregister
        """

        if DEBUG_PRINT:
            print("PipelineManager._unregister_panel()")

        if pipeline in self._pipeline_panels:
            if category in self._pipeline_panels[pipeline]:
                if panel in self._pipeline_panels[pipeline][category]:
                    path = "/".join([pipeline, category, panel])
                    pi = pipeline
                    ca = category
                    pa = panel

                    for cl in self._pipeline_panels[pi][ca][pa]['classes']:
                        try:
                            if DEBUG_PRINT:
                                print('unregister class: ', cl)
                            bpy.utils.unregister_class(cl)
                        except:
                            raise rm_error.RibmosaicError(
                                "PipelineManager._unregister_panel:"
                                " Failed to unregister panel class",
                                sys.exc_info())

                    for pr in self._pipeline_panels[pi][ca][pa]['props']:
                        try:
                            exec(pr)
                            if DEBUG_PRINT:
                                print(pr)
                        except:
                            raise rm_error.RibmosaicError(
                                "PipelineManager._unregister_panel:"
                                " Failed to delete property",
                                sys.exc_info())

                    self._pipeline_panels[pipeline][category].pop(panel)

    def _register_pipeline(self, pipeline):
        """Register all panels in pipeline"""

        if pipeline in self._pipeline_panels:
            self._unregister_pipeline(pipeline)
        else:
            self._pipeline_panels[pipeline] = {}
        if DEBUG_PRINT:
            print("PipelineManager._register_pipeline()")

        for category in ['shader_panels', 'utility_panels', 'command_panels']:
            for panel in self.list_elements(pipeline + "/" + category):
                self._register_panel(pipeline, category, panel)

    def _unregister_pipeline(self, pipeline):
        """Unregister all panels in pipeline"""
        if DEBUG_PRINT:
            print("PipelineManager._unregister_pipeline()")
        if pipeline in self._pipeline_panels:
            for category in ['shader_panels', 'utility_panels', \
              'command_panels']:
                for panel in self.list_elements(pipeline + "/" + category):
                    self._unregister_panel(pipeline, category, panel)

            self._pipeline_panels.pop(pipeline)

    # #### Public pipeline methods

    def new_pipeline(self, name, info=""):
        """Generates a new blank pipeline text and XML tree.

        name = name of new pipeline element and text file
        info = information displayed when pipeline is loaded
        """

        if DEBUG_PRINT:
            print("PipelineManager.new_pipeline()")

        try:
            if name:
                if name.endswith(".rmp"):
                    filename = name
                else:
                    filename = name + ".rmp"

                text = bpy.context.blend_data.texts.new(filename)
                text.filepath = filename
                filename = text.name
                attribs = {'filepath': filename,
                           'version': rm.VERSION,
                           'filter': name.upper()}

                self.new_element_tree("", name, 'pipeline', info, attribs)

                self._write_xml(name)
                self._register_pipeline(name)
        except:
            raise rm_error.RibmosaicError("PipelineManager.newpipeline:"
                        " Pipeline creation failed" + \
                        self._error_con, sys.exc_info())

        self._pipeline_texts = self.list_rmp()

    def load_pipeline(self, filepath):
        """Load, parse and register specified pipeline file.

        filepath = full path to pipeline .rmp file
        return = pipeline element name
        """

        if DEBUG_PRINT:
            print("PipelineManager.load_pipeline()")

        filename = os.path.split(filepath)[1]

        if not filepath:
            raise rm_error.RibmosaicError(
                "PipelineManager.load_pipeline: No path specified")
        elif not filename:
            raise rm_error.RibmosaicError(
                "PipelineManager.load_pipeline: No filename specified")
        elif os.path.splitext(filename)[1] != ".rmp":
            raise rm_error.RibmosaicError(
                "PipelineManager.load_pipeline: Invalid file extension"
                " (*.rmp)")

        try:
            text = bpy.context.blend_data.texts.load(filepath)
            filename = text.name  # Get text name again in case it was changed
        except:
            raise rm_error.RibmosaicError("PipelineManager.load_pipeline:"
                    " Load failed" + self._error_con, sys.exc_info())

        try:
            element = self._load_xml(filename)
            self._pipeline_texts = self.list_rmp()
            pipeline = element.tag
        except rm_error.RibmosaicError as err:
            err.ReportError()
            bpy.context.blend_data.texts.remove(bpy.data.texts[filename])
            raise rm_error.RibmosaicError("PipelineManager.load_pipeline: " +
                                          self._error_load)

        try:
            self._register_pipeline(pipeline)
        except rm_error.RibmosaicError as err:
            err.ReportError()
            raise rm_error.RibmosaicError("PipelineManager.load_pipeline: " +
                                          self._error_register)

        self.revisions += 1
        return pipeline

    def remove_pipeline(self, pipeline):
        """Unregister and unload specified pipeline and unlink its text file.

        pipeline = name of pipeline to remove (the element name not text name)
        """
        if DEBUG_PRINT:
            print("PipelineManager.remove_pipeline()")

        if not pipeline:
            raise rm_error.RibmosaicError(
                "PipelineManager.remove_pipeline: No pipeline specified")
        elif pipeline not in self._pipeline_panels:
            raise rm_error.RibmosaicError(
                "PipelineManager.remove_pipeline: Pipeline not loaded")

        try:
            self._unregister_pipeline(pipeline)
        except rm_error.RibmosaicError as err:
            err.ReportError()
            raise rm_error.RibmosaicError(
                "PipelineManager.remove_pipeline: " + self._error_unregister)

        try:
            filename = self._unload_xml(pipeline)
        except rm_error.RibmosaicError as err:
            err.ReportError()
            raise rm_error.RibmosaicError(
                "PipelineManager.remove_pipeline: " + self._error_unload)

        path = bpy.data.texts[filename].filepath.replace("\\", "/")

        try:
            bpy.context.blend_data.texts.remove(bpy.data.texts[filename])
            self.revisions += 1
            self._pipeline_texts = self.list_rmp()
        except:
            rm.RibmosaicInfo("PipelineManager.remove_pipeline:Unavailable"
                             "... reloading pipelines. try removal again")
             # Update all pipelines so maybe text name will reset
            self.update_pipeline()
            raise rm_error.RibmosaicError(
                "PipelineManager.remove_pipeline: Removal failed" +
                self._error_con, sys.exc_info())

        # If addon pipeline was removed then force addon update
        if "/addons/" + MODULE + "/" in path:
            self.update_pipeline(description=False)

    def update_pipeline(self, pipeline="", description=True):
        """Updates specified pipeline or all loaded pipelines if blank.
        This will force the parsed pipelines to un-register and un-load before
        re-loading and re-registering from text. If updating all pipelines also
        auto loads addon pipelines.

        pipeline = name of pipeline to update (or null for all)
        description = print pipeline descriptions to console when updating
        """

        if DEBUG_PRINT:
            print("PipelineManager.update_pipeline()")
            print(pipeline)

        if pipeline:
            if pipeline in self._pipeline_panels:
                try:
                    self._unregister_pipeline(pipeline)
                except rm_error.RibmosaicError as err:
                    err.ReportError()
                    raise rm_error.RibmosaicError(
                        "PipelineManager.update_pipeline: " +
                        self._error_unregister)

                try:
                    filename = self._unload_xml(pipeline)
                except rm_error.RibmosaicError as err:
                    err.ReportError()
                    raise rm_error.RibmosaicError(
                        "PipelineManager.update_pipeline: " +
                        self._error_unload)

                try:
                    element = self._load_xml(filename)
                except rm_error.RibmosaicError as err:
                    err.ReportError()
                    raise rm_error.RibmosaicError(
                        "PipelineManager.update_pipeline: " +
                        self._error_load)

                try:
                    self._register_pipeline(element.tag)
                except rm_error.RibmosaicError as err:
                    err.ReportError()
                    raise rm_error.RibmosaicError(
                        "PipelineManager.update_pipeline: " +
                        self._error_register)
        else:
            self.flush()

            # Autoload addon pipelines
            pipelines = self.list_rmp()
            pipelines_path = "addons" + os.sep + MODULE + os.sep + "pipelines"

            for p in bpy.utils.script_paths(subdir=pipelines_path):
                for f in [f for f in os.listdir(p) \
                          if f.endswith(".rmp") and f[:20] not in pipelines]:
                    bpy.context.blend_data.texts.load(p + os.sep + f)
                    pipelines.append(f[:20])

            # Load pipelins in text editor
            for p in pipelines:
                path = bpy.data.texts[p].filepath.replace("\\", "/")

                # Don't load pipelines from other addons
                if "/addons/" not in path or "/addons/" + MODULE + "/" in path:
                    try:
                        element = self._load_xml(p, description)
                    except rm_error.RibmosaicError as err:
                        err.ReportError()
                        raise rm_error.RibmosaicError(
                            "PipelineManager.update_pipeline: " +
                            self._error_load)

                    try:
                        self._register_pipeline(element.tag)
                    except rm_error.RibmosaicError as err:
                        err.ReportError()
                        raise rm_error.RibmosaicError(
                            "PipelineManager.update_pipeline: " +
                            self._error_register)

        self._pipeline_texts = self.list_rmp()
        self.revisions += 1

    def sync(self):
        """
        Sync XML tree and panel registration with pipelines in text editor
        """

        if self.revisions == 0 or self._pipeline_texts != self.list_rmp():
            if DEBUG_PRINT:
                print("PipelineManager.sync()")
            self.update_pipeline()

    def flush(self):
        """Unregisters and removes all pipelines in pipeline tree"""

        if DEBUG_PRINT:
            print("PipelineManager.flush()")

        for p in self.list_pipelines():
            try:
                self._unregister_pipeline(p)
            except rm_error.RibmosaicError as err:
                err.ReportError()
                raise rm_error.RibmosaicError(
                    "PipelineManager.flush:" + self._error_unregister)

            try:
                self._unload_xml(p)
            except rm_error.RibmosaicError as err:
                err.ReportError()
                raise rm_error.RibmosaicError(
                    "PipelineManager.flush:" + self._error_unload)

    def check_dependencies(self, pipeline):
        """Checks text file dependencies of specified pipeline and returns list
        of missing texts if any.
        """

        if DEBUG_PRINT:
            print("PipelineManager.checkdependecies()")
            print(pipeline)

        dependencies = []

        if pipeline:
            try:
                ec = {'context_pipeline': pipeline}
                attr = self.get_attr(ec, pipeline, "dependencies")

                if attr.strip():
                    texts = [t.name for t in bpy.data.texts]
                    dependencies = [p.strip() for p in attr.split(",") \
                                  if p.strip() not in texts]
            except rm_error.RibmosaicError as err:
                err.ReportError()
                raise rm_error.RibmosaicError(
                    "PipelineManager.check_dependencies:"
                    " Could not get dependencies")

        return dependencies

    def remove_panel(self, xmlpath):
        """Unregister and remove panel at specified xmlpath and update text.

        xmlpath = full path to panel element to remove
        """

        if DEBUG_PRINT:
            print("PipelineManager.removepanel()")
            print(xmlpath)

        try:
            segs = xmlpath.split("/")
            self._unregister_panel(segs[0], segs[1], segs[2])
            self._unload_xml(xmlpath)
            self._write_xml(segs[0])
        except rm_error.RibmosaicError as err:
            err.ReportError()
            raise rm_error.RibmosaicError(
                "PipelineManager.remove_panel: Could not remove panel" +
                self._error_con)

    def duplicate_panel(self, xmlpath, name, decoration=True):
        """Duplicate panel at specified xmlpath changing its name.

        xmlpath = full path to panel element to remove
        name = name of duplicated panel
        decoration = cleanup XML decorations
        """

        if DEBUG_PRINT:
            print("PipelineManager.duplicate_panel()")
            print(xmlpath)

        try:
            # Separate path
            segs = xmlpath.split("/")
            segs.pop()

            # Get elements
            element = self.get_element(xmlpath)
            parent = self.get_element("/".join(segs))

            # Duplicate and setup panel
            xml = ET.tostring(element)
            panel = ET.XML(xml)
            panel.tag = name
            panel.attrib['enabled'] = "True"
            panel.attrib['register'] = "True"
            panel.attrib['delete'] = "True"
            panel.tail = element.tail

            # Cleanup decorations
            if decoration:
                # Set tabs according to XML path depth
                tabs = "\t".join(["" for i in range(xmlpath.count("/") + 1)])

                previous = parent.getchildren()[-1]
                previous.tail = previous.tail.rstrip("\t") + tabs
                panel.tail = panel.tail.rstrip("\t") + tabs[:-1]

            # Apply to pipeline
            parent.append(panel)
            self._register_panel(segs[0], segs[1], name)
            self._write_xml(segs[0])
        except rm_error.RibmosaicError as err:
            err.ReportError()
            raise rm_error.RibmosaicError(
                "PipelineManager.duplicate_panel: Could not duplicate panel" +
                self._error_con)

    def new_element_tree(self, xmlpath, name, key, text="", attribs={}):
        """Creates an element and sub-elements in pipeline xmlpath from the
        specified key in _pipeline_elements.

        xmlpath = Pipeline path to create new element tree
        name = name of new root element
        key = key in _pipeline_elements dictionary to create tree from
        text = text to use in root element (overrides dict entry)
        attribs = attributes to override or append to root element
        return = root element created
        """

        if DEBUG_PRINT:
            print("PipelineManager.new_element_tree()")
            print("xmlpath: " + xmlpath)
            print("name: " + name)
            print("key: " + key)

        if not text:
            text = self.get_element_info(key, None, "text")

        tail = self.get_element_info(key, None, "tail")
        subs = self.get_element_info(key, None, "sub_elements")
        attrs = self.get_element_info(key, "", "default")

        # Apply any override attributes
        for k in attribs:
            attrs[k] = attribs[k]

        root = self._new_element(xmlpath, name, text, tail, attribs=attrs)

        # Automatically create and sub elements
        if xmlpath:
            xmlpath += "/"

        for k in subs:
            self.new_element_tree(xmlpath + name, k, k)

        return root

    # #### Public pipeline search methods

    def list_rmp(self):
        """Return list of .rmp files in text editor"""

        if DEBUG_PRINT:
            print("PipelineManager.list_rmp()")

        return [t.name for t in bpy.data.texts \
                if t.name.endswith(".rmp") or t.filepath.endswith(".rmp")]

    def list_elements(self, xmlpath, sort=False, attrs=[]):
        """List all elements as strings at specified xmlpath

        xmlpath = full path to panel elements to list
        sort = sort list before returning
        attrs = build element attribute string
                [("prefix", 'eval', "postfix"),...]
        return = list of element strings or [(element, attrs),...]
        """

        elements = []
        found_element = None

        if DEBUG_PRINT:
            print("PipelineManager.list_elements()")
            print("xmlpath: " + xmlpath)
            print("element: " + self.get_element(xmlpath).tag)

        try:
            found_element = self.get_element(xmlpath)

            if found_element is None:
                return elements

            for e in found_element.iterfind('*'):
                if DEBUG_PRINT:
                    print("element tag: " + e.tag)
                # Build element attribute string if specified
                if attrs:
                    attr_str = ""

                    for a in attrs:
                        if a[1]:
                            attr_eval = eval(a[1])
                        else:
                            attr_eval = ""

                        if attr_eval or not a[1]:
                            attr_str += a[0] + attr_eval + a[2]

                    elements.append((attr_str, e.tag))
                else:
                    elements.append(e.tag)

            if sort:
                elements.sort()
        except:
            rm.RibmosaicInfo("PipelineManager.list_elements:"
                " Invalid path or attributes for search in " + xmlpath)

        return elements

    def list_attributes(self, xmlpath, sort=True):
        """List attributes of element as strings at specified xmlpath"""

        if DEBUG_PRINT:
            print("PipelineManager.list_attributes()")
            print("xmlpath: " + xmlpath)

        try:
            attributes = list(self.get_element(xmlpath).attrib)

            if sort:
                attributes.sort()
        except:
            attributes = []

        return attributes

    def list_pipelines(self, sort=True):
        """List all pipelines currently loaded as strings"""
        if DEBUG_PRINT:
            print("PipelineManager.list_pipelines()")

        return self.list_elements('', sort)

    def list_help(self, pipeline):
        """Return pipeline's help information text as a list of lines"""

        info = []

        if DEBUG_PRINT:
            print("PipelineManager.list_help()")

        try:
            ec = {'context_pipeline': pipeline}
            message = self.get_text(ec, pipeline)
            version = self.get_attr(ec, pipeline, "version")
            dependencies = self.check_dependencies(pipeline)

            try:
                if version and float(version) > float(rm.VERSION):
                    info.append("WARNING - Pipeline was made with a "
                                "newer version of RIB Mosaic")
                    info.append("")
            except:
                pass

            if dependencies:
                info.append("WARNING - This pipeline also requires "
                            "the following texts:")
                info.extend(["- " + d for d in dependencies])
                info.append("")

            if message.strip():
                info.extend(message.replace("\\n", "\n").splitlines())
        except rm_error.RibmosaicError as err:
            info = ["Help retrieval error"]
            err.ReportError()

        return info

    def list_panels(self, category, pipelines=[], type="", window=""):
        """Lists all panel element paths for all or specified pipelines
        declared as type or any and registered under any window or any.

        category = pipeline category sub element to find panel elements
        pipelines = List of pipelines to check or all pipelines if blank
        type = Only list panels declared as type or any if null
        window = Only list panels registered as window or any if null
        """

        if DEBUG_PRINT:
            print("PipelineManager.list_panels()")

        commands = []
        cat = "/" + category

        if not pipelines:
            pipelines = self.list_pipelines()

        for rmp in pipelines:
            for pan in self.list_elements(rmp + cat):
                xmlpath = rmp + cat + "/" + pan
                windows = self.get_attr(None, xmlpath, "windows", False)
                t = self.get_attr(None, xmlpath, "type", False)

                if (not window or window in windows) and \
                  (not type or t == type):
                    commands.append(xmlpath)

        return commands

    # #### Public XML data methods

    def get_attr(self, export_object, xmlpath, attr, resolve=True, default=""):
        """Retrieve attribute using XML path and attribute name. Such as...
        xmlpath="pipeline/category/panel/sub_category/tag", attr="attrib"

        export_object = object requesting attr
                        (subclass of ExportContext, None or {})
        xmlpath = Pipeline XML path to element containing attribute
        attr = Attribute name to retrieve
        resolve = Resolve any links in attribute
        default = Value to return if attribute doesn't exist
        """

        if DEBUG_PRINT:
            print("PipelineManager.get_attr()")
            print("xmlpath: " + xmlpath)
            print("attr: " + attr)

        segs = xmlpath.split("/")

        try:
            element = self.get_element(xmlpath)
        except:
            raise rm_error.RibmosaicError("PipelineManager.get_attr:"
                                " Invalid path syntax for " + xmlpath)

        if element is None:
            if segs[0] in self.list_pipelines():
                raise rm_error.RibmosaicError("PipelineManager.get_attr:"
                    " Could not find element at \"" + xmlpath + "\"")
            else:
                raise rm_error.RibmosaicError("PipelineManager.get_attr:"
                    " Could not find pipeline \"" + segs[0] + "\"")

        try:
            attrib = element.attrib

            if attr in attrib:
                data = attrib[attr]
            else:
                data = default
        except:
            raise rm_error.RibmosaicError("PipelineManager.get_attr:"
                " Could not get attribute " + xmlpath + "." + attr)

        if not data:
            data = default

        # Check for links in data, if so resolve them
        if resolve and "@[" in data:
            if export_object is None:
                export_object = rm_context.ExportContext()

            elif type(export_object) == dict:
                attrs = dict(export_object)
                export_object = rm_context.ExportContext()

                for a in attrs.keys():
                    exec("export_object." + a + " = attrs[a]")

            data = export_object._resolve_links(data, xmlpath + "/." + attr)

        return data

    def set_attrs(self, xmlpath, update=False, write=True, **attrs):
        """Set attribute using XML path and attribute name. Such as...
        xmlpath="pipeline/category/panel/sub_category/tag", attr="attrib"

        xmlpath = pipeline XML path to element containing attribute
        update = update panel (useful if attribute is in a UI panel)
        write = write changes to pipeline text
        attrs = dictionary containing element attributes and values to set
        """

        if DEBUG_PRINT:
            print("PipelineManager.set_attrs()")

        segs = xmlpath.split("/")

        try:
            element = self.get_element(xmlpath)
        except:
            raise rm_error.RibmosaicError("PipelineManager.set_attrs:"
                " Invalid path syntax for " + xmlpath)

        if element is None:
            if segs[0] in self.list_pipelines():
                raise rm_error.RibmosaicError("PipelineManager.set_attrs:"
                    " Could not find element at \"" + \
                                              xmlpath + "\"")
            else:
                raise rm_error.RibmosaicError("PipelineManager.set_attrs:"
                    " Could not find pipeline \"" + \
                      segs[0] + "\"\nCheck pipeline info for"
                      " missing dependencies!")

        try:
            for a in attrs:
                element.attrib[a] = attrs[a]
        except:
            raise rm_error.RibmosaicError("PipelineManager.set_attrs:"
                " Could not find attribute " + xmlpath + "." + attrs[a])

        if segs[0]:
            if write:
                self._write_xml(segs[0])

            if update and len(segs) > 1:
                self._unregister_panel(segs[0], segs[1], segs[2])
                self._register_panel(segs[0], segs[1], segs[2])

    def get_text(self, export_object, xmlpath, resolve=True):
        """Retrieve element text using XML path, index and attribute name...
        xmlpath="pipeline/category/panel/sub_category/tag"

        export_object = object requesting text
                        (subclass of ExportContext or None)
        xmlpath = pipeline XML path to element containing text
        """

        if DEBUG_PRINT:
            print("PipelineManager.get_text()")

        try:
            element = self.get_element(xmlpath)
        except:
            raise rm_error.RibmosaicError("PipelineManager.get_text: " + \
                                          "Invalid path syntax for " + xmlpath)

        if element is None:
            segs = xmlpath.split("/")
            if segs[0] in self.list_pipelines():
                raise rm_error.RibmosaicError(
                    "PipelineManager.get_text: " +
                    "Could not find element at \"" + xmlpath + "\"")
            else:
                raise rm_error.RibmosaicError("PipelineManager.get_text: " +
                                              "Could not find pipeline \"" +
                      segs[0] + "\"\nCheck pipeline info for"
                      " missing dependencies!")

        try:
            text = element.text
        except:
            raise rm_error.RibmosaicError("PipelineManager.get_text: " +
                                          "Could not get text for " + xmlpath)

        if text:
            # If using more then one line strip first and last line whitespace
            if text.startswith("\n"):
                text = "\n".join(text.split("\n")[1:-1])
        else:
            text = ""

        # Check for links in data, if so resolve them
        if resolve and "@[" in text:
            if export_object is None:
                export_object = rm_context.ExportContext()
            elif type(export_object) == dict:
                attrs = dict(export_object)
                export_object = rm_context.ExportContext()

                for a in attrs.keys():
                    exec("export_object." + a + " = attrs[a]")

            text = export_object._resolve_links(text, xmlpath)

        return text

    def set_text(self, xmlpath, value, update=False, write=True):
        """Set element text using XML path, index and attribute name...
        xmlpath="pipeline/category/panel/sub_category/tag"

        xmlpath = pipeline XML path to element containing text
        value = new value of text
        update = update panel (useful if text is in a panel)
        write = write changes to pipeline text
        """

        if DEBUG_PRINT:
            print("PipelineManager.set_text()")
            print("xmlpath: " + xmlpath)

        segs = xmlpath.split("/")[0]

        try:
            element = self.get_element(xmlpath)
        except:
            raise rm_error.RibmosaicError("PipelineManager.set_text: " +
                                          "Invalid path syntax for " + xmlpath)

        if element is None:
            if segs[0] in self.list_pipelines():
                raise rm_error.RibmosaicError("PipelineManager.set_text: " +
                                              "Could not find element at \"" +
                                              xmlpath + "\"")
            else:
                raise rm_error.RibmosaicError("PipelineManager.set_text: " +
                        "Could not find pipeline \"" +
                        segs[0] + "\"\nCheck pipeline info for"
                        " missing dependencies!")

        try:
            element.text = value
        except:
            raise rm_error.RibmosaicError("PipelineManager.set_text: " +
                                          "Could not set text for " + xmlpath)

        if segs[0]:
            if write:
                self._write_xml(segs[0])

            if update:
                self._unregister_panel(segs[0], segs[1], segs[2])
                self._register_panel(segs[0], segs[1], segs[2])

    def get_element(self, xmlpath=""):
        """Get a XML element at specified XML path

        xmlpath = the full XML path to the tree to add element
        If no xmlpath is given then the root element of the pipeline
        tree is returned.
        """
        if DEBUG_PRINT:
            print("PipelineManager.get_element()")
            print("xmlpath: " + xmlpath)

        # if no path given then assume top level of pipelines
        if xmlpath == '':
            element = self._pipeline_tree.getroot()
        else:
            element = self._pipeline_tree.find(xmlpath)

        return element

    def get_element_info(self, element="", attr=None, key=""):
        """Retrieves element and/or element attribute information from the
        _pipeline_elements dictionary. The element can be specified directly or
        guessed from an xmlpath. An attribute can be specified with attr or
        null to return a dictionary of all element attribute values. If attr
        is left None no attributes are returned. Key specifies the dictionary
        info to return.

        element = dictionary element or xmlpath to guess element type from
        attr = attribute or null to retrieve all attributes (None ignores)
        key = key to info to retrives from _pipeline_elements dictionary
        return = attribute, dictionary of {attr:"value",...} or None if error
        """

        if DEBUG_PRINT:
            print("PipelineManager.get_element_info()")

        def get_key(element, key):
            """
            Retrieve a key in an element or attribute of the _pipeline_element
            dictionary, interpreting how to retrieve the data according to the
            key's name.

            element = pointer to a element or
                      attribute key in _pipeline_element
            key = the name of the key to retrieve data from
            """

            if DEBUG_PRINT:
                print("PipelineManager.get_element_info().get_key()")

            if key == 'default':
                value = element['options'][element[key]]
            else:
                value = element[key]

            return value

        try:
            # If not an xmlpath use as element
            if element in self._pipeline_elements:
                e = element
            # Otherwise guess element from path
            else:
                segs = element.split("/")
                segl = len(segs)

                if segl == 1:  # If root
                    e = "pipeline"
                elif segl == 2:  # If category
                    e = segs[-1]
                elif segl == 3:  # If sub category (drop "s" in name)
                    e = segs[-2][:-1]
                elif segl == 4:  # If panel category
                    e = segs[-1]
                elif "regexes" in segs:  # If in regexes
                    e = "regex"
                elif "properties" in segs:  # If in properties
                    e = "property"
                else:  # Otherwise must be a layout
                    # If has text a container
                    t = self.get_element(element).text

                    if t:
                        e = "container"
                    else:
                        e = "widget"

            # Get attribute
            if attr is not None:
                # Directly access attribute
                if attr:
                    k = self._pipeline_elements[e]['attributes'][attr]
                    value = get_key(k, key)
                # Otherwise return all element attributes and
                # values in dictionary
                else:
                    value = {}

                    for a in self._pipeline_elements[e]['attributes']:
                        k = self._pipeline_elements[e]['attributes'][a]
                        value[a] = get_key(k, key)
            # Otherwise use root of element
            else:
                k = self._pipeline_elements[e]
                value = get_key(k, key)
        except:
            value = None

        return value

    # #### Public utility methods

    def slmeta_to_panel(self, filepath, library, pipeline, panel,
        write=True, **attribs):
        """Generates an XML shader panel element from a K3D slmeta file.

        filepath = path and name of slmeta file to build panel from
        library = RIB path to shader's library if any
                  (prefixed to shader name)
        pipeline = name of pipeline to create panel in
        panel = name of new panel
                (if already exists will be updated from slmeta)
        write = write changes to pipeline text
        attribs = XML attributes to add to panel element
        """

        if DEBUG_PRINT:
            print("PipelineManager.slmeta_to_panel()")

        try:
            rm.RibmosaicInfo("PipelineManager.slmeta_to_panel:"
                " Generating panel from " + filepath + "...")

            # Resolve any links in filepath into a real path
            ec = rm_context.ExportContext()
            ec.context_pipeline = pipeline

            # Collect meta information
            linkpath = ec._resolve_links(filepath)
            abspath = os.path.realpath(bpy.path.abspath(linkpath))
            slmeta = ET.ElementTree(file=abspath)
            slinfo = slmeta.find("shaders/shader")
            sldesc = slmeta.find("shaders/shader/description")
            slauth = slmeta.find("shaders/shader/authors")
            slcopy = slmeta.find("shaders/shader/copyright")
            slname = slinfo.attrib['name']
            sltype = slinfo.attrib['type']

            # If panel name not specified use shaders name
            if not panel:
                panel = slname

            links = {}
            attrib = {}
            xmlcat = pipeline + "/shader_panels"
            xmlpath = xmlcat + "/" + panel

            # If panel already exists copy user settings otherwise initialize
            shader = self.get_element(xmlpath)

            if shader is not None:
                for p in self.get_element(xmlpath + "/properties"):
                    if 'link' in p.attrib and p.attrib['link']:
                        links[p.tag] = p.attrib['link']

                attrib = dict(shader.attrib)
                self.get_element(xmlcat).remove(shader)
            else:
                attrib['slmeta'] = filepath
                attrib['library'] = library
                attrib['type'] = sltype.upper()
                attrib['filter'] = sltype.upper()

            # Apply meta info to new panel
            shader = self.new_element_tree(pipeline + "/shader_panels",
                                        panel, 'shader_panel', attribs=attrib)
            attrib = dict(shader.attrib)
            message = ""

            for a in [(slauth, 'authors'),
                      (slcopy, 'copyright'),
                      (sldesc, 'description')]:
                if a[0] is not None and a[0].text is not None:
                    lines = [l.strip() for l in a[0].text.splitlines() \
                        if l.strip()]
                    message += a[1].capitalize() + ":\\n" + \
                               "\\n".join(lines) + "\\n\\n"
                else:
                    message += a[1].capitalize() + ":\\n"

            attrib['description'] = message

            # Apply any user specified attributes
            for a in attribs.keys():
                attrib[a] = attribs[a]

            # Lets build type selection enumerator based on shader type
            if sltype.lower() == "light":
                enumtype = [("LightSource", "LightSource", ""),
                            ("AreaLightSource", "AreaLightSource", "")]
                enumdef = "LightSource"
                enumwin = "LAMP"
            elif sltype.lower() == "volume":
                enumtype = [("Atmosphere", "Atmosphere", ""),
                            ("Interior", "Interior", ""),
                            ("Exterior", "Exterior", "")]
                enumdef = "Atmosphere"
                enumwin = "WORLD"
            elif sltype.lower() == "imager":
                enumtype = [("Imager", "Imager", "")]
                enumdef = "Imager"
                enumwin = "CAMERA"
            elif sltype.lower() == "displacement":
                enumtype = [("Displacement", "Displacement", "")]
                enumdef = "Displacement"
                enumwin = "MATERIAL"
            else:
                enumtype = [("Surface", "Surface", "")]
                enumdef = "Surface"
                enumwin = "MATERIAL"

            # If windows not specified use enumerated window
            if not attrib['windows']:
                attrib['windows'] = enumwin

            # Lets build shader element structure
            shader.attrib = attrib
            rib = self.get_element(xmlpath + "/rib")
            rib_decoration = rib.text[1:]

            # Build fixed properties
            prop_text = self.get_element_info("property", None, "text")
            prop_tail = self.get_element_info("property", None, "tail")
            prop_def = self.get_element_info("property", "", "default")
            widget_text = self.get_element_info("widget", None, "text")
            widget_tail = self.get_element_info("widget", None, "tail")
            widget_def = self.get_element_info("widget", "", "default")
            cont_text = self.get_element_info("container", None, "text")
            cont_tail = self.get_element_info("container", None, "tail")
            cont_def = self.get_element_info("container", "", "default")

            self._new_element(xmlpath + "/properties", "sl_name",
                              prop_text,
                              prop_tail,
                              attribs=prop_def,
                              default=slname,
                              description="Shader's name",
                              type='STRING')
            self._new_element(xmlpath + "/properties", "sl_type",
                              prop_text,
                              prop_tail,
                              attribs=prop_def,
                              type='ENUM',
                              default=enumdef,
                              description="Choose shader type",
                              items=str(enumtype))

            # Build fixed layouts
            self._new_element(xmlpath + "/layout", "info_row",
                              cont_text,
                              cont_tail,
                              attribs=cont_def,
                              type='SPLIT',
                              percent="0.8",
                              align="True")
            self._new_element(xmlpath + "/layout/info_row", "sl_name",
                              widget_text,
                              widget_tail,
                              attribs=widget_def,
                              prop="sl_name",
                              text="Name",
                              type='PROP')
            self._new_element(xmlpath + "/layout/info_row", "sl_type",
                              widget_text,
                              widget_tail,
                              attribs=widget_def,
                              prop="sl_type",
                              text="",
                              type='PROP')

            # Build RIB shader call
            rib.text = "\n@[DATA:///properties/sl_type:]@ \"" + \
                              attrib['library'] + slname + "\""

            if sltype.lower() == "light":
                rib.text += " @[EVAL:.current_lightid:]@"

            rib.text += "\n"

            # Lets build the parameters properties and layouts
            for p in slmeta.findall("shaders/shader/argument"):
                attribs = {'name': "", 'description': "",
                           'storage_class': "uniform",
                           'type': "string", 'default_value': "",
                           'array_count': "1",
                           'min': "", 'max': ""}

                # Pass any slmeta element attributes to the button element
                for a in attribs:
                    if a in p.attrib:
                        attribs[a] = p.attrib[a]

                # Build RIB parameter
                rib.text += "    \"" + attribs['storage_class'] + \
                            " " + attribs['type']

                array_count = int(attribs['array_count'])
                root_layout = xmlpath + "/layout"

                try:
                    # Attempt to translate default values into Python
                    if attribs['default_value'].startswith("{") or \
                       attribs['default_value'].startswith("("):
                        d = eval(attribs['default_value'].replace("{", "[") \
                                 .replace("}", "]").replace(",", ", "))

                        test = d[0]
                    elif attribs['type'] == 'float':
                        d = float(attribs['default_value'])
                    elif attribs['type'] == 'string':
                        d = attribs['default_value']
                    else:
                        d = eval("(" + attribs['default_value'] \
                                 .replace(" ", ",") + ")")

                    # Verify we have the correct number of elements
                    if type(d) == tuple:
                        if attribs['type'] == 'matrix':
                            test = d[15]
                        else:
                            test = d[2]
                except:
                    # Build sane defaults if could not determine from XML
                    if attribs['type'] == 'float':
                        d = "0"
                    elif attribs['type'] == 'string':
                        d = ""
                    elif attribs['type'] == 'matrix':
                        d = "(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)"
                    else:
                        d = "(0, 0, 0)"

                # Expand single entry defaults into list for arrays
                if type(d) != list:
                    d = [d for i in range(array_count)]

                # Setup for array parameters
                if array_count > 1:
                    # Root layout element for array controls
                    self._new_element(root_layout, attribs['name'] + "_lb",
                                      widget_text,
                                      widget_tail,
                                      attribs=widget_def,
                                      type='LABEL',
                                      text=attribs['name'] + " [ " + \
                                           str(array_count) + " ]")
                    self._new_element(root_layout, attribs['name'] + "_col",
                                      cont_text,
                                      cont_tail,
                                      attribs=cont_def,
                                      box="True",
                                      type='COLUMN')
                    root_layout += "/" + attribs['name'] + "_col"

                    # Add array length to RIB
                    rib.text += "[" + str(array_count) + "]"

                # Add parameter name to RIB
                rib.text += " " + attribs['name'] + "\""

                # arrays need [ ] bracketing
                if array_count > 1:
                    rib.text += " ["

                # Generate number of properties according to array count
                for i in range(array_count):
                    # Force control bounds for certain types
                    if attribs['type'] == 'color':
                        attribs['min'] = "0.0"
                        attribs['max'] = "1.0"

                    # Name according to array count
                    if array_count > 1:
                        n = str(i + 1)
                    else:
                        n = attribs['name']

                    lb_name = attribs['name'] + "_lb" + str(i)
                    prop_name = attribs['name'] + "_prop" + str(i)
                    op_name = attribs['name'] + "_op" + str(i)

                    # Restore links if any
                    if prop_name in links:
                        prop_link = links[prop_name]
                    else:
                        prop_link = ""

                    # Build property
                    self._new_element(xmlpath + "/properties", prop_name,
                                      prop_text,
                                      prop_tail,
                                      attribs=prop_def,
                                      description=attribs['description'],
                                      default=str(d[i]),
                                      type=attribs['type'].upper(),
                                      min=attribs['min'],
                                      max=attribs['max'],
                                      softmin=attribs['min'],
                                      softmax=attribs['max'],
                                      link=prop_link)

                    # Build layout, label, widget and link operator
                    prop_layout = attribs['name'] + "_row" + str(i)

                    self._new_element(root_layout, prop_layout,
                                      cont_text,
                                      cont_tail,
                                      attribs=cont_def,
                                      type='ROW',
                                      active="@[EVAL:not @[ATTR:///properties/"
                                              + prop_name + ".link:STR]@:]@")

                    prop_layout = root_layout + "/" + prop_layout

                    self._new_element(prop_layout, lb_name,
                                      widget_text,
                                      widget_tail,
                                      attribs=widget_def,
                                      type='LABEL',
                                      text=n)
                    self._new_element(prop_layout, "prop_col",
                                      cont_text,
                                      cont_tail,
                                      attribs=cont_def,
                                      type='COLUMN')
                    self._new_element(prop_layout + "/prop_col", prop_name,
                                      widget_text,
                                      widget_tail,
                                      attribs=widget_def,
                                      text="",
                                      type='PROP',
                                      prop=prop_name)
                    self._new_element(prop_layout, op_name,
                                      widget_text,
                                      widget_tail,
                                      attribs=widget_def,
                                      type='LINK',
                                      text="",
                                      trigger="@[PATH:///properties/" + \
                                              prop_name + ":]@")

                    # Add DATA link to RIB to insert buttons value
                    rib.text += " @[DATA:///properties/" + prop_name + ":RIB]@"
                # Finish RIB parameter
                if array_count > 1:
                    rib.text += " ]"
                rib.text += "\n"
            # Reapply RIB text decoration
            rib.text += "\n" + rib_decoration

            # Lets update panel
            if write:
                self._write_xml(pipeline)

            if eval(attrib['register']):
                self._unregister_panel(pipeline, "shader_panels", panel)
                self._register_panel(pipeline, "shader_panels", panel)

            del slmeta
            del ec
        except:
            rm.RibmosaicInfo("PipelineManager.slmeta_to_panel:"
                " Could not load slmeta " + filepath)
