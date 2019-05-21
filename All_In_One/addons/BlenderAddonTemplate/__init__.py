import bpy
import layers_view
import helpers.updater as updater

bl_info = {
    "name": "Material Painter",
    "author": "Antonio Aloisio",
    "version": (0, 0, 1),
    "blender": (2, 7, 8),
    "location": "3D View > Tool Shelve > Mixamo Tab",
    "description": ("Experimental PBR Material painter"),
    "warning": "",  # used for warning icon and text in addons panel
    "wiki_url": "https://github.com/gnuton/MaterialPainter/wiki",
    "tracker_url": "https://github.com/gnuton/MaterialPainter/issues",
    "category": "Texturing"
}


def register():
    layers_view.register()


def unregister():
    layers_view.unregister()


# Add here the packages you wanna to be reloaded when the developer press "Run Script"
pkgs = ["helpers", "libs", "materials_mgr", "layers_view"]
if bpy.__name__ in locals():
    import helpers.package_reloader as pr

    pr.reload(pr)  # auto-reload itself
    pr.PackageReloader().reload_packages(pkgs)

if __name__ == "__main__":
    updater.init(bl_info)
    register()
