import os
from subprocess import Popen

import bpy


ADDONS_PATH = bpy.utils.user_resource('SCRIPTS', "addons")

PLUGINS_MAX = 100


def addon_path(repo_path):
    name = os.path.basename(repo_path)
    if name.endswith(".git"):
        name = name.replace(".git", "")
    return os.path.join(ADDONS_PATH, name)


class Plug(bpy.types.Operator):
    bl_idname = "system.plug"
    bl_label = "Update plugins"

    # List of plugin repo paths.
    repos = []

    def execute(self, context):
        addon_prefs = context.user_preferences.addons[__package__].preferences
        for i in range(addon_prefs.number_of_plugs):
            exec("self.repos.append(addon_prefs.plug{})".format(i))

        for repo in self.repos:
            # If we have cloned repo already go inside and pull.
            path = addon_path(repo)
            if os.path.isdir(path):
                update_repo(path)
            else:
                clone_repo(repo).wait()

        return {'FINISHED'}


def clone_repo(repo_path):
    return Popen("git clone {}".format(repo_path).split(), cwd=ADDONS_PATH)

def update_repo(addon_path, options=""):
    return Popen("git pull {}".format(options).split(), cwd=addon_path)


class PlugPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    number_of_plugs = bpy.props.IntProperty(name="Number of Plugins",
                                            default=1,
                                            soft_min=1,
                                            soft_max=PLUGINS_MAX)

    for i in range(PLUGINS_MAX):
        exec(('plug{}'
              ' = bpy.props.StringProperty(name="",'
              'description="Path to the git repository for the plugin.")')
             .format(i))

    def draw(self, context):
        layout = self.layout
        layout.operator(Plug.bl_idname, text="Update All")
        layout.prop(self, "number_of_plugs")
        layout.label(text="Plugin repository path.")
        for i in range(self.number_of_plugs):
            layout.prop(self, "plug{}".format(i))
