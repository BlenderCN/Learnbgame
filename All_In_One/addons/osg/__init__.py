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

import sys
import os
import bpy
import pickle
import argparse


bl_info = {
    "name": "Export OSG format (.osgt)",
    "author": "Cedric Pinson, Jeremy Moles, Peter Amstutz",
    "version": (0, 15, 0),
    "blender": (2, 7, 6),
    "email": "trigrou@gmail.com, jeremy@emperorlinux.com, peter.amstutz@tseboston.com",
    "api": 36339,
    "location": "File > Export > OSG Model (*.osgt)",
    "description": "Export models and animations for use in OpenSceneGraph",
    "warning": "",
    "wiki_url": "https://github.com/cedricpinson/osgexport/wiki",
    "tracker_url": "http://github.com/cedricpinson/osgexport",
    "category": "Learnbgame"
}

__url__ = bl_info["wiki_url"]
__email__ = bl_info["email"]
__author__ = bl_info["author"]
__bpydoc__ = bl_info["description"]
__version__ = bl_info["version"]

sys.path.insert(0, "./")
BlenderExporterDir = os.getenv("BlenderExporter",
                               os.path.join(bpy.context.user_preferences.filepaths.script_directory,
                                            "blenderExporter"))
print("BlenderExporter directory ", BlenderExporterDir)
sys.path.insert(0, BlenderExporterDir)

import osg
from osg import osgdata
from osg import osgconf


def OpenSceneGraphExport(config=None):
    export = osg.osgdata.Export(config)
    print("....................", config.filename)
    export.process()
    export.write()


def main():
    # get the args passed to blender after "--", all of which are ignored by
    # blender so scripts may receive their own arguments
    argv = sys.argv

    if "--" not in argv:
        argv = []  # as if no args are passed
    else:
        argv = argv[argv.index("--") + 1:]  # get all args after "--"

    # When --help or no args are given, print this help
    usage_text = "Run blender in background mode with this script:" \
                 "blender --background --python {} -- [options]".format(__file__)

    parser = argparse.ArgumentParser(description=usage_text)

    # Example utility, add some text and renders or saves it (with options)
    # Possible types are: string, int, long, choice, float and complex.
    parser.add_argument("-o", "--output", dest="save_path", metavar='FILE|PATH',
                        help="Save the generated file to the specified path")
    parser.add_argument("-a", "--enable-animation", dest="enable_animation", action="store_true", default=False,
                        help="Enable saving of animations")
    parser.add_argument("-b", "--bake-all", dest="bake_all", action="store_true", default=False,
                        help="Force animation baking")
    parser.add_argument("-q", "--bake-quaternions", dest="use_quaternions", action="store_true", default=False,
                        help="Use quaternions for rotation baking")
    parser.add_argument("-m", "--apply-modifiers", dest="apply_modifiers", action="store_true", default=False,
                        help="Apply modifiers before exporting")
    parser.add_argument("-r", "--armature-rest", dest="arm_rest", action="store_true", default=False,
                        help="Export static armature in rest position")
    parser.add_argument("-j", "--json-materials", dest="json_materials", action="store_true", default=False,
                        help="Store materials into JSON format")
    parser.add_argument("-s", "--json-shaders", dest="json_shaders", action="store_true", default=False,
                        help="Store shader graphs into JSON format")
    parser.add_argument("--use-scene-fps", dest="use_scene_fps", action="store_true", default=False,
                        help="Use current scene FPS")

    args = parser.parse_args(argv)  # In this example we wont use the args

    if args.save_path is None:
        print("\n*** No output filename specified (use -o)")
    else:
        config = osgconf.Config()
        config.initFilePaths(args.save_path)
        config.export_anim = args.enable_animation
        config.bake_animations = args.bake_all
        config.use_quaternions = args.use_quaternions
        config.apply_modifiers = args.apply_modifiers
        config.arm_rest = args.arm_rest
        config.scene = bpy.context.scene
        config.json_materials = args.json_materials
        config.json_shaders = args.json_shaders
        if args.use_scene_fps:
            config.anim_fps = config.scene.render.fps
        OpenSceneGraphExport(config)

if __name__ == "__main__":
    main()


def menu_export_osg_model(self, context):
    # import os
    # default_path = os.path.splitext(bpy.data.filepath)[0] + "_" + bpy.context.scene.name
    # default_path = default_path.replace('.', '_')
    # self.layout.operator(OSGGUI.bl_idname, text="OSG Model(.osg)").filepath = default_path
    self.layout.operator(OSGGUI.bl_idname, text="OSG Model(.osgt)")


def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_export.append(menu_export_osg_model)


def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_export.remove(menu_export_osg_model)


from bpy.props import *
try:
    from io_utils import ExportHelper
    print("Use old import path - your blender is not the latest version")
except:
    from bpy_extras.io_utils import ExportHelper
    # print("Use new import path")


# Property subtype constant changed with r50938
if "FILE_PATH" in bpy.types.Property.bl_rna.properties['subtype'].enum_items.keys():
    FILE_NAME = "FILE_PATH"
