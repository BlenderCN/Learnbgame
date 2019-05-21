#    BlenderFDS, an open tool for the NIST Fire Dynamics Simulator
#    Copyright (C) 2013  Emanuele Gissi, http://www.blenderfds.org
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""BlenderFDS"""

print("""
    BlenderFDS  Copyright (C) 2013 Emanuele Gissi, http://www.blenderfds.org
    This program comes with ABSOLUTELY NO WARRANTY.
    This is free software, and you are welcome to redistribute it
    under certain conditions; see included license file for details.
""")

bl_info = {
    "name": "BlenderFDS",
    "author": "Emanuele Gissi",
    "version": (3, 0, 0),
    "blender": (2, 7, 3),
    "api": 35622,
    "location": "File > Export > FDS Case (.fds)",
    "description": "BlenderFDS, an open graphical editor for the NIST Fire Dynamics Simulator",
    "warning": "",
    "wiki_url": "http://www.blenderfds.org/",
    "tracker_url": "http://code.google.com/p/blenderfds/issues/list",
    "support": "COMMUNITY",
    "category": "Import-Export",
}

### Import/Reimport

if "bpy" in locals():
    import imp
    imp.reload(fds)
    imp.reload(ui)
    imp.reload(types)
else:
    import bpy
    from . import fds
    from . import ui
    from . import types

### Registration/Unregistration

def register():
    """Register Blender types"""
    # Register module classes (Eg. panels, ...)
    bpy.utils.register_module(__name__)
    # Register namelists, their properties, and the panels
    for bf_namelist in types.bf_namelists: bf_namelist.register()
    # Register menus
    bpy.types.INFO_MT_file_export.append(ui.menus.export_fds_menu)
    bpy.types.INFO_MT_file_import.append(ui.menus.import_fds_menu)
    # Register handlers
    bpy.app.handlers.load_post.append(ui.handlers.load_post)
    bpy.app.handlers.save_pre.append(ui.handlers.save_pre)
    # Simplify Blender UI
    if bpy.context.user_preferences.addons["blenderfds"].preferences.bf_pref_simplify_ui:
        ui.simplify_bl.less_space_properties()
        ui.simplify_bl.unregister_unused_classes()
    
def unregister():
    """Unregister Blender types"""
    # Unregister module classes
    bpy.utils.unregister_module(__name__)
    # Unregister namelists, their properties, and the panels
    for bf_namelist in types.bf_namelists: bf_namelist.unregister()
    # Unregister menus
    bpy.types.INFO_MT_file_export.remove(ui.menus.export_fds_menu)
    bpy.types.INFO_MT_file_import.remove(ui.menus.import_fds_menu)
    # Unregister handlers
    bpy.app.handlers.load_post.remove(ui.handlers.load_post)
    bpy.app.handlers.save_pre.remove(ui.handlers.save_pre)    

if __name__ == "__main__":
    register()
