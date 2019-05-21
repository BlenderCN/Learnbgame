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


bl_info = {
    "name": "Import cache(s)",
    "author": "Jasper van Nieuwenhuizen",
    "version": (0, 1),
    "blender": (2, 6, 6),
    "location": "File > Import > Import cache(s)",
    "description": "Import point cache(s)",
    "warning": "wip",
    "wiki_url": "",
    "tracker_url": "",
    "support": 'COMMUNITY',
    "category": "Learnbgame"
}


import bpy
from bpy.props import StringProperty, EnumProperty, CollectionProperty, BoolProperty
from bpy_extras.io_utils import ImportHelper
from os import path
from glob import glob

# Actual import operator.
class ImportCaches(bpy.types.Operator, ImportHelper):
    '''Import cache(s)'''
    bl_idname = "import_scene.caches"
    bl_label = "Import cache(s)"
    bl_options = {'PRESET', 'UNDO'}
    
    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.
    directory = StringProperty(maxlen=1024,
        subtype='DIR_PATH',
        options={'HIDDEN', 'SKIP_SAVE'})
    files = CollectionProperty(type=bpy.types.OperatorFileListElement,
        options={'HIDDEN', 'SKIP_SAVE'})

    filename_ext = ".pc2;.mdd"
    filter_glob = StringProperty(default="*.pc2;*.mdd", options={'HIDDEN'})

    use_relative_path = BoolProperty(
        name='Relative Path',
        description='Select the file relative to the blend file',
        default=True)

    cache_method = EnumProperty(
        name="",
        items=[('shape', "Shapekeys", "As shapekeys"),
            ('mod', "Modifier", "Mesh Cache Modifier")],
        description="How to import the pointcache(s)",
        default='mod')
    
    
    def execute(self, context):
        d = self.properties.directory
        fils = self.properties.files
        if not fils[0].name:
            # No files selected, getting all caches in the directory.
            import_pc2s = glob(path.join(d, "*.[pP][cC]2"))
            import_mdds = glob(path.join(d, "*.[mM][dD][dD]"))
            import_files = import_pc2s + import_mdds
        else:
            # Get the full path names for the files.
            import_files = [path.join(d, f.name) for f in fils]
        if import_files:
            # Import the caches and append the objects to "cache_objects".
            cache_objects = []
            for i, f in enumerate(import_files):
                # Determine the name of the object from the filename.
                name, ext = path.splitext(path.split(f)[1])
                print("Importing {ob} ({num} of {total})...".format(ob=name, num=i+1, total=len(import_files)))
                for ob in bpy.data.objects:
                    if ob.name == name:
                        # Found the object, make it the active scene object.
                        context.scene.objects.active = ob
                        cache_objects.append(ob)
                        # Check if the object already has a Mesh Cache modifier.
                        mc_mod = None
                        for m in ob.modifiers:
                            if m.type == "MESH_CACHE":
                                mc_mod = m
                        if self.cache_method == 'mod':
                            # Import the cache with the 'Mesh Cache Modifier'.
                            if not mc_mod:
                                mc_mod = ob.modifiers.new(name="Mesh Cache", type='MESH_CACHE')
                                # Dirty hack to move the mesh cache modifier to the top of the stack
                                for i in range(len(ob.modifiers)-1):
                                    bpy.ops.object.modifier_move_up(modifier=mc_mod.name)
                            # Determine to use relative path or not.
                            if context.blend_data.filepath and self.use_relative_path:
                                f = bpy.path.relpath(f)
                            # Set the properties of the Mesh Cache modifier.
                            mc_mod.show_render = True               # Render visibility.
                            mc_mod.show_viewport = True             # Viewport visibility.
                            mc_mod.cache_format = ext.upper()[1:]   # The cache format.
                            mc_mod.filepath = f                     # The filepath.
                            mc_mod.deform_mode = 'INTEGRATE'        # The deform mode.
                            mc_mod.frame_start = 1                  # The frame start.
                        else:
                            # Import the cache as shapekeys.
                            if mc_mod:
                                # Disable the modifier.
                                mc_mod.show_render = False
                                mc_mod.show_viewport = False
                            # Is it a .pc2 or a .mdd?
                            if ext.lower() == ".pc2":
                                try:
                                    bpy.ops.import_shape.pc2(filepath=f)
                                except AttributeError:
                                    print("PC2 importer seems not to be loaded, skipping object: {0}".format(name))
                            else:
                                try:
                                    bpy.ops.import_shape.mdd(filepath=f)
                                except AttributeError:
                                    print("MDD imported seems not to be loaded, skipping object: {0}".format(name))
            if cache_objects:
                # Select all the objects with imported caches and make the last one active.
                bpy.ops.object.select_all(action='DESELECT')
                for ob in cache_objects:
                    ob.select = True
                context.scene.objects.active = cache_objects[-1]

        return {'FINISHED'}
    
    
    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.separator()
        col.label(text="Cache Import Method:")
        col.prop(self, "cache_method")
        if self.cache_method == 'mod':
            col.separator()
            col.prop(self, "use_relative_path")


def menu_func_import(self, context):
    self.layout.operator(ImportCaches.bl_idname, text="Import cache(s)")


def register():
    bpy.utils.register_module(__name__)
    
    bpy.types.INFO_MT_file_import.append(menu_func_import)


def unregister():
    bpy.utils.unregister_module(__name__)
    
    bpy.types.INFO_MT_file_import.remove(menu_func_import)
    

if __name__ == "__main__":
    register()