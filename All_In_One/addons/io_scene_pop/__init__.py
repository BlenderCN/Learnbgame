bl_info = {
    "name": "PoP map",
    "author": "Sphere",
    "version": (0, 1),
    "blender": (2, 72, 0),
    "location": "File > Import > PoP map",
    "description": "Import PoP map",
    "category": "Learnbgame"
}


import bpy
import bpy.ops
import bpy_extras
import os
from bpy.props import StringProperty, BoolProperty
from io_scene_pop import popmap


class ImportPopWow(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    bl_idname = "import_scene.popwow"
    bl_label = "Import PoP wow"
    bl_description = "Opens decompressed .bin files and imports the " \
                     "contained map."
    bl_options = {'UNDO'}

    filename_ext = ".dec"
    filter_glob = StringProperty(default="*.dec", options={'HIDDEN'})
    filepath = StringProperty(name="File path")

    def error(self, msg):
        self.report({'ERROR'}, msg)

    def execute(self, context):
        if "wow" in self.filepath:
            wow_hashes = popmap.create_wowlist(os.path.dirname(
                                               self.filepath))
            popmap.import_wow(self.filepath, context, False, wow_hashes)
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "Selected file does not contain 'wow'!")
            return {'CANCELLED'}

            
class ImportPopWows(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    bl_idname = "import_scene.popmaps"
    bl_label = "Import PoP wows"
    bl_options = {'UNDO'}

    filername_ext = ""
    filter_glob = StringProperty(default="", options={'HIDDEN'})
    directory = StringProperty(subtype='DIR_PATH')
    textures_only = BoolProperty(name="Textures only",
                                 description="Whether to import only the "
                                             "textures")

    def execute(self, context):
        wow_hashes = popmap.create_wowlist(self.directory)    
        for file in os.listdir(self.directory):
            path = os.path.join(self.directory, file)
            if (os.path.isfile(path) and path.endswith(".dec") and
                "wow" in path):
                try:
                    popmap.import_wow(path, context, self.textures_only,
                                      wow_hashes)
                except:
                    raise RuntimeError("Error while importing '" + file + 
                                       "'!")
        return {'FINISHED'}
        
        
class ImportPopWol(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    bl_idname = "import_scene.popwol"
    bl_label = "Import PoP wol"
    bl_description = "Opens decompressed .bin files and imports the " \
                     "contained maps."
    bl_options = {'UNDO'}

    filename_ext = ".dec"
    filter_glob = StringProperty(default="*.dec", options={'HIDDEN'})
    filepath = StringProperty(name="File path")

    def error(self, msg):
        self.report({'ERROR'}, msg)

    def execute(self, context):
        if "wol" in self.filepath:
            wow_hashes = popmap.create_wowlist(os.path.dirname(
                                               self.filepath))
            popmap.import_wol(self.filepath, context, wow_hashes)
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "Selected file does not contain 'wol'!")
            return {'CANCELLED'}
            
            
class ImportPopCurrWol(bpy.types.Operator):
    bl_idname = "import_scene.popcurrwol"
    bl_label = "Import current wol"
    bl_description = "Import the wol of the currently selected trigger."
    bl_options = {'UNDO'}

    def error(self, msg):
        self.report({'ERROR'}, msg)

    def execute(self, context):
        if "wol_to_load" in context.active_object:
            path = context.active_object["wol_to_load"]
            # delete everything
            bpy.ops.object.mode_set(mode='OBJECT')
            for object in context.scene.objects:
                object.hide = False
            bpy.ops.object.select_all(action='SELECT')
            bpy.ops.object.delete()
            
            wow_hashes = popmap.create_wowlist(os.path.dirname(path))
            popmap.import_wol(path, context, wow_hashes)
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "The selected object is not a valid "
                                   "loading trigger!")
            return {'CANCELLED'}

            
class PoPPanel(bpy.types.Panel):
    """A Custom Panel in the Viewport Toolbar"""
    bl_label = "PoP Tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'

    def draw(self, context):
        layout = self.layout
        object = context.active_object
    
        if "out_of_file" in object:
            row = layout.row()
            row.label(text="Object is from file:")
            row = layout.row()
            row.label(text="'" + object["out_of_file"] + ".dec'")
            if "wol_to_load" in object:
                layout.separator()
                row = layout.row()
                row.label(text="This trigger loads:")
                row = layout.row()
                row.label(text="'" + 
                          os.path.basename(object["wol_to_load"]) + "'")
                row = layout.row()
                row.operator("import_scene.popcurrwol",
                             text="Activate Trigger")
            

def menu_import(self, context):
    self.layout.operator(ImportPopWol.bl_idname, text="PoP wol")
    self.layout.operator(ImportPopWow.bl_idname, text="PoP wow")
    self.layout.operator(ImportPopWows.bl_idname, text="PoP wows")


def register():
    bpy.utils.register_class(ImportPopWow)
    bpy.utils.register_class(ImportPopWows)
    bpy.utils.register_class(ImportPopWol)
    bpy.utils.register_class(ImportPopCurrWol)
    bpy.utils.register_class(PoPPanel)
    bpy.types.INFO_MT_file_import.append(menu_import)


def unregister():
    bpy.utils.unregister_class(ImportPopWow)
    bpy.utils.unregister_class(ImportPopWows)
    bpy.utils.unregister_class(ImportPopWol)
    bpy.utils.unregister_class(ImportPopCurrWol)
    bpy.utils.unregister_class(PoPPanel)
    bpy.types.INFO_MT_file_import.remove(menu_import)


if __name__ == "__main__":
    unregister()
    register()
