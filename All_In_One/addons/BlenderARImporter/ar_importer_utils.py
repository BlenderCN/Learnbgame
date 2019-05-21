
import bpy
from bpy.props import *
from bpy.types import Menu, Operator, Panel, UIList, AddonPreferences
from bpy.app.handlers import persistent
import os
from os.path import basename, dirname, join
import shutil
import requests

class ARImporterAddonPreferences(AddonPreferences):

    bl_idname = basename(dirname(__file__))  # directory name containing this file

    ip_address = StringProperty(
            name="IP Address",
            )

    ar_root = StringProperty(
            name="Storage root",
            subtype='FILE_PATH',
            )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "ip_address")
        layout.prop(self, "ar_root")

# -------------------------------------------------------------------------------
# UI PANEL - Extra Image List
# -------------------------------------------------------------------------------
class ARImporter_PT_ImagePreview(Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "AR Importer"
    bl_label = "Import"

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator("arimporter.latest", text="Import Latest")


class ARImportLatest(Operator):
    bl_idname = "arimporter.latest"
    bl_label = "Latest"
    bl_description = "AR Import Latest"

    def execute(self, context):
        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[basename(dirname(__file__))].preferences
        root_url = "http://%s/" % addon_prefs.ip_address

        print("Importing latest " + addon_prefs.ip_address)
        resp = requests.get(root_url + "shots").json()
        latest = resp[0]
        print(latest)
        local_shot_dir = join(addon_prefs.ar_root, latest["uuid"])

        file_types = ["_pointcloud_z.ply", ".mov", "_scene.fbx"]
        try:
            # Create target Directory
            os.mkdir(local_shot_dir)
        except FileExistsError:
            print("Directory ", local_shot_dir, " already exists")

        local_files = []
        for file_type in file_types:
            remote_url  = root_url + "content/shots/%s/shot-%s%s" % (latest["uuid"], latest["uuid"], file_type)
            file_basename = basename(remote_url)
            local_file = join(local_shot_dir, file_basename)
            local_files.append(local_file)
            r = requests.get(remote_url, allow_redirects=True)
            open(local_file, 'wb').write(r.content)

        for local_file in local_files:
            if local_file.endswith(".fbx"):
                bpy.ops.import_scene.fbx(filepath=local_file, anim_offset=0, bake_space_transform=True)
            if local_file.endswith(".ply"):
                bpy.ops.import_mesh.ply(filepath=local_file)
            if local_file.endswith(".mov"):
                clip = bpy.data.movieclips.load(local_file)
                for area in bpy.context.screen.areas:
                    if area.type == 'VIEW_3D':
                        space_data = area.spaces.active
                        space_data.show_background_images = True
                        bg = space_data.background_images.new()
                        bg.clip = clip
                        bg.source = 'MOVIE_CLIP'
                        bg.use_camera_clip = False
                        bg.opacity = 1
                        break

        return {'FINISHED'}


