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
# Initialization and global functions/variables.
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

bl_info = {
    "name": "RIB Mosaic",
    "author": "Eric Back (WHiTeRaBBiT)",
    "version": (0, 1, 1),
    "blender": (2, 5, 7),
    "api": 36103,
    "location": "Info Header (engine dropdown)",
    "description": "RenderMan production environment for Blender",
    "warning": "GIT Alpha",
    "wiki_url": "http://wiki.aqsis.org/guide/ribmosaic_install",
    "tracker_url": "http://sourceforge.net/projects/ribmosaic/develop",
    "category": "Learnbgame"
}


import os

# #############################################################################
# GLOBAL VARIABLES, FUNCTIONS AND CLASSES
# #############################################################################

# #### Global variables

MODULE = os.path.dirname(__file__).split(os.sep)[-1]
ENGINE = bl_info['name']
VERSION = ".".join([str(d) for d in bl_info['version']])
pipeline_manager = None
export_manager = None
ribify = None


# #### Manage modules
if "bpy" in locals():
    import imp
    imp.reload(rm_pipeline)
    imp.reload(rm_export)
    imp.reload(rm_ribify)
    imp.reload(rm_property)
    imp.reload(rm_panel)
    imp.reload(rm_operator)
else:
    import bpy
    from bpy.props import StringProperty, BoolProperty, IntProperty, \
        FloatProperty, FloatVectorProperty, EnumProperty
    exec("from " + MODULE + " import rm_pipeline")
    exec("from " + MODULE + " import rm_export")
    exec("from " + MODULE + " import rm_ribify")
    exec("from " + MODULE + " import rm_property")
    exec("from " + MODULE + " import rm_panel")
    exec("from " + MODULE + " import rm_operator")


# #### Global functions

def RibmosaicInfo(message, operator=None):
    """UI and console info messages"""

    if operator:
        operator.report({'INFO'}, message)

    print(ENGINE + " Info: " + message)


def PropertyHash(name):
    """Converts long property names into a 30 character or less hash"""

    return "P" + str(hash(name))[:30].replace("-", "N")


def RibPath(path):
    """Makes path RIB safe for search and archive paths"""

    return path.strip().replace(os.sep, "/")


# #############################################################################
# BLENDER REGISTRATION AND UNREGISTRATION
# #############################################################################

from bl_ui import space_text


def register():
    """Register Blender classes and setup class properties"""

    global pipeline_manager, export_manager, ribify

    # Ensure that only one RIB Mosaic addon is currently enabled
    for module in [a.module for a in bpy.context.user_preferences.addons]:
        if module != MODULE:
            exec("try:\n"
                 "\timport " + module + "\n"
                 "\t" + module + ".pipeline_manager\n"
                 "\tdel " + module + "\n"
                 "\tbpy.utils.addon_disable('" + module + "')\n"
                 "except:\n"
                 "\tpass\n")

    # Create our properties
    rm_property.create_props()

    # Add draw functions
    space_text.TEXT_MT_toolbox.append(rm_panel.ribmosaic_text_menu)

    # Create our manager objects
    pipeline_manager = rm_pipeline.PipelineManager()
    export_manager = rm_export.ExporterManager()

    # Try loading ribify module, otherwise initiate ribify class object
    try:
        import ribify
        RibmosaicInfo("ribify module found, using C level exporter")
    except ImportError:
        ribify = rm_ribify.Ribify()
        RibmosaicInfo("ribify module not found, using script level exporter")

    bpy.utils.register_module(__name__)
    bpy.ops.wm.ribmosaic_modal_sync()


def unregister():
    """Unregister Blender classes"""

    global pipeline_manager, export_manager, ribify

    # Make sure default blender engine is selected
    bpy.context.scene.render.engine = 'BLENDER_RENDER'

    # Destroy our manager objects
    pipeline_manager = None
    export_manager = None
    ribify = None

    # Remove draw functions
    space_text.TEXT_MT_toolbox.remove(rm_panel.ribmosaic_text_menu)

    # Destroy our properties
    rm_property.destroy_props()

    bpy.utils.unregister_module(__name__)


if __name__ == "__main__":
    register()
