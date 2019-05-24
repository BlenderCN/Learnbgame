bl_info = {
    "name": "Custom Icons",
    "author": "batFINGER",
    "location": "UserPrefs > Sound Drivers > Icons",
    "description": "Custom Icons",
    "warning": "Still in Testing",
    "wiki_url": "http://wiki.blender.org/index.php/\
                User:BatFINGER/Addons/Sound_Drivers",
    "version": (1, 0),
    "blender": (2, 7, 6),
    "tracker_url": "",
    "icon": 'NONE',
    "support": 'TESTING',
    "category": "Learnbgame",
}

import bpy

from os import path, listdir
from bpy.types import UILayout, AddonPreferences
from bpy.props import StringProperty, EnumProperty, FloatProperty

icon_value = UILayout.icon
enum_item_icon = UILayout.enum_item_icon
icon_dir = path.join(path.dirname(__file__), "icons")
subs =  [name for name in listdir(icon_dir)
                if path.isdir(path.join(icon_dir, name))]

preview_collections = {}

def get_icon(collection, name):
    pcoll = preview_collections.get("main")
    if pcoll:
        return pcoll.get("%s_%s" % (collection, name))
    return None

class ICONAddonPreferences(AddonPreferences):
    ''' ICON Prefs '''
    bl_idname = __name__
    def enum_previews_from_directory_items(self, context):
        """EnumProperty callback"""
        enum_items = []

        if context is None:
            return enum_items

        # Get the preview collection (defined in register func).
        pcoll = preview_collections["main"]

        i = 0
        for key, thumb in pcoll.items():
            if not key.startswith(self.collection):
                continue

            # lstrip gave wierd results
            name = key.replace("%s_" % self.collection, "")
            enum_items.append((name, name, "", thumb.icon_id, 2**i))
            i += 1

        #pcoll.sd_icons = enum_items
        #pcoll.sd_icons_dir = directory
        return enum_items

    collection = EnumProperty(items=[(n, n, n) for n in subs],
                              name="Item Collections",
                              description="Icons from folder",
                              default = "main",
                              )
    icon_dir = StringProperty(
            name="Icon Directory",
            description="Directory SoundDrivers Uses to store icons",
            subtype='DIR_PATH',
            default=icon_dir,
            )

    icon_preview_zoom = FloatProperty(min=0.5, max=5.0, default=5.0)
    sd_icons = EnumProperty(
            items=enum_previews_from_directory_items,
            )


    def draw(self, context):
        layout = self.layout
        # icon support
        # TODO change collection enum
        # TODO add a new icon
        # TODO copy icon code to clipboard
        for collection in preview_collections:
            layout.template_icon_view(self, "sd_icons", show_labels=True, scale=self.icon_preview_zoom)
            row = layout.row()
            split = row.split(percentage=0.4)
            # TODO fix this collection nightmare
            sub = split.row(align=True)
            sub.prop(self, "collection", text="")
            sub.prop(self, "sd_icons", expand=False, text="")
            split.alignment='LEFT'
            for key, icon in preview_collections[collection].items():
                if not key.startswith(self.collection):
                    continue
                split.label("", icon_value=icon.icon_id)
                
            '''
            # scale the thumb preview
            sub = row.column()
            sub.scale_x = sub.scale_y = 0.4
            sub.prop(self, "icon_preview_zoom", slider=True, text="")
            '''


def register():
    unregister()
    # Note that preview collections returned by bpy.utils.previews
    # are regular py objects - you can use them to store custom data.
    import bpy.utils.previews

    # path to the folder where the icon is
    # the path is calculated relative to this py file inside the addon folder
    # load a preview thumbnail of a file and store in the previews collection
    # use the icon_dir as a base folder

    if not icon_dir or not  path.exists(icon_dir):
        print("WTF.... No Icons")
        return 

    pcoll = bpy.utils.previews.new()
    pcoll.collections = subs

    for sub in subs:
        pcoll.id = sub
        sub_dir = path.join(icon_dir, sub)
        
        # Scan the directory for png files
        icons = []
        for fn in listdir(sub_dir):
            if fn.lower().endswith(".png"):
                icons.append(("%s_%s" % (sub, path.splitext(fn)[0]), fn))

        for key, f in icons:
            pcoll.load(key, path.join(sub_dir, f), 'IMAGE')

    preview_collections["main"] = pcoll

def unregister():
    for pcoll in preview_collections.values():
        bpy.utils.previews.remove(pcoll)

    preview_collections.clear()
