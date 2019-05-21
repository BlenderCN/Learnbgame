import bpy
from bpy.props import BoolProperty

def UpdateSpeckleClient(self, context):
    if context.scene.speckle_client is not None:
        addon_prefs = context.user_preferences.addons[__name__].preferences
        context.scene.speckle_client.verbose = addon_prefs.verbose_client


class SpeckleAddonPreferences(bpy.types.AddonPreferences):
    # this must match the addon name, use '__package__'
    # when defining this in a submodule of a python package.
    #bl_idname = __name__
    bl_idname = __package__

    verbose_client = BoolProperty(
            name="Verbose client",
            default=False,
            description="Sets SpeckleClient to output more verbose messages and outputs all responses to console.",
            update=UpdateSpeckleClient,
            )

    def draw(self, context):
        layout = self.layout
        layout.label(text="SpeckleBlender preferences")
        layout.prop(self, "verbose_client")
