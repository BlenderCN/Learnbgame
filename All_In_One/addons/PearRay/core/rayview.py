import bpy
import os
import sys
import subprocess

from .. import export

pearray_package = __import__(__name__.split('.')[0])


class RayView(bpy.types.Operator):
    bl_idname = "pearray.run_rayview"
    bl_label = "Run RayView"

    @staticmethod
    def _locate_binary():
        addon_prefs = bpy.context.user_preferences.addons[pearray_package.__package__].preferences

        # Use the system preference if its set.
        rayview_binary = bpy.path.resolve_ncase(bpy.path.abspath(addon_prefs.executable_dir + "/rayview" + (".exe" if sys.platform[:3] == "win" else "")))
        if rayview_binary:
            if os.path.exists(rayview_binary):
                return rayview_binary
            else:
                print("User Preferences path to rayview %r NOT FOUND, checking $PATH" % rayview_binary)

        # Windows Only
        if sys.platform[:3] == "win":
            import winreg
            win_reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                "Software\\PearRay\\v0.9\\Windows")
            win_home = winreg.QueryValueEx(win_reg_key, "Home")[0]
            
            rayview_binary = os.path.join(win_home, "bin", "rayview.exe")
            if os.path.exists(rayview_binary):
                return rayview_binary

        # search the path all os's
        rayview_binary_default = "rayview"

        os_path_ls = os.getenv("PATH").split(':') + [""]

        for dir_name in os_path_ls:
            rayview_binary = os.path.join(dir_name, rayview_binary_default)
            if os.path.exists(rayview_binary):
                return rayview_binary
        return ""

    def execute(self, context):
        import tempfile

        scene = context.scene

        if not scene:
            return {'CANCELLED'}

        render = scene.render

        scene.frame_set(scene.frame_current)

        renderPath = bpy.path.resolve_ncase(bpy.path.abspath(render.filepath))

        if scene.pearray.keep_prc:
            sceneFile = os.path.normpath(renderPath + "/scene.prc")
        else:
            sceneFile = tempfile.NamedTemporaryFile(suffix=".prc").name

        self.report({'INFO'}, "PearRay: Exporting data")
        scene_exporter = export.Exporter(sceneFile, scene)
        scene_exporter.write_scene()

        rayview_binary = RayView._locate_binary()
        if not rayview_binary:
            self.report({'ERROR'}, "PearRay: could not execute rayview, possibly RayView isn't installed")
            return {'CANCELLED'}
        
        args = [sceneFile]
        try:
            if sys.platform[:3] == "win":
                DETACHED_PROCESS = 0x00000008
                CREATE_NEW_PROCESS_GROUP = 0x00000200
                subprocess.Popen([rayview_binary] + args, creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                subprocess.Popen([rayview_binary] + args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except OSError:
            self.report({'ERROR'}, "PearRay: could not execute '%s'" % rayview_binary)
            import traceback
            traceback.print_exc()
            return {'CANCELLED'}

        else:
            print ("Command line arguments passed: " + str(args))
        
        return {'FINISHED'}