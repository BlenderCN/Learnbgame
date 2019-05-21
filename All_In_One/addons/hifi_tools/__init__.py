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
    "name": "HiFi Blender Add-on",
    "author": "Matti 'Menithal' Lahtinen",
    "version": (1, 3, 2),
    "blender": (2, 7, 7),
    "location": "File > Import-Export, Materials, Armature",
    "description": "Blender tools to allow for easier Content creation for High Fidelity",
    "warning": "",
    "wiki_url": "",
    "support": "COMMUNITY",
    "category": "Import-Export",
}
default_gateway_server = "http://206.189.208.218"
oauth_api = "https://metaverse.highfidelity.com/user/tokens/new?for_identity=true"
oauth_default = True

import addon_utils
import sys
import logging
import webbrowser
import bpy
from bpy.types import AddonPreferences


from hifi_tools.ext.throttle import throttle

from . import armature
from . import utils
from . import world
from . import files
from .files.hifi_json.operator import *
from .files.fst.operator import *
from .gateway import client as GatewayClient

from hifi_tools.utils.custom import custom_register, custom_unregister, scene_define, scene_delete

# TODO: This is placeholder and will be shut down after more are available.


def on_server_update(self, context):
    user_preferences = context.user_preferences
    addon_prefs = user_preferences.addons[__name__].preferences

    if len(addon_prefs["gateway_server"]) > 0 and len(addon_prefs["gateway_username"]) > 0:
        print("Server address updated" + addon_prefs["gateway_server"])
        result = GatewayClient.routes(addon_prefs["gateway_server"])

        if "oauth" in result:
            addon_prefs["oauth_required"] = result["oauth"]
            addon_prefs["oauth_api"] = result["oauth_api"]
        else:
            addon_prefs["oauth_required"] = False
            addon_prefs["oauth_api"] = ""

    else:
        addon_prefs["oauth_required"] = False
        addon_prefs["oauth_api"] = ""
        addon_prefs["gateway_username"] = ""
        addon_prefs["hifi_oauth"] = ""

    return None


def on_token_update(self, context):
    user_preferences = context.user_preferences
    addon_prefs = user_preferences.addons[__name__].preferences

    wm = context.window_manager
    username = addon_prefs["gateway_username"]

    if len(username) == 0:
        bpy.ops.wm.console_toggle()
        addon_prefs["gateway_token"] = ""
        addon_prefs["message_box"] = "No username set."
        return None

    if not "gateway_server" in addon_prefs.keys():
        addon_prefs["gateway_server"] = default_gateway_server

    server = addon_prefs["gateway_server"]

    if "oauth" in addon_prefs and addon_prefs["oauth"] or oauth_default:
        if addon_prefs["hifi_oauth"] is not None:
            response = GatewayClient.new_token_oauth(
                server, username, addon_prefs["hifi_oauth"])
        else:
            return None
    else:
        response = GatewayClient.new_token(server, username)

    result = response[0]
    message = response[1]
    if result is "Err":
        addon_prefs["gateway_token"] = ""
        addon_prefs["message_box"] = message
        return None

    addon_prefs["gateway_token"] = message
    addon_prefs["message_box"] = ""  # Success! Remember to Save Settings.
    bpy.ops.auth_success.export('INVOKE_DEFAULT')

    return None


class InfoOperator (bpy.types.Operator):
    bl_idname = "ipfs_feature_understand.confirm"

    bl_label = "Enable IPFS"
    bl_options = {'REGISTER', 'INTERNAL'}

    agree = BoolProperty(
        name="Yes", description="I am aware what it means to upload to ipfs via the hifi-ipfs gateway.", default=False)

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.label(
            text="IPFS is Interplanetary File System, https://ipfs.io is a public, ", icon="INFO")

        row = layout.row()
        row.label(
            " distributed file network.")

        row = layout.row()
        row.label(
            "The Hifi-Blender plugin allows to use an experimental services 'hifi-ipfs'")

        row = layout.row()
        row.label(
            "to upload files to the ipfs. ")
        row = layout.row()

        row = layout.row()
        row = layout.row()
        row = layout.row()
        row.label(
            "You can put anything not used as your username.")

        row = layout.row()
        row.label(
            "Save both the name and token somewhere safe. You cannot recover it."
        )

        row = layout.row()
        row.label(
            'You cannot generate new tokens, if a username that has one already.'
        )
        row = layout.row()
        row = layout.row()
        row = layout.row()
        row.label(
            "These credential are 'hifi-ipfs' service specific and the 'hifi-ipfs' service ")
        row = layout.row()
        row.label(
            "set here only tracks what have been uploaded with the username."
        )
        row = layout.row()
        row.label("and where they can be found for convenience.  ")
        row = layout.row()
        row.label(
            "Anything uploaded in another service to the ipfs network cannot be tracked.")
        row = layout.row()
        row = layout.row()
        row = layout.row()
        row.label(
            text=": Anything you put into the IPFS is public for anyone", icon="ERROR")

        row = layout.row()
        row.label(
            "with the url to see and maybe be nearly impossible to remove after ")

        row = layout.row()
        row.label(
            "being distributed / accessed from a public 'ipfs' gateway, unless forgotten.")

        row = layout.row()
        row = layout.row()
        row = layout.row()
        row.label(
            "Are you sure you want to enable the choice to upload on Export? ")
        row = layout.row()
        row.label(
            "(Currently supports avatars only)")

        row = layout.row()

        row.prop(self, "agree")

    @classmethod
    def poll(cls, context):
        return True

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=600, height=400)

    def execute(self, context):
        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__name__].preferences
        if self.agree:
            addon_prefs["ipfs"] = True
        else:
            addon_prefs["ipfs"] = False

        return {'FINISHED'}


