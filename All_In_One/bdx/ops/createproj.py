import os
import bpy
import shutil
import subprocess
from .. import utils as ut

j = os.path.join

class CreateBdxProject(bpy.types.Operator):
    """Create BDX project"""
    bl_idname = "scene.create_bdx_project"
    bl_label = "Create BDX project"

    def create_libgdx_project(self):
        sc_bdx = bpy.context.scene.bdx

        if (not sc_bdx.android_sdk.strip()):
            sc_bdx.android_sdk = j(os.getcwd(), "android-sdk")

        absp = bpy.path.abspath

        if ut.in_packed_bdx_blend():
            sc_bdx.base_path = absp("//")
            sc_bdx.java_pack = ut.internal_java_package()
            blend_name = os.path.basename(bpy.data.filepath).split('.')[0]
            sc_bdx.proj_name = blend_name
            sc_bdx.dir_name = sc_bdx.proj_name

        fmt = {"program": j(ut.gen_root(), "gdx-setup.jar"),
               "dir": j(absp(sc_bdx.base_path), sc_bdx.dir_name),
               "name": sc_bdx.proj_name,
               "package": sc_bdx.java_pack,
               "mainClass": "BdxApp",
               "sdkLocation": absp(sc_bdx.android_sdk)}

        cmd = ["java", "-jar", fmt["program"],
               "--dir", fmt["dir"],
               "--name", fmt["name"],
               "--package", fmt["package"],
               "--mainClass", fmt["mainClass"],
               "--sdkLocation", fmt["sdkLocation"]]

        subprocess.check_call(cmd)

        ut.proot = fmt["dir"]


    def create_android_assets_bdx(self):
        """Creates the bdx directory structure in android/assets"""
        bdx = j(ut.project_root(), "android", "assets", "bdx")
        os.mkdir(bdx)
        os.mkdir(j(bdx, "scenes"))
        textures = j(bdx, "textures")
        os.mkdir(textures)
        os.mkdir(j(bdx, "audio"))
        os.mkdir(j(bdx, "audio", "sounds"))
        os.mkdir(j(bdx, "audio", "music"))
        os.mkdir(j(bdx, "fonts"))
        os.mkdir(j(bdx, "shaders"))
        shaders2D = j(bdx, "shaders", "2d")
        shaders3D = j(bdx, "shaders", "3d")
        os.mkdir(shaders2D)
        os.mkdir(shaders3D)

        for png in ut.listdir(ut.gen_root(), pattern="*.png"):
            shutil.copy(png, textures)
            
        for frag in ut.listdir(j(ut.gen_root(), "shaders", "2d"), pattern="*.frag"):
            shutil.copy(frag, shaders2D)  
        for vert in ut.listdir(j(ut.gen_root(), "shaders", "2d"), pattern="*.vert"):
            shutil.copy(vert, shaders2D)
        for frag in ut.listdir(j(ut.gen_root(), "shaders", "3d"), pattern="*.frag"):
            shutil.copy(frag, shaders3D)  
        for vert in ut.listdir(j(ut.gen_root(), "shaders", "3d"), pattern="*.vert"):
            shutil.copy(vert, shaders3D)
            
    def create_blender_assets(self):
        """
        Creates the blender directory in the root project,
        for .blends, and other assorted production resources.

        """
        blender = j(ut.project_root(), "blender")
        os.mkdir(blender)
        
        shutil.copy(j(ut.gen_root(), "game.blend"), blender)

    def replace_build_gradle(self):
        """Replaces the build.gradle file with a version that includes BDX dependencies"""
        bdx_build_gradle = j(ut.gen_root(), "build.gradle")
        gdx_build_gradle = j(ut.project_root(), "build.gradle")
        shutil.copy(bdx_build_gradle, gdx_build_gradle)

        sc_bdx = bpy.context.scene.bdx
        ut.set_file_var(gdx_build_gradle, "appName", "'{}'".format(sc_bdx.proj_name))

    def set_android_sdk_version(self):
        """
        Gets latest available buildToolsVersion and compileSdkVersion,
        and sets corresponding lines in android/build.gradle
        
        """
        def get_version_dir_name(path, sort_key, default):
            if os.path.exists(path):
                return sorted(os.listdir(path), key=sort_key)[-1]
            return default
            
        def set_version(pattern, version):
            android_build_gradle_dir = j(ut.project_root(), "android", "build.gradle")
            new_line = '    ' + pattern + ' ' + version
            ut.replace_line_containing(android_build_gradle_dir, pattern, new_line)
            
        def build_tools_sort_key(strv):
            h, t, o = strv.split('.')
            return int(h) * 100 + int(t) * 10 + int(o)
            
        def compile_sdk_sort_key(strv):
            return int(strv.split('-')[-1])
            
        android_sdk_dir = bpy.context.scene.bdx.android_sdk
        
        build_tools_dir = j(android_sdk_dir, "build-tools")
        build_tools_version = get_version_dir_name(build_tools_dir, build_tools_sort_key, "20.0.0")
        set_version("buildToolsVersion", '"' + build_tools_version + '"')
        
        platforms_dir = j(android_sdk_dir, "platforms")
        compile_sdk_version = get_version_dir_name(platforms_dir, compile_sdk_sort_key, "20")
        set_version("compileSdkVersion", compile_sdk_version.split('-')[-1])

    def replace_app_class(self):
        """Replaces the LibGDX app class with the BDX app class"""
        n = "BdxApp.java"
        bdx_app = j(ut.gen_root(), n)
        gdx_app = j(ut.src_root(), n)
        shutil.copy(bdx_app, gdx_app)

        ut.set_file_line(gdx_app, 1,
                         "package " + bpy.context.scene.bdx.java_pack + ';')

    def replace_desktop_launcher(self):
        n = "DesktopLauncher.java"
        bdx_dl = j(ut.gen_root(), n)
        gdx_dl = j(ut.src_root("desktop", n), n)
        shutil.copy(bdx_dl, gdx_dl);

        sc_bdx = bpy.context.scene.bdx

        ut.set_file_line(gdx_dl, 1,
                         "package " + sc_bdx.java_pack + '.desktop;')

        ut.set_file_line(gdx_dl, 5,
                         "import " + sc_bdx.java_pack + ".BdxApp;")

    def replace_android_launcher(self):
        n = "AndroidLauncher.java"
        bdx_al = j(ut.gen_root(), n)
        gdx_al = j(ut.src_root("android", n), n)
        shutil.copy(bdx_al, gdx_al)

        sc_bdx = bpy.context.scene.bdx

        ut.set_file_line(gdx_al, 1,
                         "package " + sc_bdx.java_pack + '.android;')

        ut.set_file_line(gdx_al, 8,
                         "import " + sc_bdx.java_pack + ".BdxApp;")

    def copy_bdx_libs(self):
        bdx_libs = j(ut.plugin_root(), "libs")
        libs = j(ut.project_root(), "core", "libs")
        shutil.copytree(bdx_libs, libs)

    def open_default_blend(self):
        fp = j(ut.project_root(), "blender", "game.blend")
        try:
            bpy.ops.wm.open_mainfile(filepath=fp)
        except RuntimeError as e:
            print(e)

    def fix_texture_links(self):
        textures = j(ut.project_root(), "android", "assets", "bdx", "textures")
        bpy.ops.file.find_missing_files(directory=textures)

    def update_bdx_xml(self):
        proot = ut.project_root()
        bdx_xml = j(proot, "core/src/BdxApp.gwt.xml")
        ut.insert_lines_after(bdx_xml, "<module>", ["	<inherits name='com.Bdx' />"])

    def make_current_blend_default(self):
        shutil.move(bpy.data.filepath, j(ut.project_root(), "blender", "game.blend"))

    def unpack_resources(self):
        # sort out music from sound
        def _music(s):
            head, tail = os.path.split(s.filepath)
            _, dir_name = os.path.split(head)
            if dir_name == "music":
                return True
            return False

        music = [s.name for s in bpy.data.sounds if _music(s)]

        # dump it all
        bpy.ops.file.unpack_all()

        # move textures
        proot = ut.project_root()
        unpacked_textures = j(proot, "blender", "textures") 
        if os.path.isdir(unpacked_textures):
            bdx = j(proot, "android", "assets", "bdx")
            shutil.rmtree(j(bdx, "textures"))
            shutil.move(unpacked_textures, bdx)

        # move audio
        unpacked_sounds = j(proot, "blender", "sounds")
        if os.path.isdir(unpacked_sounds):
            audio = ut.listdir(unpacked_sounds)
            for fp in audio:
                if os.path.basename(fp) in music:
                    adir = "music"
                else:
                    adir = "sounds"
                shutil.move(fp, j(bdx, "audio", adir))

            shutil.rmtree(unpacked_sounds)

    def set_internal_package(self):
        sacky_java = bpy.data.texts["Sacky.java"]
        sacky_java.lines[0].body = "package " + ut.package_name() + ';'


    def execute(self, context):
        context.window.cursor_set("WAIT")

        self.create_libgdx_project()
        self.create_android_assets_bdx()
        self.create_blender_assets()
        self.replace_build_gradle()
        self.set_android_sdk_version()
        self.replace_app_class()
        self.replace_desktop_launcher()
        self.replace_android_launcher()
        self.copy_bdx_libs()
        self.update_bdx_xml()

        if ut.in_packed_bdx_blend():
            self.make_current_blend_default()
            self.open_default_blend()
            self.unpack_resources()
        else:
            self.open_default_blend()
            self.set_internal_package()

        self.fix_texture_links()
        bpy.ops.wm.save_mainfile()

        ut.proot = None

        #context.window.cursor_set("DEFAULT")

        return {'FINISHED'}


def register():
    bpy.utils.register_class(CreateBdxProject)


def unregister():
    bpy.utils.unregister_class(CreateBdxProject)
