# -*- coding: utf8 -*-
#
# ***** BEGIN GPL LICENSE BLOCK *****
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.
#
# ***** END GPL LICENCE BLOCK *****
#
# --------------------------------------------------------------------------
# Blender Version                     2.68
# Exporter Version                    0.0.4
# Created on                          26-Aug-2013
# Author                              NodeBench
# --------------------------------------------------------------------------


import os

bl_info = {
    "name"       : "Sunflow",
    "description": "Sunflow Render System (v0.07.3) integration for Blender (>2.67)",
    "author"     : "Nodebench" ,
    "version"    : (0, 0, 4),
    "blender"    : (2, 68, 0),
    "api"        : 58537,
    "category": "Learnbgame",
    "location"   : "Info header > render engine menu",
    "warning"    : "Pre beta version, may crash.",
    "wiki_url"   : "https://github.com/nodebench/Exporter/wiki",
    "tracker_url": "https://github.com/nodebench/Exporter/issues",
    "tooltip"    : "Sunflow Open Source Rendering System (v0.07.3) Exporter",
    "license"    : "GPL Version 2",
    "download"   : "https://github.com/nodebench/Exporter/wiki",
    "link"       : "http://sunflow.sourceforge.net/"
    }

def plugin_path():
    return os.path.dirname(os.path.realpath(__file__))

if 'core' in locals():
    import imp
    imp.reload(core)
else:
    import bpy
    
    from extensions_framework import Addon
    SunflowAddon = Addon(bl_info)
    register, unregister = SunflowAddon.init_functions()
    
    # Importing the core package causes extensions_framework managed
    # RNA class registration via @SunflowAddon.addon_register_class
    from . import core
    
