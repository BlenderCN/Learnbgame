# -*- coding: utf-8 -*-
import os
import bpy
from bpy.props import StringProperty, BoolProperty, FloatProperty, IntProperty, PointerProperty, CollectionProperty
from bpy.types import Operator, AddonPreferences
from bpy_extras.io_utils import ImportHelper


bl_info = {
    "name": "OpenSCAD importer",
    "description": "Imports OpenSCAD (.scad) files.",
    "author": "Maqq",
    "version": (1, 2),
    "blender": (2, 73, 0),
    "location": "File > Import",
    "warning": "", # used for warning icon and text in addons panel
    "category": "Import-Export"
}

# Temporary stl file
TEMPNAME = "tempexport.stl"


def read_openscad(context, filepath, scale, parameters):
    """ Exports stl using OpenSCAD and imports it. """
    from io_mesh_stl import stl_utils
    from io_mesh_stl import blender_utils
    from mathutils import Matrix
    
    user_preferences = context.user_preferences
    addon_prefs = user_preferences.addons[__name__].preferences
    openscad_path = addon_prefs.filepath
    tempfile_path = os.path.join(os.path.dirname(filepath), TEMPNAME)

    # Export stl from OpenSCAD
    command = "\"\"%s\" -o \"%s\" \"%s\"\"" % \
        (openscad_path, tempfile_path, filepath)
    
    print("Executing command:", command)
    os.system(command)
    
    if os.path.exists(tempfile_path):
        if bpy.ops.object.mode_set.poll():
            bpy.ops.object.mode_set(mode='OBJECT')
    
        if bpy.ops.object.select_all.poll():
            bpy.ops.object.select_all(action='DESELECT')

        global_matrix = Matrix.Scale(scale, 4) # Create 4x4 scale matrix
        obj_name = os.path.basename(filepath).split('.')[0]
        tris, pts = stl_utils.read_stl(tempfile_path)
        blender_utils.create_and_link_mesh(obj_name, tris, pts, global_matrix)
        os.remove(tempfile_path)
    else:
        print("Temporary export file not found:", tempfile_path)
    
    return {'FINISHED'}


class OpenSCADImporterPreferences(AddonPreferences):
    """ Addon preferences. """
    bl_idname = __name__

    filepath = StringProperty(
            name="Path to OpenSCAD executable",
            subtype='FILE_PATH',
            )

    def draw(self, context):
        self.layout.prop(self, "filepath")


class OpenSCADImporter(Operator, ImportHelper):
    """ Import OpenSCAD files. """
    bl_idname = "import_mesh.scad"
    bl_label = "Import OpenSCAD"

    # ImportHelper mixin class uses this
    filename_ext = ".scad"

    filter_glob = StringProperty(
            default="*.scad",
            options={'HIDDEN'},
            )

    scale = FloatProperty(name='Scale', default=1.0)

    # Parameters for the scad file
    p1  = StringProperty(name='P1 name')
    p1v = StringProperty(name='P1 value')
    p2  = StringProperty(name='P2 name')
    p2v = StringProperty(name='P2 value')
    p3  = StringProperty(name='P3 name')
    p3v = StringProperty(name='P3 value')
    p4  = StringProperty(name='P4 name')
    p4v = StringProperty(name='P4 value')

    def __init__(self):
        super(OpenSCADImporter, self).__init__()

    def execute(self, context):
        return read_openscad(context, self.filepath, self.scale, {self.p1:self.p1v, self.p2:self.p2v, self.p3:self.p3v, self.p4:self.p4v})


def menu_func_import(self, context):
    self.layout.operator(OpenSCADImporter.bl_idname, text="OpenSCAD (.scad)")

def register():
    bpy.utils.register_class(OpenSCADImporter)
    bpy.utils.register_class(OpenSCADImporterPreferences)
    bpy.types.INFO_MT_file_import.append(menu_func_import)

def unregister():
    bpy.utils.unregister_class(OpenSCADImporter)
    bpy.types.INFO_MT_file_import.remove(menu_func_import)

if __name__ == "__main__":
    pass
