import os

# --------------------------------------------------------------------------------
#  Custom Icons
# --------------------------------------------------------------------------------
custom_icons = {}

def registerCustomIcon():
    import bpy.utils.previews
    pcoll = bpy.utils.previews.new()
    script_path = os.path.dirname(__file__)
    icons_dir = os.path.join(script_path, "icons")
    pcoll.load("haydee_icon", os.path.join(icons_dir, "icon.png"), 'IMAGE')
    custom_icons["main"] = pcoll


def unregisterCustomIcon():
    import bpy.utils.previews
    for pcoll in custom_icons.values():
        bpy.utils.previews.remove(pcoll)
    custom_icons.clear()


