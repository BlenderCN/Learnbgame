# File: __init__.py
# Needed for python to register this folder as a module and for blender to register/unregister the addon.

# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
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

# Variable: bl_info
# Contains informations for Blender to recognize and categorize the addon.
bl_info = {
    'name': 'Import OSM',
    'author': 'Ondrej Brinkel',
    'version': (3, 20),
    'blender': (2, 5, 7),
    'api': 36273,
    'location': 'File > Import/Export > OSM ',
    'description': 'Import Openstreetmap XML data',
    'warning': 'Depends on addon "Inset Polygon"!', # used for warning icon and text in addons panel
    'category': 'Import-Export'}

if "bpy" in locals():
    import imp
    imp.reload(import_osm)
    imp.reload(osm_ui)
    imp.reload(osm_types)
    imp.reload(osm_props)
    imp.reload(osm_ops)
    
else:
    import bpy
    from . import import_osm
    from . import osm_ui
    from . import osm_types
    from . import osm_props
    from . import osm_ops


# TODO: on newer Blender builds io_utils seems to be in bpy_extras, on older ones bpy_extras does not exists. Should be removed with the official Blender release where bpy_extras is present.
try:
    from bpy_extras.io_utils import ImportHelper, ExportHelper
except ImportError:
    from io_utils import ImportHelper, ExportHelper

class ImportOSM(bpy.types.Operator, ImportHelper):
    '''Load a OSM XML file'''
    bl_idname = "import_osm.xml"
    bl_label = "Import OSM XML"

    filepath = bpy.props.StringProperty(name="File Path", default= "")
    filename_ext = ".osm"
    filter_glob = bpy.props.StringProperty(default="*.osm", options={'HIDDEN'})
    create_tag_list = bpy.props.BoolProperty(name="Create Tag list",description="Creates an internal tags.txt containing listing all tags found in the OSM-xml.",default=False)

    def execute(self, context):
        return import_osm.load(self, context, self.properties.filepath)

    def draw(self,context):
        layout = self.layout
        row = layout.row()
        row.prop(self,'create_tag_list')
	

# Function: menu_func
# Adds the export option to the menu.
#
# Parameters:
#   self - Instance to something
#   context - The Blender context object
def menu_func(self, context):
    self.layout.operator(ImportOSM.bl_idname, text="OSM (.xml)")

# Function: register
# Registers the addon with all its classes and the menu function.
def register():
    osm_props.register_props()
    osm_ops.register_ops()
    osm_ui.register_ui()
    bpy.utils.register_class(ImportOSM)
    bpy.types.INFO_MT_file_import.append(menu_func)
    #bpy.utils.register_module(__name__)

# Function: unregister
# Unregisters the addon and all its classes and removes the entry from the menu.
def unregister():
    osm_props.unregister_props()
    osm_ops.unregister_ops()
    osm_ui.unregister_ui()
    bpy.utils.unregister_class(ImportOSM)
    bpy.types.INFO_MT_file_import.remove(menu_func)
    #bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()