class AuthSuccessOperator(bpy.types.Operator):
    bl_idname = "auth_success.export"
    bl_label = ""
    bl_options = {'REGISTER', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return True

    def invoke(self, context, even):
        wm = context.window_manager
        return wm.invoke_popup(self, width=400, height=600)

    def execute(self, context):
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.label(text="Success:", icon="FILE_TICK")
        row = layout.row()
        row.label("Authentication Success! ")
        row = layout.row()
        row.label("Remember to Save Your Settings")


class HifiAddOnPreferences(AddonPreferences):
    bl_idname = __name__
    oventool = StringProperty(name="Oven Tool path (EXPERIMENTAL)",
                                   description="Point this to the High Fidelity Oven tool",
                                   subtype="FILE_PATH")

    ipfs = BoolProperty(name="IPFS (EXPERIMENTAL)",
                        description="Enabled IPFS", update=on_server_update)

    gateway_server = StringProperty(name="HIFI-IPFS Server",
                                    description="API to upload files",
                                    default=default_gateway_server,
                                    update=on_server_update)

    gateway_username = StringProperty(name="HIFI-IPFS Username",
                                      description="Enter any Username for API", default="",
                                      update=on_server_update)

    oauth_required = BoolProperty(default=oauth_default)
    oauth_api = StringProperty(default=oauth_api, options={"HIDDEN"})

    hifi_oauth = StringProperty(name="Hifi OAuth Token",
                                description="Enter an Oauth Token with identity permissions", default="",
                                update=on_token_update)

    gateway_token = StringProperty(name="HIFI-IPFS Token",
                                   description="login to API", default="")

    message_box = StringProperty(
        name="Status", default="", options={"SKIP_SAVE"})

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "oventool")

        if self.ipfs:
            layout.prop(self, "ipfs")
            layout.prop(self, "gateway_server")
            layout.prop(self, "gateway_username")

            if self.oauth_required:
                row = layout.row()
                row.prop(self, "hifi_oauth")

                if len(self.hifi_oauth) == 0:
                    row.operator(HifiGenerateToken.bl_idname)
            else:
                row = layout.row()
                row.prop(self, "gateway_token")

                if len(self.gateway_token) == 0:
                    row.operator(GatewayGenerateToken.bl_idname)

            if len(self.message_box):
                layout.prop(self, "message_box")
        else:
            layout.operator(InfoOperator.bl_idname)


class HifiGenerateToken(bpy.types.Operator):
    bl_idname = "hifi.generate_token"
    bl_label = "Get Hifi Identity Token"

    def execute(self, context):

        user_preferences = context.user_preferences
        addon_prefs = user_preferences.addons[__name__].preferences

        if "oauth_api" not in addon_prefs:
            addon_prefs["oauth_api"] = oauth_api

        if "windows-default" in webbrowser._browsers:
            webbrowser.get("windows-default").open(addon_prefs["oauth_api"])
        else:
            webbrowser.open(addon_prefs["oauth_api"])

        return {'FINISHED'}


class GatewayGenerateToken(bpy.types.Operator):
    bl_idname = "gateway.generate_token"
    bl_label = "Generate Token"

    def execute(self, context):

        on_token_update(self, context)

        # TODO: Suggest to save as token can only be generated once, until password is added to this.

        return {'FINISHED'}


if "add_mesh_extra_objects" not in addon_utils.addons_fake_modules:
    print(" Could not find add_mesh_extra_objects, Trying to add it automatically. Otherwise install it first via Blender Add Ons")
    addon_utils.enable("add_mesh_extra_objects")


def reload_module(name):
    if name in sys.modules:
        del sys.modules[name]


def menu_func_import(self, context):
    self.layout.operator(JSONLoaderOperator.bl_idname,
                         text="HiFi Metaverse Scene JSON (.json)")


def menu_func_export(self, context):
    self.layout.operator(FSTWriterOperator.bl_idname,
                         text="HiFi Avatar FST (.fst)")
    self.layout.operator(JSONWriterOperator.bl_idname,
                         text="HiFi Metaverse Scene JSON / FBX (.json/.fbx)")


def register():
    scene_define()
    bpy.utils.register_module(__name__)  # Magic Function!
    bpy.types.INFO_MT_file_import.append(menu_func_import)
    bpy.types.INFO_MT_file_export.append(menu_func_export)


def unregister():
    scene_delete()
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_import.remove(menu_func_import)
    bpy.types.INFO_MT_file_export.remove(menu_func_export)


if __name__ == "__main__":
    register()
