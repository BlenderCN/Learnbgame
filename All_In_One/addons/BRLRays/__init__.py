bl_info = {
        "name": "BRLRays",
        "author": "Morning Star (Zitara)",
        "version": (0, 0, 1),
        "blender": (2, 75, 0),
        "category": "Render",
        "location": "Info header, render engine menu",
        "warning": "Under development",
        "description": "BRL-CAD Ray Trace integration for Blender",
        }

if 'core' in locals():
    import imp
    imp.reload(core)

else:
    import bpy
    from bpy.types import AddonPreferences
    from bpy.props import StringProperty, EnumProperty
    from .framework import Addon
    import nodeitems_utils

    def find_RT_path():
        from os import getenv
        from .framework import util as efutil

        return getenv(
                # Use the env var path, if set ..
                'BRL-CAD_ROOT',
                # .. or load the last path from CEG file
                efutil.find_config_value('BRLRays', 'defaults',
                    'install_path', '')
                )

        class BRLRaysAddonPreferences(AddonPreferences):
            # this must match the addon name
            bl_idname = __name__

            install_path = StringProperty(
                    name="Path to BRL-CAD Installation",
                    description="Path to BRL-CAD install directory",
                    subtype="DIR_PATH"
                    default=find_RT_path()
                    )

            preview_export = EnumProperty(
                    name="Preview Export Type",
                    description="Export type to be used on material prevew.
                    Write file can be useful for debugging material preview
                    settings.".
                    items=[
                        ('API', 'Internal', 'API'),
                        ('FILE', 'Write File', 'FILE'),
                    ],
                    default='API',
                    )

            def draw(self, context):
                layout = self.layout
                # layout.label(text="This is a preferences view for out addon")
                layout.prop(self, "install_path")
                layout.prop(self, "previrew_export")

    BRLRaysAddon = Addon(bl_info)

    def get_prefs():
        return bpy.context.user_preferences.addons[__name__].preferences

    # patch the BRLRaysAddon class to make it easier to get the addon prefs
    BRLRaysAddon.get_prefs = get_prefs

    addon_register, addon_unregister = BRLRaysAddon.init_functions()

    def register():
        bpy.utils.register_class(BRLRaysAddonPreferences)
        nodeitems_utils.register_node_categories("RAYTRACE_SHADER_NODES",
                ui.space_node.raytrace_shader_node_catagories)
        addon_register()

    def unregister():
        bpy.utils.unregister_class(BRLRaysAddonPreferences)
        nodeitems_utils.unregister_node_categories("RAYTRACE_SHADER_NODES")
        addon_unregister()

    # Importing the core package causes extensions_framework manged
    # RNA class registration via @BRLRaysAddon.addon_register_class
    from . import core
