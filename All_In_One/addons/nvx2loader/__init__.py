# ##### BEGIN GPL LICENSE BLOCK #####
#
# nvx2loader. Copyright 2012-2017 Attila Gyoerkoes
#
# Neverblender is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# Neverblender is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Neverblender.  If not, see <http://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####

"""TODO: DOC."""

bl_info = {
    "name": "nvx2loader",
    "author": "Attila Gyoerkoes",
    'version': (1, 0),
    "blender": (2, 7, 2),
    "location": "File > Import-Export",
    "description": "Import Nebula NVX files",
    "warning": "",
    "wiki_url": ""
                "",
    "tracker_url": "",
    "category": "Learnbgame"
}

if "bpy" in locals():
    import importlib
    if "import_nvx2" in locals():
        importlib.reload(import_nvx2)
    if "import_nax" in locals():
        importlib.reload(import_nax)

import bpy
import bpy_extras


class ImportNVX2(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    """Load a Nebula NVX2 File"""
    bl_idname = "import_scene.nvx2"
    bl_label = "Import NVX2"
    bl_options = {'UNDO'}

    filename_ext = ".nvx2"
    filter_glob = bpy.props.StringProperty(
            default="*.nvx2",
            options={'HIDDEN'},
            )

    create_parent_empty = bpy.props.BoolProperty(
            name="Create Parent Empty",
            description="Create an empty "
                        "which all imported objects will be parented to",
            default=True,
            )

    single_material = bpy.props.BoolProperty(
            name="Single Material",
            description="Create only a single material for all meshes ",
            default=False,
            )

    use_image_search = bpy.props.BoolProperty(
            name="Image Search",
            description="Search subdirs for any associated images "
                        "(Warning, may be slow)",
            default=False,
            )

    def execute(self, context):
        from . import import_nvx2

        keywords = self.as_keywords(ignore=('filter_glob',
                                            'check_existing'))
        return import_nvx2.load(context, **keywords)


class ImportNAX(bpy.types.Operator, bpy_extras.io_utils.ImportHelper):
    """Load a Nebula NAX2 File"""
    bl_idname = "import_scene.nax"
    bl_label = "Import NAX"
    bl_options = {'UNDO'}

    filename_ext = ".nax2"
    filter_glob = bpy.props.StringProperty(
            default="*.nax2",
            options={'HIDDEN'},
            )

    def execute(self, context):
        from . import import_nax

        keywords = self.as_keywords(ignore=('filter_glob',
                                            'check_existing'))
        return import_nax.load(context, **keywords)


def menu_func_import(self, context):
    """TODO:Doc."""
    self.layout.operator(ImportNVX2.bl_idname,
                         text="Nebula mesh (.nvx2)")
    # self.layout.operator(ImportNAX.bl_idname,
    #                     text="Nebula animation (.nax2, .nax3)")


def register():
    """TODO:Doc."""
    bpy.utils.register_module(__name__)

    bpy.types.INFO_MT_file_import.append(menu_func_import)


def unregister():
    """TODO:Doc."""
    bpy.types.INFO_MT_file_import.remove(menu_func_import)

    bpy.utils.unregister_module(__name__)


if __name__ == "__main__":
    register()
