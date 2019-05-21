# TODO(david): blender register/unregister and other setup
bl_info = {
        "name" : "Sketch 4 Blender",
        "author" : "David Karwowski",
        "version" : (1, 0, 0),
        "location" : "File > Import-Export",
        "description" : "Import Sketch (*.sk) Files into Blender objects",
        "category" : "Import-Export",
}

import os

import bpy
from bpy.props import (
        StringProperty,
        )
from bpy_extras.io_utils import (
        ImportHelper,
        )
from .parser import SketchParser
from .geometry import Transform

parser = None


class ImportSK(bpy.types.Operator, ImportHelper):
    """Load a SK Sketch File"""
    bl_idname = "import_mesh.sk"
    bl_label = "Import SK Sketch File"
    check_extension = True
    filename_ext = ".sk"
    filter_glob = StringProperty(
            default="*.sk",
            options={'HIDDEN'},
    )

    def execute(self, context):
        keywords = self.as_keywords(ignore=('filter_glob',))
        filepath = os.fsencode(keywords["filepath"])
        with open(filepath, 'r') as sk_file:
            objects = parser.parse(sk_file.read())
            for obj in objects:
                obj = obj.flatten(Transform.Identity(4))#parser.env.camera)
                obj.render_to_blender(context)
            #print(objects)
        parser.reset()
        return {"FINISHED"}

def menu_func_import(self, context):
    self.layout.operator(ImportSK.bl_idname, text="Sketch File (.sk)")

def register():
    global parser

    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_import.append(menu_func_import)

    parser = SketchParser(optimize=1)

def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_import.remove(menu_func_import)


if __name__=="__main__":
    register()

