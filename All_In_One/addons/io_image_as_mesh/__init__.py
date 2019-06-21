# -*- coding: utf-8 -*-

import os
import sys
import bpy
from bpy_extras.io_utils import ImportHelper
from bpy.props import CollectionProperty
from io_image_as_mesh.image_as_mesh import create_mesh_from_image

bl_info = {
    "name": "Image as Mesh Importer",
    "description": "Import Image as Mesh.",
    "author": "Banbury",
    "version": (1, 2, 0),
    "blender": (2, 79, 0),
    "location": "File > Import",
    "wiki_url": "",
    "category": "Learnbgame",
}


class ImageAsMeshOps(bpy.types.Operator, ImportHelper):
    """LDR Importer Operator"""
    bl_idname = "import_scene.image_as_mesh"
    bl_description = "Import an image as a mesh."
    bl_label = "Import Image as Mesh"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_options = {'REGISTER', 'UNDO', 'PRESET'}

    # File type filter in file browser
    filename_ext = ".png"

    filter_glob = bpy.props.StringProperty(
        default="*.png",
        options={'HIDDEN'}
    )

    files = CollectionProperty(type=bpy.types.PropertyGroup)

    subdivide = bpy.props.BoolProperty(
        name="Subdivide", description="Creates smaller triangles.")

    def execute(self, context):
        dir = os.path.dirname(self.filepath)

        for f in self.files:
            path = os.path.join(dir, f.name)
            img = bpy.data.images.load(path, check_existing=True)
            obj = create_mesh_from_image(img)

            if self.subdivide:
                sub = obj.modifiers.new(name="Subsurf", type="SUBSURF")
                sub.subdivision_type = 'SIMPLE'
                sub.levels = 3
                sub.render_levels = 3
                dec = obj.modifiers.new(name="Decimate", type="DECIMATE")
                dec.decimate_type = 'COLLAPSE'
                dec.ratio = 0.1
                dec.use_symmetry = True
                dec.use_collapse_triangulate = True

        return {'FINISHED'}


def menu_import(self, context):
    """Import menu listing label"""
    self.layout.operator(ImageAsMeshOps.bl_idname, text="Image as Mesh (.png)")


def register():
    """Register Menu Listing"""
    bpy.utils.register_module(__package__)
    bpy.types.INFO_MT_file_import.append(menu_import)


def unregister():
    """Unregister Menu Listing"""
    bpy.utils.unregister_module(__package__)
    bpy.types.INFO_MT_file_import.remove(menu_import)


if __name__ == "__main__":
    register()