elif "FILE_NAME" in bpy.types.Property.bl_rna.properties['subtype'].enum_items.keys():
    FILE_NAME = "FILE_NAME"
else:
    FILE_NAME = "FILENAME"


class OSGGUI(bpy.types.Operator, ExportHelper):
    '''Export model data to an OpenSceneGraph file'''
    bl_idname = "osg.export"
    bl_label = "OSG Model"

    filename_ext = ".osgt"

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.

    AUTHOR = StringProperty(name="Author", description="Name of the Author of this model", default="")
    SELECTED = BoolProperty(name="Only Export Selected", description="Only export the selected model", default=False)
    ONLY_VISIBLE = BoolProperty(name="Only Export Visible", description="Only export the visible models",
                                default=False)
    INDENT = IntProperty(name="Number of Indent Spaces",
                         description="Number of Spaces to use for indentation in the model file",
                         default=3, min=1, max=8)
    FLOATPRE = IntProperty(name="Floating Point Precision",
                           description="The Floating Point Precision to use in exported model file",
                           min=1, max=8, default=4)
    ANIMFPS = IntProperty(name="Frames Per Second",
                          description="Number of Frames Per Second to use for exported animations",
                          min=1, max=300, default=30)
    EXPORTANIM = BoolProperty(name="Export animations", description="Export animation yes/no",
                              default=True)
    APPLYMODIFIERS = BoolProperty(name="Apply Modifiers", description="Apply modifiers before exporting yes/no",
                                  default=True)
    LOG = BoolProperty(name="Write log", description="Write log file yes/no", default=False)
    JSON_MATERIALS = BoolProperty(name="JSON Materials", description="Export materials into JSON userdata.",
                                  default=False)
    JSON_SHADERS = BoolProperty(name="JSON shaders", description="Export shader graphs into JSON userdata.",
                                default=False)
    BAKE_ALL = BoolProperty(name="Bake all animations", description="Force baking for all animations",
                            default=True)
    USE_QUATERNIONS = BoolProperty(name="Use quaternions", description="Bake rotations using quaternions",
                                   default=True)
    BAKE_CONSTRAINTS = BoolProperty(name="Bake Constraints", description="Bake constraints into actions", default=True)
    BAKE_FRAME_STEP = IntProperty(name="Bake frame step", description="Frame step when baking actions",
                                  default=1, min=1, max=30)
    ARMATURE_REST = BoolProperty(name="Export armature in REST pose",
                                 description="Static armatures are exported in REST mode (instead of POSE)",
                                 default=False)
    OSGCONV_TO_IVE = BoolProperty(name="Convert to IVE (uses osgconv)", description="Use osgconv to convert to IVE",
                                  default=False)
    OSGCONV_EMBED_TEXTURES = BoolProperty(name="Embed textures in IVE", default=False)
    OSGCONV_CLEANUP = BoolProperty(name="Cleanup after conversion", default=False)
    OSGCONV_PATH = StringProperty(name="osgconv path", subtype=FILE_NAME, default="")
    RUN_VIEWER = BoolProperty(name="Run viewer (viewer path)", description="Run viewer after export", default=False)
    VIEWER_PATH = StringProperty(name="viewer path", subtype=FILE_NAME, default="")
    TEXTURE_PREFIX = StringProperty(name="texture prefix", default="")
    EXPORT_ALL_SCENES = BoolProperty(name="Export all scenes", default=False)
    ZERO_TRANSLATIONS = BoolProperty(name="Zero world translations", default=False)

    def draw(self, context):
        layout = self.layout

        layout.row(align=True).label("Author:")
        layout.row(align=True).prop(self, "AUTHOR", text="")
        layout.row(align=True).prop(self, "SELECTED")
        layout.row(align=True).prop(self, "ONLY_VISIBLE")
        layout.row(align=True).prop(self, "EXPORTANIM")
        layout.row(align=True).prop(self, "EXPORT_ALL_SCENES")
        layout.row(align=True).prop(self, "APPLYMODIFIERS")
        layout.row(align=True).prop(self, "BAKE_ALL")
        layout.row(align=True).prop(self, "USE_QUATERNIONS")
        layout.row(align=True).prop(self, "BAKE_CONSTRAINTS")
        layout.row(align=True).prop(self, "ARMATURE_REST")
        layout.row(align=True).prop(self, "LOG")
        layout.row(align=True).prop(self, "JSON_MATERIALS")
        layout.row(align=True).prop(self, "JSON_SHADERS")
        layout.row(align=True).prop(self, "ZERO_TRANSLATIONS")
        layout.row(align=True).prop(self, "ANIMFPS")
        layout.row(align=True).prop(self, "BAKE_FRAME_STEP")
        layout.row(align=True).prop(self, "EXPORT_REST")
        layout.row(align=True).prop(self, "FLOATPRE")
        layout.row(align=True).prop(self, "INDENT")
        layout.row(align=True).label("Texture Prefix:")
        layout.row(align=True).prop(self, "TEXTURE_PREFIX", text="")
        layout.row(align=True).prop(self, "OSGCONV_TO_IVE")
        layout.row(align=True).prop(self, "OSGCONV_EMBED_TEXTURES")
        layout.row(align=True).prop(self, "OSGCONV_CLEANUP")
        layout.row(align=True).prop(self, "OSGCONV_PATH", text="")
        layout.row(align=True).prop(self, "RUN_VIEWER")
        layout.row(align=True).prop(self, "VIEWER_PATH", text="")

    def invoke(self, context, event):
        print("config is " + bpy.utils.user_resource('CONFIG'))
        self.config = osgconf.Config()

        try:
            cfg = os.path.join(bpy.utils.user_resource('CONFIG'), "osgExport.cfg")
            if os.path.exists(cfg):
                with open(cfg, 'rb') as f:
                    self.config = pickle.load(f)
        except Exception:
            pass

        self.config.activate()

        self.SELECTED = (self.config.selected == "SELECTED_ONLY_WITH_CHILDREN")
        self.ONLY_VISIBLE = self.config.only_visible
        self.INDENT = self.config.indent
        self.FLOATPRE = self.config.float_precision
        self.ANIMFPS = context.scene.render.fps

        self.EXPORTANIM = self.config.export_anim
        self.APPLYMODIFIERS = self.config.apply_modifiers
        self.ZERO_TRANSLATIONS = self.config.zero_translations
        self.LOG = self.config.log
        self.BAKE_ALL = self.config.bake_animations
        self.USE_QUATERNIONS = self.config.use_quaternions
        self.BAKE_CONSTRAINTS = self.config.bake_constraints
        self.BAKE_FRAME_STEP = self.config.bake_frame_step
        self.ARMATURE_REST = self.config.arm_rest
        self.OSGCONV_TO_IVE = self.config.osgconv_to_ive
        self.OSGCONV_EMBED_TEXTURES = self.config.osgconv_embed_textures
        self.OSGCONV_PATH = self.config.osgconv_path
        self.OSGCONV_CLEANUP = self.config.osgconv_cleanup
        self.JSON_MATERIALS = self.config.json_materials
        self.JSON_SHADERS = self.config.json_shaders

        self.RUN_VIEWER = self.config.run_viewer
        self.VIEWER_PATH = self.config.viewer_path
        self.TEXTURE_PREFIX = self.config.texture_prefix
        self.EXPORT_ALL_SCENES = self.config.export_all_scenes

        if bpy.data.filepath in self.config.history:
            self.filepath = self.config.history[bpy.data.filepath]

        return super(OSGGUI, self).invoke(context, event)

    def execute(self, context):
        if not self.filepath:
            raise Exception("filepath not set")

        self.config.initFilePaths(self.filepath)

        self.config.history[bpy.data.filepath] = self.filepath

        if self.SELECTED:
            self.config.selected = "SELECTED_ONLY_WITH_CHILDREN"
        else:
            self.config.selected = "ALL"
        self.config.indent = self.INDENT
        self.config.only_visible = self.ONLY_VISIBLE
        self.config.float_precision = self.FLOATPRE
        self.config.anim_fps = self.ANIMFPS
        self.config.export_anim = self.EXPORTANIM
        self.config.apply_modifiers = self.APPLYMODIFIERS
        self.config.log = self.LOG
        self.config.zero_translations = self.ZERO_TRANSLATIONS
        self.config.bake_animations = self.BAKE_ALL
        self.config.use_quaternions = self.USE_QUATERNIONS
        self.config.bake_constraints = self.BAKE_CONSTRAINTS
        self.config.bake_frame_step = self.BAKE_FRAME_STEP
        self.config.arm_rest = self.ARMATURE_REST
        self.config.osgconv_to_ive = self.OSGCONV_TO_IVE
        self.config.osgconv_path = self.OSGCONV_PATH
        self.config.run_viewer = self.RUN_VIEWER
        self.config.viewer_path = self.VIEWER_PATH
        self.config.texture_prefix = self.TEXTURE_PREFIX
        self.config.osgconv_embed_textures = self.OSGCONV_EMBED_TEXTURES
        self.config.export_all_scenes = self.EXPORT_ALL_SCENES
        self.config.osgconv_cleanup = self.OSGCONV_CLEANUP

        try:
            cfg = os.path.join(bpy.utils.user_resource('CONFIG'), "osgExport.cfg")
            with open(cfg, 'wb') as f:
                pickle.dump(self.config, f)
        except Exception:
            pass

        if self.config.export_all_scenes:
            for scene in bpy.data.scenes:
                self.config.scene = scene
                print(self.filepath + "_" + scene.name)
                self.config.initFilePaths(os.path.splitext(self.filepath)[0] + "_" + scene.name)
                print(self.config.fullpath)
                print(self.config.filename)
                OpenSceneGraphExport(self.config)
        else:
            print("FILENAME:" + repr(self.config.filename))
            self.config.scene = bpy.context.scene
            OpenSceneGraphExport(self.config)

        return {'FINISHED'}
